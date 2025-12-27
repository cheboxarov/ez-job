import { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface ThreeBackgroundContainerProps {
  containerRef: React.RefObject<HTMLDivElement>;
}

export const ThreeBackgroundContainer = ({ containerRef }: ThreeBackgroundContainerProps) => {
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const animationIdRef = useRef<number | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Init Three.js
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0f172a, 0.02);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 8;
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;

    // Clear any existing canvas
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 2);
    scene.add(ambientLight);

    const pointLight1 = new THREE.PointLight(0x2563eb, 4, 100);
    pointLight1.position.set(10, 10, 10);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x7c3aed, 4, 100);
    pointLight2.position.set(-10, -10, 10);
    scene.add(pointLight2);

    const pointLight3 = new THREE.PointLight(0xffffff, 2, 100);
    pointLight3.position.set(0, 10, -10);
    scene.add(pointLight3);

    // Polyhedron
    const geometry = new THREE.IcosahedronGeometry(3.5, 1);
    const wireframeGeometry = new THREE.WireframeGeometry(geometry);
    const wireframeMaterial = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.3
    });
    const polyhedron = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);
    polyhedron.position.x = 0;
    polyhedron.position.y = 0;
    scene.add(polyhedron);

    // Glow
    const glowGeometry = new THREE.IcosahedronGeometry(3.52, 1);
    const glowMaterial = new THREE.MeshBasicMaterial({
      color: 0x2563eb,
      wireframe: true,
      transparent: true,
      opacity: 0.2
    });
    const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
    polyhedron.add(glowMesh);

    // Core
    const coreGeometry = new THREE.IcosahedronGeometry(1.75, 0);
    const coreMaterial = new THREE.MeshBasicMaterial({
      color: 0x7c3aed,
      wireframe: true,
      transparent: true,
      opacity: 0.4
    });
    const core = new THREE.Mesh(coreGeometry, coreMaterial);
    polyhedron.add(core);

    // Rings
    const ringsGroup = new THREE.Group();
    scene.add(ringsGroup);

    function createRing(radius: number, tube: number, color: number, opacity: number, rotationX: number, rotationY: number) {
      const geometry = new THREE.TorusGeometry(radius, tube, 32, 100);
      const material = new THREE.MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: opacity,
        side: THREE.DoubleSide
      });
      const ring = new THREE.Mesh(geometry, material);
      ring.rotation.x = rotationX;
      ring.rotation.y = rotationY;
      return ring;
    }

    const ring1 = createRing(4.5, 0.02, 0xffffff, 0.5, Math.PI / 2.2, 0);
    const ring2 = createRing(5.5, 0.02, 0x2563eb, 0.4, Math.PI / 2.1, 0.2);
    const ring3 = createRing(7.0, 0.03, 0x7c3aed, 0.3, Math.PI / 2.3, -0.1);

    ringsGroup.add(ring1);
    ringsGroup.add(ring2);
    ringsGroup.add(ring3);

    // Stars
    const starsGeometry = new THREE.BufferGeometry();
    const starsCount = 300;
    const posArray = new Float32Array(starsCount * 3);

    for (let i = 0; i < starsCount * 3; i++) {
      posArray[i] = (Math.random() - 0.5) * 50;
    }

    starsGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const starsMaterial = new THREE.PointsMaterial({
      size: 0.15,
      color: 0xffffff,
      transparent: true,
      opacity: 0.6
    });
    const starsMesh = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(starsMesh);

    // Animation
    let mouseX = 0;
    let mouseY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    };

    container.addEventListener('mousemove', handleMouseMove);

    const clock = new THREE.Clock();

    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);

      const elapsedTime = clock.getElapsedTime();
      const baseRotation = elapsedTime * 0.1;

      const parallaxX = mouseY * 0.15;
      const parallaxY = mouseX * 0.15;

      polyhedron.rotation.x = baseRotation * 0.5 + parallaxX;
      polyhedron.rotation.y = baseRotation + parallaxY;

      core.rotation.x = -baseRotation + parallaxX;
      core.rotation.y = -baseRotation + parallaxY;

      const cameraParallaxX = mouseX * 0.5;
      const cameraParallaxY = -mouseY * 0.5;

      camera.position.x += (cameraParallaxX - camera.position.x) * 0.05;
      camera.position.y += (cameraParallaxY - camera.position.y) * 0.05;

      polyhedron.rotation.z = mouseX * 0.1;

      ringsGroup.rotation.y = elapsedTime * 0.05;
      ringsGroup.rotation.z = Math.sin(elapsedTime * 0.2) * 0.1;

      camera.lookAt(0, 0, 0);
      starsMesh.rotation.y = elapsedTime * 0.02;

      renderer.render(scene, camera);
    };

    animate();

    // Resize handler
    const handleResize = () => {
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    return () => {
      container.removeEventListener('mousemove', handleMouseMove);
      resizeObserver.disconnect();
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [containerRef]);

  return null;
};

