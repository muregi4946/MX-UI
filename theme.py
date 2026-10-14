# theme.py — MX-UI v2.3.0 "Aurora Glass" design system (single source of truth for all CSS)
#
#   Direction : calm glass surfaces floating over a slow aurora. Violet = brand/actions,
#               teal = healthy/live, amber/red = warnings. Dark-first, with a clean light theme.
#   Type      : Plus Jakarta Sans (UI) + JetBrains Mono (numbers/links) + Vazirmatn (Persian fallback).
#   Motion    : staggered reveals, springy toggles, pulsing lamps, bottom-sheet modals on phones.
#               Everything respects prefers-reduced-motion.

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&'
         'family=JetBrains+Mono:wght@400;500;600&family=Vazirmatn:wght@400;600;700&display=swap" rel="stylesheet">')

AURORA = ('<div class="aurora" aria-hidden="true"><i></i><i></i><i></i></div>')

BASE_CSS = r"""
:root{
  --bg:#f3f4fb;--card:rgba(255,255,255,.82);--card2:rgba(255,255,255,.95);--sunk:rgba(24,26,60,.05);
  --ink:#14162b;--mut:#6a6e8c;--line:rgba(24,26,60,.10);--line2:rgba(24,26,60,.20);
  --acc:#5b4bf0;--acc2:#2f7bff;--acc-ink:#fff;--acc-soft:rgba(91,75,240,.11);
  --sig:#0d9488;--sig-soft:rgba(13,148,136,.12);
  --vio:#7c3aed;--vio-soft:rgba(124,58,237,.11);--vio-ink:#6d28d9;
  --amb:#d97706;--amb-ink:#b45309;--amb-soft:rgba(217,119,6,.13);
  --red:#e11d48;--red-soft:rgba(225,29,72,.10);--navy:#3b82f6;--plum:#db2777;
  --seg-off:rgba(24,26,60,.09);--glow:rgba(91,75,240,.28);
  --sh1:0 1px 2px rgba(24,26,60,.06),0 1px 1px rgba(24,26,60,.04);
  --sh2:0 10px 30px -14px rgba(40,40,100,.22);
  --sh3:0 30px 80px -24px rgba(40,40,100,.38);
  --shadow:var(--sh2);--r:12px;--r-lg:20px;--blur:saturate(1.5) blur(18px);
  --aur1:rgba(124,108,255,.32);--aur2:rgba(34,211,238,.26);--aur3:rgba(244,114,182,.18);
  --ui:'Plus Jakarta Sans','Vazirmatn',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
  --mono:'JetBrains Mono','Vazirmatn',ui-monospace,Menlo,Consolas,monospace;
  --ease:cubic-bezier(.22,.9,.3,1);--spring:cubic-bezier(.34,1.45,.5,1);color-scheme:light}
:root[data-theme=dark]{
  --bg:#07070f;--card:rgba(23,24,42,.66);--card2:rgba(30,31,54,.8);--sunk:rgba(255,255,255,.045);
  --ink:#f2f3fb;--mut:#9a9eb9;--line:rgba(255,255,255,.085);--line2:rgba(255,255,255,.18);
  --acc:#8b7cff;--acc2:#4f9dff;--acc-ink:#fff;--acc-soft:rgba(139,124,255,.16);
  --sig:#2dd4bf;--sig-soft:rgba(45,212,191,.14);
  --vio:#c084fc;--vio-soft:rgba(192,132,252,.15);--vio-ink:#d8b4fe;
  --amb:#fbbf24;--amb-ink:#fcd34d;--amb-soft:rgba(251,191,36,.14);
  --red:#fb7185;--red-soft:rgba(251,113,133,.14);--navy:#7aa7ff;--plum:#f9a8d4;
  --seg-off:rgba(255,255,255,.08);--glow:rgba(139,124,255,.4);
  --sh1:0 1px 2px rgba(0,0,0,.35);--sh2:0 18px 50px -26px rgba(0,0,0,.85);--sh3:0 40px 100px -30px rgba(0,0,0,.95);
  --aur1:rgba(110,90,255,.34);--aur2:rgba(20,184,220,.22);--aur3:rgba(236,72,153,.16);color-scheme:dark}

*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{font-family:var(--ui);background:var(--bg);color:var(--ink);font-size:16px;line-height:1.55;min-height:100dvh;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;overflow-x:hidden;transition:background .3s,color .3s}
body.lock{overflow:hidden}
a{color:inherit}
button,input,select,textarea{font:inherit;color:inherit}
button{cursor:pointer;background:none;border:0;-webkit-tap-highlight-color:transparent}
::selection{background:var(--acc-soft)}
:focus-visible{outline:2px solid var(--acc);outline-offset:2px;border-radius:8px}
::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-thumb{background:var(--line2);border-radius:99px;border:2px solid transparent;background-clip:content-box}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
.mut{color:var(--mut)}.hidden{display:none!important}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
svg.i{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}

/* ---------- aurora backdrop ---------- */
.aurora{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none}
.aurora::after{content:"";position:absolute;inset:0;opacity:.5;
  background-image:radial-gradient(var(--line) 1px,transparent 1.2px);background-size:26px 26px;
  mask-image:radial-gradient(ellipse at 50% 0%,#000,transparent 70%);-webkit-mask-image:radial-gradient(ellipse at 50% 0%,#000,transparent 70%)}
.aurora i{position:absolute;width:min(60vw,640px);aspect-ratio:1;border-radius:50%;filter:blur(90px);will-change:transform;animation:drift 26s ease-in-out infinite alternate}
.aurora i:nth-child(1){background:var(--aur1);top:-22%;left:-12%}
.aurora i:nth-child(2){background:var(--aur2);top:-10%;right:-18%;animation-duration:32s;animation-delay:-8s}
.aurora i:nth-child(3){background:var(--aur3);bottom:-30%;left:30%;animation-duration:38s;animation-delay:-16s}
@keyframes drift{from{transform:translate3d(0,0,0) scale(1)}to{transform:translate3d(6vw,5vh,0) scale(1.18)}}

/* ---------- loader ---------- */
.page-loader{position:fixed;inset:0;z-index:9999;display:grid;place-items:center;background:var(--bg);pointer-events:none}
.page-loader.hide{animation:fadeout .35s ease forwards}
.loader-mark{width:54px;height:54px;border-radius:16px;background:linear-gradient(135deg,var(--acc),var(--acc2));box-shadow:0 0 0 0 var(--glow);animation:ping 1.2s ease-out infinite,scalein .4s var(--ease) both;margin:0 auto}
.loader-bar{width:110px;height:3px;margin:20px auto 0;border-radius:99px;background:var(--line);overflow:hidden}
.loader-bar i{display:block;width:40%;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--acc),var(--sig));animation:slide 1s ease-in-out infinite}
@keyframes slide{from{transform:translateX(-110%)}to{transform:translateX(280%)}}
@keyframes ping{0%{box-shadow:0 0 0 0 var(--glow)}100%{box-shadow:0 0 0 26px transparent}}

/* ---------- brand ---------- */
.brand{display:flex;align-items:center;gap:12px;min-width:0}
.logo{width:38px;height:38px;flex:none;border-radius:12px;box-shadow:0 8px 22px -8px var(--glow)}
.logo.lg{width:50px;height:50px;border-radius:15px}.logo.sm{width:30px;height:30px;border-radius:9px}
.wordmark{display:flex;flex-direction:column;min-width:0;line-height:1.1}
.wordmark b{font-weight:800;font-size:19px;letter-spacing:-.02em}
.wordmark b i{font-style:normal;color:var(--acc)}
.wordmark small{font:500 11.5px/1.4 var(--mono);color:var(--mut);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

/* ---------- lamp ---------- */
.lamp{--c:var(--seg-off);width:10px;height:10px;border-radius:50%;background:var(--c);flex:none;position:relative}
.lamp.on,.lamp.live{--c:var(--sig)}.lamp.warn{--c:var(--amb)}.lamp.cut{--c:var(--red)}
.lamp.off{background:transparent;box-shadow:inset 0 0 0 2px var(--line2)}
.lamp.live::after,.lamp.cut::after{content:"";position:absolute;inset:0;border-radius:50%;background:var(--c);animation:pulse 2s ease-out infinite}
.lamp.cut::after{animation-duration:1.4s}
.lamp.live,.lamp.on{box-shadow:0 0 10px -1px var(--c)}
@keyframes pulse{0%{transform:scale(1);opacity:.7}100%{transform:scale(3);opacity:0}}

/* ---------- VU meter ---------- */
.vu{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:3px;height:10px}
.vu i{border-radius:3px;background:var(--seg-off);transition:background .4s}
.vu i.f{background:var(--sig)}
.vu i.f.a{background:var(--amb)}.vu i.f.r{background:var(--red)}
.vu.inf i{opacity:.5}

/* ---------- controls ---------- */
.field{display:grid;gap:7px;min-width:0}
.field>span{font-size:13.5px;font-weight:700}
.field>small,.hint{font-size:12.5px;color:var(--mut)}
.input{width:100%;height:46px;padding:0 14px;background:var(--sunk);border:1.5px solid var(--line);border-radius:12px;font-size:16px;transition:border-color .18s,box-shadow .18s,background .18s}
.input::placeholder{color:var(--mut);opacity:.65}
.input:hover{border-color:var(--line2)}
.input:focus{outline:none;border-color:var(--acc);box-shadow:0 0 0 4px var(--acc-soft);background:var(--card2)}
textarea.input{height:auto;padding:12px 14px}
select.input{appearance:none;-webkit-appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1.5l5 5 5-5' fill='none' stroke='%239a9eb9' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");background-position:calc(100% - 14px) 50%;background-repeat:no-repeat;padding-right:36px}
select.input option{background:var(--bg);color:var(--ink)}
.join{display:flex}.join .input:first-child{border-radius:12px 0 0 12px;border-right:0}.join .input:last-child{border-radius:0 12px 12px 0;width:auto;min-width:98px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:44px;padding:0 18px;border-radius:12px;border:1.5px solid var(--line);background:var(--card);font-weight:700;font-size:15px;white-space:nowrap;position:relative;overflow:hidden;transition:background .18s,border-color .18s,transform .15s var(--spring),box-shadow .2s,filter .18s}
.btn:hover{border-color:var(--line2);background:var(--sunk);transform:translateY(-1px)}
.btn:active{transform:translateY(0) scale(.98)}.btn:disabled{opacity:.5;cursor:not-allowed;transform:none}
.btn.pri{background:linear-gradient(135deg,var(--acc),var(--acc2));border-color:transparent;color:#fff;box-shadow:0 10px 26px -12px var(--glow)}
.btn.pri:hover{filter:brightness(1.1);box-shadow:0 14px 32px -12px var(--glow)}
.btn.pri::after{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.28) 50%,transparent 70%);transform:translateX(-120%);transition:transform .6s}
.btn.pri:hover::after{transform:translateX(120%)}
.btn.bad{background:var(--red);border-color:var(--red);color:#fff}
.btn.ghost{border-color:transparent;background:transparent}.btn.ghost:hover{background:var(--sunk)}
.btn.sm{height:36px;padding:0 13px;font-size:14px;border-radius:10px}.btn.block{width:100%}
.ib{width:40px;height:40px;display:inline-grid;place-items:center;border-radius:12px;color:var(--mut);flex:none;transition:background .18s,color .18s,transform .15s var(--spring)}
.ib:hover{background:var(--sunk);color:var(--ink);transform:translateY(-1px)}.ib:active{transform:scale(.92)}
.ib.sm{width:36px;height:36px;border-radius:10px}.ib.bad:hover{color:var(--red);background:var(--red-soft)}
.chip{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 13px;border-radius:99px;font-size:13.5px;font-weight:700;background:var(--sunk);border:1px solid var(--line);color:var(--mut);white-space:nowrap}
.tag{display:inline-flex;align-items:center;height:22px;padding:0 8px;border-radius:7px;font:600 12px/1 var(--mono);background:var(--sunk);color:var(--mut);white-space:nowrap}
.tag.acc{background:var(--acc-soft);color:var(--acc)}.tag.amb{background:var(--amb-soft);color:var(--amb-ink)}
.tag.red{background:var(--red-soft);color:var(--red)}.tag.vio{background:var(--vio-soft);color:var(--vio-ink)}
.pp{display:inline-flex;align-items:center;gap:6px;height:24px;padding:0 9px 0 7px;border-radius:8px;font:700 11.5px/1 var(--ui);letter-spacing:.05em;text-transform:uppercase;white-space:nowrap}
.pp svg{width:13px;height:13px;stroke-width:2.4}
.pp.vless{background:var(--sig-soft);color:var(--sig)}.pp.trojan{background:var(--vio-soft);color:var(--vio-ink)}
.pp.vmess{background:rgba(59,130,246,.14);color:var(--navy)}.pp.ss{background:var(--amb-soft);color:var(--amb-ink)}
.alert{padding:12px 15px;border-radius:12px;background:var(--red-soft);color:var(--red);font-size:14px;font-weight:700;animation:scalein .25s var(--ease)}
.note{display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border-radius:14px;background:var(--sunk);font-size:14px}
.note.amb{background:var(--amb-soft)}.note.amb svg{color:var(--amb-ink)}.note.acc{background:var(--acc-soft)}.note.acc svg{color:var(--acc)}
.note b{display:block;font-size:15px}
.toast{position:fixed;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translate(-50%,20px) scale(.96);max-width:min(92vw,440px);background:var(--ink);color:var(--bg);padding:12px 18px;border-radius:14px;font-size:14.5px;font-weight:700;opacity:0;pointer-events:none;transition:opacity .22s,transform .35s var(--spring);z-index:300;display:flex;gap:10px;align-items:center;box-shadow:0 20px 50px -16px rgba(0,0,0,.6)}
.toast.on{opacity:1;transform:translate(-50%,0) scale(1)}
.toast.ok::before,.toast.err::before{content:"";width:9px;height:9px;border-radius:50%;background:var(--sig);box-shadow:0 0 10px var(--sig);flex:none}
.toast.err::before{background:var(--red);box-shadow:0 0 10px var(--red)}
.ic-sun{display:none}:root[data-theme=dark] .ic-sun{display:block}:root[data-theme=dark] .ic-moon{display:none}
.ib .ic-sun,.ib .ic-moon{transition:transform .5s var(--spring)}.ib:hover .ic-sun{transform:rotate(90deg)}.ib:hover .ic-moon{transform:rotate(-20deg)}
.shake{animation:shake .4s}
@keyframes shake{20%,60%{transform:translateX(-7px)}40%,80%{transform:translateX(7px)}}
@keyframes scalein{from{opacity:0;transform:scale(.95)}to{opacity:1;transform:scale(1)}}
@keyframes fadein{from{opacity:0}to{opacity:1}}
@keyframes fadeout{from{opacity:1}to{opacity:0}}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes shimmer{from{background-position:200% 0}to{background-position:-200% 0}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{transition-duration:.01ms!important;animation-duration:.01ms!important;animation-iteration-count:1!important;scroll-behavior:auto!important}.aurora i{animation:none}}
"""

MODAL_CSS = r"""
.modal{position:fixed;inset:0;z-index:100;display:grid;place-items:center;padding:18px;background:rgba(6,6,16,.55);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);opacity:0;pointer-events:none;transition:opacity .25s}
.modal.open{opacity:1;pointer-events:auto}
.sheet{width:min(var(--w,560px),100%);max-height:calc(100dvh - 36px);display:flex;flex-direction:column;background:var(--card2);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border:1px solid var(--line2);border-radius:26px;box-shadow:var(--sh3);transform:translateY(24px) scale(.97);opacity:0;transition:transform .4s var(--spring),opacity .25s;outline:none}
.modal.open .sheet{transform:none;opacity:1}
.mh{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;padding:24px 24px 0}
.mh h3{font-size:23px;font-weight:800;letter-spacing:-.025em;line-height:1.15}
.mh p{color:var(--mut);font-size:14px;margin-top:6px}
.mb{padding:20px 24px;overflow:auto;display:grid;gap:18px;min-height:0;align-content:start}
.mf{padding:4px 24px 24px;display:flex;justify-content:flex-end;gap:10px;flex-wrap:wrap;align-items:center}
.mf .btn{flex:0 1 auto}
.confirm .sheet{--w:420px}
.bdg{width:54px;height:54px;border-radius:18px;display:grid;place-items:center;background:var(--amb-soft);color:var(--amb-ink);margin-bottom:6px}
.bdg.bad{background:var(--red-soft);color:var(--red)}.bdg svg{width:26px;height:26px}
@media(max-width:640px){
  .modal{place-items:end center;padding:0}
  .sheet{width:100%;max-height:92dvh;border-radius:26px 26px 0 0;border-bottom:0;transform:translateY(100%);padding-bottom:env(safe-area-inset-bottom)}
  .sheet::before{content:"";display:block;width:42px;height:4px;border-radius:9px;background:var(--line2);margin:10px auto 0;flex:none}
  .mh{padding:14px 18px 0}.mh h3{font-size:21px}.mb{padding:16px 18px}.mf{padding:4px 18px 18px}
  .mf .btn{flex:1 1 auto}
  .confirm.modal{place-items:center;padding:18px}.confirm .sheet{border-radius:26px;max-height:calc(100dvh - 36px)}
  .confirm .sheet::before{display:none}
}
"""

ASK_EXTRA = ""

AUTH_CSS = r"""
body{display:grid;place-items:center;padding:24px 16px;position:relative}
.card{position:relative;width:100%;max-width:440px;background:var(--card);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border:1px solid var(--line2);border-radius:28px;padding:34px 30px 26px;box-shadow:var(--sh3);display:grid;gap:22px;animation:rise .7s var(--ease) both}
.card::before{content:"";position:absolute;inset:-1px;border-radius:inherit;padding:1px;background:linear-gradient(140deg,var(--acc),transparent 40%,transparent 60%,var(--sig));-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;opacity:.7;pointer-events:none}
.card>*{animation:rise .6s var(--ease) both}.card>*:nth-child(2){animation-delay:.07s}.card>*:nth-child(3){animation-delay:.14s}.card>*:nth-child(4){animation-delay:.2s}.card>*:nth-child(5){animation-delay:.26s}
.brand .ver{margin-left:auto;font:600 12px var(--mono);color:var(--mut);background:var(--sunk);border:1px solid var(--line);border-radius:99px;padding:5px 11px}
h1{font-size:clamp(30px,8vw,38px);line-height:1.05;font-weight:800;letter-spacing:-.035em;background:linear-gradient(120deg,var(--ink) 30%,var(--acc));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
h1+p{color:var(--mut);margin-top:10px}
.pw{position:relative}.pw .input{padding-right:50px}.pw button{position:absolute;right:4px;top:3px}
.strength{display:grid;grid-template-columns:repeat(4,1fr);gap:5px;height:5px}.strength i{border-radius:3px;background:var(--seg-off);transition:background .3s}
.strength[data-s="1"] i:nth-child(-n+1){background:var(--red)}.strength[data-s="2"] i:nth-child(-n+2){background:var(--amb)}
.strength[data-s="3"] i:nth-child(-n+3){background:var(--sig)}.strength[data-s="4"] i{background:var(--sig)}
.protos{display:flex;gap:8px;justify-content:center;flex-wrap:wrap}
.foot{text-align:center;font-size:13px;color:var(--mut)}
.themebtn{position:fixed;top:max(14px,env(safe-area-inset-top));right:14px;z-index:5}
@media(max-width:480px){.card{padding:26px 20px 22px;border-radius:24px;gap:20px}.themebtn{top:10px;right:10px}}
"""

DASH_CSS = r"""
.wrap{max-width:1200px;margin:0 auto;padding:0 clamp(14px,3vw,28px)}
header{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--bg) 70%,transparent);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border-bottom:1px solid var(--line);padding-top:env(safe-area-inset-top)}
.bar{min-height:72px;padding-block:12px;display:flex;align-items:center;gap:14px}
.hs{margin-left:auto;display:flex;align-items:center;justify-content:flex-end;gap:10px;min-width:0}
.tools{display:flex;gap:2px;align-items:center}
.sep{width:1px;height:24px;background:var(--line);margin:0 6px}
.scope{width:150px;height:34px;display:block;border-radius:10px;background:var(--sunk);border:1px solid var(--line)}
@media(max-width:900px){.scope{display:none}}
@media(max-width:720px){
  .bar{flex-wrap:wrap;gap:8px 10px;padding-block:10px 8px}
  .hs{display:contents}
  .bar .brand{order:1}.hs .chip{order:2;margin-left:auto;height:30px;padding:0 11px}
  .tools{order:3;flex:1 0 100%;overflow-x:auto;scrollbar-width:none;gap:2px;padding-bottom:2px}
  .tools::-webkit-scrollbar{display:none}
  .tools{justify-content:space-between}.tools .ib{width:40px;height:40px;flex:none}.tools .ib.hide-s{display:grid}
  .sep{flex:none}
}

/* hero */
.hero{display:grid;grid-template-columns:1.3fr 1fr;gap:18px;margin:30px 0 18px;animation:rise .7s var(--ease) both}
.panel{background:var(--card);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border:1px solid var(--line);border-radius:var(--r-lg);padding:24px;box-shadow:var(--shadow);min-width:0;position:relative;transition:border-color .25s,transform .3s var(--ease)}
.hero .panel:first-child{overflow:hidden}
.hero .panel:first-child::before{content:"";position:absolute;width:320px;height:320px;right:-110px;top:-140px;border-radius:50%;background:radial-gradient(circle,var(--glow),transparent 70%);opacity:.7;pointer-events:none;animation:drift 14s ease-in-out infinite alternate}
.kicker{font:600 11.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.14em;color:var(--mut);display:flex;align-items:center;gap:10px}
.big{font-size:clamp(48px,9vw,88px);font-weight:800;letter-spacing:-.05em;line-height:.95;margin-top:18px;font-variant-numeric:tabular-nums;background:linear-gradient(120deg,var(--ink) 20%,var(--acc) 70%,var(--sig));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;position:relative}
.big small{font-size:.34em;letter-spacing:-.01em;font-weight:700;margin-left:8px;-webkit-text-fill-color:var(--mut);color:var(--mut)}
.sub{color:var(--mut);font-size:14.5px;margin-top:14px;position:relative}
.kpis{display:grid;grid-template-columns:1fr 1fr;flex:1;border-radius:var(--r-lg);overflow:hidden}
.kpi{padding:18px 20px;min-width:0;border-right:1px solid var(--line);border-bottom:1px solid var(--line);transition:background .2s}
.kpi:hover{background:var(--sunk)}
.kpi:nth-child(2n){border-right:0}.kpi:nth-child(n+3){border-bottom:0}
.kpi small{display:block;color:var(--mut);font-size:12.5px;font-weight:700}
.kpi b{display:block;font-size:clamp(24px,3.4vw,32px);font-weight:800;letter-spacing:-.03em;margin-top:6px;font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi b em{font-style:normal;color:var(--mut);font-size:.55em;font-weight:700}
.kpi.live b{color:var(--sig)}
.pmix{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px;position:relative}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px;animation:rise .7s .08s var(--ease) both}
.chart{height:180px;width:100%;display:block;margin-top:14px}
.legend{display:flex;gap:14px;font-size:12.5px;color:var(--mut);font-weight:700;align-items:center;flex-wrap:wrap}
.legend i{display:inline-block;width:10px;height:10px;border-radius:4px;margin-right:6px;vertical-align:-1px}
.ph{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
.ph h3{font-size:16.5px;font-weight:800;letter-spacing:-.01em}
@media(max-width:900px){.hero,.charts{grid-template-columns:1fr}.hero{margin-top:20px}}

/* system meters */
.sys{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:40px;animation:rise .7s .16s var(--ease) both}
.meter{background:var(--card);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border:1px solid var(--line);border-radius:18px;padding:16px 18px;display:grid;gap:12px;min-width:0;box-shadow:var(--sh1);transition:transform .3s var(--ease),border-color .25s}
.meter:hover{transform:translateY(-3px);border-color:var(--line2)}
.meter .top{display:flex;justify-content:space-between;align-items:center;gap:8px}
.meter .top small{font-weight:700;font-size:13.5px;display:flex;align-items:center;gap:8px;color:var(--mut)}
.meter .top small svg{color:var(--acc)}
.meter .top b{font:600 21px/1 var(--mono);letter-spacing:-.02em}
.meter p{color:var(--mut);font-size:12.5px;font-family:var(--mono);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media(max-width:900px){.sys{grid-template-columns:1fr 1fr}}
@media(max-width:480px){.sys{gap:10px}.meter{padding:14px}.meter .top b{font-size:18px}}

/* configs */
.sec{margin-bottom:12px;animation:rise .7s .24s var(--ease) both}
.sec-h{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:18px}
.sec-h h2{font-size:clamp(26px,4vw,34px);font-weight:800;letter-spacing:-.04em;line-height:1}
.sec-h p{color:var(--mut);font-size:14.5px;margin-top:8px}
.ctrls{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.search{position:relative;display:block}.search>svg{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--mut);pointer-events:none}
.search .input{padding-left:42px;width:250px;height:44px}
.filters{display:flex;gap:6px 8px;flex-wrap:wrap;margin-bottom:16px;align-items:center}
.fgroup{display:flex;gap:6px;flex-wrap:wrap}
.fsep{width:1px;height:24px;background:var(--line);margin:0 6px}
.fchip{height:34px;padding:0 13px;border-radius:99px;border:1px solid var(--line);font-size:13.5px;font-weight:700;color:var(--mut);background:var(--card);display:inline-flex;align-items:center;gap:8px;white-space:nowrap;transition:all .2s var(--ease)}
.fchip:hover{border-color:var(--line2);color:var(--ink);transform:translateY(-1px)}
.fchip b{font:600 11.5px var(--mono);color:var(--mut);background:var(--sunk);border-radius:99px;padding:1px 8px;transition:all .2s}
.fchip[aria-pressed=true]{border-color:var(--acc);color:var(--acc);background:var(--acc-soft)}
.fchip[aria-pressed=true] b{background:var(--acc);color:#fff}
.fchip.vl[aria-pressed=true]{border-color:var(--sig);color:var(--sig);background:var(--sig-soft)}.fchip.vl[aria-pressed=true] b{background:var(--sig);color:#04201c}
.fchip.tr[aria-pressed=true]{border-color:var(--vio);color:var(--vio-ink);background:var(--vio-soft)}.fchip.tr[aria-pressed=true] b{background:var(--vio);color:#fff}
.fchip.vm[aria-pressed=true]{border-color:var(--navy);color:var(--navy);background:rgba(59,130,246,.12)}.fchip.vm[aria-pressed=true] b{background:var(--navy);color:#fff}
.fchip.ss[aria-pressed=true]{border-color:var(--amb);color:var(--amb-ink);background:var(--amb-soft)}.fchip.ss[aria-pressed=true] b{background:var(--amb);color:#1a1400}
@media(max-width:720px){
  .filters{flex-wrap:nowrap;overflow-x:auto;margin-inline:calc(-1*clamp(14px,3vw,28px));padding:0 clamp(14px,3vw,28px) 4px;scrollbar-width:none}
  .filters::-webkit-scrollbar{display:none}.fgroup{flex-wrap:nowrap}.fsep{display:block;flex:none}
}
.lines{display:grid;gap:12px}
.line{background:var(--card);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border:1px solid var(--line);border-radius:20px;padding:18px 20px;display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:18px;align-items:center;position:relative;box-shadow:var(--sh1);transition:transform .3s var(--ease),border-color .25s,box-shadow .3s}
.lines.first .line{animation:rise .55s var(--ease) both}
.lines.first .line:nth-child(2){animation-delay:.05s}.lines.first .line:nth-child(3){animation-delay:.1s}.lines.first .line:nth-child(4){animation-delay:.15s}.lines.first .line:nth-child(5){animation-delay:.2s}.lines.first .line:nth-child(n+6){animation-delay:.25s}
.line:hover{transform:translateY(-3px);border-color:var(--line2);box-shadow:var(--sh2)}
.line.off{background:transparent;border-style:dashed;box-shadow:none}.line.off .name b{color:var(--mut)}
.line.def{border-color:color-mix(in srgb,var(--acc) 45%,var(--line))}
.line.def::before{content:"";position:absolute;left:0;top:18px;bottom:18px;width:3px;border-radius:0 4px 4px 0;background:linear-gradient(var(--acc),var(--acc2))}
.name{display:flex;align-items:center;gap:8px;flex-wrap:wrap;min-width:0}
.name b{font-size:18px;font-weight:800;letter-spacing:-.015em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100%}
.meta{display:flex;gap:6px 16px;flex-wrap:wrap;margin-top:10px;font-size:13px;color:var(--mut)}
.meta span b{color:var(--ink);font-weight:600;font-family:var(--mono);font-size:12.5px}
.usage{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:center;margin-top:14px}
.usage .mono{font-size:12.5px;color:var(--mut);white-space:nowrap}
.acts{display:flex;align-items:center;gap:2px;flex-wrap:wrap;justify-content:flex-end}
.sw{position:relative;width:48px;height:28px;display:inline-block;flex:none;margin-right:8px}
.sw input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer;z-index:1;width:100%;height:100%}
.sw i{position:absolute;inset:0;border-radius:99px;background:var(--seg-off);border:1px solid var(--line);transition:background .25s,box-shadow .25s;pointer-events:none}
.sw i::after{content:"";position:absolute;left:3px;top:3px;width:20px;height:20px;border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,.3);transition:transform .35s var(--spring)}
.sw input:checked+i{background:linear-gradient(135deg,var(--sig),#22d3ee);border-color:transparent;box-shadow:0 0 16px -3px var(--sig)}
.sw input:checked+i::after{transform:translateX(20px)}
.sw input:disabled{cursor:not-allowed}.sw input:disabled+i{opacity:.4}
.sw input:focus-visible+i{outline:2px solid var(--acc);outline-offset:3px}
.empty{padding:50px 20px;text-align:center;border:1.5px dashed var(--line2);border-radius:20px;color:var(--mut);animation:scalein .4s var(--ease)}
.empty b{display:block;color:var(--ink);font-size:20px;font-weight:800;margin-bottom:6px}
.empty svg{width:36px;height:36px;color:var(--acc);margin-bottom:12px}
.sk{height:112px;border-radius:20px;border:1px solid var(--line);background:linear-gradient(100deg,var(--sunk) 30%,var(--card2) 50%,var(--sunk) 70%);background-size:200% 100%;animation:shimmer 1.6s linear infinite}
footer{display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;color:var(--mut);font-size:13px;padding:34px 0 calc(40px + env(safe-area-inset-bottom));border-top:1px solid var(--line);margin-top:40px}
footer b{color:var(--ink);font-family:var(--mono);font-weight:600}
@media(max-width:720px){
  .line{grid-template-columns:auto minmax(0,1fr);gap:12px 14px;padding:16px}
  .line .acts{grid-column:1/-1;justify-content:flex-start;border-top:1px solid var(--line);padding-top:12px;margin-top:2px;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}
  .line .acts::-webkit-scrollbar{display:none}
  .meta{gap:4px 14px}.usage{grid-template-columns:1fr;gap:8px}
  .search .input{width:100%}.search{flex:1 1 100%}.ctrls{width:100%}.ctrls .btn.pri{flex:1 1 100%;order:3}
  .name b{font-size:17px}
}
@media(max-width:560px){.panel{padding:18px}.kpi{padding:14px 15px}.chart{height:150px}}

/* modal content */
.lk{display:flex;gap:8px;align-items:center}.lk .input{font:13px var(--mono);height:42px;min-width:0;flex:1}
.ptog-row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:340px){.ptog-row{grid-template-columns:1fr}}
@media(max-width:560px){.ptog{padding:11px 12px;column-gap:9px}.ptog small{font-size:11.5px}.ptog span{font-size:14px}}
.ptog{display:grid;grid-template-columns:auto 1fr;column-gap:12px;row-gap:2px;align-items:center;padding:14px;border:1.5px solid var(--line);border-radius:16px;cursor:pointer;transition:border-color .2s,background .2s,transform .2s var(--spring)}
.ptog:hover{border-color:var(--line2)}.ptog:active{transform:scale(.98)}
.ptog input{width:18px;height:18px;accent-color:var(--acc);grid-row:span 2}
.ptog span{font-weight:700;font-size:15px;display:flex;align-items:center;gap:7px}.ptog small{color:var(--mut);font-size:12.5px}
.ptog.vl:has(input:checked){border-color:var(--sig);background:var(--sig-soft)}.ptog.vl input{accent-color:var(--sig)}
.ptog.tr:has(input:checked){border-color:var(--vio);background:var(--vio-soft)}.ptog.tr input{accent-color:var(--vio)}
.ptog.vm:has(input:checked){border-color:var(--navy);background:rgba(59,130,246,.1)}.ptog.vm input{accent-color:var(--navy)}
.ptog.ss:has(input:checked){border-color:var(--amb);background:var(--amb-soft)}.ptog.ss input{accent-color:var(--amb)}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px}.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
@media(max-width:560px){.g2,.g3{grid-template-columns:1fr}}
.sect{font:600 11.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.14em;color:var(--mut);display:flex;align-items:center;gap:10px}
.sect::after{content:"";flex:1;height:1px;background:var(--line)}
.box{border:1.5px solid var(--line);border-radius:16px;overflow:hidden}
.opt{display:flex;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid var(--line);font-size:15px;cursor:pointer;min-width:0;transition:background .15s}
.opt:last-child{border-bottom:0}.opt:hover{background:var(--sunk)}
.opt input{width:18px;height:18px;accent-color:var(--acc);flex:none}
.opt span.grow{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ipgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.ipgrid .opt{border:1.5px solid var(--line);border-radius:12px;font:500 13.5px var(--mono)}
.ipgrid .opt:hover{border-color:var(--line2)}.ipgrid .opt:has(input:checked){border-color:var(--acc);background:var(--acc-soft)}
.stats3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.mini{border:1px solid var(--line);background:var(--sunk);border-radius:14px;padding:13px 15px;min-width:0}
.mini small{display:block;color:var(--mut);font-size:12px;font-weight:700}
.mini b{font:600 19px/1.3 var(--mono);letter-spacing:-.02em;overflow-wrap:anywhere}
.qrs{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
@media(max-width:820px){.qrs{grid-template-columns:1fr 1fr}}@media(max-width:560px){.qrs{grid-template-columns:1fr}}
.qc{border:1px solid var(--line);background:var(--sunk);border-radius:18px;padding:16px;display:grid;gap:12px;justify-items:center;text-align:center;min-width:0}
.qc .qi{width:100%;max-width:220px;aspect-ratio:1;background:#fff;border-radius:14px;padding:12px;display:grid;place-items:center;box-shadow:0 12px 30px -16px rgba(0,0,0,.4)}
.qc .qi img{width:100%;height:100%;object-fit:contain;image-rendering:pixelated}
.qc p{font:500 11.5px/1.4 var(--mono);color:var(--mut);word-break:break-all;max-height:44px;overflow:hidden;width:100%}
.hres{border:1.5px solid var(--line);border-radius:16px;overflow:hidden}
.hr{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:12px;padding:12px 14px;border-bottom:1px solid var(--line);font-size:14.5px;align-items:center}
.hr>span:first-child{min-width:0;overflow-wrap:anywhere}.hr:last-child{border-bottom:0}.hr .mono{color:var(--mut);font-size:13px}
@media(max-width:480px){.hr{grid-template-columns:minmax(0,1fr) auto}.hr .mono:last-child{display:none}}
.good{color:var(--sig);font-weight:800}.bad{color:var(--red);font-weight:800}
.tw{overflow:auto;border:1.5px solid var(--line);border-radius:16px;max-height:300px}
table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:left;font:600 11.5px var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--mut);padding:11px 13px;background:var(--card2);position:sticky;top:0}
td{padding:11px 13px;border-top:1px solid var(--line);white-space:nowrap}td.r,th.r{text-align:right}
.drop{border:1.5px dashed var(--line2);border-radius:16px;padding:26px;text-align:center;color:var(--mut);cursor:pointer;transition:all .2s var(--ease);display:block}
.drop:hover,.drop.over{border-color:var(--acc);background:var(--acc-soft);color:var(--ink);transform:scale(1.01)}.dz{display:none}
.tgl{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:13px 15px;border:1.5px solid var(--line);border-radius:14px}
.tgl small{color:var(--mut);font-size:13px;display:block}
.ta{min-height:76px;padding:12px 14px;resize:vertical;font:13px var(--mono)}
.ver-foot{color:var(--mut)}
.mf .btn{flex:0 1 auto}
@media(max-width:640px){.mf .btn{flex:1 1 auto}}
@media(max-width:560px){.stats3{gap:8px}.mini{padding:11px}.mini b{font-size:16px}}
"""

LOGS_CSS = r"""
.wrap{max-width:1200px;margin:0 auto;padding:0 clamp(14px,3vw,28px)}
header{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--bg) 70%,transparent);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border-bottom:1px solid var(--line);padding-top:env(safe-area-inset-top)}
.bar{min-height:72px;padding-block:12px;display:flex;align-items:center;gap:12px}
.sp{margin-left:auto}
.h1{font-size:clamp(28px,5vw,38px);font-weight:800;letter-spacing:-.04em;margin:30px 0 6px;animation:rise .6s var(--ease) both}
.lead{color:var(--mut);margin-bottom:20px;animation:rise .6s .05s var(--ease) both}
.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:14px;animation:rise .6s .1s var(--ease) both}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--card);padding:3px;gap:2px}
.seg button{height:34px;padding:0 14px;font-weight:700;font-size:13.5px;color:var(--mut);border-radius:9px;transition:all .2s var(--ease)}
.seg button:hover{color:var(--ink)}
.seg button[aria-pressed=true]{background:linear-gradient(135deg,var(--acc),var(--acc2));color:#fff;box-shadow:0 6px 16px -8px var(--glow)}
.term{background:color-mix(in srgb,var(--bg) 60%,#000 40%);border:1px solid var(--line);border-radius:20px;padding:16px 18px;height:calc(100dvh - 320px);min-height:360px;overflow:auto;font:12.5px/1.7 var(--mono);box-shadow:var(--sh2);color:#d9dcf0;animation:rise .6s .15s var(--ease) both}
:root:not([data-theme=dark]) .term{background:#14162b}
.ln{display:grid;grid-template-columns:86px 64px minmax(0,1fr);gap:12px;padding:2px 6px;border-radius:6px;white-space:pre-wrap;word-break:break-word}
.ln:hover{background:rgba(255,255,255,.05)}
.ln time{color:#7d82a3}
.lv{font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.06em;align-self:start;padding-top:2px}
.lv.info{color:#7aa7ff}.lv.warning,.lv.warn{color:#fcd34d}.lv.error,.lv.err{color:#fb7185}.lv.ok{color:#2dd4bf}
.live{display:flex;align-items:center;gap:8px;font-size:14px;font-weight:700;color:var(--mut);cursor:pointer}
.live input{accent-color:var(--acc);width:16px;height:16px}
.empty{color:#7d82a3;padding:20px}
.pill{display:inline-flex;align-items:center;gap:8px;height:34px;padding:0 13px;border-radius:99px;font:600 12.5px var(--mono);background:var(--sunk);border:1px solid var(--line)}
@media(max-width:640px){
  .ln{grid-template-columns:64px minmax(0,1fr);gap:8px}.ln .lv{display:none}.term{padding:12px;height:calc(100dvh - 380px);border-radius:16px}
  .toolbar .btn{margin-left:auto}.seg{max-width:100%;overflow-x:auto}.bar .btn.sm{padding:0 11px}
}
"""

PORTAL_CSS = r"""
body{display:grid;place-items:start center;padding:clamp(16px,4vw,40px) 14px 56px}
.theme{position:fixed;top:max(12px,env(safe-area-inset-top));right:12px;z-index:5}
.pass{width:100%;max-width:700px;background:var(--card);backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);border:1px solid var(--line2);border-radius:28px;box-shadow:var(--sh3);overflow:hidden;position:relative;animation:rise .75s var(--ease) both}
.pass::before{content:"";position:absolute;inset:0 0 auto;height:3px;background:linear-gradient(90deg,var(--acc),var(--acc2),var(--sig));background-size:200% 100%;animation:shimmer 6s linear infinite}
.head{display:flex;align-items:center;gap:12px;padding:20px 66px 18px 24px;border-bottom:1px solid var(--line)}
.head .sp{margin-left:auto}
.body{display:grid;grid-template-columns:minmax(0,1fr) 232px;position:relative}
.main{padding:28px 28px 26px;display:grid;gap:22px;min-width:0}
.main>*{animation:rise .6s var(--ease) both}.main>*:nth-child(2){animation-delay:.08s}.main>*:nth-child(3){animation-delay:.14s}.main>*:nth-child(4){animation-delay:.2s}.main>*:nth-child(n+5){animation-delay:.26s}
.stub{padding:26px 22px;border-left:1px dashed var(--line2);display:grid;gap:14px;justify-items:center;align-content:start;background:var(--sunk);position:relative}
.stub .qr{width:100%;max-width:186px;aspect-ratio:1;background:#fff;border-radius:16px;padding:11px;display:grid;place-items:center;box-shadow:0 18px 40px -18px var(--glow);transition:transform .4s var(--spring)}
.stub .qr:hover{transform:scale(1.05) rotate(-1deg)}
.stub .qr img{width:100%;height:100%;image-rendering:pixelated}
.stub small{font:500 12px/1.4 var(--mono);color:var(--mut);text-align:center}
.body::before,.body::after{content:"";position:absolute;left:calc(100% - 232px);width:24px;height:24px;border-radius:50%;background:var(--bg);border:1px solid var(--line);z-index:2}
.body::before{top:0;transform:translate(-50%,-50%)}.body::after{bottom:0;transform:translate(-50%,50%)}
.name{font-size:clamp(30px,6vw,42px);font-weight:800;letter-spacing:-.04em;line-height:1.05;word-break:break-word;background:linear-gradient(120deg,var(--ink) 40%,var(--acc));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.stamp{display:inline-flex;align-items:center;gap:8px;height:26px;padding:0 12px;border-radius:99px;font:700 12px/1 var(--ui);letter-spacing:.1em;text-transform:uppercase;color:var(--sig);background:var(--sig-soft)}
.stamp.off{color:var(--mut);background:var(--sunk)}.stamp.bad{color:var(--red);background:var(--red-soft)}.stamp.warn{color:var(--amb-ink);background:var(--amb-soft)}
.stamp .lamp{width:8px;height:8px}
.gauge{display:grid;gap:12px}
.gauge .top{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap}
.gauge .top b{font-size:30px;font-weight:800;letter-spacing:-.035em;font-variant-numeric:tabular-nums}
.gauge .top b em{font-style:normal;font-size:.52em;color:var(--mut);font-weight:700}
.gauge .top span{font:500 12.5px var(--mono);color:var(--mut)}
.gauge .vu{height:20px;gap:4px}.gauge .vu i{border-radius:5px}
.facts{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--line);border-radius:18px;overflow:hidden;background:var(--sunk)}
.facts div{padding:14px 16px;min-width:0;transition:background .2s}.facts div:hover{background:var(--card)}
.facts div:nth-child(odd){border-right:1px solid var(--line)}.facts div:nth-child(-n+2){border-bottom:1px solid var(--line)}
.facts small{display:block;color:var(--mut);font-size:12px;font-weight:700}
.facts b{display:block;font-size:17px;font-weight:800;margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sec{display:flex;align-items:center;justify-content:space-between;gap:10px}.sec b{font-size:17px;font-weight:800}
.linkbox{border:1px solid var(--line);border-radius:16px;overflow:hidden;background:var(--sunk)}
.lrow{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:10px;align-items:center;padding:11px 12px;border-bottom:1px solid var(--line);transition:background .2s}
.lrow:hover{background:var(--card)}.lrow:last-child{border-bottom:0}
.lrow .tag{min-width:112px;justify-content:center}
.lrow input{width:100%;min-width:0;height:38px;padding:0 11px;border:1.5px solid var(--line);border-radius:10px;background:var(--card2);font:12.5px var(--mono);color:var(--mut);text-overflow:ellipsis;transition:border-color .2s}
.lrow input:focus{outline:none;border-color:var(--acc);color:var(--ink)}
.group{display:grid;gap:9px}
.group-h{display:flex;align-items:center;gap:10px;font:600 11.5px/1 var(--mono);color:var(--mut);text-transform:uppercase;letter-spacing:.12em}
.group-h::after{content:"";flex:1;height:1px;background:var(--line)}
.lrow .btn{height:38px}
.foot{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:15px 24px;border-top:1px dashed var(--line2);color:var(--mut);font-size:13px;background:var(--sunk)}
.foot b{color:var(--ink)}.none{padding:20px;text-align:center;color:var(--mut);font-size:14px}.ptags{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
@media(max-width:700px){
  body{padding-top:62px}.theme{position:absolute;top:max(10px,env(safe-area-inset-top))}.head{padding-right:20px}
  .body{grid-template-columns:1fr}
  .stub{border-left:0;border-top:1px dashed var(--line2);grid-template-columns:auto 1fr;justify-items:start;align-items:center;gap:18px}
  .stub .qr{max-width:136px}.stub small{text-align:left}
  .body::before,.body::after{display:none}
  .main{padding:24px 20px}.facts{grid-template-columns:1fr 1fr}
  .lrow{grid-template-columns:minmax(0,1fr) auto}.lrow .tag{display:none}
}
@media(max-width:420px){
  .main{padding:20px 16px;gap:20px}.stub{padding:18px 16px}.head{padding:16px 16px 14px}.foot{padding:12px 16px}
  .facts b{font-size:15.5px}.gauge .top b{font-size:25px}
  .stub{grid-template-columns:1fr;justify-items:center}.stub small{text-align:center}.stub .qr{max-width:180px}
}
"""
