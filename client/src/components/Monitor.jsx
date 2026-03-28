import React from 'react'

export default function Monitor({ position = [0, 0, 0], onClick }) {
  return (
    <group position={position}>
      {/* Screen */}
      <mesh position={[0, 0.2, 0]} castShadow onClick={onClick}>
        <boxGeometry args={[0.9, 0.5, 0.04]} />
        <meshStandardMaterial color="#0b1320" />
      </mesh>

      {/* Stand */}
      <mesh position={[0, 0.05, 0.02]}>
        <boxGeometry args={[0.12, 0.2, 0.12]} />
        <meshStandardMaterial color="#1b2631" />
      </mesh>

      {/* Click hotspot - subtle transparent sphere for pointer */}
      <mesh position={[0, 0.2, 0.06]} onClick={onClick}>
        <sphereGeometry args={[0.25, 8, 8]} />
        <meshBasicMaterial transparent opacity={0.001} />
      </mesh>
    </group>
  )
}
