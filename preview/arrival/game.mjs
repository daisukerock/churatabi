import {WIDTH,HEIGHT,spots,route,nearestFloor,walkable,cell,defaults,objective,goalId} from './world.mjs';
const $=s=>document.querySelector(s),canvas=$('#game'),ctx=canvas.getContext('2d',{alpha:false});
const KEY='churatabi-arrival-1';let state=defaults(),saveOK=true;
try{const saved=JSON.parse(localStorage.getItem(KEY));if(saved?.version===1)for(const k of Object.keys(state))state[k]=saved.flags?.[k]===true}catch{saveOK=false}
// Reject inconsistent stale or manually edited saves.
if(!state.introduced){state.card=false;state.returned=false;state.departed=false}if(!state.card){state.returned=false;state.departed=false}if(!state.returned)state.departed=false;
let started=false,ready=false,path=[],pending=null,moving=false,walking=0,last=0,camera={x:240,y:0},look=null,ring=null,near=null,keys=new Set(),held=null,lastStep=0;
const hero={x:392,y:248,dir:0},images={},dialogs=[...document.querySelectorAll('dialog')];
const blocked=()=>dialogs.some(d=>d.open)||!started;
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
let audio=null,sound=false;
function tone(notes,volume=.05){if(!sound||!audio)return;const now=audio.currentTime;for(const [freq,time,duration] of notes){let o=audio.createOscillator(),g=audio.createGain();o.type='sine';o.frequency.setValueAtTime(freq,now+time);g.gain.setValueAtTime(0,now+time);g.gain.linearRampToValueAtTime(volume,now+time+.008);g.gain.exponentialRampToValueAtTime(.001,now+time+duration);o.connect(g);g.connect(audio.destination);o.start(now+time);o.stop(now+time+duration+.02)}}
async function enableSound(){try{audio??=new(window.AudioContext||window.webkitAudioContext)();await audio.resume();sound=true;$('#sound').textContent='音 ON';$('#sound').setAttribute('aria-pressed','true');tone([[660,0,.12],[880,.09,.16]])}catch{sound=false;toast('この環境では音を再生できません')}}
$('#sound').onclick=()=>{if(sound){sound=false;$('#sound').textContent='音 OFF';$('#sound').setAttribute('aria-pressed','false')}else enableSound()};
function toast(text){$('#toast').textContent=text;$('#toast').classList.add('show');clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#toast').classList.remove('show'),3200)}
function save(){try{localStorage.setItem(KEY,JSON.stringify({version:1,flags:state}));saveOK=true}catch{saveOK=false;toast('記録を保存できません。この画面では続けて遊べます')}}
function update(){ $('#goal').textContent=objective(state);$('#progress').textContent=`${Number(state.introduced)+Number(state.returned)+Number(state.departed)} / 3`;}
function mark(key,message){if(state[key])return;state[key]=true;save();update();tone([[523,0,.15],[659,.12,.15],[784,.24,.3]],.07);if(message)toast(message)}
function open(d){path=[];pending=null;keys.clear();held=null;document.body.classList.add('modal');d.showModal()}
for(const d of dialogs)d.addEventListener('close',()=>{document.body.classList.toggle('modal',dialogs.some(x=>x.open));keys.clear();held=null;canvas.focus({preventScroll:true})});
let pages=[],page=0,finish=null;
function talk(name,texts,sprite='hero',callback=null){pages=texts;page=0;finish=callback;$('#who').textContent=name;$('#portrait').style.backgroundImage=`url(assets/${sprite}.png)`;showPage();open($('#talk'));tone([[540,0,.08]])}
function showPage(){ $('#speech').textContent=pages[page];$('#pageCount').textContent=`${page+1} / ${pages.length}`;$('#next').textContent=page===pages.length-1?'とじる →':'つづける →';}
$('#next').onclick=()=>{tone([[650,0,.055]],.025);if(++page<pages.length)showPage();else{const done=finish;finish=null;$('#talk').close();done?.()}};
$('#talk').addEventListener('cancel',e=>{e.preventDefault();$('#next').click()});
function interact(id){
 const s=spots.find(s=>s.id===id);if(!s||blocked())return;
 hero.dir=id==='grandma'?3:id==='traveler'?3:3;
 if(id==='guide')talk(s.name,state.introduced?['ゆいレールへは、2階の連絡通路からどうぞ。ロビー右奥の「2F」の案内が目印です。',state.returned?'絵はがき、無事に届いたんですね。よい島旅になりますように！':'足元に絵はがきが落ちていましたか？ ベンチのそばのおばあが、何か探していたようですよ。']:['めんそーれ！ 沖縄へようこそ。長旅、おつかれさまでした。','ゆいレールへ行くなら、2階の連絡通路から駅へ進んでくださいね。ロビー右奥に、上の階への案内があります。','お時間があれば、水槽もぜひ。到着ロビーには熱帯魚がいるんですよ。まずは、沖縄の海にごあいさつ。'],'guide',()=>mark('introduced','手帳に「旅の道しるべ」を記録しました'));
 if(id==='aquarium')talk('ロビーの水槽',['青い水の中を、小さな魚たちがすり抜けていく。サンゴのかげから、もう一匹。','飛行機の音が、少し遠くなった気がする。……沖縄に着いたんだな。'],'hero',()=>mark('fish','寄り道の記録「ひと足先に、沖縄の海」'));
 if(id==='postcard'){
  if(state.returned){toast('絵はがきは、おばあのもとへ届きました');return}
  if(state.card){toast('絵はがきを持っています。ベンチのそばのおばあへ');return}
  talk('足元の絵はがき',['床に、海の絵はがきが一枚。裏には「おばあへ。迎えに来てくれてありがとう」とある。',state.introduced?'大切なものかもしれない。ベンチのそばで探しものをしている人に聞いてみよう。':'誰かの大切なものかもしれない。先に案内係に相談してみよう。'],'hero',()=>{if(!state.introduced)toast('まずは案内係に相談しよう');else mark('card','絵はがきを拾った。持ち主を探そう')})
 }
 if(id==='grandma')talk(s.name,state.returned?['絵はがきは、ちゃんとしまったよ。孫が来るの、もうすぐさ。','旅の途中で、また誰かといい出会いがあるといいね。']:state.card?['あら、それ……私の絵はがき！ さっき、かばんから落としたのかねえ。','島を出た孫が送ってくれたの。今日は帰って来るから、迎えに来たんだよ。','見つけてくれて、ありがとうね。旅は急がず、寄り道も楽しんでいきなさい。']:['絵はがきが一枚、見当たらなくてねえ。孫からの大事な便りなんだけど。','さっきは、向こうのベンチのそばを歩いたんだよ。'],'grandma',()=>{if(state.card)mark('returned','絵はがきを届けた。「島のやさしさ」を手帳に記録')});
 if(id==='traveler')talk(s.name,['着いたね、沖縄。僕はまず、街でおいしいものを探そうかな。','あの水槽、ずっと眺めていられそう。予定を詰めすぎない旅も、いいよね。'],'traveler');
 if(id==='exit'){
  if(!state.introduced){talk('2階への案内',['「2F 連絡通路」。ゆいレールの駅へ続く案内が見える。','その前に、観光案内所で街への行き方を聞いておこう。']);return}
  if(!state.returned){talk('2階への案内',[state.card?'絵はがきは、まだポケットにある。出発する前に、持ち主へ届けたい。':'ロビーの床に、絵はがきが落ちている。誰かが探しているかもしれない。']);return}
  if(state.departed){talk('旅のつづきへ',['2階の連絡通路から、ゆいレールの那覇空港駅へ。','この候補版は、到着ロビーまで。手帳の思い出を眺めながら、もう少し寄り道していこう。']);return}
  talk('旅の第一歩',['案内を聞いて、ひとつの「ありがとう」に出会った。ロビーに降りた時より、島が少し身近に感じる。','さあ、2階の連絡通路へ。街の景色は、この先に待っている。'],'hero',()=>{mark('departed');$('#endSummary').textContent=state.fish?'旅の道しるべ / 沖縄の海 / 島のやさしさ':'旅の道しるべ / 島のやさしさ';open($('#ending'))})
 }
}
$('#explore').onclick=()=>$('#ending').close();
function journey(id){const s=spots.find(s=>s.id===id);if(!s)return;const next=route([hero.x,hero.y],s.at);if(next){path=next;pending=id;ring={x:s.at[0],y:s.at[1],t:1.5};if(!path.length){pending=null;interact(id)}}else toast('そこへは進めません。少し近くの床をタップしてください')}
function moveTo(x,y){if(blocked())return;const pos=nearestFloor(x,y);if(!pos){toast('人や設備をタップすると、近くまで歩きます');return}const next=route([hero.x,hero.y],pos);pending=null;if(next){path=next;ring={x:pos[0],y:pos[1],t:1.2}}}
$('#goal').onclick=()=>{if(blocked())return;const s=spots.find(s=>s.id===goalId(state));look={x:s.at[0],y:s.at[1],until:performance.now()+1800};ring={x:s.at[0],y:s.at[1],t:3};toast(`${s.name}の方を見ています`)};
$('#interact').onclick=()=>near&&interact(near.id);
function book(){const entries=[['introduced','旅の道しるべ','ゆいレールへは2階連絡通路から。案内係に教えてもらった。'],['fish','ひと足先に、沖縄の海','到着ロビーの水槽で、熱帯魚と静かなひととき。'],['returned','島のやさしさ','孫からの絵はがきを届けて、おばあと言葉を交わした。'],['departed','旅の第一歩','小さな思い出を胸に、次の景色へ。']];$('#entries').replaceChildren(...entries.map(([key,title,body])=>{const a=document.createElement('article'),b=document.createElement('strong'),p=document.createElement('p');b.className=state[key]?'done':'waiting';b.textContent=state[key]?title:'まだ見つけていない思い出';p.textContent=state[key]?body:'ロビーを歩いて、寄り道してみよう。';a.append(b,p);return a}));$('#book .note').innerHTML=`${saveOK?'記録はこのブラウザに保存されます。':'この環境では保存できません。現在の画面では続けて遊べます。'}<br>物語のために空間と人物を再構成しています。`;open($('#book'))}
$('#journalButton').onclick=book;$('#helpButton').onclick=()=>open($('#help'));
for(const b of document.querySelectorAll('.close'))b.onclick=()=>b.closest('dialog').close();
let resetArmed=false;$('#reset').onclick=()=>{if(!resetArmed){resetArmed=true;$('#reset').textContent='記録を消して最初から遊ぶ（もう一度押す）';return}state=defaults();hero.x=392;hero.y=248;hero.dir=0;save();update();resetArmed=false;$('#reset').textContent='この章を最初から遊ぶ';$('#book').close();toast('新しい旅をはじめました')};$('#book').addEventListener('close',()=>{resetArmed=false;$('#reset').textContent='この章を最初から遊ぶ'});
$('#play').disabled=true;$('#play').textContent='ロビーを準備しています…';
$('#play').onclick=()=>{if(!ready)return;started=true;$('#start').hidden=true;canvas.focus();toast(state.introduced?'おかえりなさい。旅の記録から続けます':'沖縄に到着。まずは右手の観光案内所へ');update()};
const dirs={ArrowUp:[0,-1,3],w:[0,-1,3],ArrowDown:[0,1,0],s:[0,1,0],ArrowLeft:[-1,0,1],a:[-1,0,1],ArrowRight:[1,0,2],d:[1,0,2]};
addEventListener('keydown',e=>{if(blocked())return;if(dirs[e.key]){e.preventDefault();keys.add(e.key);pending=null;if(!e.repeat)path=[]}else if(e.key==='Enter'||e.key===' '){e.preventDefault();near&&interact(near.id)}});
addEventListener('keyup',e=>keys.delete(e.key));addEventListener('blur',()=>{keys.clear();held=null;last=0});document.addEventListener('visibilitychange',()=>{keys.clear();held=null;last=0;if(document.hidden)audio?.suspend();else if(sound)audio?.resume()});
for(const b of document.querySelectorAll('#walkpad button')){
 const map={up:'ArrowUp',down:'ArrowDown',left:'ArrowLeft',right:'ArrowRight'};
 b.onpointerdown=e=>{e.preventDefault();if(blocked())return;b.setPointerCapture(e.pointerId);held=map[b.dataset.dir];pending=null;path=[]};b.onpointerup=b.onpointercancel=()=>{held=null};b.onlostpointercapture=()=>{held=null};
}
let pointer=null;canvas.onpointerdown=e=>{pointer={x:e.clientX,y:e.clientY,id:e.pointerId};canvas.setPointerCapture(e.pointerId)};canvas.onpointercancel=()=>pointer=null;
canvas.onpointerup=e=>{if(!pointer||pointer.id!==e.pointerId)return;const p=pointer;pointer=null;if(Math.hypot(e.clientX-p.x,e.clientY-p.y)>14||blocked())return;look=null;const box=canvas.getBoundingClientRect(),x=(e.clientX-box.left)*canvas.width/box.width+camera.x,y=(e.clientY-box.top)*canvas.height/box.height+camera.y;
 const hit=spots.filter(s=>s.id!=='postcard'||!state.card).map(s=>({s,dist:Math.hypot((x-s.x)*.9,y-(s.sprite?s.y-20:s.y))})).sort((a,b)=>a.dist-b.dist)[0];
 if(hit&&hit.dist<(hit.s.id==='aquarium'?89:hit.s.id==='exit'?53:hit.s.sprite?30:22)){journey(hit.s.id);return}
 // Counter frontage and entire tank are touch targets too.
 if(x>=512&&x<=720&&y>=150&&y<=320){journey('guide');return}
 moveTo(x,y)
};
function resize(){const b=canvas.getBoundingClientRect(),scale=b.width<600?1.5:1.5;canvas.width=Math.max(160,Math.round(b.width/scale));canvas.height=Math.max(120,Math.round(b.height/scale));ctx.imageSmoothingEnabled=false;clampCamera(true)}
function clampCamera(snap=false){const target=look&&look.until>performance.now()?look:hero,tx=canvas.width>WIDTH?(WIDTH-canvas.width)/2:Math.max(0,Math.min(WIDTH-canvas.width,target.x-canvas.width/2)),ty=Math.max(0,Math.min(HEIGHT-canvas.height,target.y-canvas.height*.48));camera.x=snap?tx:camera.x+(tx-camera.x)*.12;camera.y=snap?ty:camera.y+(ty-camera.y)*.12;camera.x=Math.max(Math.min(0,(WIDTH-canvas.width)/2),camera.x);camera.y=Math.max(0,camera.y)}
new ResizeObserver(resize).observe(canvas);
function step(dt,t){
 if(blocked()){moving=false;return}const dir=held||[...keys].at(-1);
 if(dir&&dirs[dir]&&!path.length){const [dx,dy,facing]=dirs[dir];hero.dir=facing;const [cx,cy]=cell(hero.x,hero.y);if(walkable(cx+dx,cy+dy))path=[[(cx+dx)*16+8,(cy+dy)*16+8]]}
 moving=path.length>0;
 if(moving){let remaining=dt*99;while(path.length&&remaining>0){const [x,y]=path[0],dx=x-hero.x,dy=y-hero.y,dist=Math.hypot(dx,dy);hero.dir=Math.abs(dx)>Math.abs(dy)?dx>0?2:1:dy>0?0:3;if(dist<=remaining){hero.x=x;hero.y=y;path.shift();remaining-=dist}else{hero.x+=dx/dist*remaining;hero.y+=dy/dist*remaining;remaining=0}}walking+=dt;if(t-lastStep>310){tone([[140,0,.035]],.012);lastStep=t}if(!path.length&&pending){const id=pending;pending=null;interact(id)}}else walking=0;
 near=spots.filter(s=>s.id!=='postcard'||!state.card).map(s=>({s,d:Math.hypot(hero.x-s.at[0],hero.y-s.at[1])})).filter(s=>s.d<37).sort((a,b)=>a.d-b.d)[0]?.s||null;
 $('#interact').hidden=!near;$('#interact').textContent=near?`${near.sprite?'話す':'調べる'}：${near.name}`:'';
}
function pill(x,y,text,color='#fff2cf'){
 ctx.font='8px sans-serif';const w=Math.ceil(ctx.measureText(text).width)+12;ctx.fillStyle='#254b56';ctx.fillRect(Math.round(x-w/2),Math.round(y-10),w,15);ctx.fillStyle=color;ctx.textAlign='center';ctx.fillText(text,Math.round(x),Math.round(y+1));ctx.textAlign='left';
}
function draw(t){
 ctx.fillStyle='#476b73';ctx.fillRect(0,0,canvas.width,canvas.height);if(!ready)return;
 clampCamera();const cx=Math.round(camera.x),cy=Math.round(camera.y);ctx.save();ctx.translate(-cx,-cy);ctx.drawImage(images.lobby,0,0);
 // Aquarium glints and bubbles are light effects over the finished raster master.
 if(!reduced)for(let i=0;i<5;i++){const x=89+i*31,y=243-((t*.012+i*15)%72);ctx.fillStyle='#b6ded255';ctx.fillRect(x,Math.round(y),1,2)}
 if(!state.card){ctx.drawImage(images.postcard,272,464);if(!reduced&&Math.floor(t/650)%2===0){ctx.fillStyle='#fff2cc';ctx.fillRect(291,459,1,7);ctx.fillRect(288,462,7,1)}}
 if(ring){ctx.strokeStyle='#f9edc6';ctx.lineWidth=1;ctx.beginPath();ctx.ellipse(Math.round(ring.x),Math.round(ring.y),9,4,0,0,Math.PI*2);ctx.stroke()}
 for(const actor of [...spots.filter(s=>s.sprite),{...hero,sprite:'hero'}].sort((a,b)=>a.y-b.y)){
  const x=Math.round(actor.x),y=Math.round(actor.y),frame=actor.sprite==='hero'&&moving?Math.floor(walking*9)%4:0;
  ctx.fillStyle='#304c4e44';ctx.beginPath();ctx.ellipse(x,y-1,12,4,0,0,Math.PI*2);ctx.fill();ctx.drawImage(images[actor.sprite],frame*32,(actor.dir||0)*48,32,48,x-16,y-46,32,48)
 }
 // Counter lip occludes the attendant's lower body at the correct depth.
 ctx.drawImage(images.lobby,512,253,200,60,512,253,200,60);
 pill(600,192,'観光案内');pill(360,416,'島のおばあ');pill(664,134,'2F 連絡通路');
 const goal=spots.find(s=>s.id===goalId(state));if(started&&!state.departed){const x=goal.at[0],y=goal.at[1]-16,dy=reduced?0:Math.round(Math.sin(t/240)*2);ctx.fillStyle='#ffe1a1';ctx.beginPath();ctx.moveTo(x-4,y-7+dy);ctx.lineTo(x+4,y-7+dy);ctx.lineTo(x,y-2+dy);ctx.fill()}
 ctx.restore();
 // Offscreen direction cue stays below the quest panel.
 if(started&&!state.departed&&!blocked()){
 const s=spots.find(s=>s.id===goalId(state)),x=s.at[0]-cx,y=s.at[1]-cy;
 if(x<12||y<60||x>canvas.width-12||y>canvas.height-24){const ex=Math.min(canvas.width-18,Math.max(18,x)),ey=Math.min(canvas.height-70,Math.max(68,y));ctx.fillStyle='#244752';ctx.fillRect(ex-9,ey-9,18,18);ctx.fillStyle='#ffe1a1';ctx.font='13px sans-serif';ctx.textAlign='center';ctx.fillText(Math.abs(x-canvas.width/2)>Math.abs(y-canvas.height/2)?x<0?'←':'→':y<0?'↑':'↓',ex,ey+4);ctx.textAlign='left'}
 }
}
function loop(t){const dt=last?Math.min((t-last)/1000,.04):0;last=t;if(ring&&(ring.t-=dt)<=0)ring=null;step(dt,t);draw(t);requestAnimationFrame(loop)}
async function load(){try{await Promise.all(['lobby','hero','guide','grandma','traveler','postcard'].map(name=>new Promise((resolve,reject)=>{const im=new Image;im.onload=()=>{images[name]=im;resolve()};im.onerror=reject;im.src=`assets/${name}.png`})));ready=true;$('#play').disabled=false;$('#play').innerHTML=`${state.introduced?'旅のつづきから':'旅をはじめる'} <span>→</span>`;resize();update()}catch{$('#loadError').hidden=false;$('#start').hidden=true}}
load();resize();requestAnimationFrame(loop);
if(new URLSearchParams(location.search).has('qa'))Object.defineProperty(window,'arrivalQA',{get:()=>({ready,started,hero:{...hero},camera:{...camera},state:{...state},pathLength:path.length,canvas:{width:canvas.width,height:canvas.height},near:near?.id,sound,audioState:audio?.state})});
