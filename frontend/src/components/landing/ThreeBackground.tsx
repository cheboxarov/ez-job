import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export const ThreeBackground = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Init Three.js
    const scene = new THREE.Scene();
    // Light fog for depth - matching background color
    scene.fog = new THREE.FogExp2(0xf8fafc, 0.02);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    // Clear any existing canvas
    while (containerRef.current.firstChild) {
        containerRef.current.removeChild(containerRef.current.firstChild);
    }
    containerRef.current.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 2); 
    scene.add(ambientLight);

    // Colorful lights
    const pointLight1 = new THREE.PointLight(0x2563eb, 4, 100); // Blue
    pointLight1.position.set(10, 10, 10);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x7c3aed, 4, 100); // Purple
    pointLight2.position.set(-10, -10, 10);
    scene.add(pointLight2);

    const pointLight3 = new THREE.PointLight(0x000000, 2, 100); // Dark rim light for contrast
    pointLight3.position.set(0, 10, -10);
    scene.add(pointLight3);

    // Polyhedron (Tech Wireframe)
    const geometry = new THREE.IcosahedronGeometry(2.0, 1);

    // 1. The Wireframe Structure - DARK for light theme
    const wireframeGeometry = new THREE.WireframeGeometry(geometry);
    const wireframeMaterial = new THREE.LineBasicMaterial({ 
        color: 0x1e293b, // Dark slate
        transparent: true,
        opacity: 0.15 
    });
    const polyhedron = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);
    polyhedron.position.x = 4.0; // Смещение вправо
    polyhedron.position.y = -1.5; // Смещение вниз
    scene.add(polyhedron);

    // 2. Accent Edges (Outer Glow)
    const glowGeometry = new THREE.IcosahedronGeometry(2.01, 1);
    const glowMaterial = new THREE.MeshBasicMaterial({
        color: 0x2563eb, // Blue accent
        wireframe: true,
        transparent: true,
        opacity: 0.1
    });
    const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
    polyhedron.add(glowMesh);

    // 3. Inner Core
    const coreGeometry = new THREE.IcosahedronGeometry(1.0, 0);
    const coreMaterial = new THREE.MeshBasicMaterial({ 
        color: 0x7c3aed, // Purple
        wireframe: true, 
        transparent: true, 
        opacity: 0.3
    });
    const core = new THREE.Mesh(coreGeometry, coreMaterial);
    polyhedron.add(core);

    // Rings
    const ringsGroup = new THREE.Group();
    ringsGroup.position.x = 4.0; // Смещение вправо вместе с фигурой
    ringsGroup.position.y = -1.5; // Смещение вниз вместе с фигурой
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

    const ring1 = createRing(2.5, 0.01, 0x1e293b, 0.4, Math.PI / 2.2, 0); // Dark ring
    const ring2 = createRing(3.2, 0.01, 0x2563eb, 0.3, Math.PI / 2.1, 0.2); // Blue ring
    const ring3 = createRing(4.0, 0.02, 0x7c3aed, 0.15, Math.PI / 2.3, -0.1); // Purple ring

    ringsGroup.add(ring1);
    ringsGroup.add(ring2);
    ringsGroup.add(ring3);

    // Background Particles (Stars) - DARK for light theme
    const starsGeometry = new THREE.BufferGeometry();
    const starsCount = 500;
    const posArray = new Float32Array(starsCount * 3);

    for(let i = 0; i < starsCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 50;
    }

    starsGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const starsMaterial = new THREE.PointsMaterial({
        size: 0.05,
        color: 0x1e293b, // Dark particles
        transparent: true,
        opacity: 0.4
    });
    const starsMesh = new THREE.Points(starsGeometry, starsMaterial);
    scene.add(starsMesh);

    // Position Camera
    camera.position.z = 6;

    // Animation vars
    let scrollY = window.scrollY;
    let targetScrollY = window.scrollY;
    let mouseX = 0;
    let mouseY = 0;

    const handleScroll = () => {
        targetScrollY = window.scrollY;
    };

    const handleMouseMove = (e: MouseEvent) => {
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    };

    window.addEventListener('scroll', handleScroll);
    document.addEventListener('mousemove', handleMouseMove);

    // Animation Loop
    const clock = new THREE.Clock();
    let animationId: number;

    const animate = () => {
        animationId = requestAnimationFrame(animate);

        const elapsedTime = clock.getElapsedTime();

        // Smooth Scroll Lerp - более плавное сглаживание
        scrollY += (targetScrollY - scrollY) * 0.03;

        // Base rotation
        const baseRotation = elapsedTime * 0.1;
        
        // Parallax
        const parallaxX = mouseY * 0.15;
        const parallaxY = mouseX * 0.15;

        polyhedron.rotation.x = baseRotation * 0.5 + parallaxX;
        polyhedron.rotation.y = baseRotation + parallaxY;

        core.rotation.x = -baseRotation + parallaxX;
        core.rotation.y = -baseRotation + parallaxY;

        // Scroll Effect - более плавное изменение
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        const scrollFraction = maxScroll > 0 ? Math.min(scrollY / maxScroll, 1) : 0;

        // Плавное изменение радиуса с easing
        const easedScrollFraction = scrollFraction * scrollFraction * (3 - 2 * scrollFraction); // smoothstep
        const orbitRadius = 6 - (easedScrollFraction * 4);
        const orbitAngle = easedScrollFraction * Math.PI * 1.5;
        const orbitHeight = Math.sin(easedScrollFraction * Math.PI) * 2;
        
        const orbitX = Math.sin(orbitAngle) * orbitRadius;
        const orbitZ = Math.cos(orbitAngle) * orbitRadius;
        const orbitY = orbitHeight;

        const cameraParallaxX = mouseX * 0.8;
        const cameraParallaxY = -mouseY * 0.8;
        
        // Более плавная интерполяция камеры
        camera.position.x += ((orbitX + cameraParallaxX) - camera.position.x) * 0.02;
        camera.position.y += ((orbitY + cameraParallaxY) - camera.position.y) * 0.02;
        camera.position.z += ((orbitZ + cameraParallaxX * 0.3) - camera.position.z) * 0.02;

        const bankingAngle = Math.cos(orbitAngle) * 0.3;
        polyhedron.rotation.z = bankingAngle + mouseX * 0.1;
        polyhedron.position.y = -1.5 - orbitHeight * 0.3; // Сохраняем начальное смещение вниз
        
        const ringSpeed = 0.05 + (scrollFraction * 0.03);
        ringsGroup.rotation.y = elapsedTime * ringSpeed;
        ringsGroup.rotation.z = Math.sin(elapsedTime * 0.2) * 0.1 + (scrollFraction * 0.2);

        camera.lookAt(0, 0, 0);
        starsMesh.rotation.y = elapsedTime * 0.02;

        renderer.render(scene, camera);
    };

    animate();

    // Resize handler
    const handleResize = () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    };

    window.addEventListener('resize', handleResize);

    return () => {
        window.removeEventListener('scroll', handleScroll);
        document.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('resize', handleResize);
        cancelAnimationFrame(animationId);
        if (containerRef.current && renderer.domElement) {
            containerRef.current.removeChild(renderer.domElement);
        }
        renderer.dispose();
    };
  }, []);

  return (
    <div 
      ref={containerRef} 
      style={{ 
        position: 'fixed', 
        top: 0, 
        left: 0, 
        width: '100%', 
        height: '100vh', 
        zIndex: 0,
        pointerEvents: 'none',
        opacity: 0.8
      }} 
    />
  );
};

