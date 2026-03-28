import React, { createContext, useContext, useMemo, useState } from 'react'
import { clientRoomScope, devRoomScope, getFriendlyScopeLabels, getScopeBindings, validateScopeHierarchy } from './scopeModel'
import sendWorkerCommand from './api/api'

const WorkstationBridgeContext = createContext(null)

function timeStamp() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function createJobId(prefix = 'JR') {
  return `${prefix}-${String(Date.now()).slice(-5)}`
}

function canClientHandleLocally(parsed) {
  return parsed.commandType === 'briefing' || parsed.commandType === 'snapshot'
}

export function parseWorkstationCommand(input) {
  const normalized = input.trim().toLowerCase()
  const terrainMatch = normalized.match(/build(?:\s+a)?\s+(\d+)\s*[x×]\s*(\d+)\s+terrain\b/) || normalized.match(/build(?:\s+a)?\s+terrain(?:\s+size:)?(?:\s*(\d+)\s*[x×]\s*(\d+))?/) || normalized.match(/build(?:\s+a)?\s+terrain\s+size:\s*(\d+)\s*[x×]\s*(\d+)/)

  if (terrainMatch) {
    const width = terrainMatch[1] ? Number.parseInt(terrainMatch[1], 10) : null
    const height = terrainMatch[2] ? Number.parseInt(terrainMatch[2], 10) : null

    return {
      supported: true,
      commandType: 'terrain',
      label: 'Terrain build',
      terrainSize: width && height ? { width, height } : null,
    }
  }

  if (normalized === 'workspace briefing') {
    return {
      supported: true,
      commandType: 'briefing',
      label: 'Workspace briefing',
      terrainSize: null,
    }
  }

  if (normalized === 'environment snapshot') {
    return {
      supported: true,
      commandType: 'snapshot',
      label: 'Environment snapshot',
      terrainSize: null,
    }
  }

  return {
    supported: true,
    commandType: 'worker',
    label: 'Dev Room request',
    terrainSize: null,
  }
}

export function buildDispatchPayload({ command, jobId, parsed, targetContext }) {
  const scopeBindings = getScopeBindings(targetContext)

  return {
    jobId,
    command,
    action: parsed.commandType,
    workerRequest: {
      company: '5xLiving',
      project: 'VR Workstation',
      module: 'devroom',
      message: command,
    },
    script:
      'sendScopedRequestToSharedWorker(company, project, module, message)'
    ,
    parameters: {
      terrainSize: parsed.terrainSize,
      label: parsed.label,
    },
    targetScope: {
      accountId: scopeBindings.accountId,
      workspaceId: scopeBindings.workspaceId,
      projectId: scopeBindings.projectId,
      roomId: scopeBindings.roomId,
      roomType: scopeBindings.roomType,
      environmentId: scopeBindings.environmentId,
      sectorId: scopeBindings.sectorId,
      codebookId: scopeBindings.codebookId,
      packId: scopeBindings.packId,
      packagePlan: scopeBindings.packagePlan,
    },
  }
}

export function validateDispatchRequest({ parsed, targetContext }) {
  const scopeState = validateScopeHierarchy(targetContext)
  const scopeComplete = scopeState.allIdsPresent && scopeState.relationshipsAligned
  const codebookLoaded = Boolean(scopeState.bindings.sectorId && scopeState.bindings.codebookId && scopeState.bindings.packId)
  const approvalNeeded = scopeState.bindings.environmentId === 'production'
  const supported = parsed.supported

  const issues = []
  if (!scopeState.allIdsPresent) {
    issues.push('Target scope is missing one or more required IDs.')
  }
  if (!scopeState.relationshipsAligned) {
    issues.push('Scope hierarchy is misaligned across account, workspace, project, room, environment, or rules.')
  }
  if (!codebookLoaded) {
    issues.push('Rules binding is incomplete. Sector, codebook, and pack IDs are required.')
  }
  if (!supported) {
    issues.push('Command is not supported by the local parser.')
  }

  return {
    scopeCheck: scopeComplete,
    hierarchyCheck: scopeState.relationshipsAligned,
    ruleCheck: codebookLoaded,
    approvalNeeded,
    supported,
    passes: scopeComplete && codebookLoaded && supported,
    issues,
    scopeBindings: scopeState.bindings,
  }
}

function createExecutionResult({ command, parsed, payload, targetContext, status }) {
  if (status === 'failed') {
    return null
  }

  const scopeBindings = getScopeBindings(targetContext)
  const friendlyLabels = getFriendlyScopeLabels(targetContext)

  if (parsed.commandType === 'terrain') {
    return {
      preview: `Terrain preview ready for ${parsed.terrainSize ? `${parsed.terrainSize.width} x ${parsed.terrainSize.height}` : 'default terrain footprint'}.`,
      scriptReturned: payload.script,
      buildLog: [
        `Account scope: ${scopeBindings.accountId}`,
        `Workspace target: ${scopeBindings.workspaceId}`,
        `Project target: ${scopeBindings.projectId}`,
        `Room binding: ${scopeBindings.roomId} (${scopeBindings.roomType})`,
        `Rules binding: ${scopeBindings.sectorId} / ${scopeBindings.codebookId} / ${scopeBindings.packId}`,
        'Local terrain preview assembled.',
      ],
      artifactType: 'terrain-preview',
    }
  }

  if (parsed.commandType === 'briefing') {
    return {
      preview: `Workspace briefing prepared for ${friendlyLabels.projectLabel}.`,
      scriptReturned: payload.script,
      buildLog: [
        `Scope bound to ${scopeBindings.workspaceId} / ${scopeBindings.projectId}.`,
        'Local briefing package attached to the command result.',
      ],
      artifactType: 'briefing-package',
    }
  }

  if (parsed.commandType === 'snapshot') {
    return {
      preview: `Environment snapshot prepared for ${friendlyLabels.environmentLabel}.`,
      scriptReturned: payload.script,
      buildLog: [
        `Room target: ${scopeBindings.roomId}.`,
        'Local snapshot summary attached to the command result.',
      ],
      artifactType: 'environment-snapshot',
    }
  }

  return null
}

export function WorkstationBridgeProvider({ children }) {
  const [activeExecution, setActiveExecution] = useState(null)
  const [executionEvents, setExecutionEvents] = useState([])
  const [resultsByJob, setResultsByJob] = useState({})
  const [hqQueue, setHqQueue] = useState([])
  const [clientFlowState, setClientFlowState] = useState({
    status: 'Idle',
    request: null,
    failureReason: null,
    jobId: null,
  })

  function appendEvent(stage, message, meta = {}) {
    setExecutionEvents((current) => [
      {
        id: `event-${Date.now()}-${current.length}`,
        time: timeStamp(),
        stage,
        message,
        ...meta,
      },
      ...current,
    ].slice(0, 16))
  }

  function queueHqJob(job) {
    setHqQueue((current) => [job, ...current.filter((entry) => entry.id !== job.id)].slice(0, 16))
  }

  function updateHqJob(jobId, patch) {
    setHqQueue((current) => current.map((job) => (job.id === jobId ? { ...job, ...patch } : job)))
  }

  async function dispatchCommand({ jobId, command, source, targetContext, payload, validation, onStatus }) {
    const parsed = parseWorkstationCommand(command)
    const startedAt = timeStamp()
    const resolvedPayload = payload || buildDispatchPayload({ command, jobId, parsed, targetContext })
    const resolvedValidation = validation || validateDispatchRequest({ parsed, targetContext })

    if (!resolvedValidation.passes) {
      const failedAt = timeStamp()
      const failureReason = resolvedValidation.issues.join(' ')
      const failedState = {
        jobId,
        command,
        source,
        parsed,
        payload: resolvedPayload,
        targetContext,
        validation: resolvedValidation,
        result: { failureReason },
        status: 'Failed',
        startedAt,
        completedAt: null,
        failedAt,
      }

      setActiveExecution(failedState)
      setResultsByJob((current) => ({ ...current, [jobId]: failedState.result }))
      appendEvent('Validation', `Job ${jobId} failed validation before dispatch.`, { jobId, command })
      onStatus?.('Failed', failedState.result)
      return { status: 'Failed', parsed, failedAt, result: failedState.result }
    }

    setActiveExecution({
      jobId,
      command,
      source,
      parsed,
      payload: resolvedPayload,
      targetContext,
      validation: resolvedValidation,
      result: null,
      status: 'Dispatched',
      startedAt,
      completedAt: null,
      failedAt: null,
    })

    appendEvent('Dispatch', `Job ${jobId} dispatched from ${source}.`, { jobId, command })
    onStatus?.('Dispatched')

    return new Promise((resolve) => {
      window.setTimeout(() => {
        setActiveExecution((current) => ({ ...current, status: 'Running' }))
        appendEvent('Execution', `Runner confirmed start for job ${jobId}.`, { jobId, command })
        onStatus?.('Running')

        window.setTimeout(() => {
          if (!parsed.supported) {
            const failedAt = timeStamp()
            const result = { failureReason: 'Shared worker request was rejected before execution.' }
            const nextState = {
              jobId,
              command,
              source,
              parsed,
              payload: resolvedPayload,
              targetContext,
              validation: resolvedValidation,
              result,
              status: 'Failed',
              startedAt,
              completedAt: null,
              failedAt,
            }

            setActiveExecution(nextState)
            setResultsByJob((current) => ({ ...current, [jobId]: result }))
            appendEvent('Execution', `Job ${jobId} failed during local execution.`, { jobId, command })
            onStatus?.('Failed', result)
            resolve({ status: 'Failed', parsed, startedAt, failedAt, result })
            return
          }

          const previewReadyAt = timeStamp()
          const result = createExecutionResult({ command, parsed, payload: resolvedPayload, targetContext, status: 'Preview Ready' })
          const previewState = {
            jobId,
            command,
            source,
            parsed,
            payload: resolvedPayload,
            targetContext,
            validation: resolvedValidation,
            result,
            status: 'Preview Ready',
            startedAt,
            completedAt: null,
            failedAt: null,
            previewReadyAt,
          }

          setActiveExecution(previewState)
          setResultsByJob((current) => ({ ...current, [jobId]: result }))
          appendEvent('Preview', `Preview ready for job ${jobId}.`, { jobId, command })
          onStatus?.('Preview Ready', result)

          window.setTimeout(() => {
            const completedAt = timeStamp()
            const nextState = {
              ...previewState,
              status: result ? 'Completed' : 'Failed',
              completedAt: result ? completedAt : null,
              failedAt: result ? null : completedAt,
            }

            setActiveExecution(nextState)
            appendEvent(
              'Execution',
              result ? `Job ${jobId} completed with an attached result.` : `Job ${jobId} failed because no result was attached.`,
              { jobId, command }
            )
            onStatus?.(result ? 'Completed' : 'Failed', result || { failureReason: 'No result attached.' })
            resolve({
              status: result ? 'Completed' : 'Failed',
              parsed,
              startedAt,
              completedAt: result ? completedAt : null,
              result: result || { failureReason: 'No result attached.' },
            })
          }, 350)
        }, 350)
      }, 250)
    })
  }

  async function executeHqJob({ jobId, actionLabel = 'Run' }) {
    const job = hqQueue.find((entry) => entry.id === jobId)
    if (!job) {
      return null
    }

    updateHqJob(jobId, { status: 'Dispatched' })
    appendEvent('HQ', `HQ ${actionLabel.toLowerCase()} requested for job ${jobId}.`, { jobId, command: job.command })

    const result = await dispatchCommand({
      jobId,
      command: job.command,
      payload: job.payload,
      source: 'dev-room',
      targetContext: job.targetContext,
      validation: job.validation,
      onStatus: (nextStatus) => {
        updateHqJob(jobId, { status: nextStatus })
      },
    })

    updateHqJob(jobId, {
      status: result.status,
      result: result.result,
      failureReason: result.result?.failureReason || null,
    })

    return result
  }

  function holdHqJob(jobId) {
    updateHqJob(jobId, { status: 'Held' })
    appendEvent('HQ', `Job ${jobId} moved to held state.`, { jobId })
  }

  function resetHqJob(jobId) {
    updateHqJob(jobId, { status: 'Queued' })
    appendEvent('HQ', `Job ${jobId} reset to queued state.`, { jobId })
  }

  function createHqJobFromCommand({ command, owner, source, targetContext, failureReason = null, localState = null, priority = 'Normal' }) {
    const jobId = createJobId('JR')
    const parsed = parseWorkstationCommand(command)
    const payload = buildDispatchPayload({ command, jobId, parsed, targetContext })
    const validation = validateDispatchRequest({ parsed, targetContext })
    const scopeBindings = getScopeBindings(targetContext)

    const job = {
      id: jobId,
      command,
      owner,
      source,
      status: 'Queued',
      priority,
      commandType: parsed.commandType,
      targetContext,
      scopeBindings,
      failureReason,
      localState,
      payload,
      validation,
      result: null,
    }

    queueHqJob(job)
    return job
  }

  async function submitClientRequest({ command, targetContext = devRoomScope, localState }) {
    const parsed = parseWorkstationCommand(command)
    const workerJobId = createJobId('WK')
    const payload = buildDispatchPayload({ command, jobId: workerJobId, parsed, targetContext })
    const validation = validateDispatchRequest({ parsed, targetContext })
    const startedAt = timeStamp()

    appendEvent('Dev Room', `Dev Room request received: ${command}`, { command })
    setClientFlowState({ status: 'Dispatching to shared worker', request: command, failureReason: null, jobId: workerJobId })
    setActiveExecution({
      jobId: workerJobId,
      command,
      source: 'dev-room',
      parsed,
      payload,
      targetContext,
      validation,
      result: null,
      status: 'Dispatched',
      startedAt,
      completedAt: null,
      failedAt: null,
    })
    appendEvent('Dispatch', `Posting job ${workerJobId} to the shared 5xLiving worker.`, { jobId: workerJobId, command })

    try {
      const backendResult = await sendWorkerCommand(payload.workerRequest)
      const completedAt = timeStamp()
      const normalizedResult = {
        reply: backendResult?.reply || backendResult?.message || '',
        preview: backendResult?.reply || backendResult?.message || 'Shared worker replied.',
        artifactType: 'worker-response',
        buildLog: [
          `Company: ${payload.workerRequest.company}`,
          `Project: ${payload.workerRequest.project}`,
          `Module: ${payload.workerRequest.module}`,
        ],
        workerResponse: backendResult?.workerResponse || backendResult || null,
      }
      const completedState = {
        jobId: backendResult?.jobId || workerJobId,
        command,
        source: 'dev-room',
        parsed,
        payload,
        targetContext,
        validation,
        result: normalizedResult,
        status: 'Completed',
        startedAt,
        completedAt,
        failedAt: null,
      }

      setActiveExecution(completedState)
      setResultsByJob((current) => ({ ...current, [completedState.jobId]: normalizedResult }))
      setClientFlowState({ status: 'Completed', request: command, failureReason: null, jobId: completedState.jobId })
      appendEvent('Worker', `Shared worker replied for job ${completedState.jobId}.`, { jobId: completedState.jobId, command })
      return { status: 'Completed', jobId: completedState.jobId, result: normalizedResult }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error)
      const failedAt = timeStamp()
      const failedResult = { failureReason: message }
      const failedState = {
        jobId: workerJobId,
        command,
        source: 'dev-room',
        parsed,
        payload,
        targetContext,
        validation,
        result: failedResult,
        status: 'Failed',
        startedAt,
        completedAt: null,
        failedAt,
      }

      setActiveExecution(failedState)
      setResultsByJob((current) => ({ ...current, [workerJobId]: failedResult }))
      setClientFlowState({ status: 'Failed', request: command, failureReason: message, jobId: workerJobId })
      appendEvent('Worker', `Shared worker failed job ${workerJobId}: ${message}`, { jobId: workerJobId, command })
      return { status: 'Failed', jobId: workerJobId, result: failedResult }
    }
  }

  const value = useMemo(
    () => ({
      activeExecution,
      clientFlowState,
      clientTargetContext: devRoomScope,
      createHqJobFromCommand,
      dispatchCommand,
      executeHqJob,
      executionEvents,
      holdHqJob,
      hqQueue,
      resetHqJob,
      resultsByJob,
      submitClientRequest,
      updateHqJob,
    }),
    [activeExecution, clientFlowState, executionEvents, hqQueue, resultsByJob]
  )

  return <WorkstationBridgeContext.Provider value={value}>{children}</WorkstationBridgeContext.Provider>
}

export function useWorkstationBridge() {
  const context = useContext(WorkstationBridgeContext)
  if (!context) {
    throw new Error('useWorkstationBridge must be used within WorkstationBridgeProvider')
  }

  return context
}