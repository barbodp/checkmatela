/* "Sir Checkmate" — Checkmatela's mascot: a glossy, inflated 3D gentleman who floats across the homepage like a
   balloon as you scroll (tumbling, swooping toward the camera and away again).

   Built from primitives with three.js (lazy-loaded from js/vendor only when the flight is near the viewport).
   The flight runs between #flightStart (top) and #flightEnd (bottom) on the homepage.

   Tweak the look in buildMascot() (colours/materials), the path in pose(). Debug: open the page with #mascot=0.5
   to freeze the flight at 50%. */
(() => {
  "use strict";
  const startEl = document.getElementById('flightStart');
  const endEl = document.getElementById('flightEnd');
  if (!startEl || !endEl) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const debug = /mascot=([\d.]+)/.exec(location.hash);
  const forced = debug ? parseFloat(debug[1]) : null;

  let THREE = null, renderer, scene, camera, mascot, parts, running = false, loading = false;
  let target = 0, cur = 0, last = 0, canvas;

  const pageTop = el => el.getBoundingClientRect().top + window.scrollY;
  const zone = () => {
    const vh = window.innerHeight;
    const a = pageTop(startEl) - vh * 0.35, b = pageTop(endEl) - vh * 0.45;
    return [a, Math.max(b, a + vh * 1.6)];
  };
  const measure = () => {
    const [a, b] = zone();
    target = forced !== null ? forced : Math.min(1, Math.max(0, (window.scrollY - a) / (b - a)));
  };
  const inRange = () => {
    const [a, b] = zone(), vh = window.innerHeight;
    return forced !== null || (window.scrollY > a - vh * 0.5 && window.scrollY < b + vh * 0.6);
  };

  /* ------------------------------------------------------------------ the character */
  function buildMascot() {
    const T = THREE;
    const P = o => new T.MeshPhysicalMaterial(o);
    const skin = P({ color: 0xf4e4cb, roughness: .3, clearcoat: 1, clearcoatRoughness: .1 });
    const suit = P({ color: 0x0c0c0f, roughness: .26, clearcoat: 1, clearcoatRoughness: .08 });
    const shirt = P({ color: 0xfbf8f1, roughness: .38, clearcoat: .5, clearcoatRoughness: .2 });
    const tie = P({ color: 0x8a1f3a, roughness: .28, clearcoat: .9, clearcoatRoughness: .1 });
    const green = P({ color: 0x1e4d3b, roughness: .4, clearcoat: .4 });
    const brass = new T.MeshStandardMaterial({ color: 0xdcae55, metalness: 1, roughness: .2 });
    const ink = new T.MeshBasicMaterial({ color: 0x141414 });

    const g = new T.Group();
    const add = (parent, geo, mat, pos = [0, 0, 0], scl = [1, 1, 1], rot = [0, 0, 0]) => {
      const m = new T.Mesh(geo, mat);
      m.position.set(...pos); m.scale.set(...scl); m.rotation.set(...rot);
      parent.add(m); return m;
    };
    const sph = new T.SphereGeometry(1, 48, 32);

    /* body — an inflated, slightly pear-shaped torso */
    const body = new T.Group(); g.add(body);
    add(body, sph, suit, [0, 0.9, 0], [1.05, 1.22, .9]);
    add(body, sph, shirt, [0, 1.42, .62], [.44, .78, .3]);                 // shirt front
    add(body, sph, suit, [-.3, 1.52, .78], [.2, .62, .12], [0, 0, -.35]);  // lapels
    add(body, sph, suit, [.3, 1.52, .78], [.2, .62, .12], [0, 0, .35]);
    [.9, .55].forEach(y => add(body, sph, brass, [0, y, .84 + (y < .8 ? .03 : 0)], [.07, .07, .05]));
    add(body, new T.BoxGeometry(.24, .16, .04), shirt, [.55, 1.42, .82], [1, 1, 1], [0, 0, .25]);   // pocket square
    add(body, new T.BoxGeometry(.16, .08, .045), green, [.55, 1.4, .83], [1, 1, 1], [0, 0, .25]);
    // bow tie
    const bt = new T.Group(); bt.position.set(0, 1.96, .74); body.add(bt);
    add(bt, sph, tie, [0, 0, .02], [.11, .11, .1]);
    [-1, 1].forEach(s => add(bt, new T.ConeGeometry(.2, .36, 24), tie, [s * .24, 0, 0], [1, 1, .55], [0, 0, -s * Math.PI / 2]));

    /* head */
    const head = new T.Group(); head.position.set(0, 3.3, .05); head.scale.setScalar(1.22); g.add(head);
    const R = [1.02, 1.12, .98];
    add(head, sph, skin, [0, 0, 0], R);
    const surf = (x, y, lift = 0) => [x, y, R[2] * Math.sqrt(Math.max(0, 1 - (x / R[0]) ** 2 - (y / R[1]) ** 2)) + lift];
    const tube = (pts, r, mat = ink) => {
      const c = new T.CatmullRomCurve3(pts.map(p => new T.Vector3(...p)));
      const m = new T.Mesh(new T.TubeGeometry(c, 40, r, 8, false), mat); head.add(m); return m;
    };
    // eyes
    [-1, 1].forEach(s => add(head, sph, ink, surf(s * .36, .16, .0), [.075, .12, .05]));
    // brows
    [-1, 1].forEach(s => tube([surf(s * .16, .6, .012), surf(s * .36, .67, .014), surf(s * .58, .56, .012)], .02));
    // big smile + cheek creases
    const smile = []; for (let i = 0; i <= 10; i++) { const x = -.56 + i * .112; smile.push(surf(x, -.34 - .3 * Math.sin(Math.PI * i / 10), .014)); }
    tube(smile, .026);
    [-1, 1].forEach(s => tube([surf(s * .6, -.24, .012), surf(s * .66, -.3, .012), surf(s * .7, -.4, .012)], .016));
    // nose
    add(head, sph, skin, surf(0, -.08, .05), [.1, .09, .1]);
    // ears
    [-1, 1].forEach(s => add(head, sph, skin, [s * 1.0, -.02, -.02], [.17, .28, .2]));
    // monocle (brass ring + chain)
    add(head, new T.TorusGeometry(.26, .03, 12, 48), brass, surf(.36, .16, .06));
    tube([surf(.55, .0, .07), [.85, -.55, .45], [.75, -1.2, .6], [.5, -1.55, .68]], .012, brass);
    // little brass king's crown
    const crown = new T.Group(); crown.position.set(0, R[1] * .96, 0); head.add(crown);
    add(crown, new T.CylinderGeometry(.34, .42, .16, 32), brass, [0, .02, 0]);
    add(crown, new T.CylinderGeometry(.3, .34, .06, 32), brass, [0, .12, 0]);
    add(crown, new T.BoxGeometry(.08, .34, .08), brass, [0, .38, 0]);
    add(crown, new T.BoxGeometry(.26, .08, .08), brass, [0, .42, 0]);
    add(crown, sph, brass, [0, .62, 0], [.06, .06, .06]);

    /* arms */
    const arms = [-1, 1].map(s => {
      const a = new T.Group(); a.position.set(s * 1.02, 1.62, 0); g.add(a);
      add(a, new T.CapsuleGeometry(.3, .7, 12, 24), suit, [0, -.55, 0]);
      add(a, new T.CylinderGeometry(.31, .31, .14, 24), shirt, [0, -1.12, 0]);
      add(a, new T.CylinderGeometry(.05, .05, .1, 12), brass, [s * .12, -1.12, .29], [1, 1, 1], [Math.PI / 2, 0, 0]);
      add(a, sph, skin, [0, -1.42, 0], [.3, .3, .3]);
      return a;
    });
    /* legs */
    const legs = [-1, 1].map(s => {
      const l = new T.Group(); l.position.set(s * .44, -.05, 0); g.add(l);
      add(l, new T.CapsuleGeometry(.34, .8, 12, 24), suit, [0, -.7, 0]);
      add(l, sph, suit, [0, -1.5, .22], [.44, .3, .68]);
      return l;
    });
    return { g, arms, legs, head, bow: bt };
  }

  function makeEnv() {
    const T = THREE, s = new T.Scene();
    s.add(new T.Mesh(new T.BoxGeometry(30, 30, 30), new T.MeshBasicMaterial({ color: 0xb9bec2, side: T.BackSide })));
    const panel = (w, h, pos, rot, c) => {
      const m = new T.Mesh(new T.PlaneGeometry(w, h), new T.MeshBasicMaterial({ color: new T.Color(c, c, c), side: T.DoubleSide }));
      m.position.set(...pos); m.rotation.set(...rot); s.add(m);
    };
    panel(14, 14, [0, 12, 0], [Math.PI / 2, 0, 0], 8);        // big softbox above
    panel(6, 10, [-11, 2, 6], [0, Math.PI / 2.4, 0], 5);       // key light, left
    panel(4, 8, [11, 1, 4], [0, -Math.PI / 2.4, 0], 2.5);      // fill, right
    panel(10, 3, [0, -6, 8], [-.5, 0, 0], 1.2);                // bounce from below
    return s;
  }

  async function boot() {
    if (loading) return; loading = true;
    THREE = await import('./vendor/three-0.159.module.min.js');
    canvas = document.createElement('canvas');
    canvas.className = 'mascot-canvas'; canvas.setAttribute('aria-hidden', 'true');
    document.body.appendChild(canvas);
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.setClearColor(0x000000, 0);
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(30, 1, .1, 100);
    camera.position.set(0, 0, 16);
    const pm = new THREE.PMREMGenerator(renderer);
    scene.environment = pm.fromScene(makeEnv(), .03).texture;
    const key = new THREE.DirectionalLight(0xffffff, 1.6); key.position.set(-4, 6, 8); scene.add(key);
    const rim = new THREE.DirectionalLight(0xffe7c2, .8); rim.position.set(6, 2, -4); scene.add(rim);
    parts = buildMascot(); mascot = new THREE.Group(); mascot.add(parts.g); scene.add(mascot);
    resize(); window.addEventListener('resize', resize);
    measure(); cur = target; start();
  }

  function resize() {
    if (!renderer) return;
    const w = window.innerWidth, h = window.innerHeight;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }

  /* the flight: bottom-left → across the page → top-right, looming toward the camera mid-way */
  function pose(p, t) {
    const aspect = camera.aspect, portrait = aspect < 1;
    const fit = portrait ? Math.max(.42, aspect * .95) : 1;             // keep him on screen on phones
    const halfW = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * 16 * aspect;
    const s = Math.sin(Math.PI * p);
    const x = (-1.15 + 2.3 * p) * halfW * .95 + Math.sin(p * Math.PI * 2.4) * .5;
    const y = -8.5 + 17 * p + Math.sin(p * Math.PI * 3.1) * 1.1;
    const z = -6 + 9 * Math.pow(s, 1.3);
    mascot.position.set(x, y, z);
    mascot.scale.setScalar(.62 * fit * (1 + .62 * Math.pow(s, 2.4)) * (1 + .04 * Math.sin(t * 1.7)));  // breathing, balloon-like
    mascot.rotation.set(.42 + .22 * Math.sin(p * Math.PI) - .1 * (p - .5), (p - .5) * 3.1 + Math.sin(t * .9) * .08, (.5 - p) * .9 + Math.sin(t * 1.3) * .05);
    parts.arms.forEach((a, i) => { const s2 = i ? 1 : -1; a.rotation.z = s2 * (1.2 + .16 * Math.sin(t * 2.6 + i)); a.rotation.x = .12 * Math.sin(t * 2 + i * 2); });
    parts.legs.forEach((l, i) => { l.rotation.x = .3 * Math.sin(t * 2.2 + i * Math.PI); l.rotation.z = (i ? 1 : -1) * .1; });
    parts.head.rotation.z = .06 * Math.sin(t * 1.4);
    parts.bow.rotation.z = .05 * Math.sin(t * 3);
  }

  function frame(now) {
    if (!running) return;
    const dt = Math.min(50, now - last || 16); last = now;
    if (!inRange()) { canvas.style.visibility = 'hidden'; running = false; return; }
    measure();
    cur += (target - cur) * Math.min(1, dt * .006);
    const p = Math.min(1, Math.max(0, cur));
    if (p <= .002 || p >= .998) canvas.style.visibility = 'hidden';
    else {
      canvas.style.visibility = 'visible';
      pose(p, now / 1000);
      renderer.render(scene, camera);
    }
    requestAnimationFrame(frame);
  }
  function start() { if (!running && renderer) { running = true; last = 0; requestAnimationFrame(frame); } }

  const check = () => { if (inRange()) { THREE ? start() : boot(); } };
  window.addEventListener('scroll', check, { passive: true });
  window.addEventListener('resize', check);
  window.__mascot = { set: p => { target = cur = p; } };
  check();
})();
