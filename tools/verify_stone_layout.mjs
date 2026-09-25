import assert from 'node:assert/strict';
import { startingPosition, squareColor } from '../js/stone-layout-v2.js';
const code={rook:'r',knight:'n',bishop:'b',queen:'q',king:'k',pawn:'p'};
const rows=[];
for(let rank=7;rank>=0;rank--){
  let row='',empty=0;
  for(let file=0;file<8;file++){
    const p=startingPosition.find(p=>p.file===file&&p.rank===rank);
    if(!p){empty++;continue;}
    if(empty){row+=empty;empty=0;}
    row+=p.color==='light'?code[p.type].toUpperCase():code[p.type];
  }
  if(empty)row+=empty;
  rows.push(row);
}
assert.equal(rows.join('/'),'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR');
assert.equal(new Set(startingPosition.map(p=>p.square)).size,32);
for(const color of ['light','dark']){
  assert.equal(startingPosition.filter(p=>p.color===color).length,16);
  const q=startingPosition.find(p=>p.color===color&&p.type==='queen');
  assert.equal(squareColor(q.file,q.rank),color);
}
assert.equal(squareColor(0,0),'dark');
assert.equal(squareColor(7,0),'light');
console.log('Standard chess position, piece counts, unique squares, and board orientation verified.');
