// Files run a→h from White's left; rank 1 is nearest White.
export const backRank = ['rook','knight','bishop','queen','king','bishop','knight','rook'];
export const squareColor = (file,rank) => (file+rank)%2===1?'light':'dark';
export const startingPosition = Array.from({length:8},(_,file)=>[
  {type:backRank[file],color:'light',file,rank:0},
  {type:'pawn',color:'light',file,rank:1},
  {type:'pawn',color:'dark',file,rank:6},
  {type:backRank[file],color:'dark',file,rank:7},
]).flat().map(p=>({...p,square:`${'abcdefgh'[p.file]}${p.rank+1}`}));
