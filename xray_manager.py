# xray_manager.py — Xray Core control plane (VLESS / Trojan / VMess / Shadowsocks over WebSocket)
#
# v2.1.0: a second inbound speaks Trojan over WebSocket on its own loopback port.
# Both inbounds carry every config (user email = config uuid, so traffic accounting
# stays per-config no matter which protocol the client picked); the panel's gateway
# decides which protocols a config may actually use.
#
# What changed vs v1.0.0:
#   * no more blocking time.sleep() inside the event loop (spawn runs in a thread)
#   * every config UUID lives in Xray; access control (on/off, quota, expiry, IP and
#     speed limits) is enforced by the panel's WS gateway, so toggling a config no
#     longer restarts Xray and kicks every other user
#   * new/deleted configs are hot-added/removed through the Xray API when possible,
#     with a debounced full reload as fallback
#   * supervisor restarts Xray automatically if it crashes
#   * stats poller returns deltas; main.py owns accounting
import asyncio
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from collections import deque
from datetime import datetime
from pathlib import Path

WS_PORT = int(os.environ.get("XRAY_WS_PORT", 31801))
TROJAN_WS_PORT = int(os.environ.get("XRAY_TROJAN_WS_PORT", 31802))
VMESS_WS_PORT = int(os.environ.get("XRAY_VMESS_WS_PORT", 31803))
SS_WS_PORT = int(os.environ.get("XRAY_SS_WS_PORT", 31804))
API_PORT = int(os.environ.get("XRAY_API_PORT", 20085))
INBOUND_TAG = "vless-ws"
TROJAN_TAG = "trojan-ws"
VMESS_TAG = "vmess-ws"
SS_TAG = "ss-ws"
INBOUND_TAGS = (INBOUND_TAG, TROJAN_TAG, VMESS_TAG, SS_TAG)
TAG_FOR_PROTO = {"vless": INBOUND_TAG, "trojan": TROJAN_TAG, "vmess": VMESS_TAG, "ss": SS_TAG}
PORTS = {INBOUND_TAG: WS_PORT, TROJAN_TAG: TROJAN_WS_PORT, VMESS_TAG: VMESS_WS_PORT, SS_TAG: SS_WS_PORT}
PATHS = {INBOUND_TAG: "/ws", TROJAN_TAG: "/trojan", VMESS_TAG: "/vmess", SS_TAG: "/ss"}
PROTOCOL_OF = {INBOUND_TAG: "vless", TROJAN_TAG: "trojan", VMESS_TAG: "vmess", SS_TAG: "shadowsocks"}
SS_METHOD = "chacha20-ietf-poly1305"

_LOG_BUF = deque(maxlen=1500)

BIN_NAME = "xray.exe" if sys.platform.startswith("win") else "xray"
LOCAL_BIN_DIR = Path(__file__).parent / "bin"

XRAY_BIN = None
XRAY_PROC = None
XRAY_VERSION = ""
_stdout_fh = None
_links = None
_lock = None
_logger = None
_data_dir = Path(os.environ.get("DATA_DIR", "/data"))
_known_users: dict = {}   # uuid -> trojan password currently loaded in the core
_reload_pending = False
_restart_count = 0
_started_at = None


# ---------------------------------------------------------------- logging
def _push(level, msg):
    _LOG_BUF.append((datetime.now().isoformat(timespec="seconds"), level, str(msg)))
    if _logger:
        getattr(_logger, "warning" if level in ("warning", "error") else "info")("[xray] " + str(msg).splitlines()[0])


def _log(msg, level="info"):
    _push(level, msg)


def get_logs(limit=300, level=None):
    items = list(_LOG_BUF)
    if level:
        items = [x for x in items if x[1] == level]
    items = items[-max(1, min(int(limit or 300), 1500)):]
    return [{"time": t, "level": lv, "msg": m} for t, lv, m in items]


def clear_logs():
    _LOG_BUF.clear()


def register(links, lock, logger_obj, data_dir):
    global _links, _lock, _logger, _data_dir
    _links, _lock, _logger, _data_dir = links, lock, logger_obj, Path(data_dir)


# ---------------------------------------------------------------- binary
def find_binary():
    global XRAY_BIN
    if XRAY_BIN and Path(XRAY_BIN).exists():
        return XRAY_BIN
    for c in (os.environ.get("XRAY_BIN"), "/usr/local/bin/xray", "/usr/bin/xray", str(LOCAL_BIN_DIR / BIN_NAME)):
        if c and Path(c).exists():
            XRAY_BIN = Path(c)
            return XRAY_BIN
    found = shutil.which("xray") or shutil.which("xray.exe")
    if found:
        XRAY_BIN = Path(found)
        return XRAY_BIN
    raise RuntimeError("Xray binary not found")


def _detect_version():
    global XRAY_VERSION
    try:
        r = subprocess.run([str(find_binary()), "version"], capture_output=True, text=True, timeout=5)
        out = (r.stdout or "") + (r.stderr or "")
        XRAY_VERSION = out.splitlines()[0].strip() if out.strip() else "unknown"
    except Exception as e:
        _log("could not detect version: " + str(e), "warning")
        XRAY_VERSION = "unknown"


# ---------------------------------------------------------------- config
def _client(uid):
    return {"id": uid, "email": uid, "level": 0}


def trojan_password(uid):
    """Per-config Trojan password. Falls back to the uuid for pre-2.1 configs."""
    link = (_links or {}).get(uid) or {}
    return str(link.get("trojan_password") or uid)


def ss_password(uid):
    link = (_links or {}).get(uid) or {}
    return str(link.get("ss_password") or uid)


def _creds(uid):
    return {"trojan": trojan_password(uid), "ss": ss_password(uid)}


def _user_map():
    return {uid: _creds(uid) for uid in list((_links or {}).keys())}


def _client_for(tag, uid):
    if tag == INBOUND_TAG:
        return _client(uid)
    if tag == TROJAN_TAG:
        return {"password": trojan_password(uid), "email": uid, "level": 0}
    if tag == VMESS_TAG:
        return {"id": uid, "alterId": 0, "email": uid, "level": 0}
    return {"method": SS_METHOD, "password": ss_password(uid), "email": uid, "level": 0}


def _settings_for(tag, uids):
    clients = [_client_for(tag, u) for u in uids]
    if tag == INBOUND_TAG:
        return {"clients": clients, "decryption": "none"}
    if tag == SS_TAG:
        return {"clients": clients, "network": "tcp,udp"}
    return {"clients": clients}


def _build_config():
    uids = list((_links or {}).keys())
    inbounds = []
    for tag in INBOUND_TAGS:
        # TLS is terminated by the platform edge (Railway) and the panel gateway,
        # so every inbound here is plain WebSocket on loopback.
        inbounds.append({"tag": tag, "listen": "127.0.0.1", "port": PORTS[tag],
                         "protocol": PROTOCOL_OF[tag], "settings": _settings_for(tag, uids),
                         "streamSettings": {"network": "ws", "wsSettings": {"path": PATHS[tag]}},
                         "sniffing": {"enabled": False}})
    inbounds.append({"tag": "api", "listen": "127.0.0.1", "port": API_PORT,
                     "protocol": "dokodemo-door", "settings": {"address": "127.0.0.1"}})
    return {
        "log": {"loglevel": "warning"},
        # Railway containers can advertise a broken/slow IPv6 route. Prefer
        # IPv4 for DNS answers and outbound connections.
        "dns": {"servers": ["1.1.1.1", "8.8.8.8"], "queryStrategy": "UseIPv4"},
        "api": {"tag": "api", "services": ["StatsService", "HandlerService"]},
        "stats": {},
        "policy": {
            "levels": {"0": {"statsUserUplink": True, "statsUserDownlink": True, "connIdle": 300, "handshake": 8}},
            "system": {"statsInboundUplink": True, "statsInboundDownlink": True},
        },
        "routing": {"rules": [{"type": "field", "inboundTag": ["api"], "outboundTag": "api"}]},
        "inbounds": inbounds,
        "outbounds": [{"protocol": "freedom", "tag": "direct", "settings": {"domainStrategy": "UseIPv4"}}],
    }


def _write_config():
    _data_dir.mkdir(parents=True, exist_ok=True)
    path = _data_dir / "xray_config.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(_build_config(), indent=2), encoding="utf-8")
    tmp.replace(path)
    return path


def _validate_config(cfg_path):
    try:
        r = subprocess.run([str(find_binary()), "run", "-test", "-c", str(cfg_path)],
                           capture_output=True, text=True, timeout=15)
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        return r.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, "xray -test timed out"
    except Exception as e:
        return False, str(e)


def _probe(host, port, timeout=0.25):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        return s.connect_ex((host, port)) == 0
    except Exception:
        return False
    finally:
        s.close()


def is_running():
    return bool(XRAY_PROC and XRAY_PROC.poll() is None)


# ---------------------------------------------------------------- process (runs in a worker thread)
def _spawn_sync():
    global XRAY_PROC, _stdout_fh, _known_users, _started_at
    try:
        binary = find_binary()
    except RuntimeError as e:
        _log(str(e), "error")
        return False
    cfg_path = _write_config()
    ok, msg = _validate_config(cfg_path)
    if not ok:
        _log("config invalid:\n" + msg, "error")
        return False
    try:
        if _stdout_fh:
            _stdout_fh.close()
    except Exception:
        pass
    _stdout_fh = open(_data_dir / "xray_stdout.log", "ab", buffering=0)
    _stdout_fh.write(("\n=== xray start " + datetime.now().isoformat() + " ===\n").encode())
    kwargs = {"creationflags": 0x08000000} if sys.platform.startswith("win") else {}
    XRAY_PROC = subprocess.Popen([str(binary), "run", "-c", str(cfg_path)],
                                 stdout=_stdout_fh, stderr=subprocess.STDOUT, **kwargs)
    _known_users = _user_map()
    _started_at = time.time()
    for _ in range(40):  # up to ~8s for the inbounds to come up
        if XRAY_PROC.poll() is not None:
            _log("xray exited immediately (code %s)" % XRAY_PROC.returncode, "error")
            _dump_logs()
            return False
        if all(_probe("127.0.0.1", PORTS[t]) for t in INBOUND_TAGS):
            _log("xray up pid=%s inbounds=%s api=%s"
                 % (XRAY_PROC.pid, ",".join("%s:%d" % (t, PORTS[t]) for t in INBOUND_TAGS), API_PORT))
            return True
        time.sleep(0.2)
    _log("xray started but not every inbound port is listening", "warning")
    return XRAY_PROC.poll() is None


def _stop_sync():
    global XRAY_PROC
    p = XRAY_PROC
    if p and p.poll() is None:
        try:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait(timeout=2)
        except Exception:
            pass
    XRAY_PROC = None


def _dump_logs():
    p = _data_dir / "xray_stdout.log"
    if p.exists():
        try:
            tail = p.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]
            _log("--- xray_stdout.log (tail) ---\n" + "\n".join(tail), "error")
        except Exception:
            pass


# ---------------------------------------------------------------- async API
async def start():
    # Keep binary inspection and process startup off the web server's event loop.
    # Railway should be able to serve /health and the panel while Xray boots.
    await asyncio.to_thread(_detect_version)
    _log("starting " + (XRAY_VERSION or "xray"))
    ok = await asyncio.to_thread(_spawn_sync)
    asyncio.create_task(_supervisor())
    return ok


async def stop():
    await asyncio.to_thread(_stop_sync)
    try:
        if _stdout_fh:
            _stdout_fh.close()
    except Exception:
        pass
    _log("stopped")


async def reload_config():
    _log("reloading xray")
    await asyncio.to_thread(_stop_sync)
    await asyncio.sleep(0.2)
    return await asyncio.to_thread(_spawn_sync)


async def _api_call(subcmd, *args, timeout=6.0):
    # Go's flag parser stops at the first positional arg, so --server must come
    # right after the sub-command (the old code put it last and every call failed).
    proc = await asyncio.create_subprocess_exec(
        str(find_binary()), "api", subcmd, "--server=127.0.0.1:" + str(API_PORT), *args,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError("xray api timeout")
    if proc.returncode != 0:
        raise RuntimeError((err or out).decode(errors="replace").strip() or "xray api failed")
    return out.decode(errors="replace")


async def _adu(inbound):
    fd, path = tempfile.mkstemp(suffix=".json", dir=str(_data_dir))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"inbounds": [inbound]}, f)
        await _api_call("adu", path)
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


async def _hot_add(uids):
    for tag in INBOUND_TAGS:
        await _adu({"tag": tag, "protocol": PROTOCOL_OF[tag], "settings": _settings_for(tag, uids)})


async def _hot_remove(uids):
    for tag in INBOUND_TAGS:
        await _api_call("rmu", "-tag=" + tag, *uids)


async def sync_users():
    """Make Xray's user list match LINKS. Hot-patch first, reload as fallback."""
    global _known_users
    current = _user_map()
    added = sorted(u for u in current if _known_users.get(u) != current[u])   # new or rotated creds
    removed = sorted(u for u in _known_users if u not in current)
    if not added and not removed:
        return
    await asyncio.to_thread(_write_config)  # keep the on-disk config truthful for restarts
    if not is_running():
        await reload_config()
        return
    try:
        rotated = [u for u in added if u in _known_users]
        if removed or rotated:
            await _hot_remove(sorted(set(removed) | set(rotated)))
        if added:
            await _hot_add(added)
        _known_users = current
        _log("users synced live (+%d / -%d)" % (len(added), len(removed)))
    except Exception as e:
        _log("live user sync failed (%s), doing full reload" % e, "warning")
        await reload_config()


def request_sync():
    """Debounced: several quick creates/deletes collapse into a single sync."""
    global _reload_pending
    if _reload_pending:
        return
    _reload_pending = True

    async def _later():
        global _reload_pending
        await asyncio.sleep(1.0)
        _reload_pending = False
        try:
            await sync_users()
        except Exception as e:
            _log("sync error: " + str(e), "warning")

    asyncio.get_event_loop().create_task(_later())


async def _supervisor():
    global _restart_count
    backoff = 2
    while True:
        await asyncio.sleep(5)
        try:
            if not is_running():
                _restart_count += 1
                _log("xray is down, restarting (attempt %d)" % _restart_count, "warning")
                if await asyncio.to_thread(_spawn_sync):
                    backoff = 2
                else:
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 60)
            elif _user_map() != _known_users and not _reload_pending:
                await sync_users()
        except Exception as e:
            _log("supervisor: " + str(e), "warning")


# ---------------------------------------------------------------- stats
async def query_stats(reset=True):
    args = ["-pattern", "user>>>"]
    if reset:
        args.insert(0, "-reset")
    out = await _api_call("statsquery", *args)
    res = {}
    try:
        items = (json.loads(out) or {}).get("stat", []) or []
        pairs = [(str(i.get("name", "")), i.get("value", 0)) for i in items]
    except Exception:
        # text fallback: "user>>>uid>>>traffic>>>uplink: 1234" style lines
        pairs = []
        for line in out.splitlines():
            if ">>>" in line and ":" in line:
                name, _, val = line.strip().rpartition(":")
                pairs.append((name.strip().strip('"'), val.strip().strip(",").strip('"')))
    for name, value in pairs:
        seg = name.split(">>>")
        if len(seg) == 4 and seg[0] == "user" and seg[2] == "traffic":
            try:
                res.setdefault(seg[1], {})[seg[3]] = int(value or 0)
            except Exception:
                pass
    return res


async def poll_deltas():
    """Return {uuid: {"uplink": n, "downlink": n}} since the last poll (empty on failure)."""
    if not is_running():
        return {}
    try:
        return await asyncio.wait_for(query_stats(reset=True), timeout=6.0)
    except Exception as e:
        _log("stats poll failed: " + str(e), "warning")
        return {}


# ---------------------------------------------------------------- diagnostics
def port_status():
    p = XRAY_PROC
    alive = is_running()
    return {
        "xray_running": alive,
        "xray_pid": p.pid if p else None,
        "xray_returncode": p.poll() if p else None,
        "xray_version": XRAY_VERSION or "unknown",
        "xray_uptime_s": int(time.time() - _started_at) if (alive and _started_at) else 0,
        "restarts": _restart_count,
        "users_loaded": len(_known_users),
        "listening": {
            **{"127.0.0.1:%d (%s)" % (PORTS[t], t): _probe("127.0.0.1", PORTS[t]) for t in INBOUND_TAGS},
            "127.0.0.1:%d (api)" % API_PORT: _probe("127.0.0.1", API_PORT),
        },
    }


def read_log(fname, tail=200):
    p = _data_dir / fname
    if not p.exists():
        return [fname + ": not found"]
    try:
        return p.read_text(encoding="utf-8", errors="replace").splitlines()[-max(1, min(int(tail), 2000)):]
    except Exception as e:
        return [fname + ": " + str(e)]
