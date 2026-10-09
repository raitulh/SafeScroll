'use client';

import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshTransmissionMaterial, OrbitControls, Sphere, Torus } from '@react-three/drei';
import { useRef } from 'react';
import * as THREE from 'three';

function Core() {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.y += 0.0025;
    ref.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.35) * 0.06;
  });
  return (
    <mesh ref={ref}>
      <icosahedronGeometry args={[1.15, 5]} />
      <MeshTransmissionMaterial thickness={0.45} roughness={0.22} transmission={0.95} ior={1.35} chromaticAberration={0.06} anisotropy={0.15} />
    </mesh>
  );
}

function Scene() {
  return (
    <>
      <ambientLight intensity={1.6} />
      <directionalLight position={[3, 4, 4]} intensity={2.2} />
      <pointLight position={[-3, -1, 2]} intensity={14} distance={10} />
      <Float speed={0.9} rotationIntensity={0.18} floatIntensity={0.4}>
        <Core />
        <Torus args={[1.55, 0.025, 24, 160]} rotation={[0.35, 0.2, 0.2]}>
          <meshStandardMaterial transparent opacity={0.5} roughness={0.5} />
        </Torus>
        <Torus args={[1.85, 0.012, 20, 140]} rotation={[-0.25, 0.6, -0.4]}>
          <meshStandardMaterial transparent opacity={0.32} roughness={0.5} />
        </Torus>
        <Sphere args={[0.055, 12, 12]} position={[1.5, 0.35, 0.3]}>
          <meshStandardMaterial emissive={'#b83a32'} emissiveIntensity={2} />
        </Sphere>
        <Sphere args={[0.04, 12, 12]} position={[-1.25, -0.7, 0.4]}>
          <meshStandardMaterial emissive={'#5d8065'} emissiveIntensity={2} />
        </Sphere>
      </Float>
    </>
  );
}

export default function HeroOrb() {
  return (
    <div className="h-[420px] w-full sm:h-[520px]" aria-label="Animated protective SafeScroll orb">
      <Canvas camera={{ position: [0, 0, 4.5], fov: 40 }} dpr={[1, 1.5]} gl={{ antialias: true, alpha: true }}>
        <Scene />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.18} />
      </Canvas>
    </div>
  );
}
