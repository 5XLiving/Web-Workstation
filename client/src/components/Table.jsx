import React from 'react'

export default function Table({ position = [0, 0, 0] }) {
  return (
    <group position={position}>
      {/* Table top: a round table */}
      <mesh position={[0, 0.8, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[1.2, 1.2, 0.12, 64]} />
        <meshStandardMaterial color="#2f3b4a" metalness={0.2} roughness={0.6} />
      </mesh>

      {/* Table leg */}
      <mesh position={[0, 0.4, 0]} castShadow>
        <cylinderGeometry args={[0.12, 0.12, 0.8, 32]} />
        <meshStandardMaterial color="#263238" />
      </mesh>
    </group>
  )
}
