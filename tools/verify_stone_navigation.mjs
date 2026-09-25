import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { startingPosition } from '../js/stone-layout-v2.js';
import { destinations, moveFor, motionAt } from '../js/stone-navigation.js';
const occupied=new Set(startingPosition.map(p=>`${p.file}:${p.rank}`));
for(const piece of startingPosition){
  const move=moveFor(piece);
  assert.ok(move.file>=0&&move.file<8&&move.rank>=0&&move.rank<8,`${piece.square}: landing must stay on the board`);
  assert.ok(!occupied.has(`${move.file}:${move.rank}`),`${piece.square}: landing must be empty`);
  assert.ok(existsSync(new URL(`../${destinations[piece.type]}`,import.meta.url)),'Category page exists');
  const start=motionAt(0,move.knight),end=motionAt(1,move.knight);
  assert.equal(start.x,0);assert.equal(start.z,0);assert.equal(start.lift,0);assert.equal(start.fade,0);
  assert.equal(end.x,1);assert.equal(end.z,1);assert.equal(end.lift,0);assert.equal(end.camera,1);assert.equal(end.fade,1);assert.equal(end.done,true);
  let camera=0,fade=0;
  for(let i=0;i<=100;i++){
    const state=motionAt(i/100,move.knight);
    assert.ok(state.camera>=camera&&state.fade>=fade);
    for(const key of ['x','z','lift','camera','fade'])assert.ok(state[key]>=0&&state[key]<=1);
    camera=state.camera;fade=state.fade;
  }
}
assert.ok(motionAt(.3,true).z>motionAt(.3,true).x,'Knight first travels the long leg of its L');
assert.equal(motionAt(.86).fade,0,'Keep the stone visible until the zoom finishes');
const page=readFileSync(new URL('../index.html',import.meta.url),'utf8');
for(const [piece,href] of Object.entries(destinations))assert.ok(page.includes(`data-piece="${piece}" href="${href}"`));
const old=readFileSync(new URL('../index-hero-original.html',import.meta.url),'utf8');
assert.ok(old.includes('js/hero-board.js?v=13')&&old.includes('css/hero-board.css?v=4'));
assert.ok(page.includes('js/home-stone-board.js?v=1'));
console.log('All 32 navigation paths land on empty board squares; motion, category destinations, and original version verified.');
