// Hand-authored stone silhouettes. Prototypes share geometry across the 32-piece set.
export function createSculptures(T, body, shadowStone) {
  const library = new Map();
  const add = (group, geo, mat = body, x = 0, y = 0, z = 0) => {
    const m = new T.Mesh(geo, mat); m.position.set(x,y,z);
    m.castShadow = m.receiveShadow = true; group.add(m); return m;
  };
  function turned(points, {flutes=0, depth=.014, segments=80}={}) {
    const curve = new T.SplineCurve(points.map(p=>new T.Vector2(...p)));
    const geo = new T.LatheGeometry(curve.getPoints(110),segments);
    const pos=geo.attributes.position;
    for(let i=0;i<pos.count;i++) {
      const x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i),r=Math.hypot(x,z),a=Math.atan2(x,z);
      if(r<.005)continue;
      const mask=T.MathUtils.smoothstep(y,.42,.66)*(1-T.MathUtils.smoothstep(y,1.3,1.56));
      const channel=flutes?depth*Math.pow((1+Math.cos(a*flutes))/2,3)*mask:0;
      // Continuous deterministic surface wear avoids UV seams and random geometry on reload.
      const wear=.0018*Math.sin(x*91+y*57)*Math.sin(z*83-y*63)+.002*Math.sin(a*13+y*39);
      const k=(r-channel+wear)/r;
      pos.setXYZ(i,x*k,y,z*k);
    }
    geo.computeVertexNormals();return geo;
  }
  const base = [[0,0],[.37,0],[.44,.025],[.465,.065],[.465,.12],[.44,.15],[.43,.2],[.385,.225],[.385,.25],[.435,.27],[.44,.305],[.42,.34],[.365,.37],[.345,.4],[.31,.47],[.275,.61],[.23,.86],[.20,1.12],[.20,1.32],[.245,1.47],[.31,1.53],[.325,1.57],[.32,1.615],[.25,1.655],[.19,1.68]];
  const ball=(g,r,y)=>add(g,new T.SphereGeometry(r,48,32),body,0,y);
  const ring=(g,r,y,t=.012)=>{const m=add(g,new T.TorusGeometry(r,t,8,64),body,0,y);m.rotation.x=Math.PI/2;return m;};
  function extrude(points,depth,bevel=.015) {
    const shape=new T.Shape();points.forEach(([x,y],i)=>i?shape.lineTo(x,y):shape.moveTo(x,y));shape.closePath();
    const geo=new T.ExtrudeGeometry(shape,{depth,bevelEnabled:true,bevelSize:bevel,bevelThickness:bevel,bevelSegments:3,curveSegments:8,steps:1});
    geo.translate(0,0,-depth/2);return geo;
  }
  function clippedHead(geometry,threshold,below) {
    const src=geometry.toNonIndexed(),a=src.attributes.position,n=src.attributes.normal,out=[],normals=[],cuts=[];
    const signed=v=>(v.x+v.y-threshold)*(below?1:-1);
    const emit=v=>{out.push(v.x,v.y,v.z);normals.push(v.normal.x,v.normal.y,v.normal.z);};
    for(let i=0;i<a.count;i+=3) {
      const poly=[0,1,2].map(j=>{const p=new T.Vector3().fromBufferAttribute(a,i+j);p.normal=new T.Vector3().fromBufferAttribute(n,i+j);return p;}),result=[];
      for(let j=0;j<3;j++) {
        const p=poly[j],q=poly[(j+1)%3],dp=signed(p),dq=signed(q);
        if(dp<=0)result.push(p);
        if((dp<=0)!==(dq<=0)) {const t=dp/(dp-dq),v=p.clone().lerp(q,t);v.normal=p.normal.clone().lerp(q.normal,t).normalize();result.push(v);cuts.push(v);}
      }
      for(let j=1;j<result.length-1;j++) [result[0],result[j],result[j+1]].forEach(emit);
    }
    if(cuts.length) {
      const c=cuts.reduce((sum,p)=>sum.add(p),new T.Vector3()).multiplyScalar(1/cuts.length);
      const normal=new T.Vector3(1,1,0).normalize().multiplyScalar(below?1:-1);
      c.normal=normal;
      cuts.sort((a,b)=>Math.atan2(a.z-c.z,(a.x-c.x)*Math.SQRT2)-Math.atan2(b.z-c.z,(b.x-c.x)*Math.SQRT2));
      for(let i=0;i<cuts.length;i++) {
        const p=cuts[i].clone(),q=cuts[(i+1)%cuts.length].clone();p.normal=q.normal=normal;
        const tri=below?[q,p,c]:[c,p,q];tri.forEach(emit);
      }
    }
    const result=new T.BufferGeometry();result.setAttribute('position',new T.Float32BufferAttribute(out,3));result.setAttribute('normal',new T.Float32BufferAttribute(normals,3));
    result.setAttribute('uv',new T.Float32BufferAttribute(new Float32Array(out.length/3*2),2));src.dispose();return result;
  }
  for(const type of ['king','queen','bishop','knight','rook','pawn']) {
    const g=new T.Group();
    if(type==='pawn') {
      add(g,turned(base.map(([r,y])=>[r*.77,y*.59]).concat([[.14,1.03],[0,1.06]]),{flutes:8,depth:.008}));
      ball(g,.258,1.275);ring(g,.17,1.007,.009);
    } else if(type==='rook') {
      const p=base.map(([r,y])=>[r,y*.78]);
      p.push([.255,1.4],[.325,1.48],[.35,1.52],[.35,1.67],[.29,1.69],[.27,1.6],[.27,1.49],[0,1.49]);
      add(g,turned(p,{flutes:10,depth:.026}));ring(g,.262,1.405,.012);
      const merlon = [[.265,1.60],[.345,1.60],[.35,1.63],[.35,1.94],[.34,1.955],[.285,1.955],[.265,1.94],[.265,1.60]];
      for(let i=0;i<6;i++) {
        const angle=i*Math.PI/3;
        add(g,new T.LatheGeometry(merlon.map(p=>new T.Vector2(...p)),12,angle,.68));
        const shape=extrude([[.265,1.6],[.345,1.6],[.35,1.94],[.285,1.955],[.265,1.94]],.001,.001);
        // Radial cut faces close the crenellations, including their visible interiors.
        for(const a of [angle,angle+.68]) {const cap=add(g,shape);cap.rotation.y=Math.PI/2-a;}
      }
      // A shallow carved waist line; same rough stone, with a darker recessed lip.
      const recess=add(g,new T.TorusGeometry(.242,.007,8,64),shadowStone,0,1.385);recess.rotation.x=Math.PI/2;
    } else if(type==='knight') {
      add(g,turned(base.map(([r,y])=>[r,y*.43]).concat([[.235,.76],[0,.77]]),{flutes:0}));
      const horse=new T.Group();g.add(horse);
      const outline=[[-.23,.69],[-.31,.92],[-.32,1.23],[-.26,1.47],[-.12,1.70],[.07,1.87],[.16,1.89],[.23,1.88],[.34,1.77],[.4,1.57],[.56,1.4],[.64,1.32],[.63,1.16],[.54,1.12],[.46,1.23],[.27,1.27],[.16,1.11],[.20,.90],[.3,.73]];
      add(horse,extrude(outline,.25,.055));
      for(const side of [-1,1]) {
        const cheek=add(horse,new T.SphereGeometry(.16,32,24),body,.07,1.43,side*.12);cheek.scale.set(.78,1.18,.6);
        const eye=add(horse,new T.SphereGeometry(.032,20,14),shadowStone,.26,1.68,side*.186);eye.scale.set(1,.62,.36);
        const brow=add(horse,new T.TorusGeometry(.043,.016,8,24,Math.PI),body,.26,1.705,side*.184);brow.rotation.z=.14;
        const nostril=add(horse,new T.SphereGeometry(.023,16,12),shadowStone,.535,1.35,side*.17);nostril.scale.set(1,.62,.34);
        // A second ear and a carved mane make the piece legible away from its side profile.
        add(horse,extrude([[.065,1.85],[.055,2.04],[.12,2.1],[.19,1.87]],.025,.015),body,0,0,side*.1);
      }
      for(let i=0;i<7;i++) {
        const t=i/6, rib=add(horse,new T.CapsuleGeometry(.014,.16,4,8),body,-.334+t*.15,1.18+t*.54,-.0);
        rib.rotation.x=Math.PI/2;rib.rotation.z=-.3;
      }
      horse.rotation.y=Math.PI/2;
    } else {
      add(g,turned(base,{flutes:type==='king'?16:type==='queen'?12:10,depth:type==='king'?.022:.017}));
      ring(g,.276,1.50,.009);
      if(type==='king') {
        add(g,turned([[.18,1.66],[.23,1.76],[.27,1.92],[.25,2.08],[.18,2.24],[.135,2.3],[.125,2.38],[0,2.39]],{segments:72}));
        ring(g,.13,2.345,.01);
        const cross=[[-.067,0],[.067,0],[.067,.17],[.19,.17],[.21,.19],[.21,.29],[.19,.31],[.067,.31],[.067,.46],[-.067,.46],[-.067,.31],[-.19,.31],[-.21,.29],[-.21,.19],[-.19,.17],[-.067,.17]];
        add(g,extrude(cross,.125,.018),body,0,2.37);
        // Recessed lozenge on each face of the cross, like a small stone mason's cut.
        for(const z of [-.085,.085])add(g,extrude([[0,-.034],[.025,0],[0,.034],[-.025,0]],.001,.001),shadowStone,0,2.61,z);
      } else if(type==='queen') {
        add(g,turned([[.18,1.66],[.19,1.75],[.24,1.86],[.32,2.06],[.33,2.11],[.275,2.12],[.23,1.94],[.12,1.82],[0,1.81]]));
        // Six rising crown leaves, with rounded edges and open spaces between them.
        for(let i=0;i<6;i++) {
          const leaf=add(g,extrude([[-.085,0],[.085,0],[.067,.17],[0,.34],[-.067,.17]],.066,.016),body,Math.sin(i*Math.PI/3)*.30,2.01,Math.cos(i*Math.PI/3)*.30);
          leaf.rotation.y=i*Math.PI/3;
        }
        ball(g,.085,2.03);ring(g,.30,2.052,.012);
      } else if(type==='bishop') {
        const h=turned([[0,1.67],[.15,1.68],[.235,1.78],[.27,1.94],[.22,2.105],[.14,2.30],[.035,2.44],[0,2.455]]);
        add(g,clippedHead(h,2.16,true));add(g,clippedHead(h,2.245,false));h.dispose();
        ball(g,.048,2.475);
      }
    }
    g.scale.setScalar(.80);
    library.set(type,g);
  }
  return library;
}
