# main.py — MX-UI v2.3.0 (FastAPI control plane + VLESS-WS / Trojan-WS gateways in front of Xray)
import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import socket
import time
import uuid as uuidlib
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import aiofiles
import psutil
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Query, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

import limits
import xray_manager
from ip_suggest import get_random_ips, is_valid_address
from pages import LOGIN_HTML, SETUP_HTML
from pages_dashboard import DASHBOARD_HTML, LOGS_HTML
from pages_portal import render_portal
from qr_generator import generate_qr_base64, qr_png_bytes

VERSION = "2.3.0"

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper(),
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MX-UI")

# ============================================================ paths & secrets
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
DATA_FILE = DATA_DIR / "mxui_state.json"
SECRET_FILE = DATA_DIR / "mxui_secret.key"
SETUP_COMPLETE_FILE = DATA_DIR / "setup_complete.lock"
SAVE_LOCK = asyncio.Lock()


def _load_or_create_secret() -> str:
    env_secret = os.environ.get("SECRET_KEY")
    if env_secret:
        return env_secret
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if SECRET_FILE.exists():
            existing = SECRET_FILE.read_text(encoding="utf-8").strip()
            if existing:
                return existing
        new_secret = secrets.token_urlsafe(32)
        SECRET_FILE.write_text(new_secret, encoding="utf-8")
        try:
            os.chmod(SECRET_FILE, 0o600)
        except Exception:
            pass
        return new_secret
    except Exception as e:
        logger.warning(f"Could not persist SECRET_KEY: {e}")
        return secrets.token_urlsafe(32)


CONFIG = {
    "secret": _load_or_create_secret(),
    "host": os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost"),
    "dashboard_path": "/dashboard",
    "login_path": "/login",
    "sub_path": "/sub",
    "setup_path": "/setup",
}
PUBLIC_PORT = int(os.environ.get("PORT", 8080) or 8080)

# ============================================================ runtime state
LINKS: dict = {}
LINKS_LOCK = asyncio.Lock()
AUTH: dict = {"password_hash": None}
SESSIONS: dict = {}            # sha256(token) -> expiry epoch
connections: dict = {}         # conn_id -> {uuid, ip, connected_at, up, down}
TRAFFIC_SERIES: dict = {}      # "YYYY-MM-DDTHH" -> bytes (last 48h)
NET_SAMPLES: deque = deque(maxlen=72)   # (epoch, rx_bps, tx_bps) every 5s = 6 min
activity_logs: deque = deque(maxlen=300)
stats = {"total_bytes": 0, "total_requests": 0, "rejected": 0, "start_time": time.time()}
_login_fails: dict = defaultdict(deque)
_save_dirty = False

SS_METHOD = "chacha20-ietf-poly1305"   # must match xray_manager.SS_METHOD
PROTOCOLS = ("vless", "trojan", "vmess", "ss")
DEFAULT_PROTOCOLS = ["vless", "trojan"]
PROTO_LABEL = {"vless": "VLESS", "trojan": "Trojan", "vmess": "VMess", "ss": "Shadowsocks"}
WS_PATH = "/ws"
TROJAN_WS_PATH = "/trojan"
FINGERPRINTS = ("chrome", "firefox", "safari", "ios", "android", "edge", "360", "qq", "random", "randomized")
DEFAULT_FINGERPRINT = "chrome"
DEFAULT_PORT = 443
SESSION_COOKIE = "mxui_session"
SESSION_TTL = 60 * 60 * 24 * 30
MIN_PASSWORD = 6
_LEGACY_DEFAULT_PW = "MUVIXO"


def log_activity(kind: str, message: str, level: str = "info"):
    activity_logs.append({"kind": kind, "level": level, "message": message,
                          "time": datetime.now().isoformat(timespec="seconds")})


# ============================================================ persistence
async def load_state():
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not DATA_FILE.exists():
            return
        async with aiofiles.open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.loads(await f.read())
        for uid, link in (data.get("links") or {}).items():
            LINKS[uid] = _normalize_link(link, uid)
        AUTH["password_hash"] = data.get("password_hash") or None
        for key, value in (data.get("paths") or {}).items():
            if key in CONFIG and isinstance(value, str) and value.startswith("/"):
                CONFIG[key] = value
        now = time.time()
        SESSIONS.update({k: v for k, v in (data.get("sessions") or {}).items() if v > now})
        TRAFFIC_SERIES.update(data.get("traffic_series") or {})
        stats["total_bytes"] = int(data.get("total_bytes") or sum(l.get("used_bytes", 0) for l in LINKS.values()))
        logger.info(f"State loaded: {len(LINKS)} configs")
    except Exception as e:
        logger.warning(f"Could not load state: {e}")


async def save_state():
    async with SAVE_LOCK:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            now = time.time()
            data = {
                "version": VERSION,
                "links": dict(LINKS),
                "password_hash": AUTH["password_hash"],
                "sessions": {k: v for k, v in SESSIONS.items() if v > now},
                "traffic_series": dict(TRAFFIC_SERIES),
                "total_bytes": stats["total_bytes"],
                "saved_at": datetime.now().isoformat(),
                "paths": {k: CONFIG[k] for k in ("dashboard_path", "login_path", "sub_path", "setup_path")},
            }
            tmp = DATA_FILE.with_suffix(".tmp")
            async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
            tmp.replace(DATA_FILE)
        except Exception as e:
            logger.warning(f"Could not save state: {e}")


def mark_dirty():
    global _save_dirty
    _save_dirty = True


async def _autosave_loop():
    global _save_dirty
    while True:
        await asyncio.sleep(10)
        if _save_dirty:
            _save_dirty = False
            await save_state()


# ============================================================ auth
def _pbkdf2(pw: str, salt: bytes, it: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, it).hex()


def hash_password(pw: str) -> str:
    salt, it = secrets.token_bytes(16), 240_000
    return f"pbkdf2${it}${salt.hex()}${_pbkdf2(pw, salt, it)}"


def _legacy_hash(pw: str) -> str:
    return hashlib.sha256(f"{pw}{CONFIG['secret']}".encode()).hexdigest()


def verify_password(pw: str, stored: Optional[str]) -> bool:
    if not stored:
        return False
    if stored.startswith("pbkdf2$"):
        try:
            _, it, salt, h = stored.split("$", 3)
            return hmac.compare_digest(_pbkdf2(pw, bytes.fromhex(salt), int(it)), h)
        except Exception:
            return False
    return hmac.compare_digest(_legacy_hash(pw), stored)


def is_setup_complete() -> bool:
    h = AUTH.get("password_hash")
    if not h:
        return False
    if SETUP_COMPLETE_FILE.exists():
        return True
    # v1 installs that never left the factory password must go through /setup
    return not verify_password(_LEGACY_DEFAULT_PW, h)


def _mark_setup_complete():
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SETUP_COMPLETE_FILE.write_text("setup_complete", encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not mark setup complete: {e}")


def _tok(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_session() -> str:
    token = secrets.token_urlsafe(32)
    SESSIONS[_tok(token)] = time.time() + SESSION_TTL
    mark_dirty()
    return token


def is_valid_session(token: Optional[str]) -> bool:
    if not token:
        return False
    exp = SESSIONS.get(_tok(token))
    if exp is None:
        return False
    if exp < time.time():
        SESSIONS.pop(_tok(token), None)
        return False
    return True


async def require_auth(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if not is_valid_session(token):
        raise HTTPException(status_code=401, detail="unauthorized")
    return token


def _rate_limited(ip: str) -> bool:
    q = _login_fails[ip]
    cutoff = time.time() - 600
    while q and q[0] < cutoff:
        q.popleft()
    return len(q) >= 8


def _set_session_cookie(resp: Response, request: Request, token: str):
    resp.set_cookie(SESSION_COOKIE, token, max_age=SESSION_TTL, httponly=True,
                    samesite="lax", path="/", secure=is_https(request))


# ============================================================ request helpers
def get_client_ip(conn) -> str:
    h = conn.headers
    for key in ("cf-connecting-ip", "x-real-ip"):
        v = h.get(key)
        if v:
            return v.strip()
    fwd = h.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return conn.client.host if conn.client else "unknown"


def get_host(request: Optional[Request] = None) -> str:
    if request is not None:
        h = request.headers.get("x-forwarded-host") or request.headers.get("host")
        if h:
            h = h.split(",")[0].strip()
            if h.startswith("["):
                return h.split("]")[0] + "]"
            return h.split(":")[0]
    return os.environ.get("RAILWAY_PUBLIC_DOMAIN", CONFIG["host"])


def is_https(request: Optional[Request] = None) -> bool:
    if request is not None:
        proto = request.headers.get("x-forwarded-proto", "")
        if proto:
            return proto.split(",")[0].strip().lower() == "https"
        if request.url.scheme == "https":
            return True
    return bool(os.environ.get("RAILWAY_PUBLIC_DOMAIN"))


def get_base_url(request: Optional[Request] = None) -> str:
    return f"{'https' if is_https(request) else 'http'}://{get_host(request)}"


def uptime() -> str:
    secs = int(time.time() - stats["start_time"])
    d, rem = divmod(secs, 86400)
    h, m, s = rem // 3600, (rem % 3600) // 60, rem % 60
    return (f"{d}d " if d else "") + f"{h:02d}:{m:02d}:{s:02d}"


def fmt_bytes(b: int) -> str:
    b = int(b or 0)
    for unit, size in (("TB", 1024 ** 4), ("GB", 1024 ** 3), ("MB", 1024 ** 2), ("KB", 1024)):
        if b >= size:
            return f"{b / size:.2f} {unit}"
    return f"{b} B"


def parse_size_to_bytes(value: float, unit: str) -> int:
    mult = {"TB": 1024 ** 4, "GB": 1024 ** 3, "MB": 1024 ** 2, "KB": 1024}.get((unit or "GB").upper(), 1)
    return max(0, int(float(value or 0) * mult))


def parse_speed_to_bytes(value: float, unit: str) -> int:
    value = float(value or 0)
    if value <= 0:
        return 0
    unit = (unit or "MBIT").upper()
    if unit == "MBIT":
        return int(value * 1_000_000 / 8)
    if unit == "KB":
        return int(value * 1024)
    if unit == "MB":
        return int(value * 1024 * 1024)
    return int(value)


def _num(body: dict, key: str, default=0.0) -> float:
    try:
        v = float(body.get(key) if body.get(key) not in (None, "") else default)
        return v if v == v and v >= 0 else default  # NaN / negatives -> default
    except Exception:
        return default


# ============================================================ link model
def _derive(tag: str, uid: str) -> str:
    """Stable per-config secret for one protocol, so a config keeps working across restarts."""
    return hashlib.sha256(f"{tag}:{uid}:{CONFIG['secret']}".encode()).hexdigest()[:24]


def _derive_trojan_password(uid: str) -> str:
    """Stable per-config Trojan password, so a config keeps working across restarts."""
    return hashlib.sha256(f"trojan:{uid}:{CONFIG['secret']}".encode()).hexdigest()[:24]


def _clean_protocols(value, fallback=None) -> list:
    """Accepts 'vless', 'vless-ws', 'trojan', or a list of those. Returns known protocols in canonical order."""
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set)):
        return list(fallback or DEFAULT_PROTOCOLS)
    alias = {"shadowsocks": "ss", "ss-ws": "ss", "vmess-ws": "vmess"}
    wanted = {alias.get(str(v).strip().lower(), str(v).strip().lower().replace("-ws", "")) for v in value}
    out = [p for p in PROTOCOLS if p in wanted]
    return out or list(fallback or DEFAULT_PROTOCOLS)


def _normalize_link(link: dict, uid: Optional[str] = None) -> dict:
    link = dict(link or {})
    link.setdefault("label", "Config")
    link.setdefault("limit_bytes", 0)
    link.setdefault("used_bytes", 0)
    link.setdefault("up_bytes", 0)
    link.setdefault("down_bytes", 0)
    link.setdefault("created_at", datetime.now().isoformat())
    link.setdefault("active", True)
    link.setdefault("expires_at", None)
    link.setdefault("note", "")
    link.setdefault("is_default", False)
    # v1/v2.0 stored a single "protocol" string; v2.1 keeps a list and adds Trojan.
    link["protocols"] = _clean_protocols(link.get("protocols") or link.get("protocol"))
    link.pop("protocol", None)
    if uid and not str(link.get("trojan_password") or "").strip():
        link["trojan_password"] = _derive_trojan_password(uid)
    if uid and not str(link.get("ws_token") or "").strip():
        link["ws_token"] = _derive("ws", uid)          # path secret for VMess and Shadowsocks
    if uid and not str(link.get("ss_password") or "").strip():
        link["ss_password"] = _derive("ss", uid)
    link.setdefault("fingerprint", DEFAULT_FINGERPRINT)
    link.setdefault("alpn", "")
    link.setdefault("ip_limit", 0)
    link.setdefault("speed_limit_bytes", 0)
    link.setdefault("last_used", None)
    link["ip_pool"] = [e for e in (link.get("ip_pool") or []) if isinstance(e, dict) and e.get("ip")]
    return link


def is_link_expired(link: dict) -> bool:
    exp = link.get("expires_at")
    if not exp:
        return False
    try:
        return datetime.now() > datetime.fromisoformat(exp)
    except Exception:
        return False


def is_over_quota(link: dict) -> bool:
    lb = int(link.get("limit_bytes") or 0)
    return lb > 0 and int(link.get("used_bytes") or 0) >= lb


def link_state(link: Optional[dict]) -> str:
    if link is None:
        return "missing"
    if not link.get("active", True):
        return "disabled"
    if is_link_expired(link):
        return "expired"
    if is_over_quota(link):
        return "depleted"
    return "active"


def is_link_allowed(link: Optional[dict]) -> bool:
    return link_state(link) == "active"


def unique_ips_for_uuid(uid: str) -> set:
    return {c["ip"] for c in connections.values() if c.get("uuid") == uid and c.get("ip")}


def days_left(link: dict):
    exp = link.get("expires_at")
    if not exp:
        return None
    try:
        return max(0.0, (datetime.fromisoformat(exp) - datetime.now()).total_seconds() / 86400)
    except Exception:
        return None


def _remark(link: dict, suffix: str = "") -> str:
    name = str(link.get("label") or "MX-UI").strip()
    return f"{name} · {suffix}" if suffix else name


def _ws_params(host: str, path: str, fingerprint: Optional[str], alpn: Optional[str]) -> dict:
    return {
        "security": "tls", "type": "ws", "host": host, "path": path, "sni": host,
        "fp": (fingerprint or DEFAULT_FINGERPRINT).strip(),
        "alpn": (alpn or "http/1.1").strip(),
    }


def _bracket(addr: str) -> str:
    return f"[{addr}]" if (":" in addr and not addr.startswith("[")) else addr


def _qs(params: dict) -> str:
    return "&".join(f"{k}={quote(str(v), safe='')}" for k, v in params.items())


def generate_vless_link(uid: str, host: str, remark: str, fingerprint: Optional[str] = None,
                        alpn: Optional[str] = None, address: Optional[str] = None,
                        port: Optional[int] = None) -> str:
    params = {"encryption": "none", **_ws_params(host, WS_PATH, fingerprint, alpn)}
    return (f"vless://{uid}@{_bracket(address or host)}:{port or DEFAULT_PORT}"
            f"?{_qs(params)}#{quote(remark, safe='')}")


def generate_trojan_link(password: str, host: str, remark: str, fingerprint: Optional[str] = None,
                         alpn: Optional[str] = None, address: Optional[str] = None,
                         port: Optional[int] = None) -> str:
    params = _ws_params(host, TROJAN_WS_PATH, fingerprint, alpn)
    return (f"trojan://{quote(str(password), safe='')}@{_bracket(address or host)}:{port or DEFAULT_PORT}"
            f"?{_qs(params)}#{quote(remark, safe='')}")


def generate_vmess_link(uid: str, host: str, remark: str, fingerprint: Optional[str] = None,
                        alpn: Optional[str] = None, address: Optional[str] = None,
                        port: Optional[int] = None, token: str = "") -> str:
    cfg = {"v": "2", "ps": remark, "add": address or host, "port": str(port or DEFAULT_PORT),
           "id": uid, "aid": "0", "scy": "auto", "net": "ws", "type": "none", "host": host,
           "path": f"/vmess/{token}", "tls": "tls", "sni": host,
           "alpn": (alpn or "http/1.1").strip(), "fp": (fingerprint or DEFAULT_FINGERPRINT).strip()}
    return "vmess://" + base64.b64encode(json.dumps(cfg, ensure_ascii=False).encode()).decode()


def generate_ss_link(password: str, host: str, remark: str, address: Optional[str] = None,
                     port: Optional[int] = None, token: str = "") -> str:
    """Shadowsocks over WebSocket+TLS, the way v2ray-plugin clients expect it."""
    userinfo = base64.urlsafe_b64encode(f"{SS_METHOD}:{password}".encode()).decode().rstrip("=")
    plugin = f"v2ray-plugin;mode=websocket;host={host};path=/ss/{token};tls"
    return (f"ss://{userinfo}@{_bracket(address or host)}:{port or DEFAULT_PORT}"
            f"/?plugin={quote(plugin, safe='')}#{quote(remark, safe='')}")


def link_protocols(link: dict) -> list:
    return _clean_protocols(link.get("protocols"))


def trojan_password_of(uid: str, link: dict) -> str:
    return str(link.get("trojan_password") or _derive_trojan_password(uid))


def build_all_links(link: dict, uid: str, host: str) -> list[dict]:
    """Every shareable URL for a config: one per protocol per address."""
    fp, alpn = link.get("fingerprint"), link.get("alpn")
    protos = link_protocols(link)
    pw = trojan_password_of(uid, link)
    token = str(link.get("ws_token") or "")
    ss_pw = str(link.get("ss_password") or _derive("ss", uid))
    targets = [("Domain", host, DEFAULT_PORT)]
    for i, e in enumerate(link.get("ip_pool") or [], start=1):
        targets.append((f"IP {i}", e["ip"], int(e.get("port") or DEFAULT_PORT)))
    out = []
    for proto in protos:
        for where, addr, port in targets:
            suffix = f"{PROTO_LABEL[proto]}" + ("" if where == "Domain" else f" · {where}")
            remark = _remark(link, suffix)
            if proto == "vless":
                url = generate_vless_link(uid, host, remark, fp, alpn, addr, port)
            elif proto == "trojan":
                url = generate_trojan_link(pw, host, remark, fp, alpn, addr, port)
            elif proto == "vmess":
                url = generate_vmess_link(uid, host, remark, fp, alpn, addr, port, token)
            else:
                url = generate_ss_link(ss_pw, host, remark, addr, port, token)
            out.append({"protocol": proto, "label": PROTO_LABEL[proto], "where": where,
                        "tag": f"{PROTO_LABEL[proto]} · {where}", "address": addr,
                        "port": port, "url": url})
    return out


def _first_url(variants: list, proto: str) -> str:
    for v in variants:
        if v["protocol"] == proto:
            return v["url"]
    return ""


def sub_url_for(base: str, uid: str) -> str:
    return f"{base}{CONFIG['sub_path'].rstrip('/')}/{uid}"


def link_public(uid: str, link: dict, request: Request) -> dict:
    host, base = get_host(request), get_base_url(request)
    variants = build_all_links(link, uid, host)
    live = [c for c in connections.values() if c.get("uuid") == uid]
    return {
        "uuid": uid, **{k: v for k, v in link.items() if not k.startswith("_")},
        "state": link_state(link),
        "expired": is_link_expired(link),
        "days_left": days_left(link),
        "protocols": link_protocols(link),
        "trojan_password": trojan_password_of(uid, link),
        "vless_link": _first_url(variants, "vless"),
        "trojan_link": _first_url(variants, "trojan"),
        "primary_link": variants[0]["url"] if variants else "",
        "variants": variants,
        "sub_url": sub_url_for(base, uid),
        "info_url": sub_url_for(base, uid) + "/info",
        "connected_ips": len({c["ip"] for c in live}),
        "live_connections": len(live),
        "applied_ips_count": len(link.get("ip_pool") or []),
    }


async def ensure_default_link():
    async with LINKS_LOCK:
        if any(l.get("is_default") for l in LINKS.values()):
            return
        h = hashlib.sha256(f"default{CONFIG['secret']}".encode()).hexdigest()
        uid = str(uuidlib.UUID(h[:32]))
        LINKS.setdefault(uid, _normalize_link({"label": "Default", "is_default": True}, uid))
    mark_dirty()


# ============================================================ background loops
async def _stats_loop():
    while True:
        await asyncio.sleep(5)
        try:
            deltas = await xray_manager.poll_deltas()
            if not deltas:
                continue
            total = 0
            async with LINKS_LOCK:
                for uid, d in deltas.items():
                    link = LINKS.get(uid)
                    if not link:
                        continue
                    up, down = int(d.get("uplink", 0)), int(d.get("downlink", 0))
                    if up + down <= 0:
                        continue
                    link["up_bytes"] = int(link.get("up_bytes", 0)) + up
                    link["down_bytes"] = int(link.get("down_bytes", 0)) + down
                    link["used_bytes"] = int(link.get("used_bytes", 0)) + up + down
                    link["last_used"] = datetime.now().isoformat(timespec="seconds")
                    total += up + down
                    if is_over_quota(link) and not link.get("_quota_logged"):
                        link["_quota_logged"] = True
                        log_activity("quota", f"{link.get('label')} reached its data limit", "warn")
            if total:
                stats["total_bytes"] += total
                key = datetime.now().strftime("%Y-%m-%dT%H")
                TRAFFIC_SERIES[key] = TRAFFIC_SERIES.get(key, 0) + total
                for k in sorted(TRAFFIC_SERIES)[:-48]:
                    TRAFFIC_SERIES.pop(k, None)
                mark_dirty()
        except Exception as e:
            logger.debug(f"[stats] {e}")


async def _net_sampler_loop():
    last = psutil.net_io_counters()
    last_t = time.time()
    psutil.cpu_percent(None)
    while True:
        await asyncio.sleep(5)
        try:
            cur, t = psutil.net_io_counters(), time.time()
            dt = max(t - last_t, 0.001)
            NET_SAMPLES.append((int(t), int((cur.bytes_recv - last.bytes_recv) / dt),
                                int((cur.bytes_sent - last.bytes_sent) / dt)))
            last, last_t = cur, t
            now = time.time()
            for k in [k for k, v in SESSIONS.items() if v < now]:
                SESSIONS.pop(k, None)
        except Exception as e:
            logger.debug(f"[net] {e}")


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    await load_state()
    await ensure_default_link()
    xray_manager.register(LINKS, LINKS_LOCK, logger, DATA_DIR)
    # Do not hold application startup on Xray validation/boot. On Railway this
    # made the first page request wait several seconds (or until a failed boot
    # timed out), even though the control panel itself was ready.
    async def start_xray():
        try:
            ok = await xray_manager.start()
            log_activity("system", "Xray core started" if ok else "Xray failed to start, retrying in background",
                         "ok" if ok else "err")
        except Exception as e:
            logger.error(f"[xray] start failed: {e}")
            log_activity("system", f"Xray failed: {e}", "err")

    xray_start_task = asyncio.create_task(start_xray())
    tasks = [asyncio.create_task(f()) for f in (_stats_loop, _net_sampler_loop, _autosave_loop)]
    log_activity("system", f"MX-UI {VERSION} started", "ok")
    yield
    if not xray_start_task.done():
        xray_start_task.cancel()
        try:
            await xray_start_task
        except asyncio.CancelledError:
            pass
    for t in tasks:
        t.cancel()
    await save_state()
    try:
        await xray_manager.stop()
    except Exception as e:
        logger.warning(f"[xray] stop failed: {e}")


app = FastAPI(title="MX-UI", docs_url=None, redoc_url=None, openapi_url=None, lifespan=_lifespan)


@app.middleware("http")
async def _security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "no-referrer")
    if resp.headers.get("content-type", "").startswith("text/html"):
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Cache-Control", "no-store")
    return resp


# ============================================================ health
@app.get("/health")
@app.get("/healthz")
async def healthz():
    return {"ok": True, "service": "mx-ui", "version": VERSION,
            "xray_running": xray_manager.is_running(), "uptime": uptime()}


@app.get("/readyz")
async def readyz():
    if xray_manager.is_running():
        return {"ready": True}
    raise HTTPException(status_code=503, detail="xray not running")


# ============================================================ pages
def _html(s: str) -> HTMLResponse:
    return HTMLResponse(content=s)


async def render_dashboard(request: Request):
    if not is_setup_complete():
        return RedirectResponse(CONFIG["setup_path"], status_code=302)
    if not is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(CONFIG["login_path"], status_code=302)
    return _html(DASHBOARD_HTML)


async def render_login(request: Request):
    if not is_setup_complete():
        return RedirectResponse(CONFIG["setup_path"], status_code=302)
    if is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(CONFIG["dashboard_path"], status_code=302)
    return _html(LOGIN_HTML)


async def render_setup(request: Request):
    if is_setup_complete():
        return RedirectResponse(CONFIG["login_path"], status_code=302)
    return _html(SETUP_HTML)


@app.get("/")
async def root(request: Request):
    return RedirectResponse(CONFIG["dashboard_path"], status_code=302)


@app.get("/dashboard")
async def dashboard_page(request: Request):
    return await render_dashboard(request)


@app.get("/login")
async def login_page(request: Request):
    return await render_login(request)


@app.get("/setup")
async def setup_page(request: Request):
    return await render_setup(request)


@app.get("/logs")
async def logs_page(request: Request):
    if not is_setup_complete():
        return RedirectResponse(CONFIG["setup_path"], status_code=302)
    if not is_valid_session(request.cookies.get(SESSION_COOKIE)):
        return RedirectResponse(CONFIG["login_path"], status_code=302)
    return _html(LOGS_HTML)


# ============================================================ subscriptions
def _userinfo_header(link: dict) -> str:
    up = int(link.get("up_bytes") or 0)
    down = max(0, int(link.get("used_bytes") or 0) - up)
    parts = [f"upload={up}", f"download={down}", f"total={int(link.get('limit_bytes') or 0)}"]
    exp = link.get("expires_at")
    if exp:
        try:
            parts.append(f"expire={int(datetime.fromisoformat(exp).timestamp())}")
        except Exception:
            pass
    return "; ".join(parts)


async def subscription_raw(uid: str, request: Request):
    link = LINKS.get(uid)
    if not link:
        raise HTTPException(status_code=404, detail="not found")
    host = get_host(request)
    lines = [v["url"] for v in build_all_links(link, uid, host)] if is_link_allowed(link) else []
    body = base64.b64encode("\n".join(lines).encode()).decode()
    title = "base64:" + base64.b64encode(str(link.get("label") or "MX-UI").encode()).decode()
    return Response(content=body, media_type="text/plain; charset=utf-8", headers={
        "subscription-userinfo": _userinfo_header(link),
        "profile-title": title,
        "profile-update-interval": "6",
        "profile-web-page-url": sub_url_for(get_base_url(request), uid) + "/info",
        "Cache-Control": "no-store",
    })


async def subscription_portal(uid: str, request: Request):
    link = LINKS.get(uid)
    if not link:
        raise HTTPException(status_code=404, detail="not found")
    data = link_public(uid, link, request)
    data.pop("ip_pool", None)
    data.pop("note", None)
    data["qr"] = generate_qr_base64(data["sub_url"], size=360)
    return _html(render_portal(data))


@app.get("/sub/user")
async def sub_user_legacy(request: Request, uuid: str = Query(...)):
    return await subscription_portal(uuid, request)


@app.get("/sub/{uid}/info")
async def sub_info(uid: str, request: Request):
    return await subscription_portal(uid, request)


@app.get("/sub/{uid}")
async def sub_single(uid: str, request: Request):
    # Browsers get the friendly page, VPN clients get the base64 list.
    accept = request.headers.get("accept", "")
    if "text/html" in accept and request.query_params.get("raw") is None:
        return await subscription_portal(uid, request)
    return await subscription_raw(uid, request)


@app.get("/sub-all")
async def sub_all(request: Request, _=Depends(require_auth)):
    host = get_host(request)
    lines = []
    for uid, d in list(LINKS.items()):
        if is_link_allowed(d):
            lines.extend(v["url"] for v in build_all_links(d, uid, host))
    return Response(content=base64.b64encode("\n".join(lines).encode()).decode(), media_type="text/plain")


# ============================================================ auth API
async def _json(request: Request) -> dict:
    try:
        body = await request.json()
        return body if isinstance(body, dict) else {}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")


@app.post("/api/setup")
async def api_setup(request: Request):
    if is_setup_complete():
        raise HTTPException(status_code=403, detail="Setup is already complete")
    body = await _json(request)
    pw = str(body.get("password", ""))
    if len(pw) < MIN_PASSWORD:
        raise HTTPException(status_code=400, detail=f"Password must be at least {MIN_PASSWORD} characters")
    AUTH["password_hash"] = hash_password(pw)
    _mark_setup_complete()
    SESSIONS.clear()
    token = await create_session()
    await save_state()
    log_activity("auth", "Admin password set", "ok")
    resp = JSONResponse({"ok": True})
    _set_session_cookie(resp, request, token)
    return resp


@app.post("/api/login")
async def api_login(request: Request):
    if not is_setup_complete():
        raise HTTPException(status_code=403, detail="Setup required")
    ip = get_client_ip(request)
    if _rate_limited(ip):
        raise HTTPException(status_code=429, detail="Too many attempts. Wait 10 minutes.")
    body = await _json(request)
    pw = str(body.get("password", ""))
    stored = AUTH["password_hash"]
    if not verify_password(pw, stored):
        _login_fails[ip].append(time.time())
        await asyncio.sleep(0.6)
        log_activity("auth", f"Failed login from {ip}", "warn")
        raise HTTPException(status_code=401, detail="Wrong password")
    _login_fails.pop(ip, None)
    if not stored.startswith("pbkdf2$"):
        AUTH["password_hash"] = hash_password(pw)  # upgrade v1 hash in place
    token = await create_session()
    await save_state()
    resp = JSONResponse({"ok": True})
    _set_session_cookie(resp, request, token)
    return resp


@app.post("/api/logout")
async def api_logout(request: Request):
    t = request.cookies.get(SESSION_COOKIE)
    if t:
        SESSIONS.pop(_tok(t), None)
        mark_dirty()
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(SESSION_COOKIE, path="/")
    return resp


@app.get("/api/me")
async def api_me(request: Request):
    return {"authenticated": is_valid_session(request.cookies.get(SESSION_COOKIE)), "version": VERSION}


@app.get("/api/current-paths")
async def api_paths():
    return {"dashboard": CONFIG["dashboard_path"], "login": CONFIG["login_path"],
            "sub": CONFIG["sub_path"], "setup": CONFIG["setup_path"]}


@app.post("/api/change-password")
async def api_change_password(request: Request, _=Depends(require_auth)):
    body = await _json(request)
    if not verify_password(str(body.get("current_password", "")), AUTH["password_hash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    new = str(body.get("new_password", ""))
    if len(new) < MIN_PASSWORD:
        raise HTTPException(status_code=400, detail=f"New password must be at least {MIN_PASSWORD} characters")
    AUTH["password_hash"] = hash_password(new)
    _mark_setup_complete()
    SESSIONS.clear()
    await save_state()
    log_activity("auth", "Admin password changed", "ok")
    return {"ok": True, "requires_login": True}


# ============================================================ stats
@app.get("/stats")
async def api_stats(_=Depends(require_auth)):
    snap = dict(LINKS)
    ram, swap = psutil.virtual_memory(), psutil.swap_memory()
    try:
        disk = psutil.disk_usage(str(DATA_DIR) if DATA_DIR.exists() else "/")
    except Exception:
        disk = psutil.disk_usage("/")
    try:
        load = [round(x, 2) for x in os.getloadavg()]
    except Exception:
        load = []
    states = defaultdict(int)
    protos = defaultdict(int)
    for l in snap.values():
        states[link_state(l)] += 1
        for p in link_protocols(l):
            protos[p] += 1
    now = datetime.now()
    series = []
    for i in range(23, -1, -1):
        k = (now - timedelta(hours=i)).strftime("%Y-%m-%dT%H")
        series.append({"hour": k[-2:] + ":00", "bytes": int(TRAFFIC_SERIES.get(k, 0))})
    x = xray_manager.port_status()
    return {
        "version": VERSION,
        "uptime": uptime(),
        "timestamp": now.isoformat(timespec="seconds"),
        "total_bytes": stats["total_bytes"],
        "total_traffic_mb": round(stats["total_bytes"] / 1024 ** 2, 2),
        "total_requests": stats["total_requests"],
        "rejected": stats["rejected"],
        "active_connections": len(connections),
        "online_ips": len({c["ip"] for c in connections.values()}),
        "links_count": len(snap),
        "active_links": states["active"],
        "states": dict(states),
        "protocols": {p: protos.get(p, 0) for p in PROTOCOLS},
        "series_24h": series,
        "net": [{"t": t, "rx": rx, "tx": tx} for t, rx, tx in NET_SAMPLES],
        "cpu_percent": round(psutil.cpu_percent(None), 1),
        "cpu_cores": psutil.cpu_count(logical=True),
        "load_avg": load,
        "ram_used_mb": ram.used // 1048576, "ram_total_mb": ram.total // 1048576,
        "ram_available_mb": ram.available // 1048576, "ram_percent": ram.percent,
        "swap_used_mb": swap.used // 1048576, "swap_total_mb": swap.total // 1048576, "swap_percent": swap.percent,
        "disk_used_gb": round(disk.used / 1024 ** 3, 2), "disk_total_gb": round(disk.total / 1024 ** 3, 2),
        "disk_percent": disk.percent,
        "xray": {"running": x["xray_running"], "version": x["xray_version"], "restarts": x["restarts"]},
        "activity": list(activity_logs)[-20:],
    }


# ============================================================ links API
@app.get("/api/links")
async def list_links(request: Request, _=Depends(require_auth)):
    out = [link_public(uid, l, request) for uid, l in list(LINKS.items())]
    out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    out.sort(key=lambda x: not x.get("is_default"))  # stable: default first, then newest
    return {"links": out}


def _apply_limits(link: dict, body: dict):
    if "limit_value" in body:
        lv = _num(body, "limit_value")
        link["limit_bytes"] = 0 if lv <= 0 else parse_size_to_bytes(lv, body.get("limit_unit") or "GB")
    if "expires_days" in body:
        d = _num(body, "expires_days")
        link["expires_at"] = (datetime.now() + timedelta(days=d)).isoformat(timespec="seconds") if d > 0 else None
    if "expires_at" in body:
        v = body.get("expires_at")
        if not v:
            link["expires_at"] = None
        else:
            try:
                link["expires_at"] = datetime.fromisoformat(str(v)).isoformat(timespec="seconds")
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid expiry date")
    if "ip_limit" in body:
        link["ip_limit"] = int(_num(body, "ip_limit"))
    if "speed_limit_value" in body:
        link["speed_limit_bytes"] = parse_speed_to_bytes(_num(body, "speed_limit_value"),
                                                         body.get("speed_limit_unit") or "MBIT")
    if "protocols" in body:
        want = _clean_protocols(body.get("protocols"), fallback=link_protocols(link))
        if not want:
            raise HTTPException(status_code=400, detail="Pick at least one protocol")
        link["protocols"] = want
    if "fingerprint" in body:
        fp = str(body.get("fingerprint") or DEFAULT_FINGERPRINT)
        link["fingerprint"] = fp if fp in FINGERPRINTS else DEFAULT_FINGERPRINT
    if "alpn" in body:
        link["alpn"] = str(body.get("alpn") or "").strip()[:100]
    if "note" in body:
        link["note"] = str(body.get("note") or "").strip()[:300]
    if "label" in body:
        label = str(body.get("label") or "").strip()[:64]
        if label:
            link["label"] = label
    if not is_over_quota(link):
        link.pop("_quota_logged", None)


@app.post("/api/links")
async def create_link(request: Request, _=Depends(require_auth)):
    body = await _json(request)
    uid = str(uuidlib.uuid4())
    link = _normalize_link({"label": "Config"}, uid)
    _apply_limits(link, {**body, "label": body.get("label") or f"Config {len(LINKS) + 1}"})
    async with LINKS_LOCK:
        LINKS[uid] = link
    xray_manager.request_sync()
    await save_state()
    log_activity("config", f"Created {link['label']}", "ok")
    return link_public(uid, link, request)


@app.patch("/api/links/{uid}")
async def update_link(uid: str, request: Request, _=Depends(require_auth)):
    body = await _json(request)
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if not link:
            raise HTTPException(status_code=404, detail="Config not found")
        if link.get("is_default"):
            body = {k: v for k, v in body.items() if k in ("active", "fingerprint", "alpn", "protocols")}
        if "active" in body:
            link["active"] = bool(body["active"])
        _apply_limits(link, body)
    mark_dirty()
    return link_public(uid, link, request)


@app.patch("/api/links/{uid}/toggle")
async def toggle_link(uid: str, request: Request, _=Depends(require_auth)):
    body = await _json(request)
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if not link:
            raise HTTPException(status_code=404, detail="Config not found")
        link["active"] = bool(body.get("active", not link.get("active", True)))
    mark_dirty()
    log_activity("config", f"{link['label']} {'enabled' if link['active'] else 'disabled'}")
    return {"ok": True, "active": link["active"]}


@app.delete("/api/links/{uid}")
async def delete_link(uid: str, _=Depends(require_auth)):
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if not link:
            raise HTTPException(status_code=404, detail="Config not found")
        if link.get("is_default"):
            raise HTTPException(status_code=403, detail="The default config can't be deleted")
        del LINKS[uid]
    limits.drop_buckets(uid)
    xray_manager.request_sync()
    await save_state()
    log_activity("config", f"Deleted {link.get('label')}", "warn")
    return {"ok": True}


@app.post("/api/links/{uid}/reset-traffic")
async def reset_traffic(uid: str, _=Depends(require_auth)):
    async with LINKS_LOCK:
        link = LINKS.get(uid)
        if not link:
            raise HTTPException(status_code=404, detail="Config not found")
        link["used_bytes"] = link["up_bytes"] = link["down_bytes"] = 0
        link.pop("_quota_logged", None)
    mark_dirty()
    return {"ok": True}


@app.get("/api/connections")
async def api_connections(_=Depends(require_auth)):
    out = []
    for cid, c in list(connections.items()):
        l = LINKS.get(c["uuid"]) or {}
        out.append({"id": cid, "uuid": c["uuid"], "label": l.get("label", "?"), "ip": c["ip"],
                    "since": c["connected_at"], "up": c["up"], "down": c["down"]})
    out.sort(key=lambda x: x["since"], reverse=True)
    return {"connections": out}


# ============================================================ tools API
@app.get("/api/qr")
async def api_qr(request: Request, data: str = Query(..., max_length=4096), size: int = 300, format: str = "json",
                 _=Depends(require_auth)):
    if format == "image":
        return Response(qr_png_bytes(data, size), media_type="image/png")
    return {"qr": generate_qr_base64(data, size)}


@app.get("/api/domain/check")
async def check_domain(request: Request, _=Depends(require_auth)):
    host = get_host(request)
    return {"host": host, "is_railway": host.endswith(".railway.app") or host.endswith(".up.railway.app")}


@app.get("/api/ips/suggest")
async def suggest_ips(count: int = 10, _=Depends(require_auth)):
    ips = get_random_ips(count)
    return {"ips": ips, "count": len(ips)}


@app.post("/api/ips/apply")
async def apply_ips(request: Request, _=Depends(require_auth)):
    body = await _json(request)
    port = int(_num(body, "port", DEFAULT_PORT)) or DEFAULT_PORT
    clean = []
    for addr in body.get("ips") or []:
        addr = str(addr).strip()
        if is_valid_address(addr) and addr not in clean:
            clean.append(addr)
    mode = body.get("mode", "replace")
    n = 0
    async with LINKS_LOCK:
        for uid in body.get("target_uuids") or []:
            link = LINKS.get(uid)
            if not link:
                continue
            pool = [] if mode == "replace" else list(link.get("ip_pool") or [])
            have = {e["ip"] for e in pool}
            pool += [{"ip": ip, "port": port} for ip in clean if ip not in have]
            link["ip_pool"] = pool[:50]
            n += 1
    await save_state()
    return {"ok": True, "updated": n}


def _tcp_ping(host: str, port: int, timeout: float = 3.0):
    try:
        t0 = time.perf_counter()
        with socket.create_connection((host, port), timeout=timeout):
            return (time.perf_counter() - t0) * 1000
    except Exception:
        return None


@app.post("/api/configs/test")
async def test_configs(request: Request, _=Depends(require_auth)):
    body = await _json(request)
    uuids = [u for u in (body.get("uuids") or []) if u in LINKS][:50]
    if not uuids:
        raise HTTPException(status_code=400, detail="No configs selected")
    host = get_host(request)

    async def one(uid):
        link = LINKS[uid]
        targets = []
        if host and host not in ("localhost", "127.0.0.1"):
            targets.append(("Domain", host, DEFAULT_PORT))
        targets += [(f"IP {i}", e["ip"], int(e.get("port") or DEFAULT_PORT))
                    for i, e in enumerate(link.get("ip_pool") or [], start=1)]
        probes = await asyncio.gather(*[asyncio.to_thread(_tcp_ping, h, p) for _, h, p in targets])
        rows = [{"tag": t, "address": h, "port": p, "ms": None if ms is None else round(ms, 1)}
                for (t, h, p), ms in zip(targets, probes)]
        ok = [r for r in rows if r["ms"] is not None]
        return uid, {
            "healthy": bool(ok) and is_link_allowed(link),
            "state": link_state(link),
            "latency": min((r["ms"] for r in ok), default=None),
            "targets": rows,
            "error": None if ok else ("No targets (open the panel through its public domain)" if not rows else "Unreachable"),
        }

    results = dict(await asyncio.gather(*[one(u) for u in uuids]))
    return {"results": results}


@app.get("/api/database/export")
async def export_db(_=Depends(require_auth)):
    return JSONResponse({"version": VERSION, "exported_at": datetime.now().isoformat(), "links": dict(LINKS)},
                        headers={"Content-Disposition": 'attachment; filename="mx-ui-backup.json"'})


@app.post("/api/database/import")
async def import_db(request: Request, _=Depends(require_auth)):
    body = await _json(request)
    incoming = body.get("links")
    if not isinstance(incoming, dict):
        raise HTTPException(status_code=400, detail="Backup file has no 'links' object")
    mode = body.get("mode", "merge")
    added = 0
    async with LINKS_LOCK:
        if mode == "replace":
            for uid in [u for u, l in LINKS.items() if not l.get("is_default")]:
                LINKS.pop(uid, None)
        for uid, link in incoming.items():
            try:
                uid = str(uuidlib.UUID(str(uid)))
            except ValueError:
                continue
            if not isinstance(link, dict):
                continue
            link = _normalize_link(link, uid)
            if link.get("is_default") and any(l.get("is_default") for l in LINKS.values()):
                link["is_default"] = False
            LINKS[uid] = link
            added += 1
    xray_manager.request_sync()
    await save_state()
    log_activity("backup", f"Imported {added} configs ({mode})", "ok")
    return {"ok": True, "imported": added}


# ============================================================ logs API
@app.get("/api/logs")
async def api_logs(_=Depends(require_auth), limit: int = 300, level: Optional[str] = None):
    return {"logs": xray_manager.get_logs(limit=limit, level=level), "activity": list(activity_logs)}


@app.post("/api/logs/clear")
async def api_logs_clear(_=Depends(require_auth)):
    xray_manager.clear_logs()
    activity_logs.clear()
    return {"ok": True}


@app.get("/api/logs/ports")
async def api_logs_ports(_=Depends(require_auth)):
    return xray_manager.port_status()


@app.get("/api/logs/files/{name}")
async def api_logs_files(name: str, _=Depends(require_auth), tail: int = 200):
    if name != "xray_stdout.log":
        raise HTTPException(status_code=404, detail="not found")
    return {"lines": xray_manager.read_log(name, tail=tail)}


# ============================================================ WebSocket gateways (VLESS-WS / Trojan-WS)
async def _first_chunk(ws: WebSocket, timeout: float = 15.0):
    msg = await asyncio.wait_for(ws.receive(), timeout=timeout)
    if msg.get("type") == "websocket.disconnect":
        return None
    return msg.get("bytes") or (msg.get("text") or "").encode()


def _uid_for_vless(chunk: bytes):
    return limits.vless_uuid_from_chunk(chunk or b"")


def _uid_for_trojan(chunk: bytes):
    """Map the Trojan password hash in the first chunk back to the config uuid."""
    digest = limits.trojan_hash_from_chunk(chunk or b"")
    if not digest:
        return None
    for uid, link in list(LINKS.items()):
        if link.get("protocols") and "trojan" not in link_protocols(link):
            continue
        if limits.trojan_hash(trojan_password_of(uid, link)) == digest:
            return uid
    return None


def _uid_for_token(token: str):
    """VMess and Shadowsocks carry the config's secret path token in the URL."""
    for uid, link in list(LINKS.items()):
        t = str(link.get("ws_token") or "")
        if t and hmac.compare_digest(t, token):
            return uid
    return None


async def _gateway(websocket: WebSocket, proto: str, token: Optional[str] = None):
    import websockets as _ws

    ip = get_client_ip(websocket)
    proto_hdr = websocket.headers.get("sec-websocket-protocol")
    early = limits.decode_early_data(proto_hdr)
    subproto = proto_hdr.split(",")[0].strip() if (proto_hdr and early) else None
    await websocket.accept(subprotocol=subproto)
    stats["total_requests"] += 1

    try:
        first = early if early else await _first_chunk(websocket)
    except Exception:
        first = None

    if token is not None:
        uid = _uid_for_token(token)
    else:
        resolve = _uid_for_vless if proto == "vless" else _uid_for_trojan
        uid = resolve(first or b"")
    link = LINKS.get(uid) if uid else None

    def reject(reason: str):
        stats["rejected"] += 1
        logger.debug(f"[{proto}] reject {ip}: {reason}")

    if not is_link_allowed(link):
        reject(f"config {uid} is {link_state(link)}")
        await websocket.close(code=1008)
        return
    if proto not in link_protocols(link):
        reject(f"config {uid} does not allow {proto}")
        await websocket.close(code=1008)
        return
    ip_limit = int(link.get("ip_limit") or 0)
    if ip_limit > 0:
        ips = unique_ips_for_uuid(uid)
        if ip not in ips and len(ips) >= ip_limit:
            reject(f"ip limit {ip_limit} reached for {uid}")
            await websocket.close(code=1008)
            return

    tag = xray_manager.TAG_FOR_PROTO[proto]
    upstream = f"ws://127.0.0.1:{xray_manager.PORTS[tag]}{xray_manager.PATHS[tag]}"
    try:
        # The core never needs our subprotocol token; early data is replayed as a normal frame.
        xray_ws = await _ws.connect(upstream, max_size=None, ping_interval=None,
                                    open_timeout=10, close_timeout=3, compression=None)
    except Exception as e:
        logger.warning(f"[{proto}] xray unreachable: {e}")
        await websocket.close(code=1011)
        return

    cid = secrets.token_hex(6)
    conn = {"uuid": uid, "ip": ip, "proto": proto,
            "connected_at": datetime.now().isoformat(timespec="seconds"), "up": 0, "down": 0}
    connections[cid] = conn
    stop = asyncio.Event()

    async def c2x():
        try:
            if first:  # protocol header (from early data or the first frame) goes to the core first
                await xray_ws.send(first)
                conn["up"] += len(first)
            while not stop.is_set():
                msg = await websocket.receive()
                if msg.get("type") == "websocket.disconnect":
                    break
                data = msg.get("bytes") or (msg.get("text") or "").encode()
                if not data:
                    continue
                b = limits.bucket_for(uid, "up", int(LINKS.get(uid, {}).get("speed_limit_bytes") or 0))
                if b:
                    await b.consume(len(data))
                await xray_ws.send(data)
                conn["up"] += len(data)
        except Exception:
            pass
        finally:
            stop.set()

    async def x2c():
        try:
            async for m in xray_ws:
                if stop.is_set():
                    break
                data = m if isinstance(m, (bytes, bytearray)) else m.encode()
                b = limits.bucket_for(uid, "down", int(LINKS.get(uid, {}).get("speed_limit_bytes") or 0))
                if b:
                    await b.consume(len(data))
                await websocket.send_bytes(bytes(data))
                conn["down"] += len(data)
        except Exception:
            pass
        finally:
            stop.set()

    async def guard():
        # Cuts live sessions within ~5s of being disabled, expiring or running out of data.
        while not stop.is_set():
            await asyncio.sleep(5)
            if not is_link_allowed(LINKS.get(uid)) or proto not in link_protocols(LINKS.get(uid) or {}):
                stop.set()

    tasks = [asyncio.create_task(f()) for f in (c2x, x2c, guard)]
    try:
        await stop.wait()
    finally:
        for t in tasks:
            t.cancel()
        connections.pop(cid, None)
        try:
            await xray_ws.close()
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass


@app.websocket(WS_PATH)
async def ws_gateway(websocket: WebSocket):
    await _gateway(websocket, "vless")


@app.websocket(TROJAN_WS_PATH)
async def trojan_gateway(websocket: WebSocket):
    await _gateway(websocket, "trojan")


@app.websocket("/vmess/{token}")
async def vmess_gateway(websocket: WebSocket, token: str):
    await _gateway(websocket, "vmess", token)


@app.websocket("/ss/{token}")
async def ss_gateway(websocket: WebSocket, token: str):
    await _gateway(websocket, "ss", token)


# ============================================================ custom-path catch-all (keep last)
@app.get("/{path:path}")
async def catchall(request: Request, path: str):
    if path in ("ws", "trojan") or path.startswith(("ws/", "trojan/", "vmess/", "ss/", "api/", "stats", "health")):
        raise HTTPException(status_code=404, detail="Not Found")
    p = "/" + path.strip("/")
    if p == CONFIG["dashboard_path"]:
        return await render_dashboard(request)
    if p == CONFIG["login_path"]:
        return await render_login(request)
    if p == CONFIG["setup_path"]:
        return await render_setup(request)
    sub = CONFIG["sub_path"].rstrip("/")
    if sub != "/sub" and p.startswith(sub + "/"):
        rest = p[len(sub) + 1:]
        if rest.endswith("/info"):
            return await subscription_portal(rest[:-5], request)
        return await sub_single(rest, request)
    raise HTTPException(status_code=404, detail="Not Found")


if __name__ == "__main__":
    logger.info(f"MX-UI {VERSION} listening on :{PUBLIC_PORT}")
    uvicorn.run("main:app", host="0.0.0.0", port=PUBLIC_PORT, log_level="warning", workers=1,
                proxy_headers=True, forwarded_allow_ips="*", ws_max_size=64 * 1024 * 1024,
                ws_ping_interval=20, ws_ping_timeout=30)
