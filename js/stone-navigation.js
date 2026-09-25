// Navigation choreography, not a playable chess game. Landing squares are empty.
export const destinations={king:'king.html',queen:'queen.html',pawn:'pawn.html',bishop:'bishop.html',rook:'rook.html',knight:'book-a-fitting.html'};
export const categories={king:'Men',queen:'Women',pawn:'Kids',bishop:'Accessories',rook:'Shoes',knight:'Book a fitting'};
const clamp=v=>Math.min(1,Math.max(0,v));
const smooth=v=>{const t=clamp(v);return t*t*(3-2*t);};
export function moveFor({type,color,file,rank}) {
  const forward=color==='light'?1:-1,inward=file<4?1:-1;
  let df=0,dr=3;
  if(type==='pawn'||type==='king')dr=2;
  if(type==='bishop'||type==='queen')df=inward*3;
  if(type==='knight'){df=inward;dr=2;}
  return {file:file+df,rank:rank+forward*dr,lift:type==='pawn'?.15:1.48,knight:type==='knight'};
}
export function motionAt(progress,knight=false) {
  const t=clamp(progress),travel=smooth((t-.12)/.45);
  return {
    x:knight?smooth((t-.34)/.23):travel,
    z:knight?smooth((t-.12)/.26):travel,
    lift:smooth(t/.16)*(1-smooth((t-.52)/.17)),
    camera:smooth((t-.24)/.72),
    fade:smooth((t-.87)/.13),
    done:t===1,
  };
}
