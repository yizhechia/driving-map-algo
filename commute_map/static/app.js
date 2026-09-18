'use strict';
const $ = id => document.getElementById(id);
let result = null, selected = null, busy = false;
const canvas = $('map'), ctx = canvas.getContext('2d');
const box = {left:70, top:45, width:720, height:570};
const px = x => box.left + x/32*box.width;
const py = y => box.top + (32-y)/32*box.height;
const fmt = n => n == null ? '—' : Number(n).toFixed(1);
function config() {
  const size = Number($('size').value), method = $('method').value;
  return {threshold:Number($('threshold').value),direction:$('direction').value,
    period:$('period').value,buffer_min_per_km:Number($('buffer').value),
    condo_minutes:Number($('condo').value),size,method,
    budget:method==='full'?size*size:Number($('budget').value)};
}
function samplingControl() { $('budget').disabled = $('method').value === 'full'; }
function settingsMatchResult() {
  return result !== null && Object.entries(config()).every(([key,value])=>value===result.config[key]);
}
function showResultStatus() {
  const current = settingsMatchResult();
  $('run-status').textContent = current ? 'Updated · synthetic scenario' :
    'Settings changed. Update the map to apply them.';
  $('download').disabled = busy || !current;
}
function element(tag, text, className) {
  const node=document.createElement(tag); if(text!==undefined)node.textContent=text;
  if(className)node.className=className;return node;
}
function draw() {
  ctx.clearRect(0,0,canvas.width,canvas.height);
  if(!result)return;
  const g=result.grid,n=g.size,w=box.width/n,h=box.height/n;
  for(let y=0;y<n;y++)for(let x=0;x<n;x++){
    const label=g.labels[y][x],v=g.values[y][x];
    if(label==='inside')ctx.fillStyle=`hsl(160 28% ${Math.max(58,84-(result.config.threshold-v)*0.7)}%)`;
    else if(label==='outside')ctx.fillStyle=`hsl(34 53% ${Math.max(70,90-(v-result.config.threshold)*0.4)}%)`;
    else ctx.fillStyle=label==='no_route'?'#c4cfca':'#e9ece8';
    ctx.globalAlpha = g.observed[y][x]?1:0.65;
    ctx.fillRect(box.left+x*w,box.top+(n-y-1)*h,w+0.2,h+0.2);
  }
  ctx.globalAlpha=1;
  for(let i=0;i<=n;i++){
    ctx.strokeStyle=i%(n/4)===0?'#78978d':'rgba(255,255,255,.42)';
    ctx.lineWidth=i%(n/4)===0?1.25:0.5;
    ctx.beginPath();ctx.moveTo(box.left+i*w,box.top);ctx.lineTo(box.left+i*w,box.top+box.height);ctx.stroke();
    ctx.beginPath();ctx.moveTo(box.left,box.top+i*h);ctx.lineTo(box.left+box.width,box.top+i*h);ctx.stroke();
  }
  ctx.strokeStyle='#236851';ctx.lineWidth=2;
  ctx.beginPath();for(const [a,b] of result.outline){ctx.moveTo(px(a[0]*32/n),py(a[1]*32/n));ctx.lineTo(px(b[0]*32/n),py(b[1]*32/n));}ctx.stroke();
  ctx.font='12px system-ui';ctx.fillStyle='#63796e';ctx.textAlign='center';
  for(let v=0;v<=32;v+=8){ctx.fillText(v+' km',px(v),box.top+box.height+25);ctx.fillText(String(v),box.left-25,py(v)+4);}
  ctx.textAlign='left';ctx.fillText('SCHEMATIC LOCAL GRID',box.left,22);
  ctx.textAlign='right';ctx.fillText('N ↑',box.left+box.width,22);
  if(selected&&selected.route_points){
    ctx.beginPath();selected.route_points.forEach((p,i)=>i?ctx.lineTo(px(p[0]),py(p[1])):ctx.moveTo(px(p[0]),py(p[1])));
    ctx.strokeStyle='#fff';ctx.lineWidth=8;ctx.stroke();ctx.strokeStyle='#4f4682';ctx.lineWidth=4;ctx.stroke();
    const points=selected.route_points;
    for(let i=1;i<points.length;i++){
      const a=points[i-1],b=points[i],x=(px(a[0])+px(b[0]))/2,y=(py(a[1])+py(b[1]))/2;
      const angle=Math.atan2(py(b[1])-py(a[1]),px(b[0])-px(a[0]));
      ctx.save();ctx.translate(x,y);ctx.rotate(angle);ctx.beginPath();ctx.moveTo(6,0);ctx.lineTo(-5,-4);ctx.lineTo(-5,4);ctx.closePath();ctx.fillStyle='#4f4682';ctx.fill();ctx.restore();
    }
  }
  for(const p of result.landmarks){
    const x=px(p.x),y=py(p.y),name=p.id==='KLCC'?'KLCC':p.id==='SB'?'Sungai Buloh':p.id==='RAWANG'?'Rawang':'Cheras';
    ctx.beginPath();ctx.arc(x,y,p.id==='KLCC'?7:5,0,2*Math.PI);ctx.fillStyle=p.id==='KLCC'?'#173b30':'#fff';ctx.fill();ctx.strokeStyle='#173b30';ctx.lineWidth=2;ctx.stroke();
    ctx.font='600 14px system-ui';const tw=ctx.measureText(name).width;ctx.fillStyle='rgba(255,255,255,.94)';ctx.fillRect(x-tw/2-7,y-31,tw+14,22);ctx.fillStyle='#244d3c';ctx.textAlign='center';ctx.fillText(name,x,y-15);
  }
  if(selected&&selected.x!==undefined){ctx.beginPath();ctx.arc(px(selected.x),py(selected.y),7,0,2*Math.PI);ctx.fillStyle='#4f4682';ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=3;ctx.stroke();}
}
function select(detail) {
  selected=detail;
  const panel=$('detail');panel.replaceChildren();panel.append(element('p','ROUTE DETAILS','eyebrow'));
  const top=element('div',undefined,'detail-top'),left=element('div');left.append(element('h2',detail.name));
  left.append(element('div',detail.status==='inside'?'Within your limit':detail.status==='outside'?'Above your limit':detail.status==='no_route'?'No route in this model':'Not directly sampled','status'));top.append(left);
  const total=element('div',fmt(detail.planning_minutes)+' ', 'time-big');total.append(element('small','min'));top.append(total);panel.append(top);
  if(detail.breakdown&&detail.planning_minutes!==null){
    const breakdown=element('div',undefined,'breakdown');
    for(const [key,label] of [['corridor','Main corridor'],['local','Local roads'],['access','Home access'],['buffer','Distance buffer']]){
      const cell=element('div',label);cell.append(element('b',fmt(detail.breakdown[key])+' min'));breakdown.append(cell);
    }panel.append(breakdown);
    panel.append(element('p',detail.path.join(' → ')+' · '+fmt(detail.distance_km)+' assumed road km'));
  }else panel.append(element('p',detail.note||'This access point has no directed connection in the synthetic network. No travel time is assigned.'));
  document.querySelectorAll('.card').forEach(card=>card.classList.toggle('selected',card.dataset.id===detail.id));draw();
}
function render() {
  const c=result.config,g=result.grid;
  $('map-heading').textContent=(c.direction==='work_to_home'?'KLCC → home':'Home → KLCC')+' · '+fmt(c.threshold)+' min limit';
  $('coverage').textContent=`${g.queries.toLocaleString()} / ${(g.size*g.size).toLocaleString()} cell centres sampled · ${g.estimated_cells} interpolated · ${g.counts.unknown} unknown · ${g.counts.no_route} no route`;
  if(result.potentially_truncated)$('coverage').textContent+=' · Region reaches the study edge; it may continue beyond it.';
  $('cards').replaceChildren();
  for(const item of result.examples){
    const card=element('button',undefined,'card');card.type='button';card.dataset.id=item.id;
    card.append(element('h3',item.name));
    const pill=element('span',item.status==='inside'?'Within limit':item.status==='outside'?'Above limit':'No route','pill'+(item.status==='outside'?' out':''));card.append(pill);
    const total=element('span',fmt(item.planning_minutes)+' ', 'total');total.append(element('small','min'));card.append(total);
    card.append(element('p',item.planning_minutes===null?'Unconnected in the example network':`${fmt(item.breakdown.corridor)} corridor + ${fmt(item.breakdown.local)} local + ${fmt(item.breakdown.access+item.breakdown.buffer)} allowances`));
    card.addEventListener('click',()=>select(item));$('cards').append(card);
  }
  const last=result.examples.find(i=>selected&&i.id===selected.id)||result.examples[0];select(last);
}
async function update(event){
  if(event)event.preventDefault();if(busy)return;
  busy=true;$('run').disabled=true;$('download').disabled=true;$('error').hidden=true;$('run-status').textContent='Calculating routes and grid…';
  try{
    const response=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config())});
    const data=await response.json();if(!response.ok)throw Error(data.error||'Could not update the map');
    result=data;render();showResultStatus();
  }catch(error){$('error').textContent=error.message;$('error').hidden=false;$('run-status').textContent=result?'Update failed. The previous result is still displayed.':'No result available.';}
  finally{busy=false;$('run').disabled=false;$('download').disabled=!settingsMatchResult();}
}
$('settings').addEventListener('submit',update);
$('settings').addEventListener('input',()=>{showResultStatus();samplingControl();});
canvas.addEventListener('click',event=>{
  if(!result||busy)return;const rect=canvas.getBoundingClientRect();
  const x=(event.clientX-rect.left)*canvas.width/rect.width,y=(event.clientY-rect.top)*canvas.height/rect.height,n=result.grid.size;
  const col=Math.floor((x-box.left)/box.width*n),row=n-1-Math.floor((y-box.top)/box.height*n);
  if(col<0||row<0||col>=n||row>=n)return;
  const direct=result.cell_details[`${col},${row}`];
  if(direct)select(direct);
  else select({id:`estimate_${col}_${row}`,name:`Access ${col}, ${row} · estimated`,status:'unknown',planning_minutes:result.grid.values[row][col],x:(col+.5)*32/n,y:(row+.5)*32/n,note:'This cell centre was not queried. Any displayed time is interpolated; route and component details are unavailable.'});
});
$('download').addEventListener('click',async()=>{
  if(!result||busy||!settingsMatchResult())return;$('download').disabled=true;
  try{const response=await fetch('/api/export',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(result.config)});const data=await response.json();if(!response.ok)throw Error(data.error||'Export failed');const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/geo+json'});const url=URL.createObjectURL(blob);const a=element('a');a.href=url;a.download='synthetic-commute-region.geojson';a.click();URL.revokeObjectURL(url);}catch(error){$('error').textContent=error.message;$('error').hidden=false;}finally{$('download').disabled=busy||!settingsMatchResult();}
});
samplingControl();update();
