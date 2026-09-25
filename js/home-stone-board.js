// Production hero, based on the preserved raw-stone V2 study.
// Geometry/materials stay still until a visitor rotates the board or chooses a collection.
import { createSculptures } from './stone-sculptures-v2.js?v=1';
import { startingPosition, squareColor } from './stone-layout-v2.js?v=1';
import { destinations, categories, moveFor, motionAt } from './stone-navigation.js?v=1';
const root=document.querySelector('#heroBoard');
const stage=root.querySelector('.hb-stage'),canvas=stage.querySelector('canvas');
const links=[...root.querySelectorAll('.hb-key')],tip=stage.querySelector('.hb-tip');
const wipe=root.querySelector('.hb-wipe'),status=root.querySelector('.hb-status');
const controls=[...root.querySelectorAll('[data-action]')];
const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
let renderRequested=false;
// Keep the existing floating mascot below the realistic hero.
new IntersectionObserver(([entry])=>document.body.classList.toggle('stone-hero-in-view',entry.isIntersecting)).observe(root);
try {
  const T=await import('./vendor/three-0.159.module.min.js');
  const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:false,preserveDrawingBuffer:false});
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
  function material(color, scale = .85, dark = false, followsPiece = false) {
    const m = new T.MeshStandardMaterial({ color, map: surfaces[dark ? 1 : 0], bumpMap: reliefs[dark ? 1 : 0],
      bumpScale: dark ? .06 : .075, roughness: .91, metalness: 0 });
    m.onBeforeCompile = shader => {
      shader.uniforms.grainScale = { value: scale };
      shader.vertexShader = 'varying vec3 grainPos; varying vec3 grainNormal;\n' + shader.vertexShader;
      shader.vertexShader = shader.vertexShader.replace('#include <worldpos_vertex>', `#include <worldpos_vertex>
        grainPos = (modelMatrix * vec4(transformed, ${followsPiece ? '0.0' : '1.0'})).xyz;
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
    m.customProgramCacheKey = () => `home-stone-v2-triplanar-${followsPiece}`;
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
  const stone=material(0xf8f3e9,.92,false,true),basalt=material(0xffffff,.95,true,true);
  basalt.color.multiplyScalar(1.5);
  const lightCut=material(0x9d9484,.92,false,true),darkCut=material(0x737978,.95,true,true);
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
  let yaw=.48,pitch=.66,zoom=1.08,down=null,journey=null,hovered=null,navigationTimer=null;
  const raycaster=new T.Raycaster(),pointer=new T.Vector2(),target=new T.Vector3();
  const homes=new Map([...pieces].map(([id,g])=>[id,g.position.clone()]));
  const selection=mesh(new T.RingGeometry(.43,.465,64),new T.MeshBasicMaterial({color:0x9b8658,transparent:true,opacity:.7,side:T.DoubleSide,depthWrite:false}),scene);
  selection.rotation.x=-Math.PI/2;selection.visible=false;selection.castShadow=false;
  function cameraDistance(bounds,center) {
    const direction=new T.Vector3(Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch));
    const right=new T.Vector3(Math.cos(yaw),0,-Math.sin(yaw)),up=new T.Vector3().crossVectors(direction,right);
    const tan=Math.tan(T.MathUtils.degToRad(camera.fov/2));let d=0;
    for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]) {
      const v=new T.Vector3(x,y,z).sub(center),depth=v.dot(direction);
      d=Math.max(d,Math.abs(v.dot(right))/(tan*camera.aspect*.93)+depth,Math.abs(v.dot(up))/(tan*.83)+depth);
    }
    return {d:d/zoom,direction};
  }
  function positionCamera() {
    target.set(0,.65,0);
    const {d,direction}=cameraDistance(boardBounds,target);
    camera.position.copy(target).addScaledVector(direction,d);camera.lookAt(target);camera.updateMatrixWorld();
  }
  function render(now=performance.now()) {
    renderRequested=false;
    if(journey) {
      renderer.shadowMap.needsUpdate=true;
      const j=journey,k=motionAt((now-j.started)/j.duration,j.move.knight);
      j.piece.position.set(T.MathUtils.lerp(j.home.x,j.end.x,k.x),top+j.move.lift*k.lift,T.MathUtils.lerp(j.home.z,j.end.z,k.z));
      const contact=j.piece.userData.contact;
      contact.position.x=j.piece.position.x;contact.position.z=j.piece.position.z;
      contact.scale.setScalar(1+k.lift*.3);
      const focus=j.piece.position.clone();focus.y+=j.piece.userData.height*.52;
      target.copy(j.lookFrom).lerp(focus,k.camera);
      camera.position.copy(j.cameraFrom).lerp(j.cameraTo,k.camera);camera.lookAt(target);camera.updateMatrixWorld();
      wipe.style.opacity=String(k.fade);
      root.dataset.phase=k.done?'opening':k.camera>.9?'zooming':'moving';
      if(k.done)navigate();else requestRender();
    } else positionCamera();
    renderer.render(scene,camera);
  }
  function requestRender(){if(!renderRequested){renderRequested=true;requestAnimationFrame(render);}}
  function fit(){const w=canvas.clientWidth,h=canvas.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();requestRender();}
  function pick(e) {
    const r=canvas.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);raycaster.setFromCamera(pointer,camera);
    const hit=raycaster.intersectObjects(meshes,false)[0];return hit?pieces.get(hit.object.userData.id):null;
  }
  const preferred={king:'e1',queen:'d1',pawn:'e2',bishop:'f1',rook:'h1',knight:'g1'};
  function pieceFor(type){return pieces.get(`light-${preferred[type]}`);}
  function highlight(g,e) {
    if(journey)return;
    const changed=hovered!==g;hovered=g;
    links.forEach(l=>l.classList.toggle('is-on',l.dataset.piece===g?.userData.type));
    canvas.style.cursor=g?'pointer':'grab';tip.classList.toggle('is-on',!!g&&!!e);
    selection.visible=!!g;
    if(g)selection.position.set(g.position.x,top+.012,g.position.z);
    if(g&&e){const r=stage.getBoundingClientRect(),type=g.userData.type;tip.textContent=`${type[0].toUpperCase()+type.slice(1)} · ${categories[type]} ↗`;tip.style.left=`${Math.max(105,Math.min(r.width-105,e.clientX-r.left))}px`;tip.style.top=`${Math.max(45,e.clientY-r.top-18)}px`;}
    if(changed)requestRender();
  }
  function navigate(){if(!journey||journey.navigated)return;journey.navigated=true;clearTimeout(navigationTimer);location.assign(destinations[journey.piece.userData.type]);}
  function choose(g) {
    if(journey||!g)return;
    const type=g.userData.type;
    if(reducedMotion.matches){location.assign(destinations[type]);return;}
    highlight(null);down=null;
    const home=homes.get(g.userData.id),move=moveFor(g.userData),end=new T.Vector3((move.file-3.5)*tile,top,(3.5-move.rank)*tile);
    const direction=new T.Vector3(Math.sin(yaw)*.91,.42,Math.cos(yaw)*.91).normalize();
    const focus=end.clone();focus.y+=g.userData.height*.52;
    journey={piece:g,home,move,end,started:performance.now(),duration:1900,cameraFrom:camera.position.clone(),lookFrom:target.clone(),cameraTo:focus.clone().addScaledVector(direction,4.9),navigated:false};
    root.classList.add('is-moving');root.setAttribute('aria-busy','true');root.dataset.phase='moving';
    status.textContent=`Opening ${categories[type]}…`;controls.forEach(b=>b.disabled=true);
    // Navigation still completes if rendering is suspended while the tab is hidden.
    navigationTimer=setTimeout(navigate,2200);requestRender();
  }
  canvas.addEventListener('pointerdown',e=>{if(e.button!==0||journey||down)return;down={id:e.pointerId,x:e.clientX,y:e.clientY,yaw,pitch,moved:false};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{
    if(journey)return;
    if(down){if(e.pointerId!==down.id)return;const dx=e.clientX-down.x,dy=e.clientY-down.y;if(Math.hypot(dx,dy)>7)down.moved=true;if(down.moved){yaw=down.yaw-dx*.005;pitch=T.MathUtils.clamp(down.pitch+dy*.003,.22,1.35);highlight(null);requestRender();}}
    else if(e.pointerType!=='touch')highlight(pick(e),e);
  });
  canvas.addEventListener('pointerup',e=>{if(!down||e.pointerId!==down.id)return;const clicked=!down.moved;down=null;if(canvas.hasPointerCapture(e.pointerId))canvas.releasePointerCapture(e.pointerId);if(clicked){const g=pick(e);if(g){if(e.metaKey||e.ctrlKey||e.shiftKey)window.open(destinations[g.userData.type],'_blank','noopener');else choose(g);}}});
  const cancelPointer=()=>{down=null;highlight(null);};
  canvas.addEventListener('pointercancel',cancelPointer);canvas.addEventListener('lostpointercapture',cancelPointer);
  canvas.addEventListener('pointerleave',()=>{if(!down)highlight(null);});
  links.forEach(l=>{
    for(const event of ['mouseenter','focus'])l.addEventListener(event,()=>highlight(pieceFor(l.dataset.piece)));
    for(const event of ['mouseleave','blur'])l.addEventListener(event,()=>highlight(null));
    l.addEventListener('click',e=>{if(root.classList.contains('is-fallback')||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button!==0)return;e.preventDefault();choose(pieceFor(l.dataset.piece));});
  });
  function reset(){if(journey)return;yaw=.48;pitch=.66;zoom=1.08;highlight(null);requestRender();}
  function zoomBy(f){if(journey)return;zoom=T.MathUtils.clamp(zoom*f,.8,1.55);requestRender();}
  controls.forEach(b=>b.addEventListener('click',()=>b.dataset.action==='reset'?reset():zoomBy(b.dataset.action==='in'?1.13:1/1.13)));
  canvas.addEventListener('keydown',e=>{if(journey||!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','Home'].includes(e.key))return;e.preventDefault();if(e.key==='ArrowLeft')yaw-=.12;if(e.key==='ArrowRight')yaw+=.12;if(e.key==='ArrowUp')pitch=Math.min(1.35,pitch+.06);if(e.key==='ArrowDown')pitch=Math.max(.22,pitch-.06);if(e.key==='+'||e.key==='=')zoomBy(1.13);if(e.key==='-')zoomBy(1/1.13);if(e.key==='Home')reset();highlight(null);requestRender();});
  function restore(){
    clearTimeout(navigationTimer);journey=null;down=null;wipe.style.opacity='0';root.classList.remove('is-moving');root.removeAttribute('aria-busy');root.dataset.phase='ready';status.textContent='';controls.forEach(b=>b.disabled=false);
    for(const [id,g] of pieces){g.position.copy(homes.get(id));g.userData.contact.position.set(g.position.x,top+.001,g.position.z);g.userData.contact.scale.setScalar(1);}
    renderer.shadowMap.needsUpdate=true;reset();
  }
  window.addEventListener('pageshow',e=>{if(e.persisted)restore();});
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();const destination=journey&&destinations[journey.piece.userData.type];restore();root.classList.add('is-fallback');if(destination)location.assign(destination);});
  canvas.addEventListener('webglcontextrestored',()=>location.reload());
  reducedMotion.addEventListener('change',e=>{if(e.matches&&journey)navigate();});
  renderer.shadowMap.autoUpdate=false;renderer.shadowMap.needsUpdate=true;
  new ResizeObserver(fit).observe(stage);fit();root.classList.add('is-ready');root.dataset.phase='ready';
} catch(error){root.classList.add('is-fallback');console.error('Home stone board:',error);}
