/* Two intentionally separate material studies. Real meshes, photographic texture maps,
   no idle animation. Category navigation stays available without WebGL or JavaScript. */
const stage = document.querySelector('#materialStage');
const canvas = stage.querySelector('canvas');
const kind = document.body.dataset.material;
const wood = kind === 'wood';
const categories = { king: 'Men', queen: 'Women', pawn: 'Kids', bishop: 'Accessories', rook: 'Shoes' };
const links = [...document.querySelectorAll('.category')];
const tip = stage.querySelector('.tip');
const inspectButton = document.querySelector('#inspectButton');
const inspection = document.querySelector('#inspection');
const inspectSelect = document.querySelector('#inspectPiece');
let renderRequested = false;

try {
  const T = await import('./vendor/three-0.159.module.min.js');
  const renderer = new T.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setClearColor(0xf1eee7);
  renderer.outputColorSpace = T.SRGBColorSpace;
  renderer.toneMapping = T.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.08;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = T.VSMShadowMap;
  const scene = new T.Scene();
  scene.background = new T.Color(0xf1eee7);
  const camera = new T.PerspectiveCamera(31, 1, .05, 100);
  const assembly = new T.Group();
  scene.add(assembly);
  const meshes = [];
  const pieces = new Map();

  // Broad, restrained studio illumination. Non-metallic materials have no clearcoat.
  scene.add(new T.HemisphereLight(0xfff7e6, 0xbeb8ab, 2.1));
  const key = new T.DirectionalLight(0xfff8eb, 2.7);
  key.position.set(-5, 9, 7);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  Object.assign(key.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8, near: .1, far: 30 });
  key.shadow.normalBias = .014;
  key.shadow.bias = -.00015;
  key.shadow.radius = 10;
  key.shadow.blurSamples = 16;
  scene.add(key);
  const fill = new T.DirectionalLight(0xe4edff, .65);
  fill.position.set(5, 4, -5);
  scene.add(fill);

  const textureLoader = new T.TextureLoader();
  const surface = await textureLoader.loadAsync(`assets/img/material-studies/${wood ? 'walnut' : 'travertine'}.jpg`);
  surface.colorSpace = T.SRGBColorSpace;
  surface.wrapS = surface.wrapT = T.RepeatWrapping;
  surface.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  const relief = surface.clone();
  relief.colorSpace = T.NoColorSpace;
  relief.needsUpdate = true;

  // World-space triplanar projection keeps grain running through the whole carving,
  // instead of stretching a small UV image over collars, crowns, and cross cuts.
  function material(color, scale = .7, isWood = wood) {
    const m = new T.MeshStandardMaterial({ color, map: surface, bumpMap: relief,
      bumpScale: isWood ? .035 : .055, roughness: isWood ? .78 : .88, metalness: 0 });
    m.onBeforeCompile = shader => {
      shader.uniforms.grainScale = { value: scale };
      shader.vertexShader = 'varying vec3 grainPos; varying vec3 grainNormal;\n' + shader.vertexShader;
      shader.vertexShader = shader.vertexShader.replace('#include <worldpos_vertex>', `#include <worldpos_vertex>
        grainPos = (modelMatrix * vec4(transformed, 1.0)).xyz;
        grainNormal = normalize(mat3(modelMatrix) * objectNormal);`);
      shader.fragmentShader = `varying vec3 grainPos; varying vec3 grainNormal; uniform float grainScale;
        vec4 grainSample(sampler2D tex, vec3 p) {
          vec3 w = pow(abs(normalize(grainNormal)), vec3(6.0)); w /= max(w.x + w.y + w.z, 0.001);
          p *= grainScale;
          return texture2D(tex,p.zy)*w.x + texture2D(tex,p.xz)*w.y + texture2D(tex,p.xy)*w.z;
        }\n` + shader.fragmentShader;
      shader.fragmentShader = shader.fragmentShader.replace('#include <map_fragment>',
        'diffuseColor *= grainSample(map, grainPos);');
      const bump = T.ShaderChunk.bumpmap_pars_fragment.replace(/vec2 dHdxy_fwd\(\) \{[\s\S]*?\n\t\}/,
        `vec2 dHdxy_fwd() {
          float h = grainSample(bumpMap,grainPos).r;
          float hx = grainSample(bumpMap,grainPos+dFdx(grainPos)).r;
          float hy = grainSample(bumpMap,grainPos+dFdy(grainPos)).r;
          return bumpScale * vec2(hx-h,hy-h);
        }`);
      shader.fragmentShader = shader.fragmentShader.replace('#include <bumpmap_pars_fragment>', bump);
      shader.fragmentShader = shader.fragmentShader.replace('#include <roughnessmap_fragment>',
        'float roughnessFactor = clamp(roughness + (0.5-grainSample(map,grainPos).r)*0.16, 0.65, 0.98);');
    };
    m.customProgramCacheKey = () => 'material-study-triplanar-v1';
    return m;
  }

  const floor = new T.Mesh(new T.PlaneGeometry(200, 200), new T.ShadowMaterial({ color: 0x62584b, opacity: .15 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -.25;
  floor.receiveShadow = true;
  scene.add(floor);

  function mesh(geometry, mat, parent, x = 0, y = 0, z = 0) {
    const m = new T.Mesh(geometry, mat);
    m.position.set(x, y, z);
    m.castShadow = m.receiveShadow = true;
    parent.add(m);
    return m;
  }
  function profile(points, segments = 96, smooth = false) {
    const p = points.map(([r, y]) => new T.Vector2(r, y));
    return new T.LatheGeometry(smooth ? new T.SplineCurve(p).getPoints(150) : p, segments);
  }
  function roundedBox(w, h, d, radius) {
    const s = new T.Shape(), x = -w / 2, y = -h / 2, r = radius;
    s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
    s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
    s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
    const g = new T.ExtrudeGeometry(s, { depth: d - 2 * r, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: r, bevelThickness: r, curveSegments: 4 });
    g.translate(0, 0, -d / 2 + r); return g;
  }

  // A real 8×8 board, with low satin contrast instead of mirror-like squares.
  const boardLight = material(wood ? 0xc3a986 : 0xfff9eb, .6);
  const boardDark = material(wood ? 0x38322b : 0x343535, .6);
  const edgeMat = material(wood ? 0x5c4e3d : 0xd4cbbb, .62);
  const board = mesh(roundedBox(9.0, 9.0, .22, .04), edgeMat, assembly, 0, -.12, -.8);
  board.rotation.x = -Math.PI / 2;
  const square = new T.BoxGeometry(1.04, .035, 1.04);
  for (let row = 0; row < 8; row++) for (let col = 0; col < 8; col++) {
    mesh(square, (row + col) % 2 ? boardLight : boardDark, assembly, (col - 3.5) * 1.04, .0175, (row - 3.5) * 1.04 - .8);
  }
  const top = .038;
  const felt = new T.MeshStandardMaterial({ color: 0x31372d, roughness: 1 });
  const woodFoot = [[0,0],[.42,0],[.45,.055],[.46,.17],[.43,.28],[.32,.52],[.23,.75],[.16,1.12],[.17,1.36],[.23,1.5],[.31,1.57],[.33,1.62],[.32,1.67],[.24,1.7]];
  const stoneFoot = [[0,0],[.43,0],[.49,.035],[.5,.09],[.48,.16],[.43,.2],[.43,.23],[.49,.25],[.49,.29],[.45,.32],[.39,.34],[.39,.38],[.42,.41],[.41,.45],[.34,.49],[.29,.57],[.24,.76],[.19,1.03],[.18,1.22],[.2,1.4],[.29,1.5],[.32,1.53],[.34,1.58],[.33,1.63],[.28,1.67],[.2,1.7]];

  // Polygon clipping gives the bishop a genuine diagonal cut, including its cut faces.
  function clippedHead(geometry, threshold, keepBelow) {
    const src = geometry.toNonIndexed(), a = src.attributes.position, out = [], cuts = [];
    const signed = v => (v.x + v.y - threshold) * (keepBelow ? 1 : -1);
    for (let i = 0; i < a.count; i += 3) {
      const poly = [0,1,2].map(j => new T.Vector3().fromBufferAttribute(a, i+j));
      const clipped = [];
      for (let j=0;j<3;j++) {
        const p=poly[j],q=poly[(j+1)%3],dp=signed(p),dq=signed(q);
        if(dp<=0) clipped.push(p);
        if((dp<=0)!==(dq<=0)) { const v=p.clone().lerp(q,dp/(dp-dq)); clipped.push(v); cuts.push(v); }
      }
      for(let j=1;j<clipped.length-1;j++) [clipped[0],clipped[j],clipped[j+1]].forEach(v=>out.push(v.x,v.y,v.z));
    }
    if(cuts.length) {
      const c=cuts.reduce((sum,p)=>sum.add(p),new T.Vector3()).multiplyScalar(1/cuts.length);
      const sorted=cuts.sort((a,b)=>Math.atan2(a.z-c.z,(a.x-c.x)*Math.SQRT2)-Math.atan2(b.z-c.z,(b.x-c.x)*Math.SQRT2));
      for(let i=0;i<sorted.length;i++) {
        const tri=[c,sorted[i],sorted[(i+1)%sorted.length]];
        if(keepBelow) tri.reverse(); tri.forEach(p=>out.push(p.x,p.y,p.z));
      }
    }
    const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(out,3));
    g.setAttribute('uv',new T.Float32BufferAttribute(new Float32Array(out.length/3*2),2));g.computeVertexNormals();
    src.dispose();return g;
  }

  function makePiece(type, i) {
    const group = new T.Group();
    const body = material(wood ? [0xc8c3b9,0xf1e7d7,0xdfd8cd,0xbcb9b2,0xcfc7b7][i] : [0xfff8e5,0xe8decc,0xfff9ed,0xe6dac5,0xf7edd9][i], wood ? .73 : .9);
    const facetMat = body.clone(); facetMat.onBeforeCompile = body.onBeforeCompile; facetMat.customProgramCacheKey = body.customProgramCacheKey;
    facetMat.flatShading = wood;
    const lathe = (p, faceted = false) => mesh(profile(p, faceted ? 10 : 96, !faceted), faceted ? facetMat : body, group);
    const ball = (r,y) => mesh(new T.SphereGeometry(r,64,48),body,group,0,y,0);
    const feltRadius=type==='pawn'?.33:.4;
    mesh(new T.CylinderGeometry(feltRadius,feltRadius,.012,64),felt,group,0,.006,0);
    const foot = (wood ? woodFoot : stoneFoot).map(p=>[...p]);
    if (type === 'pawn') {
      const p = foot.map(([r,y])=>[r*.83,y*.68]);
      p.push([.14,1.21],[0,1.22]); lathe(p,wood); ball(.29,1.48);
    } else if (type === 'rook') {
      lathe(foot.map(([r,y])=>[r,y*.76]).concat([[.29,1.34],[.35,1.39],[.37,1.47],[.37,1.64],[.29,1.67],[.29,1.51],[0,1.51]]),wood);
      for(let j=0;j<6;j++) {
        const g = new T.LatheGeometry([[.29,1.58],[.37,1.58],[.37,1.9],[.29,1.9],[.29,1.58]].map(p=>new T.Vector2(...p)),wood?3:12,j*Math.PI/3,.62);
        mesh(g,body,group);
        // Seal both vertical sides of each merlon, so the crown is solid from any angle.
        for(const a of [j*Math.PI/3,j*Math.PI/3+.62]) {
          const cap=mesh(new T.PlaneGeometry(.08,.32),body,group,Math.sin(a)*.33,1.74,Math.cos(a)*.33);
          cap.rotation.y=a-Math.PI/2;cap.material=body;body.side=T.DoubleSide;
        }
      }
    } else {
      lathe(foot,wood);
      if (type === 'king') {
        lathe([[.2,1.68],[.25,1.8],[.32,2.01],[.3,2.16],[.19,2.37],[.13,2.43],[.13,2.49],[0,2.49]],wood);
        const s = new T.Shape();
        const points=[[-.065,0],[.065,0],[.065,.18],[.2,.18],[.2,.3],[.065,.3],[.065,.45],[-.065,.45],[-.065,.3],[-.2,.3],[-.2,.18],[-.065,.18]];
        points.forEach(([x,y],n)=>n?s.lineTo(x,y):s.moveTo(x,y));s.closePath();
        const cross = new T.ExtrudeGeometry(s,{depth:.12,bevelEnabled:true,bevelSize:.016,bevelThickness:.016,bevelSegments:3,steps:1});
        mesh(cross,body,group,0,2.46,-.06);
      } else if (type === 'queen') {
        if (wood) {
          lathe([[.18,1.67],[.3,1.83],[.38,2.1],[.24,2.32],[.07,2.54],[0,2.56]],true);
          ball(.105,2.64);
        } else {
          lathe([[.19,1.67],[.21,1.78],[.28,1.94],[.36,2.13],[.37,2.19],[.3,2.2],[.26,2.06],[.13,1.95],[0,1.94]]);
          for(let j=0;j<8;j++) {
            const a=j*Math.PI/4;
            mesh(new T.SphereGeometry(.064,24,18),body,group,Math.sin(a)*.337,2.25,Math.cos(a)*.337);
          }
          ball(.11,2.14);
        }
      } else if (type === 'bishop') {
        const head=profile([[0,1.67],[.17,1.69],[.26,1.78],[.29,1.94],[.22,2.12],[.13,2.31],[.02,2.44],[0,2.45]],wood?10:96,!wood);
        mesh(clippedHead(head,2.22,true),wood?facetMat:body,group);
        mesh(clippedHead(head,2.30,false),wood?facetMat:body,group);
        head.dispose();ball(.055,2.47);
      }
    }
    const x = (i-2)*1.62;
    group.position.set(x,top,[.1,-.22,.55,-.07,.2][i]);
    group.rotation.y=[-.12,.14,.18,-.2,.1][i];
    group.userData = {type};
    group.traverse(o=>{if(o.isMesh) {o.userData.type=type;meshes.push(o);}});
    assembly.add(group);pieces.set(type,group);
    const bbox=new T.Box3().setFromObject(group);
    group.userData.height=bbox.max.y-top;
    // Subtle contact occlusion, layered under real cast shadows; never a mirror clone.
    const c=document.createElement('canvas');c.width=c.height=64;
    const ctx=c.getContext('2d'),g=ctx.createRadialGradient(32,32,2,32,32,32);
    g.addColorStop(0,'rgba(35,29,21,.38)');g.addColorStop(.48,'rgba(35,29,21,.16)');g.addColorStop(1,'rgba(35,29,21,0)');
    ctx.fillStyle=g;ctx.fillRect(0,0,64,64);
    const shadow=mesh(new T.PlaneGeometry(1.32,1.32),new T.MeshBasicMaterial({map:new T.CanvasTexture(c),transparent:true,depthWrite:false}),assembly,x,top+.001,group.position.z);
    shadow.rotation.x=-Math.PI/2;shadow.castShadow=false;group.userData.contact=shadow;
  }
  Object.keys(categories).forEach(makePiece);

  let yaw=0, pitch=.27, zoom=1, inspecting=false, hovered=null;
  const raycaster=new T.Raycaster();
  const pointer=new T.Vector2();
  const target=new T.Vector3();
  function fit() {
    const w=canvas.clientWidth,h=canvas.clientHeight;
    renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();requestRender();
  }
  function positionCamera() {
    const aspect=camera.aspect;
    if(inspecting) {
      const p=pieces.get(inspectSelect.value);
      target.copy(p.position);target.y+=p.userData.height*.55;
      const d=6.5*Math.max(1,.82/aspect)/zoom;
      camera.position.set(target.x+Math.sin(yaw)*d*Math.cos(pitch),target.y+Math.sin(pitch)*d,target.z+Math.cos(yaw)*d*Math.cos(pitch));
    } else {
      target.set(0,1.02,-.2);
      const d=Math.max(10.4,5.1/(Math.tan(T.MathUtils.degToRad(camera.fov/2))*aspect))/zoom;
      camera.position.set(Math.sin(yaw)*d*Math.cos(pitch),target.y+Math.sin(pitch)*d,Math.cos(yaw)*d*Math.cos(pitch)+target.z);
    }
    camera.lookAt(target);camera.updateMatrixWorld();
  }
  function render() {renderRequested=false;positionCamera();renderer.render(scene,camera);}
  function requestRender() {if(!renderRequested) {renderRequested=true;requestAnimationFrame(render);}}
  function pick(e) {
    const r=canvas.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);
    raycaster.setFromCamera(pointer,camera);
    return raycaster.intersectObjects(meshes.filter(m=>pieces.get(m.userData.type).visible),false)[0]?.object.userData.type || null;
  }
  function highlight(type,e) {
    hovered=type;
    links.forEach(l=>l.classList.toggle('active',l.dataset.piece===type));
    canvas.style.cursor=type?'pointer':'grab';
    tip.classList.toggle('visible',!!type&&!!e);
    if(type&&e) {
      const r=stage.getBoundingClientRect();
      tip.textContent=`${type[0].toUpperCase()+type.slice(1)} / ${categories[type]}${type==='queen'?' · Coming soon':''} ↗`;
      tip.style.left=`${Math.max(95,Math.min(r.width-100,e.clientX-r.left))}px`;
      tip.style.top=`${Math.max(45,e.clientY-r.top-18)}px`;
    }
  }
  let down=null;
  canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;down={x:e.clientX,y:e.clientY,yaw,pitch,moved:false};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{
    if(down) {
      const dx=e.clientX-down.x,dy=e.clientY-down.y;
      if(Math.hypot(dx,dy)>6)down.moved=true;
      if(down.moved) {yaw=down.yaw-dx*.005;pitch=T.MathUtils.clamp(down.pitch+dy*.003,.1,.8);highlight(null);requestRender();}
    } else if(e.pointerType!=='touch')highlight(pick(e),e);
  });
  canvas.addEventListener('pointerup',e=>{
    if(!down)return;const clicked=!down.moved;down=null;
    if(canvas.hasPointerCapture(e.pointerId))canvas.releasePointerCapture(e.pointerId);
    if(clicked) {const type=pick(e);if(type) {const url=`${type}.html`;if(e.ctrlKey||e.metaKey)window.open(url,'_blank','noopener');else location.href=url;}}
  });
  canvas.addEventListener('pointercancel',()=>{down=null;highlight(null);});
  canvas.addEventListener('pointerleave',()=>{if(!down)highlight(null);});
  links.forEach(l=>{l.addEventListener('mouseenter',()=>highlight(l.dataset.piece));l.addEventListener('mouseleave',()=>highlight(null));l.addEventListener('focus',()=>highlight(l.dataset.piece));l.addEventListener('blur',()=>highlight(null));});
  function reset() {yaw=0;pitch=.27;zoom=1;highlight(null);requestRender();}
  function zoomBy(factor) {zoom=T.MathUtils.clamp(zoom*factor,.75,1.8);requestRender();}
  document.querySelectorAll('[data-action]').forEach(b=>b.addEventListener('click',()=>b.dataset.action==='reset'?reset():zoomBy(b.dataset.action==='in'?1.13:1/1.13)));
  canvas.addEventListener('keydown',e=>{
    if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','Home'].includes(e.key))e.preventDefault();else return;
    if(e.key==='ArrowLeft')yaw-=.12;if(e.key==='ArrowRight')yaw+=.12;
    if(e.key==='ArrowUp')pitch=Math.min(.8,pitch+.06);if(e.key==='ArrowDown')pitch=Math.max(.1,pitch-.06);
    if(e.key==='+'||e.key==='=')zoomBy(1.13);if(e.key==='-')zoomBy(1/1.13);if(e.key==='Home')reset();requestRender();
  });
  function showInspection() {
    stage.classList.toggle('is-inspecting',inspecting);
    for(const [type,piece] of pieces) {piece.visible=!inspecting||type===inspectSelect.value;piece.userData.contact.visible=piece.visible;}
    fit();
  }
  inspectButton.addEventListener('click',()=>{
    inspecting=!inspecting;inspection.hidden=!inspecting;inspectButton.setAttribute('aria-expanded',String(inspecting));
    inspectButton.textContent=inspecting?'Back to the board ↙':'Closer look ↗';showInspection();reset();
  });
  inspectSelect.addEventListener('change',()=>{
    const type=inspectSelect.value;document.querySelector('#inspectLink').href=`${type}.html`;
    document.querySelector('#inspectLink').textContent=`Explore ${categories[type]}${type==='queen'?' · Coming soon':''} ↗`;showInspection();reset();
  });
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();stage.classList.add('fallback');});
  canvas.addEventListener('webglcontextrestored',()=>location.reload());
  new ResizeObserver(fit).observe(stage);fit();
  stage.classList.add('ready');
  // Read-only diagnostics support click-target and framing checks without changing navigation.
  window.materialStudy = {get material(){return kind;},get pieceCount(){return pieces.size;},
    targets(){positionCamera();return [...pieces].map(([type,g])=>{
      const p=g.position.clone();p.y+=g.userData.height*.56;p.project(camera);
      return {type,x:(p.x+1)*canvas.clientWidth/2,y:(1-p.y)*canvas.clientHeight/2,href:`${type}.html`};
    });}};
} catch(error) {
  stage.classList.add('fallback');
  console.error('Material study:',error);
}
