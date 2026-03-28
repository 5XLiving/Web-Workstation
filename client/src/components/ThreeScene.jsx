import React, { Suspense, useEffect, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stats } from '@react-three/drei'
import Room from './Room'
import Table from './Table'
import Monitor from './Monitor'
import PreviewWall from './PreviewWall'

export default function ThreeScene({ onMonitorClick, sceneRequest, debug }) {
  const [terrain, setTerrain] = useState(null)

  useEffect(() => {
    if (!sceneRequest) return
    const { command, result, error, mode } = sceneRequest
    // Log receipt
    if (debug && debug.pushLog) debug.pushLog({ time: new Date().toISOString(), stage: 'parser', level: 'info', message: 'Scene request received', details: { command, mode, error } })

    try {
      // Parse terrain build commands: e.g. "build 7200 x 7200 terrain"
      const txt = (command || '').trim()
      const re = /build(?:\s+a)?\s+(\d+)\s*[x×]\s*(\d+)\s*terrain/i
      const m = txt.match(re)
      if (m) {
        const w = parseInt(m[1], 10)
        const h = parseInt(m[2], 10)
        // Scale down large numbers to a manageable size for web rendering
        const scaleFactor = 0.01 // map units -> scene meters
        const width = Math.max(1, w * scaleFactor)
        const height = Math.max(1, h * scaleFactor)
        const segments = 64
        setTerrain({ width, height, segments })
        if (debug && debug.pushLog) debug.pushLog({ time: new Date().toISOString(), stage: 'scene', level: 'info', message: 'Terrain build scheduled', details: { width, height, segments, source: mode || (error ? 'local-preview' : 'backend') } })
        return
      }

      // If unknown command, clear terrain and log
      setTerrain(null)
      if (debug && debug.pushLog) debug.pushLog({ time: new Date().toISOString(), stage: 'parser', level: 'error', message: 'Unsupported command', details: { command } })
    } catch (e) {
      setTerrain(null)
      const msg = e && e.message ? e.message : String(e)
      if (debug && debug.pushLog) debug.pushLog({ time: new Date().toISOString(), stage: 'scene', level: 'error', message: 'Scene build failed', details: { command: sceneRequest.command, error: msg } })
      console.error('Scene build failed:', e)
    }
  }, [sceneRequest, debug])

  return (
    <div className="canvas-wrap">
      <Canvas shadows camera={{ position: [0, 2, 5], fov: 60 }}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 10, 5]} intensity={0.8} castShadow />
        <Suspense fallback={null}>
          <Room />
          <Table position={[0, 0, 0]} />
          <Monitor position={[0, 0.9, 0.8]} onClick={() => onMonitorClick({ target: 'monitor' })} />
          <PreviewWall position={[-2.4, 1.2, 0]} />
          {terrain && (
            <mesh position={[0, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
              <planeGeometry args={[terrain.width, terrain.height, terrain.segments, terrain.segments]} />
              <meshStandardMaterial color="#7bb26a" roughness={0.8} />
            </mesh>
          )}
        </Suspense>
        <OrbitControls enableDamping dampingFactor={0.1} rotateSpeed={0.6} />
        <Stats />
      </Canvas>
    </div>
  )
}
