import React from 'react'

export default function Room() {
  // Simple enclosed room: floor, four walls, ceiling
  return (
    <group>
      {/* Floor */}
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#f6f7f9" />
      </mesh>

      {/* Back wall */}
      <mesh position={[0, 1.5, -5]}>
        <boxGeometry args={[10, 3, 0.1]} />
        <meshStandardMaterial color="#e6e9ee" />
      </mesh>

      {/* Left wall */}
      <mesh position={[-5, 1.5, 0]}>
        <boxGeometry args={[0.1, 3, 10]} />
        <meshStandardMaterial color="#eef0f4" />
      </mesh>

      {/* Right wall */}
      <mesh position={[5, 1.5, 0]}>
        <boxGeometry args={[0.1, 3, 10]} />
        <meshStandardMaterial color="#eef0f4" />
      </mesh>

      {/* Ceiling */}
      <mesh position={[0, 3, 0]}>
        <boxGeometry args={[10, 0.1, 10]} />
        <meshStandardMaterial color="#fafbfc" />
      </mesh>
    </group>
  )
}
