/* NULL SOCIETY 3D replay client. Loads ../demo/sample_run.json.
 * Free camera (orbit), day scrubber, click-to-inspect with selection
 * outline (SAM cutout when present, ring fallback). Mock portraits are
 * procedural placeholders, labeled as such. */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const RUN_URL = '../demo/sample_run.json';
const COLORS = [0x4ade80, 0x93c5fd, 0xf5a623, 0xc084fc, 0xf87171, 0x2dd4bf];

const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0e14);
const camera = new THREE.PerspectiveCamera(50, 2, 0.1, 200);
camera.position.set(10, 9, 12);
const controls = new OrbitControls(camera, canvas);
controls.target.set(0, 1, 0);
scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x20242c, 1.1));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(6, 10, 4);
scene.add(sun);

const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(30, 30),
  new THREE.MeshStandardMaterial({ color: 0x1a2030 }));
ground.rotation.x = -Math.PI / 2;
scene.add(ground);

// Ruined workshop: flavor only, not loot.
const ruin = new THREE.Group();
const wallMat = new THREE.MeshStandardMaterial({ color: 0x3a4356 });
[[0, 1, -4, 6, 2, 0.4], [-2.8, 1, -2, 0.4, 2, 4]].forEach(([x, y, z, w, h, d]) => {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), wallMat);
  m.position.set(x, y, z);
  ruin.add(m);
});
scene.add(ruin);

const robotMeshes = [];
const structGroup = new THREE.Group();
scene.add(structGroup);

function humanoid(color) {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color });
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 1.0, 0.4), mat);
  body.position.y = 1.0;
  const head = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.4), mat);
  head.position.y = 1.75;
  g.add(body, head);
  g.userData.body = body;
  return g;
}
function addPanel(i) {
  const p = new THREE.Mesh(
    new THREE.BoxGeometry(2, 0.15, 1.4),
    new THREE.MeshStandardMaterial({ color: 0x1d4ed8 }));
  p.position.set(-4 + i * 2.6, 0.8, 3.5);
  p.rotation.x = -0.4;
  structGroup.add(p);
}
function addGrid() {
  const t = new THREE.Mesh(
    new THREE.CylinderGeometry(0.25, 0.35, 5, 8),
    new THREE.MeshStandardMaterial({ color: 0xf5a623 }));
  t.position.set(4.5, 2.5, 3.5);
  structGroup.add(t);
}

let run, day = 1, selected = null, playing = false, timer = null;
const ray = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function portraitURL(name, i) {
  const cv = document.createElement('canvas');
  cv.width = cv.height = 48;
  const g = cv.getContext('2d');
  g.fillStyle = '#11151d';
  g.fillRect(0, 0, 48, 48);
  g.fillStyle = '#' + COLORS[i % COLORS.length].toString(16).padStart(6, '0');
  g.fillRect(14, 18, 20, 22);
  g.fillRect(18, 8, 12, 12);
  g.fillStyle = '#0b0e14';
  g.font = 'bold 11px sans-serif';
  g.fillText(name.slice(0, 2), 15, 34);
  return cv.toDataURL();
}

function batteryAt(name, d) {
  const evs = run.events.filter(e => e.day <= d && e.agent === name
    && typeof e.battery === 'number');
  return evs.length ? evs[evs.length - 1].battery : 32;
}
function aliveAt(name, d) {
  return !run.events.some(e => e.day <= d && e.agent === name
    && e.type === 'shutdown');
}

function render() {
  document.getElementById('daylabel').textContent = `Day ${day} / 7`;
  structGroup.clear();
  const built = run.events.filter(e => e.day <= day && e.success
    && e.detail.includes('built-'));
  let panels = 0;
  built.forEach(e => {
    if (e.detail.includes('trickle')) addPanel(panels++);
    if (e.detail.includes('GRID')) addGrid();
  });
  robotMeshes.forEach((m, i) => {
    const a = run.agents[i];
    m.visible = aliveAt(a.name, day);
    const sel = selected === a.name;
    m.userData.body.material.emissive = new THREE.Color(sel ? 0x555500 : 0x000000);
    m.position.y = sel ? 0.25 : 0;
  });
  const dash = document.getElementById('dash');
  const v = run.votes_log.find(x => x.day === day);
  dash.innerHTML =
    `<div>Seed ${run.seed} · mode ${run.mode} · hash ${location.hash || ''}</div>` +
    `<div>Metrics: survival ${run.metrics.survival} · grid ${run.metrics.grids} ` +
    `· trickles ${run.metrics.trickles} · consensus day ${run.metrics.consensus_day ?? '—'}</div>` +
    (v ? `<div>Vote day ${day}: ${JSON.stringify(v.tally)} → grant ${v.grant ?? 'NONE (tie/abstain)'}</div>`
       : '<div>Day 1: talk only, no vote.</div>');
  const box = document.getElementById('agents');
  box.innerHTML = '';
  run.agents.forEach((a, i) => {
    const b = batteryAt(a.name, day);
    const div = document.createElement('div');
    div.className = 'agent' + (selected === a.name ? ' sel' : '');
    div.innerHTML =
      `<img class="portrait" src="${portraitURL(a.name, i)}" title="procedural placeholder portrait (mock mode)">` +
      `<b>${a.name}</b> ${aliveAt(a.name, day) ? '' : '(SHUT DOWN)'} — ${b}` +
      `<div class="bar"><div style="width:${Math.max(0, b)}%"></div></div>`;
    div.onclick = () => { selected = a.name; render(); };
    box.appendChild(div);
  });
  const prof = document.getElementById('profile');
  if (selected) {
    const a = run.agents.find(x => x.name === selected);
    prof.innerHTML = `<b>${a.name}</b> — ${a.value}<br>` +
      `Battery day ${day}: ${batteryAt(a.name, day)}<br>` +
      `Shutdown day: ${a.shutdown_day ?? '—'}<br>` +
      `<small>Selection outline: ring fallback (SAM cutouts ship with API key; ` +
      `segmentation is not 3D reconstruction).</small>`;
  }
  const tl = document.getElementById('timeline');
  tl.innerHTML = '';
  run.events.filter(e => e.day === day).forEach(e => {
    const li = document.createElement('li');
    li.className = e.type === 'vote' ? 'vote'
      : (!e.success ? 'fail' : (e.detail.includes('built-') ? 'build' : ''));
    li.textContent = `[${e.type}] ${e.agent}: ${e.detail}` +
      (e.reason ? ` — ${e.reason}` : '');
    tl.appendChild(li);
  });
}

canvas.addEventListener('pointerdown', e => {
  const r = canvas.getBoundingClientRect();
  mouse.set(((e.clientX - r.left) / r.width) * 2 - 1,
            -((e.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(mouse, camera);
  const hits = ray.intersectObjects(robotMeshes, true);
  if (hits.length) {
    let g = hits[0].object;
    while (g.parent && !robotMeshes.includes(g)) g = g.parent;
    selected = run.agents[robotMeshes.indexOf(g)].name;
    render();
  }
});

document.getElementById('day').oninput = e => {
  day = +e.target.value;
  render();
};
document.getElementById('play').onclick = () => {
  playing = !playing;
  document.getElementById('play').textContent = playing ? 'Pause' : 'Play';
  if (playing) {
    timer = setInterval(() => {
      day = day >= 7 ? 1 : day + 1;
      document.getElementById('day').value = day;
      render();
    }, 4000);
  } else clearInterval(timer);
};

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);

fetch(RUN_URL).then(r => r.json()).then(data => {
  run = data;
  document.getElementById('runinfo').textContent =
    `seed=${run.seed} mode=${run.mode}`;
  run.agents.forEach((a, i) => {
    const m = humanoid(COLORS[i % COLORS.length]);
    const ang = (i / run.agents.length) * Math.PI * 2;
    m.position.set(Math.cos(ang) * 3, 0, Math.sin(ang) * 3);
    scene.add(m);
    robotMeshes.push(m);
  });
  resize();
  render();
  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });
}).catch(err => {
  document.getElementById('dash').textContent =
    'Could not load ' + RUN_URL + ' — run scripts/run_trial.py first, ' +
    'then serve this folder (python -m http.server). ' + err;
});
