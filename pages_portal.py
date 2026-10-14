# pages_portal.py — the page a subscriber sees when they open their link in a browser (v2.3.0).
#
# Lineage: a boarding pass. The QR sits on a perforated stub, the quota is a segmented
# fuel-gauge, and the status is a rubber stamp. Links are grouped by protocol (VLESS / Trojan).
# Everything is server-rendered; JS is only used for copy buttons and the theme toggle.
import html as _h

from pages import page, ic, SPRITE, UTIL_JS, THEME_BTN, brand
from theme import PORTAL_CSS



PORTAL_JS = r"""
function copyAll(){var v=$$('.lrow input').map(function(i){return i.value;}).filter(Boolean);if(!v.length)return toast('Nothing to copy','err');copyText(v.join('\n'),'All '+v.length+' links copied');}
document.addEventListener('click',function(e){var b=e.target.closest('[data-copy]');if(b){var i=document.getElementById(b.dataset.copy);copyText(i.value,'Link copied');}});
document.querySelectorAll('.lrow input').forEach(function(i){i.addEventListener('focus',function(){i.select();});});
"""


def _gb(n) -> str:
    n = float(n or 0)
    for unit, size in (("TB", 1024 ** 4), ("GB", 1024 ** 3), ("MB", 1024 ** 2), ("KB", 1024)):
        if n >= size:
            return f"{n / size:.2f} {unit}"
    return f"{int(n)} B"


def _fmt_date(iso):
    if not iso:
        return "Never"
    try:
        from datetime import datetime
        return datetime.fromisoformat(iso).strftime("%d %b %Y")
    except Exception:
        return str(iso)[:10]


def _vu(pct: float, n: int = 30, unlimited: bool = False) -> str:
    if unlimited:
        return '<div class="vu inf" role="img" aria-label="Unlimited">' + "<i></i>" * n + "</div>"
    pct = max(0.0, min(100.0, pct))
    filled = round(pct / 100 * n)
    if pct > 0 and filled == 0:
        filled = 1
    cells = []
    for i in range(n):
        p = (i + 1) / n * 100
        cls = ""
        if i < filled:
            cls = "f" + (" r" if p > 90 else " a" if p > 70 else "")
        cells.append(f'<i class="{cls}"></i>')
    return f'<div class="vu" role="img" aria-label="{pct:.0f}% used">' + "".join(cells) + "</div>"


_PP = {"vless": ("vless", "bolt", "VLESS"), "trojan": ("trojan", "shield", "Trojan"),
       "vmess": ("vmess", "cpu", "VMess"), "ss": ("ss", "key", "Shadowsocks")}
_PORTAL_ORDER = [(k, v[2]) for k, v in _PP.items()]


def _pill(proto: str) -> str:
    cls, icon, name = _PP.get(proto, _PP["vless"])
    return f'<span class="pp {cls}">{ic(icon)}{name}</span>'


def _variant_row(rid: str, v: dict, e) -> str:
    proto = str(v.get("protocol") or "vless")
    pill = ('<span class="pp trojan">' + ic("shield") + 'Trojan</span>') if proto == "trojan" \
        else ('<span class="pp vless">' + ic("bolt") + 'VLESS</span>')
    where = e(str(v.get("where") or "Domain"))
    return (f'<div class="lrow"><span class="tag">{where}</span>'
            f'<input id="{rid}" readonly value="{e(v["url"])}" aria-label="{e(v.get("tag", proto))} link">'
            f'<button class="btn sm" data-copy="{rid}">{ic("copy")}<span>Copy</span></button></div>'), pill


def render_portal(d: dict) -> str:
    """d: output of main.link_public() without ip_pool/note, plus a 'qr' data-URI."""
    e = _h.escape
    label = e(str(d.get("label") or "Config"))
    state = d.get("state", "active")
    limit = int(d.get("limit_bytes") or 0)
    used = int(d.get("used_bytes") or 0)
    pct = 0.0 if limit <= 0 else min(100.0, used / limit * 100)
    unlimited = limit <= 0

    stamp_cls, stamp_text, lamp = {
        "active": ("", "Active", "live"),
        "disabled": ("off", "Paused", "off"),
        "expired": ("bad", "Expired", "cut"),
        "depleted": ("warn", "Out of data", "warn"),
    }.get(state, ("off", "Unavailable", "off"))

    days = d.get("days_left")
    if d.get("expires_at"):
        exp_text = _fmt_date(d.get("expires_at"))
        exp_sub = f"{int(days) if days is not None else 0} day(s) left" if state == "active" else ""
    else:
        exp_text, exp_sub = "Never", "No expiry"

    protos = d.get("protocols") or ["vless"]
    pills = "".join(_pill(x) for x in protos)

    variants = d.get("variants") or []
    groups, idx = [], 0
    for proto, title in _PORTAL_ORDER:
        rows = []
        for v in variants:
            if v.get("protocol") != proto:
                continue
            rid = f"lk{idx}"
            idx += 1
            rows.append(_variant_row(rid, v, e)[0])
        if rows:
            groups.append(f'<div class="group"><div class="group-h">{title} · {len(rows)} link'
                          f'{"s" if len(rows) != 1 else ""}</div><div class="linkbox">{"".join(rows)}</div></div>')
    links_html = "".join(groups) if groups else '<div class="none">No links available right now.</div>'

    sub_url = e(str(d.get("sub_url") or ""))
    rows_sub = (f'<div class="lrow"><span class="tag">Subscription</span>'
                f'<input id="subUrl" readonly value="{sub_url}" aria-label="Subscription URL">'
                f'<button class="btn sm" data-copy="subUrl">{ic("copy")}<span>Copy</span></button></div>')

    return page(f"{label} · MX-UI", PORTAL_CSS, f"""<body>
{SPRITE}
<div class="theme">{THEME_BTN}</div>
<article class="pass" aria-labelledby="pname">
  <header class="head">
    {brand("Subscription pass", "sm")}
    <span class="sp"></span>
    <span class="lamp {lamp}"></span>
  </header>
  <div class="body">
    <section class="main">
      <div style="display:grid;gap:12px">
        <h1 class="name" id="pname">{label}</h1>
        <div class="ptags">{pills}<span class="stamp {stamp_cls}"><span class="lamp {lamp}"></span>{stamp_text}</span></div>
      </div>
      <div class="gauge">
        <div class="top"><b>{_gb(used)}<em> / {_gb(limit) if not unlimited else "∞"}</em></b><span>{"unlimited" if unlimited else f"{pct:.0f}% used"}</span></div>
        {_vu(pct, 30, unlimited)}
      </div>
      <div class="facts">
        <div><small>Remaining</small><b>{"∞" if unlimited else _gb(max(0, limit - used))}</b></div>
        <div><small>Expires</small><b>{exp_text}</b><small>{exp_sub}</small></div>
        <div><small>Last seen</small><b>{_fmt_date(d.get("last_used")) if d.get("last_used") else "—"}</b></div>
        <div><small>Live devices</small><b>{int(d.get("live_connections") or 0)}</b></div>
      </div>
      <div class="sec"><b>Connection links</b><button class="btn sm" onclick="copyAll()">{ic("copy")}<span>Copy all</span></button></div>
      {links_html}
      <div class="linkbox">{rows_sub}</div>
    </section>
    <aside class="stub">
      <div class="qr"><img src="{d.get("qr", "")}" alt="Subscription QR code"></div>
      <small>Scan with your client<br>to import everything</small>
    </aside>
  </div>
  <footer class="foot"><span>Created by Muvixo</span><span>MX-UI <b>v2.3.0</b></span></footer>
</article>
<div id="toast" class="toast" role="status" aria-live="polite"></div>
<script>{UTIL_JS}{PORTAL_JS}</script>
</body></html>""")
