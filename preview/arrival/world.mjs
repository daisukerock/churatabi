export const TILE=16, WIDTH=768, HEIGHT=640;
export const fixtures=[
 [0,0,768,120],[0,0,16,640],[752,0,16,640],[0,616,768,24],
 [64,150,192,162],[512,150,208,170],[608,16,128,112],
 [16,152,48,64],[704,176,48,64],[16,400,48,64],[704,512,48,64],
 [80,400,144,40],[480,432,144,40],[80,560,144,40],[480,576,144,32],
 [688,312,48,96],[272,144,32,48],[272,528,32,48],[24,264,32,72],
];
export const spots=[
 {id:'guide',name:'案内係・みな',x:600,y:248,at:[600,344],sprite:'guide',dir:0},
 {id:'aquarium',name:'沖縄の海の水槽',x:168,y:224,at:[168,344]},
 {id:'grandma',name:'島のおばあ',x:360,y:472,at:[360,504],sprite:'grandma',dir:0},
 {id:'traveler',name:'旅人・はる',x:472,y:200,at:[472,232],sprite:'traveler',dir:1},
 {id:'postcard',name:'落とし物の絵はがき',x:280,y:472,at:[280,488]},
 {id:'exit',name:'2階・連絡通路へ',x:664,y:100,at:[664,136]},
];
export const cell=(x,y)=>[Math.floor(x/16),Math.floor(y/16)];
export function walkable(x,y){
 if(x<0||y<0||x>=WIDTH/16||y>=HEIGHT/16)return false;
 const px=x*16+8,py=y*16+8;
 if(fixtures.some(([a,b,w,h])=>px>=a&&px<a+w&&py>=b&&py<b+h))return false;
 return !spots.some(s=>s.sprite&&Math.abs(s.x-px)<12&&Math.abs(s.y-py)<12);
}
export function route(start,end){
 const [sx,sy]=cell(...start),[ex,ey]=cell(...end);
 if(!walkable(ex,ey))return null;
 const key=(x,y)=>y*48+x,origin=key(sx,sy),goal=key(ex,ey),queue=[[sx,sy]],seen=new Map([[origin,null]]);
 for(let i=0;i<queue.length;i++){
  const [x,y]=queue[i],k=key(x,y);if(k===goal){let out=[],c=k;while(c!==origin){out.push([c%48*16+8,Math.floor(c/48)*16+8]);c=seen.get(c)}return out.reverse()}
  for(const [dx,dy] of [[0,1],[1,0],[0,-1],[-1,0]]){const a=x+dx,b=y+dy,n=key(a,b);if(walkable(a,b)&&!seen.has(n)){seen.set(n,k);queue.push([a,b])}}
 }
 return null;
}
export function nearestFloor(x,y){
 const [cx,cy]=cell(x,y);let options=[];
 for(let b=-2;b<=2;b++)for(let a=-2;a<=2;a++)if(walkable(cx+a,cy+b))options.push([(cx+a)*16+8,(cy+b)*16+8]);
 return options.sort((a,b)=>Math.hypot(a[0]-x,a[1]-y)-Math.hypot(b[0]-x,b[1]-y))[0]||null;
}
export const defaults=()=>({introduced:false,fish:false,card:false,returned:false,departed:false});
export function objective(s){return !s.introduced?'案内係に話しかける':!s.card?'床の絵はがきを調べる':!s.returned?'絵はがきをおばあに届ける':!s.departed?'2階への案内を確かめる':'到着ロビーの旅、達成'}
export function goalId(s){return !s.introduced?'guide':!s.card?'postcard':!s.returned?'grandma':'exit'}
