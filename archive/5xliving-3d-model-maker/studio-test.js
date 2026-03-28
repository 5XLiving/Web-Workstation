// Minimal test harness that uses the existing window.apiClient
// Runs a series of calls and prints JSON to the debug panel.

const out = document.getElementById('output');
function log(obj) {
  const time = new Date().toISOString();
  out.textContent += `\n[${time}] ${JSON.stringify(obj, null, 2)}\n`;
  out.scrollTop = out.scrollHeight;
}

async function runFlow() {
  out.textContent = '(running)\n';

  try {
    log({ step: 'generate3DModel - request' });
    const gen = await window.apiClient.generate3DModel({ prompt: 'Test pet model', modelType: 'pet' });
    log({ step: 'generate3DModel - response', gen });

    log({ step: 'saveAsset - request' });
    const saved = await window.apiClient.saveAsset({ title: 'Test Asset', modelUrl: gen.modelUrl || null });
    log({ step: 'saveAsset - response', saved });

    log({ step: 'getSavedAssets - request' });
    const list = await window.apiClient.getSavedAssets({ limit: 10, offset: 0 });
    log({ step: 'getSavedAssets - response', list });

    const assetId = saved.assetId || (list.items && list.items[0] && list.items[0].assetId) || null;
    log({ chosenAssetId: assetId });

    if (assetId) {
      log({ step: 'sendToDressingRoom - request', assetId });
      const dr = await window.apiClient.sendToDressingRoom(assetId, { openImmediately: false });
      log({ step: 'sendToDressingRoom - response', dr });

      log({ step: 'exportToUnity - request', assetId });
      const u = await window.apiClient.exportToUnity(assetId, { format: 'glb' });
      log({ step: 'exportToUnity - response', u });

      log({ step: 'exportToPrinter - request', assetId });
      const p = await window.apiClient.exportToPrinter(assetId, { format: 'stl' });
      log({ step: 'exportToPrinter - response', p });
    } else {
      log({ warning: 'No assetId available; skipping dressing room and export tests.' });
    }

    log({ done: true });
  } catch (err) {
    log({ error: String(err), stack: err.stack });
  }
}

document.getElementById('btn-run-flow').addEventListener('click', runFlow);
document.getElementById('btn-clear').addEventListener('click', () => { out.textContent = ''; });
