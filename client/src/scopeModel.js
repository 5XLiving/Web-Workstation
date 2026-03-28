export const clientRoomScope = {
  account: {
    accountId: 'acct-5xliving-001',
    email: 'studio@5xliving.com',
    displayName: '5xLiving',
  },
  workspace: {
    workspaceId: 'ws-client-experience-01',
    accountId: 'acct-5xliving-001',
    name: 'Client Experience Workspace',
    packagePlan: 'Signature',
  },
  project: {
    projectId: 'proj-web-workstation-01',
    workspaceId: 'ws-client-experience-01',
    name: 'Web Workstation',
    sectorId: 'living-spaces',
    environmentId: 'sandbox',
  },
  room: {
    roomId: 'room-client-shell-01',
    projectId: 'proj-web-workstation-01',
    roomType: 'client-room',
  },
  environment: {
    environmentId: 'sandbox',
    label: 'Sandbox',
  },
  rules: {
    sectorId: 'living-spaces',
    codebookId: 'terrain-ops-v2',
    packId: 'living-spaces-core',
  },
}

export const devRoomScope = {
  account: {
    accountId: 'acct-5xliving-001',
    email: 'studio@5xliving.com',
    displayName: '5xLiving Internal Ops',
  },
  workspace: {
    workspaceId: 'ws-client-experience-01',
    accountId: 'acct-5xliving-001',
    name: 'Client Experience Workspace',
    packagePlan: 'Signature',
  },
  project: {
    projectId: 'proj-web-workstation-01',
    workspaceId: 'ws-client-experience-01',
    name: 'Web Workstation',
    sectorId: 'living-spaces',
    environmentId: 'sandbox',
  },
  room: {
    roomId: 'room-dev-hq-01',
    projectId: 'proj-web-workstation-01',
    roomType: 'dev-room',
  },
  environment: {
    environmentId: 'sandbox',
    label: 'Sandbox',
  },
  rules: {
    sectorId: 'living-spaces',
    codebookId: 'terrain-ops-v2',
    packId: 'living-spaces-core',
  },
}

export function getScopeBindings(scope) {
  return {
    accountId: scope?.account?.accountId || null,
    email: scope?.account?.email || null,
    displayName: scope?.account?.displayName || null,
    workspaceId: scope?.workspace?.workspaceId || null,
    workspaceAccountId: scope?.workspace?.accountId || null,
    workspaceName: scope?.workspace?.name || null,
    packagePlan: scope?.workspace?.packagePlan || scope?.workspace?.plan || null,
    plan: scope?.workspace?.packagePlan || scope?.workspace?.plan || null,
    projectId: scope?.project?.projectId || null,
    projectWorkspaceId: scope?.project?.workspaceId || null,
    projectName: scope?.project?.name || null,
    roomId: scope?.room?.roomId || null,
    roomProjectId: scope?.room?.projectId || null,
    roomType: scope?.room?.roomType || null,
    environmentId: scope?.environment?.environmentId || scope?.project?.environmentId || null,
    environmentLabel: scope?.environment?.label || null,
    sectorId: scope?.rules?.sectorId || scope?.project?.sectorId || null,
    codebookId: scope?.rules?.codebookId || null,
    packId: scope?.rules?.packId || null,
  }
}

export function validateScopeHierarchy(scope) {
  const bindings = getScopeBindings(scope)
  const relationships = {
    accountToWorkspace: Boolean(bindings.accountId && bindings.workspaceAccountId && bindings.accountId === bindings.workspaceAccountId),
    workspaceToProject: Boolean(bindings.workspaceId && bindings.projectWorkspaceId && bindings.workspaceId === bindings.projectWorkspaceId),
    projectToRoom: Boolean(bindings.projectId && bindings.roomProjectId && bindings.projectId === bindings.roomProjectId),
    projectToEnvironment: Boolean(bindings.projectId && bindings.environmentId && scope?.project?.environmentId === bindings.environmentId),
    projectToRules: Boolean(bindings.projectId && bindings.sectorId && scope?.project?.sectorId === bindings.sectorId),
  }

  return {
    bindings,
    allIdsPresent: Boolean(
      bindings.accountId &&
      bindings.workspaceId &&
      bindings.packagePlan &&
      bindings.projectId &&
      bindings.roomId &&
      bindings.roomType &&
      bindings.environmentId &&
      bindings.sectorId &&
      bindings.codebookId &&
      bindings.packId
    ),
    relationships,
    relationshipsAligned: Object.values(relationships).every(Boolean),
  }
}

export function getFriendlyScopeLabels(scope) {
  const bindings = getScopeBindings(scope)

  return {
    accountLabel: bindings.displayName || bindings.accountId || 'Unknown account',
    workspaceLabel: bindings.workspaceName || bindings.workspaceId || 'Unknown workspace',
    projectLabel: bindings.projectName || bindings.projectId || 'Unknown project',
    roomLabel: bindings.roomType === 'dev-room' ? 'Dev Room' : bindings.roomType === 'client-room' ? 'Client Room' : bindings.roomId || 'Room',
    environmentLabel: bindings.environmentLabel || bindings.environmentId || 'Environment',
    planLabel: bindings.packagePlan || 'Plan not set',
  }
}

export function formatScopeLine(scope) {
  const bindings = getScopeBindings(scope)
  return [bindings.accountId, bindings.workspaceId, bindings.projectId, bindings.roomId, bindings.environmentId].filter(Boolean).join(' / ')
}