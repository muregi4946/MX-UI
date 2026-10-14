# pages_dashboard.py — admin dashboard + logs page (v2.3.0)
#
# Signature: the "lamp" per config (lit = carrying traffic) and the segmented VU meters.
# Each config can speak VLESS, Trojan, or both. Everything is one HTML file, no CDN scripts.
from pages import page, ic, UTIL_JS, SPRITE, MODAL_CSS, ASK_MODAL, THEME_BTN, brand
from theme import DASH_CSS, LOGS_CSS



DASH_BODY = r"""<body>
<header><div class="wrap bar">
  __BRAND__
  <div class="hs">
    <span class="chip" id="xrayChip"><span class="lamp" id="xrayLamp"></span><span id="xrayText">Xray</span></span>
    <canvas class="scope" id="scope" width="300" height="68" aria-label="Live throughput scope"></canvas>
    <div class="tools">
      <button class="ib hide-s" onclick="location.href='/logs'" title="Logs" aria-label="Logs">__IC_terminal__</button>
      <button class="ib" onclick="openModal('connModal')" title="Live connections" aria-label="Live connections">__IC_users__</button>
      <button class="ib hide-s" onclick="openModal('ipModal')" title="IP suggestions" aria-label="IP suggestions">__IC_globe__</button>
      <button class="ib hide-s" onclick="openModal('healthModal')" title="Health check" aria-label="Health check">__IC_pulse__</button>
      <button class="ib" onclick="openModal('dbModal')" title="Backup and restore" aria-label="Backup and restore">__IC_db__</button>
      <button class="ib" onclick="openModal('setModal')" title="Settings" aria-label="Settings">__IC_cog__</button>
      __THEME__
      <span class="sep"></span>
      <button class="ib bad" onclick="logout()" title="Log out" aria-label="Log out">__IC_out__</button>
    </div>
  </div>
</div></header>

<main class="wrap">
  <section class="hero" aria-label="Overview">
    <div class="panel">
      <div class="kicker"><span class="lamp live" style="width:8px;height:8px"></span>Traffic since boot</div>
      <div class="big" id="bigTotal">0<small>B</small></div>
      <div class="sub" id="bigSub">Waiting for the first poll…</div>
      <div class="pmix" id="pmix"></div>
    </div>
    <div class="panel" style="padding:0;display:flex">
      <div class="kpis" style="flex:1">
        <div class="kpi live"><small>Live connections</small><b id="kConn">0</b></div>
        <div class="kpi"><small>Unique IPs online</small><b id="kIps">0</b></div>
        <div class="kpi"><small>Active configs</small><b id="kActive">0<em> / 0</em></b></div>
        <div class="kpi"><small>Uptime</small><b id="kUp" class="mono" style="font-size:24px;padding-top:4px">--</b></div>
      </div>
    </div>
  </section>

  <section class="charts" aria-label="Charts">
    <div class="panel">
      <div class="ph"><h3>Throughput</h3><div class="legend"><span><i style="background:var(--sig)"></i>Down</span><span><i style="background:var(--navy)"></i>Up</span></div></div>
      <svg class="chart" id="netChart" viewBox="0 0 600 170" preserveAspectRatio="none" role="img" aria-label="Network throughput, last 6 minutes"></svg>
    </div>
    <div class="panel">
      <div class="ph"><h3>Last 24 hours</h3><span class="mut mono" style="font-size:13px" id="serTotal">0 B</span></div>
      <svg class="chart" id="serChart" viewBox="0 0 600 170" preserveAspectRatio="none" role="img" aria-label="Traffic per hour, last 24 hours"></svg>
    </div>
  </section>

  <section aria-label="System">
    <div class="sys">
      <div class="meter"><div class="top"><small>__IC_cpu__CPU</small><b id="mCpu">0%</b></div><div id="vCpu"></div><p id="pCpu">--</p></div>
      <div class="meter"><div class="top"><small>__IC_gauge__Memory</small><b id="mRam">0%</b></div><div id="vRam"></div><p id="pRam">--</p></div>
      <div class="meter"><div class="top"><small>__IC_sliders__Swap</small><b id="mSwap">0%</b></div><div id="vSwap"></div><p id="pSwap">--</p></div>
      <div class="meter"><div class="top"><small>__IC_server__Storage</small><b id="mDisk">0%</b></div><div id="vDisk"></div><p id="pDisk">--</p></div>
    </div>
  </section>

  <section class="sec" aria-label="Configs">
    <div class="sec-h">
      <div><h2>Configs</h2><p id="cfgSub">Every config is a line. A lit lamp means it's carrying traffic.</p></div>
      <div class="ctrls">
        <label class="search"><span class="sr">Search</span>__IC_search__<input id="q" class="input" type="search" placeholder="Search configs" autocomplete="off"></label>
        <button class="btn pri" onclick="newConfig()">__IC_plus__<span>New config</span></button>
      </div>
    </div>
    <div class="filters" role="group" aria-label="Filter">
      <div class="fgroup" id="filters">
        <button class="fchip" data-f="all" aria-pressed="true">All <b id="cAll">0</b></button>
        <button class="fchip" data-f="active" aria-pressed="false">Active <b id="cActive">0</b></button>
        <button class="fchip" data-f="disabled" aria-pressed="false">Disabled <b id="cDisabled">0</b></button>
        <button class="fchip" data-f="expired" aria-pressed="false">Expired <b id="cExpired">0</b></button>
        <button class="fchip" data-f="depleted" aria-pressed="false">Out of data <b id="cDepleted">0</b></button>
      </div>
      <span class="fsep"></span>
      <div class="fgroup" id="pfilters">
        <button class="fchip" data-p="all" aria-pressed="true">Any protocol</button>
        <button class="fchip vl" data-p="vless" aria-pressed="false">VLESS <b id="cVless">0</b></button>
        <button class="fchip tr" data-p="trojan" aria-pressed="false">Trojan <b id="cTrojan">0</b></button>
        <button class="fchip vm" data-p="vmess" aria-pressed="false">VMess <b id="cVmess">0</b></button>
        <button class="fchip ss" data-p="ss" aria-pressed="false">Shadowsocks <b id="cSs">0</b></button>
      </div>
    </div>
    <div class="lines" id="lines"><div class="sk"></div><div class="sk"></div></div>
  </section>

  <footer><span>MX-UI v2.3.0 · Created by Muvixo</span><span>Core <b id="foot">--</b></span></footer>
</main>

<!-- ============ modals ============ -->
<div id="cfgModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="cfgTitle"><div class="sheet" tabindex="-1" style="--w:660px">
  <div class="mh"><div><h3 id="cfgTitle">New config</h3><p id="cfgSub2">A tunnel line with its own quota and limits.</p></div><button class="ib" onclick="closeModal('cfgModal')" aria-label="Close">__IC_x__</button></div>
  <div class="mb">
    <input type="hidden" id="cUid">
    <div class="sect">Protocols</div>
    <div class="ptog-row">
      <label class="ptog vl"><input type="checkbox" id="pV" checked><span>__IC_bolt__VLESS</span><small>WebSocket over TLS</small></label>
      <label class="ptog tr"><input type="checkbox" id="pT"><span>__IC_shield__Trojan</span><small>WebSocket over TLS</small></label>
      <label class="ptog vm"><input type="checkbox" id="pM"><span>__IC_cpu__VMess</span><small>WebSocket over TLS</small></label>
      <label class="ptog ss"><input type="checkbox" id="pS"><span>__IC_key__Shadowsocks</span><small>v2ray-plugin over TLS</small></label>
    </div>
    <div class="sect">Identity</div>
    <div class="g2">
      <label class="field"><span>Name</span><input id="cLabel" class="input" maxlength="64" placeholder="e.g. Frankfurt-1" autocomplete="off"></label>
      <label class="field"><span>Fingerprint (uTLS)</span><select id="cFp" class="input"></select></label>
    </div>
    <div class="sect">Limits</div>
    <div class="g2">
      <label class="field"><span>Data quota</span><div class="join"><input id="cLimit" class="input" type="number" min="0" step="any" inputmode="decimal" value="0"><select id="cLimitUnit" class="input"><option>GB</option><option>MB</option></select></div><small class="hint">0 = unlimited</small></label>
      <label class="field" id="cExpWrap"><span>Expires in (days)</span><input id="cExpDays" class="input" type="number" min="0" step="1" inputmode="numeric" value="0"><small class="hint">0 = never. Applies on create.</small></label>
      <label class="field" id="cExpDateWrap" style="display:none"><span>Expiry date</span><input id="cExpDate" class="input" type="date"><small class="hint">Empty = never expires.</small></label>
      <label class="field"><span>Device limit</span><input id="cIpLimit" class="input" type="number" min="0" step="1" inputmode="numeric" value="0"><small class="hint">Distinct client IPs. 0 = unlimited</small></label>
      <label class="field"><span>Speed cap</span><div class="join"><input id="cSpeed" class="input" type="number" min="0" step="0.5" inputmode="decimal" value="0"><select id="cSpeedUnit" class="input"><option value="MBIT">Mbps</option><option value="KB">KB/s</option><option value="MB">MB/s</option></select></div><small class="hint">0 = unlimited</small></label>
      <label class="field"><span>ALPN <small style="display:inline">(optional)</small></span><input id="cAlpn" class="input" placeholder="http/1.1" autocomplete="off"></label>
    </div>
    <label class="field"><span>Note <small style="display:inline">(optional)</small></span><input id="cNote" class="input" maxlength="300" placeholder="Internal remarks" autocomplete="off"></label>
    <div id="cfgErr" class="alert hidden" role="alert"></div>
  </div>
  <div class="mf"><button class="btn" onclick="closeModal('cfgModal')">Cancel</button><button class="btn pri" id="cfgSave" onclick="saveConfig()">Create config</button></div>
</div></div>

<div id="qrModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="qrTitle"><div class="sheet" tabindex="-1" style="--w:920px">
  <div class="mh"><div><h3 id="qrTitle">Share</h3><p id="qrName">Config</p></div><button class="ib" onclick="closeModal('qrModal')" aria-label="Close">__IC_x__</button></div>
  <div class="mb"><div class="qrs" id="qrGrid"></div></div>
</div></div>

<div id="ipModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="ipTitle"><div class="sheet" tabindex="-1" style="--w:760px">
  <div class="mh"><div><h3 id="ipTitle">Clean IP suggestions</h3><p>Pull a fresh batch from the curated list and pin it to configs.</p></div><button class="ib" onclick="closeModal('ipModal')" aria-label="Close">__IC_x__</button></div>
  <div class="mb">
    <div id="ipDomain" class="note amb hidden">__IC_alert__<div><b>You're on a Railway default domain</b><span>Attach a custom domain so clients can use the IP variants reliably. Suggestions still work here.</span></div></div>
    <div class="ph"><span class="sect" style="flex:1">Suggested</span><button class="btn sm" onclick="loadIps()">__IC_refresh__Refresh</button></div>
    <div id="ipGrid" class="ipgrid"></div>
    <div class="sect">Apply to</div>
    <div id="ipTargets" class="box"></div>
    <div class="g2">
      <label class="field"><span>Port</span><input id="ipPort" class="input" type="number" value="443" min="1" max="65535"></label>
      <label class="field"><span>Mode</span><select id="ipMode" class="input"><option value="replace">Replace existing IPs</option><option value="append">Add to existing IPs</option></select></label>
    </div>
  </div>
  <div class="mf"><span id="ipStatus" class="hint" style="margin-right:auto"></span><button class="btn" onclick="closeModal('ipModal')">Close</button><button class="btn pri" id="ipApply" onclick="applyIps()" disabled>__IC_check__Apply</button></div>
</div></div>

<div id="healthModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="hTitle"><div class="sheet" tabindex="-1" style="--w:680px">
  <div class="mh"><div><h3 id="hTitle">Health check</h3><p>TCP-probe the domain and every pinned IP. Nothing is sent through the tunnel.</p></div><button class="ib" onclick="closeModal('healthModal')" aria-label="Close">__IC_x__</button></div>
  <div class="mb"><div id="hList" class="box"></div><div id="hRes"></div></div>
  <div class="mf"><span id="hStatus" class="hint" style="margin-right:auto"></span><button class="btn" onclick="closeModal('healthModal')">Close</button><button class="btn pri" id="hGo" onclick="runHealth()" disabled>__IC_play__Test selected</button></div>
</div></div>

<div id="connModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="coTitle"><div class="sheet" tabindex="-1" style="--w:720px">
  <div class="mh"><div><h3 id="coTitle">Live connections</h3><p>Sessions open right now, refreshed every 3 seconds.</p></div><button class="ib" onclick="closeModal('connModal')" aria-label="Close">__IC_x__</button></div>
  <div class="mb"><div class="tw"><table><thead><tr><th>Config</th><th>Protocol</th><th>Client IP</th><th>Since</th><th class="r">Down</th><th class="r">Up</th></tr></thead><tbody id="connBody"></tbody></table></div></div>
  <div class="mf"><button class="btn" onclick="closeModal('connModal')">Close</button></div>
</div></div>

<div id="dbModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="dbTitle"><div class="sheet" tabindex="-1" style="--w:640px">
  <div class="mh"><div><h3 id="dbTitle">Backup &amp; restore</h3><p>Everything lives in one JSON file. Download it before you move servers.</p></div><button class="ib" onclick="closeModal('dbModal')" aria-label="Close">__IC_x__</button></div>
  <div class="mb">
    <div class="stats3"><div class="mini"><small>Configs</small><b id="dbN">0</b></div><div class="mini"><small>Active</small><b id="dbA" style="color:var(--acc)">0</b></div><div class="mini"><small>Traffic</small><b id="dbT">0 B</b></div></div>
    <button class="btn block" onclick="exportDb()">__IC_dl__Download backup (.json)</button>
    <div class="sect">Restore</div>
    <label class="drop" id="drop" tabindex="0">__IC_up__<div style="margin-top:8px">Drop a backup file here, or click to choose one</div><input type="file" id="dbFile" accept="application/json,.json" class="dz"></label>
    <div id="dbPick" class="hidden tgl"><div><b id="dbPickName">backup.json</b><small id="dbPickInfo"></small></div><button class="btn sm" onclick="clearPick()">Clear</button></div>
    <div class="g2"><label class="field"><span>Mode</span><select id="dbMode" class="input"><option value="merge">Merge (keep current, add new)</option><option value="replace">Replace all non-default configs</option></select></label><div></div></div>
  </div>
  <div class="mf"><button class="btn" onclick="closeModal('dbModal')">Close</button><button class="btn pri" id="dbGo" onclick="importDb()" disabled>Restore</button></div>
</div></div>

<div id="setModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="stTitle"><div class="sheet" tabindex="-1" style="--w:520px">
  <div class="mh"><div><h3 id="stTitle">Settings</h3><p>Change the admin password. You'll be signed out everywhere.</p></div><button class="ib" onclick="closeModal('setModal')" aria-label="Close">__IC_x__</button></div>
  <div class="mb">
    <label class="field"><span>Current password</span><input type="password" id="sCur" class="input" autocomplete="current-password"></label>
    <label class="field"><span>New password</span><input type="password" id="sNew" class="input" autocomplete="new-password" placeholder="At least 6 characters"></label>
    <label class="field"><span>Repeat new password</span><input type="password" id="sNew2" class="input" autocomplete="new-password"></label>
    <div id="sErr" class="alert hidden" role="alert"></div>
  </div>
  <div class="mf"><button class="btn" onclick="closeModal('setModal')">Cancel</button><button class="btn pri" id="sGo" onclick="changePw()">Update password</button></div>
</div></div>

__ASK__
<div id="toast" class="toast" role="status" aria-live="polite"></div>
"""

DASH_JS = r"""
var STATE={links:[],filter:'all',proto:'all',q:'',stats:null,cur:null,lastNet:[],lastSer:[]};
var errOf=function(r,d){return r.json().then(function(j){return j.detail||d;},function(){return d;});};
var PROTOS=['vless','trojan','vmess','ss'];
function lnk(l){return l.primary_link||l.vless_link||l.trojan_link||'';}

/* ---------- modal hooks ---------- */
window.onModalOpen=function(id){
  if(id==='ipModal')loadIps();if(id==='healthModal')loadHealthTargets();if(id==='connModal')loadConns();if(id==='dbModal'){refreshDbInfo();clearPick();}
  if(id==='setModal'){['sCur','sNew','sNew2'].forEach(function(k){$(k).value='';});$('sErr').classList.add('hidden');}};
window.onModalClose=function(id){if(id==='connModal'&&connT){clearInterval(connT);connT=null;}};
window.onThemeChange=function(){drawScope();if(STATE.lastNet.length||STATE.lastSer.length)redrawCharts();};

/* ---------- header / system ---------- */
function bump(id){var e=$(id);if(!e||!e.animate)return;e.animate([{transform:'translateY(5px)',opacity:.55},{transform:'none',opacity:1}],{duration:380,easing:'cubic-bezier(.22,.9,.3,1)'});}
var scopeHist=[];
function drawScope(){var c=$('scope');if(!c||!c.getContext)return;var x=c.getContext('2d');var W=c.width,H=c.height;x.clearRect(0,0,W,H);
  x.strokeStyle=getCss('--line');x.lineWidth=1;x.beginPath();for(var g=1;g<4;g++){x.moveTo(0,g*H/4);x.lineTo(W,g*H/4);}x.stroke();
  if(scopeHist.length<2)return;var max=Math.max(1024,Math.max.apply(null,scopeHist));
  x.beginPath();scopeHist.forEach(function(v,i){var px=i/(scopeHist.length-1)*W,py=H-6-(v/max)*(H-14);i?x.lineTo(px,py):x.moveTo(px,py);});
  x.strokeStyle=getCss('--sig');x.lineWidth=2;x.shadowColor=getCss('--sig');x.shadowBlur=6;x.stroke();x.shadowBlur=0;}
function getCss(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim()||'#8b7cff';}
function pushScope(v){scopeHist.push(v);if(scopeHist.length>90)scopeHist.shift();drawScope();}
window.addEventListener('resize',drawScope);
drawScope();

function lineChart(svgId,points,opts){
  var s=$(svgId);if(!s)return;var W=600,H=170,pad=8;var keys=opts.keys;var max=1;
  points.forEach(function(p){keys.forEach(function(k){max=Math.max(max,p[k[0]]||0);});});
  var out='';
  for(var g=1;g<4;g++)out+='<line x1="0" x2="'+W+'" y1="'+(g*H/4)+'" y2="'+(g*H/4)+'" stroke="'+getCss('--line')+'" stroke-dasharray="3 5"/>';
  if(points.length<2){s.innerHTML=out+'<text x="300" y="90" text-anchor="middle" fill="'+getCss('--mut')+'" font-size="14">collecting samples…</text>';return;}
  keys.forEach(function(k,ki){var d='';points.forEach(function(p,i){var x=i/(points.length-1)*W,y=H-pad-((p[k[0]]||0)/max)*(H-pad*2);d+=(i?' L':'M')+x.toFixed(1)+' '+y.toFixed(1);});
    if(ki===0){out+='<path d="'+d+' L'+W+' '+H+' L0 '+H+'Z" fill="'+getCss('--sig')+'" fill-opacity=".14"/>';}
    out+='<path d="'+d+'" fill="none" stroke="'+getCss(k[1])+'" stroke-width="2.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>';});
  s.innerHTML=out;}
function barChart(svgId,series){
  var s=$(svgId);if(!s)return;var W=600,H=170,n=series.length,gap=6,bw=(W-gap*(n-1))/n;var max=Math.max.apply(null,series.map(function(x){return x.bytes;}).concat([1]));
  var out='';for(var g=1;g<4;g++)out+='<line x1="0" x2="'+W+'" y1="'+(g*H/4)+'" y2="'+(g*H/4)+'" stroke="'+getCss('--line')+'" stroke-dasharray="3 5"/>';
  series.forEach(function(p,i){var h=Math.max(p.bytes?3:0,(p.bytes/max)*(H-24));var x=i*(bw+gap),y=H-h-16;
    out+='<rect x="'+x.toFixed(1)+'" y="'+y.toFixed(1)+'" width="'+bw.toFixed(1)+'" height="'+h.toFixed(1)+'" rx="3" fill="'+(i===n-1?getCss('--sig'):getCss('--navy'))+'" opacity="'+(i===n-1?1:.55)+'"><title>'+p.hour+' · '+fmtBytes(p.bytes)+'</title></rect>';
    if(i%4===0)out+='<text x="'+(x).toFixed(1)+'" y="'+(H-2)+'" font-size="12" fill="'+getCss('--mut')+'" font-family="JetBrains Mono,monospace">'+p.hour+'</text>';});
  s.innerHTML=out;}
function redrawCharts(){lineChart('netChart',STATE.lastNet.map(function(x){return {rx:x.rx,tx:x.tx};}),{keys:[['rx','--sig'],['tx','--navy']]});barChart('serChart',STATE.lastSer);}

function renderStats(d){
  STATE.stats=d;
  var tot=d.total_bytes||0,u=fmtBytes(tot).split(' ');
  $('bigTotal').innerHTML=u[0]+'<small>'+u[1]+'</small>';bump('bigTotal');
  $('bigSub').textContent=(d.active_connections||0)+' live session'+((d.active_connections||0)===1?'':'s')+' · '+(d.total_requests||0)+' requests since boot';
  var pr=d.protocols||{};
  $('pmix').innerHTML=PROTOS.map(function(p){return protoPill(p)+'<span class="tag" style="height:24px">'+(pr[p]||0)+' configs</span>';}).join('');
  $('kConn').textContent=d.active_connections||0;$('kIps').textContent=d.online_ips||0;
  $('kActive').innerHTML=(d.active_links||0)+'<em> / '+(d.links_count||0)+'</em>';
  $('kUp').textContent=d.uptime||'--';$('foot').textContent='uptime '+(d.uptime||'--');
  var ser=d.series_24h||[];STATE.lastSer=ser;
  $('serTotal').textContent=fmtBytes(ser.reduce(function(a,x){return a+x.bytes;},0))+' in 24h';
  var net=d.net||[];STATE.lastNet=net;
  barChart('serChart',ser);
  lineChart('netChart',net.map(function(x){return {rx:x.rx,tx:x.tx};}),{keys:[['rx','--sig'],['tx','--navy']]});
  if(net.length)pushScope(net[net.length-1].rx+net[net.length-1].tx);
  var x=d.xray||{};$('xrayText').textContent=x.running?'Xray '+(x.version||'').replace(/^Xray /,'').split(' ')[0]:'Xray down';
  $('xrayLamp').className='lamp '+(x.running?'live':'cut');
  var sy=function(id,pct){$(id).innerHTML=vu(pct,24);};
  $('mCpu').textContent=Math.round(d.cpu_percent)+'%';sy('vCpu',d.cpu_percent);$('pCpu').textContent=d.cpu_cores+' cores · load '+(d.load_avg||[]).join(' / ');
  $('mRam').textContent=Math.round(d.ram_percent)+'%';sy('vRam',d.ram_percent);$('pRam').textContent=(d.ram_used_mb/1024).toFixed(2)+' / '+(d.ram_total_mb/1024).toFixed(2)+' GB';
  $('mSwap').textContent=Math.round(d.swap_percent)+'%';sy('vSwap',d.swap_percent);$('pSwap').textContent=(d.swap_used_mb/1024).toFixed(2)+' / '+(d.swap_total_mb/1024).toFixed(2)+' GB';
  $('mDisk').textContent=Math.round(d.disk_percent)+'%';sy('vDisk',d.disk_percent);$('pDisk').textContent=d.disk_used_gb.toFixed(1)+' / '+d.disk_total_gb.toFixed(1)+' GB';
  var st=d.states||{};
  $('cActive').textContent=st.active||0;$('cDisabled').textContent=st.disabled||0;$('cExpired').textContent=st.expired||0;$('cDepleted').textContent=st.depleted||0;
  $('cVless').textContent=pr.vless||0;$('cTrojan').textContent=pr.trojan||0;$('cVmess').textContent=pr.vmess||0;$('cSs').textContent=pr.ss||0;
}
async function pollStats(){try{var r=await api('/stats');if(r.ok)renderStats(await r.json());}catch(e){}}

/* ---------- configs list ---------- */
function stateTag(l){
  if(l.state==='active')return '<span class="chip" style="background:var(--sig-soft);color:var(--sig);border-color:transparent">Active</span>';
  if(l.state==='disabled')return '<span class="chip">Disabled</span>';
  if(l.state==='expired')return '<span class="chip" style="background:var(--red-soft);color:var(--red)">Expired</span>';
  if(l.state==='depleted')return '<span class="chip" style="background:var(--amb-soft);color:var(--amb-ink)">Out of data</span>';
  return '';}
function lampFor(l){return l.state==='active'?(l.live_connections>0?'live':'on'):(l.state==='depleted'||l.state==='expired'?'warn':'off');}
function protoPills(l){return (l.protocols||['vless']).map(protoPill).join('');}
function rowHtml(l){
  var lim=l.limit_bytes>0,pct=lim?Math.min(100,l.used_bytes/l.limit_bytes*100):0;
  var meta=[];
  meta.push('<span>Live <b>'+(l.live_connections||0)+'</b></span>');
  if(l.ip_limit)meta.push('<span>Devices <b>'+l.connected_ips+' / '+l.ip_limit+'</b></span>');
  meta.push('<span>Speed <b>'+(l.speed_limit_bytes>0?fmtRate(l.speed_limit_bytes):'uncapped')+'</b></span>');
  meta.push('<span>Expiry <b>'+(l.expires_at?new Date(l.expires_at).toLocaleDateString():'never')+(l.days_left!=null&&l.state==='active'?' ('+Math.ceil(l.days_left)+'d)':'')+'</b></span>');
  if(l.applied_ips_count)meta.push('<span>Pinned IPs <b>'+l.applied_ips_count+'</b></span>');
  if(l.last_used)meta.push('<span>Seen <b>'+new Date(l.last_used).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})+'</b></span>');
  var sw='<label class="sw" title="'+(l.is_default?'Protected':(l.active?'Disable':'Enable'))+'"><input type="checkbox" data-t '+(l.active?'checked':'')+' '+(l.is_default?'disabled':'')+' aria-label="'+esc(l.label)+' enabled"><i></i></label>';
  var acts='<button class="ib sm" data-a="copy" title="Copy link" aria-label="Copy link">'+ic('copy')+'</button>'
    +'<button class="ib sm" data-a="qr" title="Share" aria-label="Share">'+ic('share')+'</button>'
    +'<button class="ib sm" data-a="open" title="Subscription page" aria-label="Subscription page">'+ic('open')+'</button>';
  if(!l.is_default)acts+='<button class="ib sm" data-a="edit" title="Edit" aria-label="Edit">'+ic('edit')+'</button>'
    +'<button class="ib sm" data-a="reset" title="Reset traffic" aria-label="Reset traffic">'+ic('reset')+'</button>'
    +'<button class="ib sm bad" data-a="del" title="Delete" aria-label="Delete">'+ic('trash')+'</button>';
  else acts+='<span class="tag acc" style="margin-left:6px">Protected</span>';
  return '<article class="line'+(l.state!=='active'?' off':'')+(l.is_default?' def':'')+'" data-uuid="'+esc(l.uuid)+'">'
    +'<div style="display:flex;align-items:center;gap:6px"><span class="lamp '+lampFor(l)+'"></span></div>'
    +'<div style="min-width:0"><div class="name"><b>'+esc(l.label)+'</b>'+protoPills(l)+stateTag(l)+(l.is_default?'<span class="tag amb">default</span>':'')+(l.fingerprint&&l.fingerprint!=='chrome'?'<span class="tag">'+esc(l.fingerprint)+'</span>':'')+'</div>'
    +'<div class="meta">'+meta.join('')+'</div>'
    +'<div class="usage">'+vu(lim?pct:0,28,!lim)+'<span class="mono">'+fmtBytes(l.used_bytes)+' / '+(lim?fmtBytes(l.limit_bytes):'∞')+'</span></div></div>'
    +'<div class="acts">'+sw+acts+'</div></article>';}
function filtered(){var q=STATE.q.trim().toLowerCase();return STATE.links.filter(function(l){
  if(STATE.filter!=='all'&&l.state!==STATE.filter)return false;
  if(STATE.proto!=='all'&&(l.protocols||[]).indexOf(STATE.proto)<0)return false;
  if(q&&String(l.label).toLowerCase().indexOf(q)<0&&String(l.note||'').toLowerCase().indexOf(q)<0)return false;return true;});}
function renderList(){
  var items=filtered(),box=$('lines');
  if(!STATE.links.length){box.innerHTML='<div class="empty">'+ic('plus')+'<b>No configs yet</b>Create your first line and share it as a subscription.</div>';return;}
  if(!items.length){box.innerHTML='<div class="empty"><b>Nothing matches</b>Try another filter or search term.</div>';return;}
  if(!renderList.done){renderList.done=1;box.classList.add('first');setTimeout(function(){box.classList.remove('first');},1200);}
  box.innerHTML=items.map(rowHtml).join('');
  var on=STATE.links.filter(function(l){return l.state==='active';}).length;
  $('cfgSub').textContent=on+' of '+STATE.links.length+' lines live. A lit lamp means it\'s carrying traffic right now.';
  $('cAll').textContent=STATE.links.length;
}
async function loadLinks(){try{var r=await api('/api/links');if(!r.ok)throw 0;var d=await r.json();STATE.links=d.links||[];renderList();}catch(e){}}

$('q').addEventListener('input',function(){STATE.q=this.value;renderList();});
$$('#filters .fchip').forEach(function(b){b.onclick=function(){STATE.filter=b.dataset.f;$$('#filters .fchip').forEach(function(x){x.setAttribute('aria-pressed',x===b);});renderList();};});
$$('#pfilters .fchip').forEach(function(b){b.onclick=function(){STATE.proto=b.dataset.p;$$('#pfilters .fchip').forEach(function(x){x.setAttribute('aria-pressed',x===b);});renderList();};});

$('lines').addEventListener('click',function(e){
  var b=e.target.closest('[data-a]');if(!b)return;var row=b.closest('.line');var l=STATE.links.find(function(x){return x.uuid===row.dataset.uuid;});if(!l)return;
  var a=b.dataset.a;
  if(a==='copy')copyText(lnk(l),'Link copied');
  else if(a==='qr')showQr(l);
  else if(a==='open')window.open(l.info_url||(l.sub_url+'/info'),'_blank','noopener');
  else if(a==='edit')editConfig(l);
  else if(a==='reset')resetTraffic(l);
  else if(a==='del')deleteConfig(l);
});
$('lines').addEventListener('change',function(e){
  if(!e.target.matches('[data-t]'))return;var row=e.target.closest('.line');var l=STATE.links.find(function(x){return x.uuid===row.dataset.uuid;});
  var want=e.target.checked;
  api('/api/links/'+l.uuid+'/toggle','PATCH',{active:want}).then(function(r){if(!r.ok)throw 0;toast((want?'Enabled ':'Disabled ')+l.label,'ok');loadLinks();pollStats();}).catch(function(){e.target.checked=!want;toast('Could not change status','err');});
});

/* ---------- config form ---------- */
var FPS=['chrome','firefox','safari','ios','android','edge','360','qq','random','randomized'];
(function(){$('cFp').innerHTML=FPS.map(function(f){return '<option value="'+f+'">'+f+'</option>';}).join('');})();
function setProtos(list){$('pV').checked=list.indexOf('vless')>=0;$('pT').checked=list.indexOf('trojan')>=0;$('pM').checked=list.indexOf('vmess')>=0;$('pS').checked=list.indexOf('ss')>=0;}
function getProtos(){var o=[];if($('pV').checked)o.push('vless');if($('pT').checked)o.push('trojan');if($('pM').checked)o.push('vmess');if($('pS').checked)o.push('ss');return o;}
function resetForm(){$('cUid').value='';$('cLabel').value='';$('cFp').value='chrome';$('cLimit').value='0';$('cLimitUnit').value='GB';$('cExpDays').value='0';$('cExpDate').value='';$('cIpLimit').value='0';$('cSpeed').value='0';$('cSpeedUnit').value='MBIT';$('cAlpn').value='';$('cNote').value='';setProtos(['vless','trojan']);$('cfgErr').classList.add('hidden');}
function newConfig(){resetForm();STATE.cur=null;$('cfgTitle').textContent='New config';$('cfgSub2').textContent='A tunnel line with its own quota and limits.';$('cfgSave').textContent='Create config';$('cExpWrap').style.display='';$('cExpDateWrap').style.display='none';openModal('cfgModal');$('cLabel').focus();}
function editConfig(l){resetForm();STATE.cur=l;$('cUid').value=l.uuid;$('cLabel').value=l.label;$('cFp').value=l.fingerprint||'chrome';$('cAlpn').value=l.alpn||'';$('cNote').value=l.note||'';setProtos(l.protocols||['vless']);
  var gb=l.limit_bytes/1073741824;$('cLimit').value=l.limit_bytes?(gb>=1?+gb.toFixed(2):+(l.limit_bytes/1048576).toFixed(1)):0;$('cLimitUnit').value=l.limit_bytes&&gb<1?'MB':'GB';
  $('cIpLimit').value=l.ip_limit||0;var sp=l.speed_limit_bytes?(l.speed_limit_bytes*8/1000000):0;$('cSpeed').value=+sp.toFixed(2);$('cSpeedUnit').value='MBIT';
  $('cExpDate').value=l.expires_at?l.expires_at.slice(0,10):'';$('cExpWrap').style.display='none';$('cExpDateWrap').style.display='';
  $('cfgTitle').textContent='Edit '+l.label;$('cfgSub2').textContent='Changes apply immediately to live connections.';$('cfgSave').textContent='Save changes';openModal('cfgModal');$('cLabel').focus();}
function buildBody(){
  var v=function(id){return $(id).value;};
  var protos=getProtos();
  var b={label:v('cLabel').trim()||'Config',fingerprint:v('cFp'),alpn:v('cAlpn').trim(),note:v('cNote').trim(),
    protocols:protos,limit_value:parseFloat(v('cLimit'))||0,limit_unit:v('cLimitUnit'),ip_limit:parseInt(v('cIpLimit'),10)||0,
    speed_limit_value:parseFloat(v('cSpeed'))||0,speed_limit_unit:v('cSpeedUnit')};
  if(STATE.cur){ // only send what changed, so an edit never resets the clock or truncates values
    var c=STATE.cur,out={};
    if(b.label!==c.label)out.label=b.label;
    if(b.protocols.join()!==(c.protocols||['vless']).join())out.protocols=b.protocols;
    if(b.fingerprint!==(c.fingerprint||'chrome'))out.fingerprint=b.fingerprint;
    if(b.alpn!==(c.alpn||''))out.alpn=b.alpn;
    if(b.note!==(c.note||''))out.note=b.note;
    if(b.ip_limit!==(c.ip_limit||0))out.ip_limit=b.ip_limit;
    var cur=c.limit_bytes?c.limit_bytes/1073741824:0;if(Math.abs(b.limit_value-(+cur.toFixed(2)))>0.001||(b.limit_value===0&&c.limit_bytes))out.limit_value=b.limit_value,out.limit_unit=b.limit_unit;
    var curSp=c.speed_limit_bytes?c.speed_limit_bytes*8/1000000:0;if(Math.abs(b.speed_limit_value-(+curSp.toFixed(2)))>0.001)out.speed_limit_value=b.speed_limit_value,out.speed_limit_unit='MBIT';
    var curExp=c.expires_at?c.expires_at.slice(0,10):'';if(v('cExpDate')!==curExp)out.expires_at=v('cExpDate')||'';
    return out;}
  b.expires_days=parseInt(v('cExpDays'),10)||0;return b;}
async function saveConfig(){
  var btn=$('cfgSave'),er=$('cfgErr');er.classList.add('hidden');
  if(!getProtos().length){er.textContent='Pick at least one protocol.';er.classList.remove('hidden');return;}
  var body=buildBody();
  if(STATE.cur&&!Object.keys(body).length){closeModal('cfgModal');toast('Nothing to change','');return;}
  btn.disabled=true;var was=btn.textContent;btn.textContent='Saving…';
  try{
    var r=STATE.cur?await api('/api/links/'+STATE.cur.uuid,'PATCH',body):await api('/api/links','POST',body);
    if(!r.ok)throw new Error(await errOf(r,'Could not save'));
    closeModal('cfgModal');toast(STATE.cur?'Config updated':'Config created','ok');loadLinks();pollStats();
  }catch(e){er.textContent=e.message;er.classList.remove('hidden');}
  finally{btn.disabled=false;btn.textContent=was;}
}
async function resetTraffic(l){
  if(!await ask('Reset traffic?','Usage for '+l.label+' goes back to zero and it comes back online if it had run out of data.','Reset',true))return;
  try{var r=await api('/api/links/'+l.uuid+'/reset-traffic','POST');if(!r.ok)throw 0;toast('Traffic reset','ok');loadLinks();}catch(e){toast('Could not reset','err');}}
async function deleteConfig(l){
  if(!await ask('Delete '+l.label+'?','Its links stop working immediately for every device. This cannot be undone.','Delete',true))return;
  try{var r=await api('/api/links/'+l.uuid,'DELETE');if(!r.ok)throw new Error(await errOf(r,'Could not delete'));toast('Config deleted','ok');loadLinks();}catch(e){toast(e.message,'err');}}

/* ---------- share / QR ---------- */
async function qrFor(data){var r=await api('/api/qr?size=320&data='+encodeURIComponent(data));var j=await r.json();return j.qr;}
async function showQr(l){
  $('qrName').textContent=l.label;
  var grid=$('qrGrid');
  var cards=(l.variants||[]).filter(function(x){return x.where==='Domain';}).map(function(x){
    return {title:PROTO_META[x.protocol]?PROTO_META[x.protocol].n:x.protocol,url:x.url,pill:protoPill(x.protocol),cap:'Copy '+(PROTO_META[x.protocol]?PROTO_META[x.protocol].n:'link')};});
  cards.push({title:'Subscription',url:l.sub_url,pill:'<b>Subscription</b>',cap:'Copy subscription'});
  grid.innerHTML=cards.map(function(c,i){return '<div class="qc">'+c.pill+'<div class="qi"><img id="qr'+i+'" alt="'+esc(c.title)+' QR"></div><p>'+esc(c.url)+'</p><button class="btn sm" data-copy-i="'+i+'">'+ic('copy')+esc(c.cap)+'</button></div>';}).join('');
  $$('button[data-copy-i]',grid).forEach(function(b){b.onclick=function(){copyText(cards[+b.dataset.copyI].url,'Copied');};});
  openModal('qrModal');
  try{for(var i=0;i<cards.length;i++){$('qr'+i).src=await qrFor(cards[i].url);}}catch(e){toast('Could not draw QR','err');}}

/* ---------- clean IPs ---------- */
async function loadIps(){
  try{
    var d=await (await api('/api/domain/check')).json();
    $('ipDomain').classList.toggle('hidden',!d.is_railway);
    var r=await (await api('/api/ips/suggest?count=12')).json();
    $('ipGrid').innerHTML=(r.ips||[]).map(function(ip){return '<label class="opt"><input type="checkbox" class="ipc" value="'+esc(ip)+'" checked><span class="grow">'+esc(ip)+'</span></label>';}).join('')||'<p class="hint">No IPs available.</p>';
    var t=await (await api('/api/links')).json();
    $('ipTargets').innerHTML=(t.links||[]).filter(function(l){return !l.is_default;}).map(function(l){return '<label class="opt"><input type="checkbox" class="ipt" value="'+esc(l.uuid)+'"><span class="grow">'+esc(l.label)+'</span>'+(l.applied_ips_count?'<span class="tag acc">'+l.applied_ips_count+' pinned</span>':'')+'</label>';}).join('')||'<p class="hint" style="padding:12px">Create a config first.</p>';
    syncIpBtn();$('ipStatus').textContent=(r.ips||[]).length+' IPs loaded';
  }catch(e){toast('Could not load suggestions','err');}}
function syncIpBtn(){$('ipApply').disabled=!$$('.ipt:checked').length||!$$('.ipc:checked').length;}
document.addEventListener('change',function(e){if(e.target.matches('.ipt,.ipc'))syncIpBtn();if(e.target.matches('.hc'))syncHealth();});
async function applyIps(){
  var ips=$$('.ipc:checked').map(function(x){return x.value;}),tg=$$('.ipt:checked').map(function(x){return x.value;});
  var ok=await ask('Apply '+ips.length+' IP'+(ips.length>1?'s':'')+'?','Pinned to '+tg.length+' config'+(tg.length>1?'s':'')+' in '+$('ipMode').value+' mode.','Apply',false);if(!ok)return;
  var b=$('ipApply');b.disabled=true;
  try{var r=await api('/api/ips/apply','POST',{ips:ips,target_uuids:tg,port:parseInt($('ipPort').value,10)||443,mode:$('ipMode').value});
    if(!r.ok)throw new Error(await errOf(r,'Apply failed'));closeModal('ipModal');toast('Pinned IPs updated','ok');loadLinks();}
  catch(e){toast(e.message,'err');}finally{b.disabled=false;}}

/* ---------- health ---------- */
async function loadHealthTargets(){
  $('hRes').innerHTML='';$('hStatus').textContent='';
  try{var t=await (await api('/api/links')).json();
    $('hList').innerHTML=(t.links||[]).map(function(l){return '<label class="opt"><input type="checkbox" class="hc" value="'+esc(l.uuid)+'" checked><span class="grow">'+esc(l.label)+'</span>'+protoPills(l)+stateTag(l)+'</label>';}).join('')||'<p class="hint" style="padding:12px">No configs.</p>';
    syncHealth();}catch(e){toast('Could not load configs','err');}}
function syncHealth(){var n=$$('.hc:checked').length;$('hGo').disabled=!n;$('hStatus').textContent=n+' selected';}
async function runHealth(){
  var uu=$$('.hc:checked').map(function(x){return x.value;});if(!uu.length)return;
  var b=$('hGo');b.disabled=true;$('hStatus').textContent='Probing…';
  try{var r=await (await api('/api/configs/test','POST',{uuids:uu})).json();var res=r.results||{};
    var rows='';Object.keys(res).forEach(function(k){var x=res[k];var l=STATE.links.find(function(z){return z.uuid===k;});
      rows+='<div class="hr"><span>'+esc(l?l.label:'config')+' <span class="mono">· '+x.targets.length+' target'+(x.targets.length===1?'':'s')+'</span></span><span class="'+(x.healthy?'good':'bad')+'">'+(x.healthy?'Reachable':'Unreachable')+'</span><span class="mono">'+(x.latency!=null?x.latency.toFixed(0)+' ms':'—')+'</span></div>';
      if(x.error&&!x.healthy)rows+='<div class="hr" style="grid-template-columns:1fr;color:var(--mut);font-size:13px">'+esc(x.error)+'</div>';
      x.targets.forEach(function(t){rows+='<div class="hr" style="grid-template-columns:minmax(0,1fr) auto auto;padding-left:30px;font-size:13.5px"><span class="mono">'+esc(t.tag)+' · '+esc(t.address)+':'+t.port+'</span><span class="'+(t.ms!=null?'good':'bad')+'">'+(t.ms!=null?'open':'closed')+'</span><span class="mono">'+(t.ms!=null?t.ms.toFixed(0)+' ms':'—')+'</span></div>';});});
    $('hRes').innerHTML='<div class="hres" style="margin-top:4px">'+rows+'</div>';$('hStatus').textContent='Done';
  }catch(e){toast('Probe failed','err');}finally{b.disabled=false;}}

/* ---------- live connections ---------- */
var connT=null;
async function loadConns(){
  var tick=async function(){try{var d=await (await api('/api/connections')).json();var c=d.connections||[];
    $('connBody').innerHTML=c.length?c.map(function(x){return '<tr><td>'+esc(x.label)+'</td><td>'+protoPill(x.proto||'vless')+'</td><td class="mono">'+esc(x.ip)+'</td><td class="mono">'+new Date(x.since).toLocaleTimeString()+'</td><td class="r mono">'+fmtBytes(x.down)+'</td><td class="r mono">'+fmtBytes(x.up)+'</td></tr>';}).join(''):'<tr><td colspan="6" style="text-align:center;color:var(--mut);padding:26px">Nobody is connected right now.</td></tr>';}catch(e){}};
  await tick();if(connT)clearInterval(connT);connT=setInterval(tick,3000);}

/* ---------- backup ---------- */
var PICK=null;
async function refreshDbInfo(){try{var t=await (await api('/api/links')).json();var L=t.links||[];
  $('dbN').textContent=L.length;$('dbA').textContent=L.filter(function(x){return x.state==='active';}).length;$('dbT').textContent=fmtBytes(L.reduce(function(a,x){return a+x.used_bytes;},0));}catch(e){}}
async function exportDb(){try{var r=await api('/api/database/export');if(!r.ok)throw 0;var blob=new Blob([await r.text()],{type:'application/json'});var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='mx-ui-backup-'+new Date().toISOString().slice(0,10)+'.json';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},500);toast('Backup downloaded','ok');}catch(e){toast('Export failed','err');}}
function clearPick(){PICK=null;$('dbFile').value='';$('dbPick').classList.add('hidden');$('dbGo').disabled=true;}
(function(){var f=$('dbFile'),d=$('drop');
  var take=function(file){if(!file)return;var rd=new FileReader();rd.onload=function(){try{var j=JSON.parse(rd.result);if(!j.links||typeof j.links!=='object')throw 0;PICK=j;$('dbPickName').textContent=file.name;$('dbPickInfo').textContent=Object.keys(j.links).length+' configs · '+fmtBytes(file.size);$('dbPick').classList.remove('hidden');$('dbGo').disabled=false;}catch(e){toast('That file is not an MX-UI backup','err');clearPick();}};rd.readAsText(file);};
  f.onchange=function(){take(f.files[0]);};
  ['dragenter','dragover'].forEach(function(ev){d.addEventListener(ev,function(e){e.preventDefault();d.classList.add('over');});});
  ['dragleave','drop'].forEach(function(ev){d.addEventListener(ev,function(e){e.preventDefault();d.classList.remove('over');});});
  d.addEventListener('drop',function(e){take(e.dataTransfer.files[0]);});
  d.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();f.click();}});
})();
async function importDb(){
  if(!PICK)return;var mode=$('dbMode').value;
  var ok=await ask(mode==='replace'?'Replace all configs?':'Merge backup?',mode==='replace'?'Every non-default config is removed and replaced by the backup.':'Configs in the backup are added or updated. Nothing else is removed.',mode==='replace'?'Replace':'Merge',mode==='replace');if(!ok)return;
  try{var r=await api('/api/database/import','POST',{links:PICK.links,mode:mode});if(!r.ok)throw new Error(await errOf(r,'Restore failed'));var j=await r.json();toast('Restored '+j.imported+' configs','ok');clearPick();closeModal('dbModal');loadLinks();pollStats();}
  catch(e){toast(e.message,'err');}}

/* ---------- settings ---------- */
async function changePw(){
  var c=$('sCur').value,n=$('sNew').value,n2=$('sNew2').value,er=$('sErr');er.classList.add('hidden');
  var fail=function(m){er.textContent=m;er.classList.remove('hidden');};
  if(!c||!n)return fail('Fill in all fields.');if(n.length<6)return fail('New password needs 6+ characters.');if(n!==n2)return fail("New passwords don't match.");
  var b=$('sGo');b.disabled=true;
  try{var r=await api('/api/change-password','POST',{current_password:c,new_password:n});if(!r.ok)throw new Error(await errOf(r,'Could not change password'));
    toast('Password changed. Signing you out…','ok');setTimeout(function(){location.replace('/login');},900);}
  catch(e){fail(e.message);}finally{b.disabled=false;}}
async function logout(){try{await api('/api/logout','POST');}catch(e){}location.replace('/login');}

/* ---------- boot ---------- */
loadLinks();pollStats();
setInterval(pollStats,5000);setInterval(loadLinks,15000);
"""



LOGS_BODY = r"""<body>
<header><div class="wrap bar">
  __BRAND__
  <div class="sp"></div>
  <button class="btn sm ghost" onclick="location.href='/dashboard'">__IC_back__Dashboard</button>
  __THEME__
</div></header>
<main class="wrap">
  <h1 class="h1">Logs</h1>
  <p class="lead">Core output and panel activity. Newest at the bottom.</p>
  <div class="toolbar">
    <div class="seg" role="group" aria-label="Level"><button data-l="" aria-pressed="true">All</button><button data-l="info" aria-pressed="false">Info</button><button data-l="warning" aria-pressed="false">Warnings</button><button data-l="error" aria-pressed="false">Errors</button></div>
    <div class="seg" role="group" aria-label="Source"><button data-s="core" aria-pressed="true">Core</button><button data-s="file" aria-pressed="false">Core file</button><button data-s="activity" aria-pressed="false">Panel</button></div>
    <label class="live"><input type="checkbox" id="auto" checked> Live</label>
    <span class="pill" id="ports">ports…</span>
    <span class="sp"></span>
    <button class="btn sm" onclick="clearLogs()">__IC_trash__Clear</button>
  </div>
  <div class="term" id="term" role="log" aria-live="off"></div>
</main>
__ASK__
<div id="toast" class="toast" role="status"></div>
"""

LOGS_JS = r"""
var LV='',SRC='core';
$$('[data-l]').forEach(function(b){b.onclick=function(){LV=b.dataset.l;$$('[data-l]').forEach(function(x){x.setAttribute('aria-pressed',x===b);});load();};});
$$('[data-s]').forEach(function(b){b.onclick=function(){SRC=b.dataset.s;$$('[data-s]').forEach(function(x){x.setAttribute('aria-pressed',x===b);});load();};});
function row(t,lv,m){var d=t?new Date(t):null;var ts=d&&!isNaN(d)?d.toLocaleTimeString([],{hour12:false}):(t||'');return '<div class="ln"><time>'+esc(ts)+'</time><span class="lv '+esc(lv||'info')+'">'+esc(lv||'info')+'</span><span>'+esc(m)+'</span></div>';}
async function load(){
  var box=$('term'),html='';
  try{
    if(SRC==='core'){var r=await api('/api/logs?limit=500'+(LV?'&level='+LV:''));var d=await r.json();
      html=(d.logs||[]).map(function(x){return row(x.time,x.level,x.msg);}).join('');}
    else if(SRC==='file'){var f=await (await api('/api/logs/files/xray_stdout.log?tail=300')).json();
      html=(f.lines||[]).map(function(s){return '<div class="ln"><span></span><span></span><span>'+esc(s)+'</span></div>';}).join('');}
    else {var a=await (await api('/api/logs?limit=1')).json();
      html=(a.activity||[]).map(function(x){return row(x.time,x.level,'['+x.kind+'] '+x.message);}).join('');}
    var atBottom=box.scrollTop+box.clientHeight>=box.scrollHeight-40;
    box.innerHTML=html||'<div class="empty">Nothing here yet.</div>';
    if(atBottom)box.scrollTop=box.scrollHeight;
  }catch(e){}
  try{var p=await (await api('/api/logs/ports')).json();var l=p.listening||{};var ok=Object.keys(l).filter(function(k){return l[k];}).length;
    $('ports').innerHTML='<span class="lamp '+(p.xray_running?'live':'cut')+'" style="width:8px;height:8px"></span>&nbsp;core '+(p.xray_running?'running':'down')+' · '+ok+'/'+Object.keys(l).length+' ports';}catch(e){}
}
async function clearLogs(){if(!await ask('Clear logs?','Core and panel logs are wiped from memory.','Clear',true))return;await api('/api/logs/clear','POST');load();toast('Logs cleared','ok');}
function tick(){if($('auto').checked)load();}
load();setInterval(tick,2500);
"""


def _icons(s: str) -> str:
    import re
    return re.sub(r"__IC_(\w+?)__", lambda m: ic(m.group(1)), s)


def _body(tpl: str, sub: str) -> str:
    from pages import THEME_BTN as TB
    return (tpl.replace("__BRAND__", brand(sub))
               .replace("__THEME__", TB)
               .replace("__ASK__", ASK_MODAL))


DASHBOARD_HTML = page("MX-UI · Dashboard", DASH_CSS + MODAL_CSS,
                      _icons(SPRITE + _body(DASH_BODY, "v2.3.0")) + "<script>" + UTIL_JS + DASH_JS + "</script></body></html>")

LOGS_HTML = page("MX-UI · Logs", LOGS_CSS + MODAL_CSS,
                 _icons(SPRITE + _body(LOGS_BODY, "logs")) + "<script>" + UTIL_JS + LOGS_JS + "</script></body></html>")
