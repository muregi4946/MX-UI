# pages.py — MX-UI v2.2.0 front-end foundation (no build step, no CDN scripts)
#
# Design notes
#   Subject : a self-hosted VLESS + Trojan tunnel panel run by one operator, shared with end users.
#   Lineage : a telephone exchange patch bay. Every config is a "line" with a status lamp
#             and a segmented VU meter; the header carries a live oscilloscope trace.
#   Mark    : "MX" monogram with two signal arcs, flat signal teal, 13/48 corner radius.
#   Type    : Red Hat Display (UI + statement numerals) / JetBrains Mono (data) / Vazirmatn (fa names)
#   Color   : signal teal #00b7a7 leads; violet #6d5ce7 = Trojan; amber #ffcd12 = attention;
#             carmine #a40000 = cut; ink-navy #16317d = upload trace. Neutrals tint toward teal.
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&family=Vazirmatn:wght@400;600;700&display=swap" rel="stylesheet">')

BASE_CSS = r"""
:root{
  --bg:#eef4f3;--card:#fcfefd;--card2:#f6faf9;--sunk:#e6eeec;--ink:#0f1e1d;--mut:#5a706d;
  --line:#d7e3e0;--line2:#c0d2ce;
  --sig:#00b7a7;--acc:#06796f;--acc-ink:#fff;--acc-soft:rgba(0,183,167,.13);
  --vio:#6d5ce7;--vio-soft:rgba(109,92,231,.13);--vio-ink:#4b3cc4;
  --amb:#ffcd12;--amb-ink:#7a5c00;--amb-soft:rgba(255,205,18,.22);
  --red:#b00014;--red-soft:rgba(176,0,20,.09);--navy:#16317d;--plum:#b86092;
  --seg-off:#d9e4e1;
  --sh1:0 1px 2px rgba(15,30,29,.06);
  --sh2:0 1px 0 rgba(15,30,29,.04),0 10px 30px -14px rgba(15,30,29,.22);
  --sh3:0 24px 70px -24px rgba(15,30,29,.45);
  --shadow:var(--sh2);
  --r:14px;--r-lg:20px;
  --ui:'Red Hat Display','Vazirmatn',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
  --mono:'JetBrains Mono','Vazirmatn',ui-monospace,Menlo,Consolas,monospace;color-scheme:light}
:root[data-theme=dark]{
  --bg:#081110;--card:#101c1b;--card2:#142221;--sunk:#0b1514;--ink:#e4efed;--mut:#8ca3a0;
  --line:#1f2f2d;--line2:#2c423e;
  --sig:#1ed3c0;--acc:#1ed3c0;--acc-ink:#042220;--acc-soft:rgba(30,211,192,.14);
  --vio:#9b8cff;--vio-soft:rgba(155,140,255,.15);--vio-ink:#b5a9ff;
  --amb:#ffcd12;--amb-ink:#ffd84a;--amb-soft:rgba(255,205,18,.13);
  --red:#ff6f61;--red-soft:rgba(255,111,97,.13);--navy:#86a2ff;--plum:#e08fbd;
  --seg-off:#1c2c2a;
  --sh1:0 1px 2px rgba(0,0,0,.4);
  --sh2:0 1px 0 rgba(0,0,0,.25),0 14px 36px -16px rgba(0,0,0,.7);
  --sh3:0 28px 80px -24px rgba(0,0,0,.85);color-scheme:dark}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{font-family:var(--ui);background:var(--bg);color:var(--ink);font-size:16px;line-height:1.5;min-height:100dvh;-webkit-font-smoothing:antialiased;font-feature-settings:"tnum" 1}
body.lock{overflow:hidden}
a{color:inherit}
button,input,select,textarea{font:inherit;color:inherit}
button{cursor:pointer;background:none;border:0}
::selection{background:var(--acc-soft)}
:focus-visible{outline:2px solid var(--sig);outline-offset:2px;border-radius:6px}
.mono{font-family:var(--mono);font-feature-settings:"zero" 1}
.mut{color:var(--mut)}.hidden{display:none!important}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
svg.i{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}
/* ---------- brand ---------- */
.logo{width:34px;height:34px;flex:none;border-radius:10px;box-shadow:var(--sh1)}
.logo.lg{width:46px;height:46px;border-radius:13px}
.logo.sm{width:26px;height:26px;border-radius:8px}
.wordmark{display:flex;flex-direction:column;min-width:0;line-height:1.05}
.wordmark b{font-weight:900;font-size:18px;letter-spacing:-.025em}
.wordmark b i{font-style:normal;color:var(--sig)}
.wordmark small{font:500 11.5px/1.4 var(--mono);color:var(--mut)}
/* ---------- lamp: the signature status light ---------- */
.lamp{--c:var(--seg-off);width:10px;height:10px;border-radius:50%;background:var(--c);flex:none;position:relative;box-shadow:inset 0 -1px 2px rgba(0,0,0,.25)}
.lamp.on{--c:var(--sig)}
.lamp.live{--c:var(--sig)}
.lamp.warn{--c:var(--amb)}
.lamp.cut{--c:var(--red)}
.lamp.off{background:transparent;box-shadow:inset 0 0 0 2px var(--line2)}

/* ---------- segmented VU meter ---------- */
.vu{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:3px;height:12px}
.vu i{border-radius:2px;background:var(--seg-off);transition:background .4s}
.vu i.f{background:var(--sig)}.vu i.f.a{background:var(--amb)}.vu i.f.r{background:var(--red)}
.vu.inf i{background:var(--seg-off);opacity:.55}
/* ---------- controls ---------- */
.field{display:grid;gap:6px;min-width:0}
.field>span{font-size:14px;font-weight:700}
.field>small{font-size:13.5px;color:var(--mut)}
.input{width:100%;height:46px;padding:0 14px;background:var(--card);border:1.5px solid var(--line);border-radius:11px;font-size:16px;transition:border-color .15s,box-shadow .15s}
.input::placeholder{color:var(--mut);opacity:.7}
.input:focus{outline:none;border-color:var(--sig);box-shadow:0 0 0 4px var(--acc-soft)}
textarea.input{height:auto;padding:12px 14px}
select.input{appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1.5l5 5 5-5' fill='none' stroke='%235a706d' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");background-position:calc(100% - 14px) 50%;background-size:12px 8px;background-repeat:no-repeat;padding-right:34px}
.join{display:flex}.join .input:first-child{border-radius:11px 0 0 11px;border-right:0}.join .input:last-child{border-radius:0 11px 11px 0;width:auto;min-width:96px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:44px;padding:0 18px;border-radius:11px;border:1.5px solid var(--line);background:var(--card);font-weight:700;font-size:15px;white-space:nowrap;transition:background .15s,border-color .15s,transform .08s,filter .15s,box-shadow .15s}
.btn:hover{border-color:var(--line2);background:var(--sunk)}.btn:active{transform:translateY(1px)}.btn:disabled{opacity:.5;cursor:not-allowed}
.btn.pri{background:var(--acc);border-color:var(--acc);color:#fff}
.btn.pri:hover{filter:brightness(1.08)}
.btn.bad{background:var(--red);border-color:var(--red);color:#fff}
.btn.ghost{border-color:transparent;background:transparent}.btn.ghost:hover{background:var(--sunk)}
.btn.sm{height:36px;padding:0 13px;font-size:14px;border-radius:9px}.btn.block{width:100%}
.ib{width:40px;height:40px;display:inline-grid;place-items:center;border-radius:11px;color:var(--mut);transition:background .15s,color .15s}
.ib:hover{background:var(--sunk);color:var(--ink)}.ib.sm{width:36px;height:36px;border-radius:10px}.ib.bad:hover{color:var(--red);background:var(--red-soft)}
.chip{display:inline-flex;align-items:center;gap:7px;height:30px;padding:0 12px;border-radius:99px;font-size:14px;font-weight:700;background:var(--sunk);color:var(--mut);white-space:nowrap}
.tag{display:inline-flex;align-items:center;height:22px;padding:0 8px;border-radius:6px;font:600 12.5px/1 var(--mono);background:var(--sunk);color:var(--mut);white-space:nowrap}
.tag.acc{background:var(--acc-soft);color:var(--acc)}.tag.amb{background:var(--amb-soft);color:var(--amb-ink)}
.tag.red{background:var(--red-soft);color:var(--red)}.tag.vio{background:var(--vio-soft);color:var(--vio-ink)}
/* protocol pills */
.pp{display:inline-flex;align-items:center;gap:6px;height:24px;padding:0 9px 0 7px;border-radius:7px;font:800 11.5px/1 var(--ui);letter-spacing:.06em;text-transform:uppercase;white-space:nowrap}
.pp svg{width:13px;height:13px;stroke-width:2.4}
.pp.vless{background:var(--acc-soft);color:var(--acc)}
.pp.trojan{background:var(--vio-soft);color:var(--vio-ink)}
.pp.vmess{background:rgba(22,49,125,.12);color:var(--navy)}
.pp.ss{background:var(--amb-soft);color:var(--amb-ink)}
.alert{padding:11px 14px;border-radius:11px;background:var(--red-soft);color:var(--red);font-size:14px;font-weight:700}
.note{display:flex;gap:12px;align-items:flex-start;padding:13px 15px;border-radius:12px;background:var(--sunk);font-size:14px}
.note.amb{background:var(--amb-soft)}.note.amb svg{color:var(--amb-ink)}
.note.acc{background:var(--acc-soft)}.note.acc svg{color:var(--acc)}
.note b{display:block;font-size:15px}
.toast{position:fixed;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translate(-50%,18px);max-width:min(92vw,440px);background:var(--ink);color:var(--bg);padding:12px 18px;border-radius:12px;font-size:15px;font-weight:700;opacity:0;pointer-events:none;transition:opacity .2s,transform .25s cubic-bezier(.2,.9,.3,1.3);z-index:200;display:flex;gap:10px;align-items:center;box-shadow:var(--sh3)}
.toast.on{opacity:1;transform:translate(-50%,0)}
.toast.ok::before,.toast.err::before{content:"";width:9px;height:9px;border-radius:50%;background:var(--sig);box-shadow:0 0 8px var(--sig)}
.toast.err::before{background:#ff6f61;box-shadow:0 0 8px #ff6f61}
/* theme toggle swaps glyphs with the root attribute */
.ic-sun{display:none}
:root[data-theme=dark] .ic-sun{display:block}
:root[data-theme=dark] .ic-moon{display:none}
@keyframes scalein{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:scale(1)}}
@keyframes scaleout{from{opacity:1;transform:scale(1)}to{opacity:0;transform:scale(.96)}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}
"""

SPRITE_ICONS = {
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "copy": '<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>',
    "qr": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3M21 14v.01M14 21h3M21 17v4"/>',
    "open": '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "edit": '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "trash": '<path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6"/>',
    "reset": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "pulse": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "db": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5M3 12c0 1.7 4 3 9 3s9-1.3 9-3"/>',
    "cog": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z"/>',
    "out": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
    "sun": '<circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M19.1 4.9l-1.8 1.8M6.7 17.3l-1.8 1.8"/>',
    "moon": '<path d="M21 13.2A9 9 0 1 1 10.8 3a7.2 7.2 0 0 0 10.2 10.2Z"/>',
    "refresh": '<path d="M21 12a9 9 0 0 0-15-6.7L3 8M3 3v5h5M3 12a9 9 0 0 0 15 6.7L21 16M21 21v-5h-5"/>',
    "dl": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
    "up": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>',
    "chev": '<path d="m6 9 6 6 6-6"/>',
    "back": '<path d="m15 18-6-6 6-6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 16v-5M12 8h.01"/>',
    "play": '<path d="m6 3 14 9-14 9Z"/>',
    "terminal": '<rect x="2.5" y="4" width="19" height="16" rx="3"/><path d="m7 10 2.5 2.5L7 15M12.5 15H17"/>',
    "dots": '<circle cx="5" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="19" cy="12" r="1.2"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "shield": '<path d="M12 22s8-3.5 8-10V5.3L12 2 4 5.3V12c0 6.5 8 10 8 10Z"/><path d="m8.8 12 2.2 2.2L15.4 10"/>',
    "key": '<circle cx="8" cy="15" r="4.2"/><path d="m11 12 8.5-8.5M16 4.5l3.5 3.5M13.5 7l3.5 3.5"/>',
    "bolt": '<path d="M13.5 2 4 14h6l-1.5 8L19 10h-6Z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3.2 2"/>',
    "cpu": '<rect x="6" y="6" width="12" height="12" rx="2.5"/><path d="M9 2.5v3M15 2.5v3M9 18.5v3M15 18.5v3M2.5 9h3M2.5 15h3M18.5 9h3M18.5 15h3"/>',
    "server": '<rect x="3" y="3.5" width="18" height="7" rx="2.2"/><rect x="3" y="13.5" width="18" height="7" rx="2.2"/><path d="M7 7h.01M7 17h.01"/>',
    "gauge": '<path d="M20.5 16a9 9 0 1 0-17 0"/><path d="m14.5 10.5-3 4.5"/>',
    "wifi": '<path d="M2.5 9a16 16 0 0 1 19 0M5.5 12.6a11.5 11.5 0 0 1 13 0M8.5 16.2a7 7 0 0 1 7 0M12 20h.01"/>',
    "sliders": '<path d="M5 21v-7M5 10V3M12 21v-9M12 8V3M19 21v-5M19 12V3M2.5 14h5M9.5 8h5M16.5 16h5"/>',
    "filter": '<path d="M3 4.5h18l-7 8.2V20l-4-2.3v-5z"/>',
    "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 10.6 6.8-4.2M8.6 13.4l6.8 4.2"/>',
}
# Protocol marks: VLESS = braided signal, Trojan = shielded key
_BRAND_DEFS = (
    '<symbol id="i-brand" viewBox="0 0 48 48">'
    '<rect width="48" height="48" rx="13" fill="#0a7f73"/>'
    '<path d="M10.5 34V14.6L19.3 25.4 28 14.6V34" fill="none" stroke="#fff" stroke-width="3.5" '
    'stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M33.6 19.4a8.4 8.4 0 0 1 0 9.2" fill="none" stroke="#fff" stroke-width="2.8" '
    'stroke-linecap="round" opacity=".95"/>'
    '<path d="M38.4 15.4a14 14 0 0 1 0 17.2" fill="none" stroke="#fff" stroke-width="2.8" '
    'stroke-linecap="round" opacity=".55"/>'
    '</symbol>'
)
SPRITE = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
          + _BRAND_DEFS
          + "".join('<symbol id="i-%s" viewBox="0 0 24 24">%s</symbol>' % kv for kv in SPRITE_ICONS.items())
          + '</defs></svg>')


def ic(name):
    return '<svg class="i" aria-hidden="true"><use href="#i-%s"/></svg>' % name


def logo(cls=""):
    return '<svg class="logo %s" viewBox="0 0 48 48" aria-hidden="true"><use href="#i-brand"/></svg>' % cls


def wordmark(sub="", cls=""):
    return ('<div class="wordmark %s"><b>MX<i>-</i>UI</b>%s</div>'
            % (cls, ("<small>%s</small>" % sub) if sub else ""))


def brand(sub="", logo_cls="", wrap_style=""):
    return ('<div class="brand" style="%s">%s%s</div>' % (wrap_style, logo(logo_cls), wordmark(sub)))


THEME_BTN = ('<button class="ib" onclick="toggleTheme()" title="Light / dark theme" aria-label="Toggle theme">'
             '<svg class="i ic-moon" aria-hidden="true"><use href="#i-moon"/></svg>'
             '<svg class="i ic-sun" aria-hidden="true"><use href="#i-sun"/></svg></button>')

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Cdefs%3E"
           "%3Crect width='48' height='48' rx='13' fill='%230a7f73'/%3E"
           "%3Cpath d='M10.5 34V14.6L19.3 25.4 28 14.6V34' fill='none' stroke='%23fff' stroke-width='3.5' "
           "stroke-linecap='round' stroke-linejoin='round'/%3E"
           "%3Cpath d='M33.6 19.4a8.4 8.4 0 0 1 0 9.2' fill='none' stroke='%23fff' stroke-width='2.8' "
           "stroke-linecap='round'/%3E%3C/svg%3E")

HEAD = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#081110" media="(prefers-color-scheme:dark)">
<meta name="theme-color" content="#eef4f3" media="(prefers-color-scheme:light)">
<meta name="robots" content="noindex,nofollow">
<title>__TITLE__</title>
<link rel="icon" href="__FAVICON__">
<link rel="apple-touch-icon" href="__FAVICON__">
__FONTS__
<script>try{var t=localStorage.getItem('mx-theme')}catch(e){}document.documentElement.dataset.theme=t||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light')</script>
<style>__BASE__
__CSS__</style>
</head>
"""


def page(title, css, body):
    return (HEAD.replace("__TITLE__", title).replace("__FONTS__", FONTS).replace("__FAVICON__", FAVICON)
            .replace("__BASE__", BASE_CSS).replace("__CSS__", css) + body)


UTIL_JS = r"""
var $=function(id){return document.getElementById(id);};
var $$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));};
var api=function(u,m,b){var o={method:m||'GET',headers:{'Content-Type':'application/json'},credentials:'same-origin'};if(b!==undefined)o.body=JSON.stringify(b);return fetch(u,o).then(function(r){if(r.status===401&&!/^\/api\/(login|setup)/.test(u)){location.replace('/login');throw new Error('Signed out');}return r;});};
var esc=function(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
var ic=function(n){return '<svg class="i" aria-hidden="true"><use href="#i-'+n+'"/></svg>';};
var PROTO_META={vless:{n:'VLESS',c:'vless',i:'bolt'},trojan:{n:'Trojan',c:'trojan',i:'shield'},vmess:{n:'VMess',c:'vmess',i:'cpu'},ss:{n:'Shadowsocks',c:'ss',i:'key'}};
function protoPill(p){var m=PROTO_META[String(p||'').toLowerCase()]||PROTO_META.vless;return '<span class="pp '+m.c+'">'+ic(m.i)+m.n+'</span>';}
function toast(t,k){var e=$('toast');if(!e)return;e.textContent=t;e.className='toast on '+(k||'');clearTimeout(toast.t);toast.t=setTimeout(function(){e.classList.remove('on');},2600);}
function copyText(t,msg){
  var ok=function(){toast(msg||'Copied','ok');};
  var fb=function(){var a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.cssText='position:fixed;opacity:0;left:-9999px';document.body.appendChild(a);a.select();try{document.execCommand('copy');ok();}catch(e){toast('Copy failed','err');}a.remove();};
  if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok,fb);}else{fb();}
}
function fmtBytes(b){b=Number(b)||0;var u=['B','KB','MB','GB','TB'],i=0;while(b>=1024&&i<u.length-1){b/=1024;i++;}return (i?b.toFixed(b>=100?0:b>=10?1:2):b)+' '+u[i];}
function fmtRate(bps){return fmtBytes(bps)+'/s';}
function vu(pct,n,inf){n=n||20;var h='';if(inf){for(var j=0;j<n;j++)h+='<i></i>';return '<div class="vu inf" role="img" aria-label="Unlimited">'+h+'</div>';}
  pct=Math.max(0,Math.min(100,pct||0));var f=Math.round(pct/100*n);if(pct>0&&f===0)f=1;
  for(var i=0;i<n;i++){var p=(i+1)/n*100,c=i<f?'f'+(p>90?' r':p>70?' a':''):'';h+='<i class="'+c+'"></i>';}
  return '<div class="vu" role="img" aria-label="'+pct.toFixed(0)+'% used">'+h+'</div>';}
function toggleTheme(){var d=document.documentElement;d.dataset.theme=d.dataset.theme==='dark'?'light':'dark';try{localStorage.setItem('mx-theme',d.dataset.theme);}catch(e){}if(window.onThemeChange)window.onThemeChange();}
/* confirm dialog, shared by every page that includes #askModal */
function ask(title,msg,ok,danger){return new Promise(function(res){
  var t=$('askTitle'),m=$('askMsg'),y=$('askYes'),n=$('askNo');
  if(!t||!y){res(window.confirm(msg||title));return;}
  t.textContent=title;m.textContent=msg||'';y.textContent=ok||'Confirm';y.className='btn '+(danger?'bad':'pri');
  var bd=$('askBdg');if(bd)bd.className='bdg'+(danger?' bad':'');
  var done=function(v){y.onclick=n.onclick=null;closeModal('askModal');res(v);};
  y.onclick=function(){done(true);};n.onclick=function(){done(false);};openModal('askModal');y.focus();});}
function openModal(id){var m=$(id);if(!m)return;m._from=document.activeElement;m.classList.add('open');document.body.classList.add('lock');
  setTimeout(function(){var s=m.querySelector('.sheet');if(s)s.focus();},40);
  if(window.onModalOpen)window.onModalOpen(id);}
function closeModal(id){var m=$(id);if(!m)return;m.classList.remove('open');if(!$$('.modal.open').length)document.body.classList.remove('lock');
  if(m._from&&m._from.focus)m._from.focus();if(window.onModalClose)window.onModalClose(id);}
document.addEventListener('pointerdown',function(e){if(e.target.classList&&e.target.classList.contains('modal'))closeModal(e.target.id);});
document.addEventListener('keydown',function(e){if(e.key==='Escape'){var o=$$('.modal.open');if(o.length)closeModal(o[o.length-1].id);}});
"""

# shared modal + dialog chrome (dashboard and logs both use it)
MODAL_CSS = r"""
.modal{position:fixed;inset:0;z-index:100;display:grid;place-items:center;padding:18px;background:rgba(4,12,11,.55);backdrop-filter:blur(7px);-webkit-backdrop-filter:blur(7px);opacity:0;pointer-events:none;transition:opacity .2s}.modal.open{opacity:1;pointer-events:auto;animation:scalein .22s ease both}
.modal.open{opacity:1;pointer-events:auto}
.sheet{width:min(var(--w,560px),100%);max-height:calc(100dvh - 36px);display:flex;flex-direction:column;background:var(--card);border:1.5px solid var(--line);border-radius:22px;box-shadow:var(--sh3);transform:translateY(14px) scale(.985);transition:transform .3s cubic-bezier(.2,.9,.3,1.1);outline:none}.modal.open .sheet{animation:scalein .28s cubic-bezier(.2,.8,.2,1) both}
.modal.open .sheet{transform:none}
.mh{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;padding:22px 22px 0}
.mh h3{font-size:24px;font-weight:900;letter-spacing:-.025em;line-height:1.1}
.mh p{color:var(--mut);font-size:14.5px;margin-top:6px}
.mb{padding:18px 22px;overflow:auto;display:grid;gap:16px;min-height:0}
.mf{padding:0 22px 22px;display:flex;justify-content:flex-end;gap:10px;flex-wrap:wrap;align-items:center}
.confirm .sheet{--w:420px}
.bdg{width:52px;height:52px;border-radius:16px;display:grid;place-items:center;background:var(--amb-soft);color:var(--amb-ink);margin-bottom:6px}
.bdg.bad{background:var(--red-soft);color:var(--red)}
.bdg svg{width:24px;height:24px}
"""

ASK_MODAL = (
    '<div id="askModal" class="modal confirm" role="alertdialog" aria-modal="true" aria-labelledby="askTitle">'
    '<div class="sheet" tabindex="-1"><div class="mb" style="gap:12px;padding:26px">'
    '<div class="bdg" id="askBdg">' + ic("alert") + '</div>'
    '<h3 id="askTitle" style="font-size:22px;font-weight:900;letter-spacing:-.02em">Are you sure?</h3>'
    '<p id="askMsg" class="mut"></p></div>'
    '<div class="mf"><button class="btn" id="askNo">Cancel</button>'
    '<button class="btn pri" id="askYes">Confirm</button></div></div></div>')

# trace used behind auth screens: a slow oscilloscope sweep
TRACE_SVG = ('<svg class="trace" viewBox="0 0 1200 400" preserveAspectRatio="none" aria-hidden="true">'
             '<path class="grid" d="M0 100H1200M0 200H1200M0 300H1200M200 0V400M400 0V400M600 0V400M800 0V400M1000 0V400"/>'
             '<path class="wave" d="M0 210 C60 210 80 150 120 150 S180 260 240 260 300 120 360 120 420 230 480 230 540 180 600 180 660 300 720 300 780 90 840 90 900 220 960 220 1020 170 1080 170 1140 210 1200 210"/>'
             '<path class="wave w2" d="M0 250 C80 250 110 230 160 230 S260 280 330 280 420 210 500 210 600 260 680 260 780 220 860 220 960 270 1040 270 1140 240 1200 240"/></svg>')

# ============================================================ AUTH (login / setup)
AUTH_CSS = r"""
body{display:grid;place-items:center;padding:24px 18px;overflow-x:hidden;position:relative}
.trace{position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none}
.trace .grid{stroke:var(--line);stroke-width:1;fill:none;opacity:.7}
.trace .wave{fill:none;stroke:var(--sig);stroke-width:2.5;opacity:.5;filter:drop-shadow(0 0 6px var(--sig))}
.trace .w2{stroke:var(--vio);opacity:.22;animation-delay:-4.5s;filter:none}

.card{position:relative;z-index:1;width:100%;max-width:430px;background:var(--card);border:1.5px solid var(--line);border-radius:24px;padding:32px 30px 26px;box-shadow:var(--sh3);display:grid;gap:20px}
.card::before{content:"";position:absolute;inset:0 0 auto;height:3px;border-radius:24px 24px 0 0;background:var(--acc)}
.brand{display:flex;align-items:center;gap:12px}
.brand .ver{margin-left:auto;font:600 12px var(--mono);color:var(--mut);background:var(--sunk);border-radius:99px;padding:5px 10px}
h1{font-size:36px;line-height:1.04;font-weight:900;letter-spacing:-.035em}
h1+p{color:var(--mut);margin-top:8px}
.pw{position:relative}.pw .input{padding-right:48px}.pw button{position:absolute;right:4px;top:3px}
.strength{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;height:6px}.strength i{border-radius:3px;background:var(--seg-off);transition:background .25s}
.strength[data-s="1"] i:nth-child(-n+1){background:var(--red)}.strength[data-s="2"] i:nth-child(-n+2){background:var(--amb)}
.strength[data-s="3"] i:nth-child(-n+3){background:var(--sig)}.strength[data-s="4"] i{background:var(--sig)}
.shake{outline:2px solid var(--red);outline-offset:2px}
.protos{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}
.foot{text-align:center;font-size:13.5px;color:var(--mut)}
.themebtn{position:fixed;top:14px;right:14px;z-index:2}
@media(max-width:480px){.card{padding:26px 20px 22px;border-radius:20px}h1{font-size:31px}.themebtn{top:auto;bottom:12px;right:12px}}
"""


def _auth_page(title, heading, sub, form_inner, script):
    return page(title, AUTH_CSS, '<body>' + SPRITE + TRACE_SVG +
                '<div class="themebtn">' + THEME_BTN + '</div>'
                '<main class="card"><div class="brand">' + logo("lg") + wordmark("Xray control panel") +
                '<span class="ver">v2.2</span></div>'
                '<div><h1>' + heading + '</h1><p>' + sub + '</p></div>' + form_inner +
                '<div class="protos">' + '<span class="pp vless">' + ic("bolt") + 'VLESS</span>'
                '<span class="pp trojan">' + ic("shield") + 'Trojan</span>'
                '<span class="pp vmess">' + ic("cpu") + 'VMess</span><span class="pp ss">' + ic("key") + 'Shadowsocks</span>'
                '<span class="pp vless" style="background:var(--sunk);color:var(--mut)">' + ic("wifi") + 'WebSocket</span></div>'
                '<p class="foot">Created by Muvixo</p></main><div id="toast" class="toast" role="status"></div>'
                '<script>' + UTIL_JS + script + '</script></body></html>')


def _pw_field(fid, label, ac, ph):
    return ('<label class="field"><span>' + label + '</span><div class="pw"><input type="password" id="' + fid +
            '" class="input" required autocomplete="' + ac + '" placeholder="' + ph + '">'
            '<button type="button" class="ib sm" data-eye="' + fid + '" aria-label="Show password">' + ic("eye") + '</button></div></label>')


_EYE_JS = r"""
document.querySelectorAll('[data-eye]').forEach(function(b){b.onclick=function(){var i=$(b.dataset.eye);i.type=i.type==='password'?'text':'password';i.focus();};});
"""

LOGIN_HTML = _auth_page(
    "Sign in · MX-UI", "Patch in.", "Admin password opens the switchboard.",
    '<form id="f" class="field" style="gap:16px" novalidate>' + _pw_field("pw", "Password", "current-password", "Your admin password") +
    '<div id="err" class="alert hidden" role="alert"></div>'
    '<button type="submit" id="go" class="btn pri block">Sign in</button></form>',
    _EYE_JS + r"""
$('pw').focus();
$('f').onsubmit=async function(e){
  e.preventDefault();var b=$('go'),er=$('err'),pw=$('pw');
  if(!pw.value){pw.focus();return;}
  er.classList.add('hidden');b.disabled=true;b.textContent='Checking…';
  try{
    var r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw.value})});
    if(!r.ok){var m='Wrong password';try{var d=await r.json();if(d.detail)m=d.detail;}catch(x){}throw new Error(m);}
    var p={};try{p=await (await fetch('/api/current-paths')).json();}catch(x){}
    location.replace(p.dashboard||'/dashboard');
  }catch(x){
    er.textContent=x.message;er.classList.remove('hidden');b.disabled=false;b.textContent='Sign in';
    var c=document.querySelector('.card');c.classList.remove('shake');void c.offsetWidth;c.classList.add('shake');pw.select();
  }
};
""")

SETUP_HTML = _auth_page(
    "First run · MX-UI", "Set the master key.", "First boot. Pick the password that guards this panel.",
    '<form id="f" class="field" style="gap:16px" novalidate>' + _pw_field("pw", "New password", "new-password", "At least 6 characters") +
    '<div class="strength" id="st" data-s="0" aria-hidden="true"><i></i><i></i><i></i><i></i></div>' +
    _pw_field("pw2", "Repeat it", "new-password", "Same again") +
    '<div id="err" class="alert hidden" role="alert"></div>'
    '<button type="submit" id="go" class="btn pri block">Save and open dashboard</button></form>',
    _EYE_JS + r"""
$('pw').focus();
$('pw').oninput=function(){var v=this.value,s=0;if(v.length>=6)s++;if(v.length>=10)s++;if(/[A-Z]/.test(v)&&/[a-z]/.test(v))s++;if(/[0-9]/.test(v)&&/[^A-Za-z0-9]/.test(v))s++;$('st').dataset.s=v?Math.max(1,s):0;};
$('f').onsubmit=async function(e){
  e.preventDefault();var b=$('go'),er=$('err'),a=$('pw').value,c=$('pw2').value;
  var fail=function(m){er.textContent=m;er.classList.remove('hidden');};
  er.classList.add('hidden');
  if(a.length<6)return fail('Use at least 6 characters.');
  if(a!==c)return fail("Passwords don't match.");
  b.disabled=true;b.textContent='Saving…';
  try{
    var r=await fetch('/api/setup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:a})});
    var d=await r.json().catch(function(){return {};});
    if(!r.ok)throw new Error(d.detail||'Setup failed');
    var p={};try{p=await (await fetch('/api/current-paths')).json();}catch(x){}
    location.replace(p.dashboard||'/dashboard');
  }catch(x){fail(x.message);b.disabled=false;b.textContent='Save and open dashboard';}
};
""")
