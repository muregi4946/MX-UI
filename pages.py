# pages.py — MX-UI v2.3.0 front-end foundation (no build step). All CSS lives in theme.py ("Aurora Glass").
from theme import FONTS, AURORA, BASE_CSS, MODAL_CSS, AUTH_CSS
#
# Design notes
#   Subject : a self-hosted tunnel control plane for one operator.
#   Direction: NIGHT SHIFT / a quiet operations room, with hard-edged telemetry and luminous status.
#   Mark    : MX monogram, signal cyan, graphite surfaces, acid-lime health accents.
#   Type    : Red Hat Display + JetBrains Mono + Vazirmatn.



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
    '<defs><linearGradient id="mxg" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse"><stop stop-color="#0a7f73"/><stop offset="1" stop-color="#16b9a5"/></linearGradient></defs>'
    '<rect width="48" height="48" rx="14" fill="url(#mxg)"/>'
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
<meta name="theme-color" content="#07070f" media="(prefers-color-scheme:dark)">
<meta name="theme-color" content="#eef3f4">
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
    loader = '<div class="page-loader" aria-hidden="true"><div><div class="loader-mark"></div><div class="loader-bar"><i></i></div></div></div>'
    loader_script = ('<script>(function(){function h(){var l=document.querySelector(".page-loader");if(l){requestAnimationFrame(function(){l.classList.add("hide");setTimeout(function(){l.remove();},380);});}}'
                     'if(document.readyState==="complete"||document.readyState==="interactive")h();else document.addEventListener("DOMContentLoaded",h);})();</script>')
    if body.lstrip().startswith("<body>"):
        body = body.replace("<body>", "<body>" + AURORA + loader, 1)
    else:
        body = AURORA + loader + body
    body = body + loader_script
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


ASK_MODAL = (
    '<div id="askModal" class="modal confirm" role="alertdialog" aria-modal="true" aria-labelledby="askTitle">'
    '<div class="sheet" tabindex="-1"><div class="mb" style="gap:12px;padding:26px">'
    '<div class="bdg" id="askBdg">' + ic("alert") + '</div>'
    '<h3 id="askTitle" style="font-size:22px;font-weight:900;letter-spacing:-.02em">Are you sure?</h3>'
    '<p id="askMsg" class="mut"></p></div>'
    '<div class="mf"><button class="btn" id="askNo">Cancel</button>'
    '<button class="btn pri" id="askYes">Confirm</button></div></div></div>')


# ============================================================ AUTH (login / setup)



def _auth_page(title, heading, sub, form_inner, script):
    return page(title, AUTH_CSS, '<body>' + SPRITE +
                '<div class="themebtn">' + THEME_BTN + '</div>'
                '<main class="card"><div class="brand">' + logo("lg") + wordmark("Xray control panel") +
                '<span class="ver">v2.3</span></div>'
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
