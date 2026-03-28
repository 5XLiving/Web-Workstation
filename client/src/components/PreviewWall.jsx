import React from 'react'

export default function PreviewWall({ position = [0, 0, 0] }) {
  return (
    <group position={position}>
      <mesh position={[0, 0, 0]}>
        <planeGeometry args={[1.6, 1.0]} />
        <meshStandardMaterial color="#ffffff" emissive="#f8f9fb" />
      </mesh>
    </group>
  )
}
