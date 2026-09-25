// Preserved independently of the original study. No idle motion; genuine 32-piece layout.
import { createSculptures } from './stone-sculptures-v2.js?v=1';
import { startingPosition, squareColor } from './stone-layout-v2.js?v=1';
const stage=document.querySelector('#materialStage'),canvas=stage.querySelector('canvas');
const links=[...document.querySelectorAll('.category')],tip=stage.querySelector('.tip');
const inspectButton=document.querySelector('#inspectButton'),inspection=document.querySelector('#inspection');
const inspectSelect=document.querySelector('#inspectPiece'),colorSelect=document.querySelector('#inspectColor');
const overheadButton=document.querySelector('#overheadButton');
const categories={king:'Men',queen:'Women',pawn:'Kids',bishop:'Accessories',rook:'Shoes',knight:'Book a fitting'};
const destinations={king:'king.html',queen:'queen.html',pawn:'pawn.html',bishop:'bishop.html',rook:'rook.html',knight:'book-a-fitting.html'};
const details={king:'Sixteen carved flutes. A stepped collar. A weathered cross with a recessed mason’s mark.',queen:'An open, six-leaf crown above a gently fluted stem. Soft edges and natural mineral pores.',bishop:'A deep diagonal mitre cut, a fine stone finial, and ten shallow channels in the stem.',knight:'A sculpted horse with shaped cheeks, paired ears, recessed eyes, nostrils, and a carved mane.',rook:'Six deep battlements, closed stone walls, an inset crown, and a grooved tower stem.',pawn:'A quiet spherical finial, a compact fluted stem, and a softly stepped foot.'};
let renderRequested=false;
try {
  const T=await import('./vendor/three-0.159.module.min.js');
  const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:false,preserveDrawingBuffer:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0xf1eee7);
  renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.12;
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.VSMShadowMap;
  const scene=new T.Scene();scene.background=new T.Color(0xf1eee7);
  const camera=new T.PerspectiveCamera(32,1,.05,150);
  const assembly=new T.Group(),boardGroup=new T.Group();assembly.add(boardGroup);scene.add(assembly);
  const meshes=[],pieces=new Map();
  scene.add(new T.HemisphereLight(0xfff9ed,0xb8b2a5,2.15));
  const key=new T.DirectionalLight(0xfff8ee,2.75);key.position.set(-6,11,7);key.castShadow=true;
  key.shadow.mapSize.set(2048,2048);Object.assign(key.shadow.camera,{left:-8,right:8,top:8,bottom:-8,near:.1,far:32});
  key.shadow.normalBias=.013;key.shadow.bias=-.0001;key.shadow.radius=9;key.shadow.blurSamples=12;scene.add(key);
  const fill=new T.DirectionalLight(0xe5edff,.7);fill.position.set(6,5,-7);scene.add(fill);
  const loader=new T.TextureLoader();
  const surfaces=await Promise.all(['raw-travertine','basalt'].map(n=>loader.loadAsync(`assets/img/stone-v2/${n}.jpg`)));
  const reliefs=surfaces.map(t=>{t.colorSpace=T.SRGBColorSpace;t.wrapS=t.wrapT=T.RepeatWrapping;t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());const r=t.clone();r.colorSpace=T.NoColorSpace;r.needsUpdate=true;return r;});
  // World-space triplanar projection keeps grain running through the whole carving,
  // instead of stretching a small UV image over collars, crowns, and cross cuts.
  function material(color, scale = .85, dark = false) {
    const m = new T.MeshStandardMaterial({ color, map: surfaces[dark ? 1 : 0], bumpMap: reliefs[dark ? 1 : 0],
      bumpScale: dark ? .06 : .075, roughness: .91, metalness: 0 });
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
    m.customProgramCacheKey = () => 'stone-study-v2-triplanar';
    return m;
  }

  function mesh(geometry, mat, parent, x = 0, y = 0, z = 0) {
    const m = new T.Mesh(geometry, mat);
    m.position.set(x, y, z);
    m.castShadow = m.receiveShadow = true;
    parent.add(m);
    return m;
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

  const floor=mesh(new T.PlaneGeometry(200,200),new T.ShadowMaterial({color:0x514c43,opacity:.23}),scene,0,-.35,0);
  floor.rotation.x=-Math.PI/2;floor.castShadow=false;
  const stone=material(0xf8f3e9,.92),basalt=material(0xffffff,.95,true);
  basalt.color.multiplyScalar(1.5);
  const lightCut=material(0x9d9484,.92),darkCut=material(0x737978,.95,true);
  const paleSquare=material(0xf5f1e9,.63),darkSquare=material(0x777a78,.63,true),edge=material(0xd5caba,.68);
  const board=mesh(roundedBox(9.30,9.30,.34,.045),edge,boardGroup,0,-.16,0);board.rotation.x=-Math.PI/2;
  const tile=1.08,top=.032;
  const squareGeometry=new T.BoxGeometry(tile-.003,.03,tile-.003);
  const squareMaterials=[];
  for(let rank=0;rank<8;rank++)for(let file=0;file<8;file++) {
    const light=squareColor(file,rank)==='light';
    mesh(squareGeometry,light?paleSquare:darkSquare,boardGroup,(file-3.5)*tile,.015,(3.5-rank)*tile);
    squareMaterials.push({square:`${'abcdefgh'[file]}${rank+1}`,color:light?'light':'dark'});
  }
  // Fine inset border and engraved-looking notation make board orientation unambiguous.
  const groove=new T.MeshStandardMaterial({color:0x736f62,roughness:1});
  for(const [x,z,w,d] of [[0,-4.365,8.74,.013],[0,4.365,8.74,.013],[-4.365,0,.013,8.74],[4.365,0,.013,8.74]])mesh(new T.BoxGeometry(w,.008,d),groove,boardGroup,x,.02,z);
  function notation(text,x,z,rotation=0) {
    const c=document.createElement('canvas');c.width=c.height=128;
    const ctx=c.getContext('2d');ctx.fillStyle='#504c43';ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='42px Georgia';ctx.fillText(text,64,64);
    const mat=new T.MeshBasicMaterial({map:new T.CanvasTexture(c),transparent:true,depthWrite:false,opacity:.75});
    const label=mesh(new T.PlaneGeometry(.20,.20),mat,boardGroup,x,.018,z);label.rotation.set(-Math.PI/2,0,rotation);label.castShadow=false;
  }
  for(let i=0;i<8;i++) {
    notation('abcdefgh'[i],(i-3.5)*tile,4.5);notation('abcdefgh'[i],(i-3.5)*tile,-4.5,Math.PI);
    notation(String(i+1),-4.5,(3.5-i)*tile);notation(String(i+1),4.5,(3.5-i)*tile,Math.PI);
  }
  const prototypes={light:createSculptures(T,stone,lightCut),dark:createSculptures(T,basalt,darkCut)};
  const shadowCanvas=document.createElement('canvas');shadowCanvas.width=shadowCanvas.height=64;
  const sc=shadowCanvas.getContext('2d'),gradient=sc.createRadialGradient(32,32,4,32,32,32);
  gradient.addColorStop(0,'rgba(25,22,17,.45)');gradient.addColorStop(.45,'rgba(25,22,17,.20)');gradient.addColorStop(1,'rgba(25,22,17,0)');sc.fillStyle=gradient;sc.fillRect(0,0,64,64);
  const contactMat=new T.MeshBasicMaterial({map:new T.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false});
  const contactGeometry=new T.PlaneGeometry(.94,.94);
  function addPiece(type,color,file,rank) {
    const g=prototypes[color].get(type).clone(true),square=`${'abcdefgh'[file]}${rank+1}`,id=`${color}-${square}`;
    g.position.set((file-3.5)*tile,top,(3.5-rank)*tile);
    g.rotation.y=color==='dark'?Math.PI:0;
    const contact=mesh(contactGeometry,contactMat,assembly,g.position.x,top+.001,g.position.z);contact.rotation.x=-Math.PI/2;contact.castShadow=false;
    g.userData={id,type,color,file,rank,square,contact};
    g.traverse(o=>{if(o.isMesh){o.userData={id,type};meshes.push(o);}});assembly.add(g);pieces.set(id,g);
    g.userData.height=new T.Box3().setFromObject(g).max.y-top;
  }
  for(const p of startingPosition)addPiece(p.type,p.color,p.file,p.rank);
  const boardBounds=new T.Box3(new T.Vector3(-4.72,-.35,-4.72),new T.Vector3(4.72,2.35,4.72));
  let yaw=.48,pitch=.66,zoom=1,inspecting=false,overhead=false,down=null;
  const raycaster=new T.Raycaster(),pointer=new T.Vector2(),target=new T.Vector3();
  function selectedPiece() {return [...pieces.values()].find(p=>p.userData.type===inspectSelect.value&&p.userData.color===colorSelect.value);}
  function cameraDistance(bounds,center) {
    const direction=new T.Vector3(Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch));
    const right=new T.Vector3(Math.cos(yaw),0,-Math.sin(yaw)),up=new T.Vector3().crossVectors(direction,right);
    const tan=Math.tan(T.MathUtils.degToRad(camera.fov/2));let d=0;
    for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]) {
      const v=new T.Vector3(x,y,z).sub(center),depth=v.dot(direction);
      d=Math.max(d,Math.abs(v.dot(right))/(tan*camera.aspect*.9)+depth,Math.abs(v.dot(up))/(tan*.77)+depth);
    }
    return {d:d/zoom,direction};
  }
  function positionCamera() {
    let bounds=boardBounds;
    if(inspecting) {bounds=new T.Box3().setFromObject(selectedPiece());bounds.getCenter(target);}
    else target.set(0,.65,0);
    const {d,direction}=cameraDistance(bounds,target);camera.position.copy(target).addScaledVector(direction,d);camera.lookAt(target);camera.updateMatrixWorld();
  }
  function render(){renderRequested=false;positionCamera();renderer.render(scene,camera);}
  function requestRender(){if(!renderRequested){renderRequested=true;requestAnimationFrame(render);}}
  function fit(){renderer.setSize(canvas.clientWidth,canvas.clientHeight,false);camera.aspect=canvas.clientWidth/canvas.clientHeight;camera.updateProjectionMatrix();requestRender();}
  function pick(e) {
    const r=canvas.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);raycaster.setFromCamera(pointer,camera);
    const hit=raycaster.intersectObjects(meshes.filter(m=>pieces.get(m.userData.id).visible),false)[0];return hit?pieces.get(hit.object.userData.id).userData:null;
  }
  function highlight(p,e) {
    links.forEach(l=>l.classList.toggle('active',l.dataset.piece===p?.type));canvas.style.cursor=p?'pointer':'grab';tip.classList.toggle('visible',!!p&&!!e);
    if(p&&e){const r=stage.getBoundingClientRect();tip.textContent=`${p.type[0].toUpperCase()+p.type.slice(1)} / ${categories[p.type]}${p.type==='queen'?' · Coming soon':''} ↗`;tip.style.left=`${Math.max(96,Math.min(r.width-96,e.clientX-r.left))}px`;tip.style.top=`${Math.max(45,e.clientY-r.top-18)}px`;}
  }
  canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;down={x:e.clientX,y:e.clientY,yaw,pitch,moved:false};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{
    if(down){const dx=e.clientX-down.x,dy=e.clientY-down.y;if(Math.hypot(dx,dy)>6)down.moved=true;if(down.moved){yaw=down.yaw-dx*.005;pitch=T.MathUtils.clamp(down.pitch+dy*.003,.14,1.45);overhead=false;overheadButton.setAttribute('aria-pressed','false');highlight(null);requestRender();}}
    else if(e.pointerType!=='touch')highlight(pick(e),e);
  });
  canvas.addEventListener('pointerup',e=>{if(!down)return;const clicked=!down.moved;down=null;if(canvas.hasPointerCapture(e.pointerId))canvas.releasePointerCapture(e.pointerId);if(clicked){const p=pick(e);if(p){if(e.metaKey||e.ctrlKey)window.open(destinations[p.type],'_blank','noopener');else location.href=destinations[p.type];}}});
  canvas.addEventListener('pointercancel',()=>{down=null;highlight(null);});canvas.addEventListener('pointerleave',()=>{if(!down)highlight(null);});
  links.forEach(l=>{for(const event of ['mouseenter','focus'])l.addEventListener(event,()=>highlight({type:l.dataset.piece}));for(const event of ['mouseleave','blur'])l.addEventListener(event,()=>highlight(null));});
  function reset(){yaw=inspecting?(inspectSelect.value==='knight'?1.18+(colorSelect.value==='dark'?Math.PI:0):-.22):.48;pitch=inspecting?.19:.66;zoom=1;overhead=false;overheadButton.setAttribute('aria-pressed','false');highlight(null);requestRender();}
  function zoomBy(f){zoom=T.MathUtils.clamp(zoom*f,.75,1.85);requestRender();}
  document.querySelectorAll('[data-action]').forEach(b=>b.addEventListener('click',()=>b.dataset.action==='reset'?reset():zoomBy(b.dataset.action==='in'?1.13:1/1.13)));
  canvas.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','Home'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.12;if(e.key==='ArrowRight')yaw+=.12;if(e.key==='ArrowUp')pitch=Math.min(1.45,pitch+.06);if(e.key==='ArrowDown')pitch=Math.max(.14,pitch-.06);if(e.key==='+'||e.key==='=')zoomBy(1.13);if(e.key==='-')zoomBy(1/1.13);if(e.key==='Home')reset();requestRender();});
  function showInspection() {
    inspection.hidden=!inspecting;stage.classList.toggle('is-inspecting',inspecting);inspectButton.setAttribute('aria-expanded',String(inspecting));inspectButton.textContent=inspecting?'Full board ↙':'Closer look ↗';
    const selected=selectedPiece();for(const p of pieces.values()){p.visible=!inspecting||p===selected;p.userData.contact.visible=p.visible;}
    boardGroup.visible=!inspecting;floor.position.y=inspecting?top-.006:-.35;
    const type=inspectSelect.value,link=document.querySelector('#inspectLink');link.href=destinations[type];link.textContent=`Explore ${categories[type]}${type==='queen'?' · Coming soon':''} ↗`;
    document.querySelector('#pieceDetail').textContent=details[type];fit();
  }
  inspectButton.addEventListener('click',()=>{inspecting=!inspecting;showInspection();reset();});
  for(const select of [inspectSelect,colorSelect])select.addEventListener('change',()=>{showInspection();reset();});
  overheadButton.addEventListener('click',()=>{const next=!overhead;inspecting=false;showInspection();reset();overhead=next;overheadButton.setAttribute('aria-pressed',String(overhead));if(overhead){pitch=1.45;yaw=0;}requestRender();});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();stage.classList.add('fallback');});canvas.addEventListener('webglcontextrestored',()=>location.reload());
  new ResizeObserver(fit).observe(stage);fit();stage.classList.add('ready');
  // Deterministic read-only diagnostics verify square colors, counts, links and visible targets.
  window.stoneStudy={version:2,getState(){positionCamera();return{inspecting,overhead,squareColors:squareMaterials,pieces:[...pieces.values()].map(g=>{const p=g.position.clone();p.y+=g.userData.height*.65;p.project(camera);const {id,type,color,square,file,rank}=g.userData;return{id,type,color,square,file,rank,visible:g.visible,href:destinations[type],x:(p.x+1)*canvas.clientWidth/2,y:(1-p.y)*canvas.clientHeight/2};})};}};
} catch(error){stage.classList.add('fallback');console.error('Stone study V2:',error);}
