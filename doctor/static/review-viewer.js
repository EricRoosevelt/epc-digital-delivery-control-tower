import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

// Coordinates stay in metres and Z-up, matching the IFC geometry contract.
export function createViewer(host, onSelect) {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color("#e7edf1");
  const camera = new THREE.PerspectiveCamera(38, 1, 0.01, 100000);
  camera.up.set(0, 0, 1);
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.setAttribute("aria-label", host.getAttribute("aria-label"));
  host.append(renderer.domElement);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = false;
  controls.screenSpacePanning = true;
  scene.add(new THREE.HemisphereLight(0xffffff, 0x7b8792, 2.5));
  const light = new THREE.DirectionalLight(0xffffff, 3);
  light.position.set(30, -20, 50);
  scene.add(light);
  const root = new THREE.Group();
  scene.add(root);
  const meshes = new Map();
  let selected = null;
  let isolated = false;
  let modelKeys = null;
  let elementModels = new Map();
  let overall = new THREE.Box3();
  let initial = new THREE.Box3();
  let grid = null;
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let down = null;
  const draw = () => renderer.render(scene, camera);
  controls.addEventListener("change", draw);
  const resize = new ResizeObserver(() => {
    const { width, height } = host.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    draw();
  });
  resize.observe(host);
  renderer.domElement.addEventListener("pointerdown", e => { down = [e.clientX, e.clientY]; });
  renderer.domElement.addEventListener("pointerup", e => {
    if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return;
    down = null;
    const rect = renderer.domElement.getBoundingClientRect();
    pointer.set((e.clientX - rect.left) / rect.width * 2 - 1, -(e.clientY - rect.top) / rect.height * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects([...meshes.values()].filter(m => m.visible))[0];
    if (hit) onSelect(hit.object.userData.elementKey);
  });
  function frame(box, top = false) {
    if (box.isEmpty()) return;
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const radius = Math.max(size.length() / 2, 0.5);
    const halfFov = Math.atan(Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * Math.min(camera.aspect, 1));
    const distance = radius / Math.sin(halfFov) * 1.05;
    const direction = top ? new THREE.Vector3(0, -0.001, 1) : new THREE.Vector3(1, -1.35, 0.95).normalize();
    camera.position.copy(center).addScaledVector(direction, distance);
    camera.near = Math.max(distance / 10000, 0.001);
    camera.far = Math.max(distance * 100, 1000);
    camera.updateProjectionMatrix();
    controls.target.copy(center);
    controls.maxDistance = distance * 20;
    controls.minDistance = Math.max(radius / 500, 0.01);
    controls.update();
    draw();
  }
  function visibleBox() {
    const box = new THREE.Box3();
    for (const mesh of meshes.values()) if (mesh.visible) box.expandByObject(mesh);
    return box;
  }
  function mainClusterBox() {
    const entries = [...meshes.values()].map(mesh => ({ mesh, center: new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3()) }));
    if (entries.length < 8) return overall.clone();
    const median = values => values.sort((a, b) => a - b)[Math.floor(values.length / 2)];
    const center = new THREE.Vector3(...["x", "y", "z"].map(axis => median(entries.map(e => e.center[axis]))));
    const distances = entries.map(e => e.center.distanceTo(center)).sort((a, b) => a - b);
    const q1 = distances[Math.floor(distances.length * .25)];
    const q3 = distances[Math.floor(distances.length * .75)];
    const threshold = q3 + Math.max((q3 - q1) * 1.5, 1);
    const cluster = entries.filter(e => e.center.distanceTo(center) <= threshold);
    if (cluster.length < entries.length * .75) return overall.clone();
    const box = new THREE.Box3();
    cluster.forEach(e => box.expandByObject(e.mesh));
    return box;
  }
  function update() {
    for (const [key, mesh] of meshes) {
      mesh.visible = (!modelKeys || modelKeys.has(elementModels.get(key))) && (!isolated || key === selected);
      mesh.material.color.copy(mesh.userData.baseColor);
      mesh.material.emissive.set(key === selected ? "#087b93" : "#000000");
      if (key === selected) mesh.material.color.set("#54d8ed");
    }
    draw();
  }
  return {
    load(data, report) {
      for (const mesh of meshes.values()) { root.remove(mesh); mesh.geometry.dispose(); mesh.material.dispose(); }
      meshes.clear(); selected = null; isolated = false; modelKeys = null;
      elementModels = new Map(report.elements.map(e => [e.element_key, e.model_key]));
      const failed = new Set(report.findings.filter(f => f.status === "FAIL" && f.severity === "ERROR").map(f => f.element_key));
      for (const item of data.meshes || []) {
        if (!item.positions?.length || !item.indices?.length) continue;
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute("position", new THREE.Float32BufferAttribute(item.positions, 3));
        geometry.setIndex(item.indices);
        geometry.computeVertexNormals();
        const source = Array.isArray(item.color) ? new THREE.Color(...item.color.slice(0, 3)) : new THREE.Color("#adbcc5");
        const color = failed.has(item.element_key) ? new THREE.Color("#d58c62") : source;
        const material = new THREE.MeshStandardMaterial({ color, roughness: 0.78, metalness: 0, side: THREE.DoubleSide });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.userData = { elementKey: item.element_key, baseColor: color.clone() };
        // A backend mesh is one element; retain all parts if extraction yields multiple chunks.
        if (meshes.has(item.element_key)) {
          geometry.dispose(); material.dispose(); continue;
        }
        meshes.set(item.element_key, mesh); root.add(mesh);
      }
      overall = new THREE.Box3().setFromObject(root);
      initial = mainClusterBox();
      if (grid) { scene.remove(grid); grid.geometry.dispose(); grid.material.dispose(); }
      if (!overall.isEmpty()) {
        const size = overall.getSize(new THREE.Vector3());
        const center = overall.getCenter(new THREE.Vector3());
        grid = new THREE.GridHelper(Math.max(size.x, size.y, 10) * 1.6, 20, 0xa8b7c2, 0xd1dbe2);
        grid.rotation.x = Math.PI / 2;
        grid.position.set(center.x, center.y, overall.min.z - 0.03);
        scene.add(grid);
        // Frame the main spatial cluster; source origin/georeference helpers remain
        // visible and Show all always uses the complete, unchanged world bounds.
        frame(initial);
      }
      draw();
      return meshes.size;
    },
    select(key) { selected = key; update(); return meshes.has(key); },
    filter(key) { modelKeys = key ? new Set([key]) : null; update(); },
    focus() { const mesh = meshes.get(selected); if (mesh) frame(new THREE.Box3().setFromObject(mesh)); },
    isolate() { isolated = !isolated; update(); if (isolated) this.focus(); return isolated; },
    reset() { isolated = false; update(); frame(modelKeys ? visibleBox() : initial); },
    fit(top = false) { frame(visibleBox(), top); },
    zoom(factor) { camera.position.sub(controls.target).multiplyScalar(factor).add(controls.target); controls.update(); draw(); },
    rotate(angle) { const offset = camera.position.clone().sub(controls.target); offset.applyAxisAngle(new THREE.Vector3(0, 0, 1), angle); camera.position.copy(controls.target).add(offset); controls.update(); draw(); },
    has(key) { return meshes.has(key); },
    visibleCount() { return [...meshes.values()].filter(m => m.visible).length; },
  };
}
