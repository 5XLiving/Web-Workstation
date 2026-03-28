/**
 * API Client for 5XLiving 3D Virtual Studio Backend
 *
 * Main flow:
 * Prompt/Image -> AI 3D generation -> Save -> Send to Dressing Room / Export
 *
 * Plans:
 * FREE, YEAR, VIP
 */

const API_BASE_URL = 'http://localhost:5000/api';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('5xliving_token') || 'FREE';
        this.plan = null;
        this.quotas = null;
        this.userId = localStorage.getItem('5xliving_user_id') || null;
    }

    // ===================================
    // INTERNAL HELPERS
    // ===================================

    async _post(path, payload = {}) {
        const response = await fetch(`${API_BASE_URL}${path}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            if (data.quotaExceeded) {
                throw new Error(`Quota exceeded: ${data.error}`);
            }
            throw new Error(data.error || `Request failed: ${path}`);
        }

        return data;
    }

    async _get(path) {
        const response = await fetch(`${API_BASE_URL}${path}`);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.error || `Request failed: ${path}`);
        }

        return data;
    }

    // ===================================
    // TOKEN / PLAN
    // ===================================

    async verifyToken(token) {
        const data = await this._post('/auth/verify', { token });

        if (!data.ok) {
            throw new Error(data.error || 'Token verification failed');
        }

        this.token = token;
        this.plan = data.plan || null;
        this.quotas = data.dailyRemaining || null;
        this.userId = data.userId || this.userId;

        localStorage.setItem('5xliving_token', token);
        if (this.userId) {
            localStorage.setItem('5xliving_user_id', this.userId);
        }

        return data;
    }

    getToken() {
        return this.token;
    }

    getPlan() {
        return this.plan;
    }

    getQuotas() {
        return this.quotas;
    }

    getUserId() {
        return this.userId;
    }

    // ===================================
    // IMAGE GENERATION
    // ===================================

    async generateImage(prompt, options = {}) {
        return this._post('/image/generate', {
            token: this.token,
            prompt,
            style: options.style || 'realistic',
            aspect: options.aspect || '1:1',
            negativePrompt: options.negativePrompt || '',
            referenceImageDataUrl: options.referenceImageDataUrl || null
        });
    }

    // ===================================
    // 3D MODEL GENERATION (MAIN)
    // Supports:
    // - prompt only
    // - image only
    // - prompt + image
    // ===================================

    async generate3DModel(input = {}) {
        /**
         * input = {
         *   prompt?: string,
         *   imageDataUrl?: string,
         *   modelType?: 'humanoid' | 'pet' | 'prop' | 'vehicle' | 'auto',
         *   style?: string,
         *   autoRig?: boolean,
         *   rigType?: 'humanoid_rigid' | 'pet_rigid' | 'none',
         *   generateTextures?: boolean,
         *   generateMaterials?: boolean,
         *   exportFormat?: 'glb' | 'fbx' | 'usd',
         *   title?: string,
         *   tags?: string[]
         * }
         */

        return this._post('/studio/generate-3d', {
            token: this.token,
            userId: this.userId,
            prompt: input.prompt || '',
            imageDataUrl: input.imageDataUrl || null,
            modelType: input.modelType || 'auto',
            style: input.style || 'stylized',
            autoRig: input.autoRig !== false,
            rigType: input.rigType || 'humanoid_rigid',
            generateTextures: input.generateTextures !== false,
            generateMaterials: input.generateMaterials !== false,
            exportFormat: input.exportFormat || 'glb',
            title: input.title || 'Untitled Model',
            tags: input.tags || []
        });
    }

    // ===================================
    // AUTO RIG / RE-RIG
    // Use if you generate/import a model first,
    // then want to add a rigid skeleton later.
    // ===================================

    async autoRigModel(assetId, options = {}) {
        return this._post('/studio/auto-rig', {
            token: this.token,
            userId: this.userId,
            assetId,
            rigType: options.rigType || 'humanoid_rigid',
            preserveMaterials: options.preserveMaterials !== false,
            generateSockets: options.generateSockets !== false
        });
    }

    // ===================================
    // SAVE GENERATED ASSET TO LIBRARY
    // ===================================

    async saveAsset(asset = {}) {
        /**
         * asset = {
         *   assetId?: string,
         *   title: string,
         *   description?: string,
         *   modelUrl?: string,
         *   previewImageUrl?: string,
         *   modelType?: string,
         *   rigType?: string,
         *   sourcePrompt?: string,
         *   sourceImageDataUrl?: string,
         *   tags?: string[],
         *   metadata?: object
         * }
         */

        return this._post('/studio/assets/save', {
            token: this.token,
            userId: this.userId,
            asset
        });
    }

    async getSavedAssets(options = {}) {
        const query = new URLSearchParams({
            token: this.token,
            userId: this.userId || '',
            limit: String(options.limit || 50),
            offset: String(options.offset || 0)
        });

        return this._get(`/studio/assets?${query.toString()}`);
    }

    async getAssetById(assetId) {
        return this._get(`/studio/assets/${assetId}?token=${encodeURIComponent(this.token)}&userId=${encodeURIComponent(this.userId || '')}`);
    }

    async deleteAsset(assetId) {
        return this._post('/studio/assets/delete', {
            token: this.token,
            userId: this.userId,
            assetId
        });
    }

    // ===================================
    // SEND TO DRESSING ROOM
    // ===================================

    async sendToDressingRoom(assetId, options = {}) {
        /**
         * options = {
         *   targetCharacterId?: string,
         *   slotMap?: object,
         *   openImmediately?: boolean
         * }
         */

        return this._post('/studio/send-to-dressing-room', {
            token: this.token,
            userId: this.userId,
            assetId,
            targetCharacterId: options.targetCharacterId || null,
            slotMap: options.slotMap || {},
            openImmediately: options.openImmediately !== false
        });
    }

    // ===================================
    // EXPORTS
    // ===================================

    async exportToUnity(assetId, options = {}) {
        /**
         * options = {
         *   format?: 'glb' | 'fbx' | 'usd',
         *   includeRig?: boolean,
         *   includeTextures?: boolean,
         *   unityPreset?: 'prop' | 'character' | 'pet' | 'generic'
         * }
         */

        return this._post('/studio/export/unity', {
            token: this.token,
            userId: this.userId,
            assetId,
            format: options.format || 'glb',
            includeRig: options.includeRig !== false,
            includeTextures: options.includeTextures !== false,
            unityPreset: options.unityPreset || 'generic'
        });
    }

    async exportToPrinter(assetId, options = {}) {
        /**
         * options = {
         *   format?: 'stl' | 'obj' | 'usd',
         *   watertight?: boolean,
         *   solidify?: boolean,
         *   scaleMm?: number,
         *   splitParts?: boolean
         * }
         */

        return this._post('/studio/export/printer', {
            token: this.token,
            userId: this.userId,
            assetId,
            format: options.format || 'stl',
            watertight: options.watertight !== false,
            solidify: options.solidify !== false,
            scaleMm: options.scaleMm || 100,
            splitParts: options.splitParts || false
        });
    }

    // ===================================
    // JOBS
    // ===================================

    async getJobStatus(jobId) {
        return this._get(`/jobs/${jobId}`);
    }

    /**
     * Poll a job until it completes or fails.
     * @param {string} jobId
     * @param {(progress:number, job:object)=>void} onProgress
     * @param {object} options
     * @returns {Promise<object>} job.result
     */
    async pollJob(jobId, onProgress = null, options = {}) {
        const maxAttempts = options.maxAttempts || 240; // 240 * 500ms = 120s
        const intervalMs = options.intervalMs || 500;

        let attempts = 0;

        while (attempts < maxAttempts) {
            const job = await this.getJobStatus(jobId);

            if (onProgress) {
                onProgress(job.progress || 0, job);
            }

            if (job.status === 'done') {
                return job.result;
            }

            if (job.status === 'error') {
                throw new Error(job.error || 'Job failed');
            }

            await new Promise(resolve => setTimeout(resolve, intervalMs));
            attempts++;
        }

        throw new Error('Job timeout: generation took too long');
    }

    // ===================================
    // HIGH-LEVEL STUDIO FLOWS
    // ===================================

    /**
     * Full flow:
     * generate -> wait -> optionally save -> return final result
     */
    async generateAndSave3D(input = {}, saveOptions = {}, onProgress = null) {
        const job = await this.generate3DModel(input);
        const result = await this.pollJob(job.jobId, onProgress);

        const saved = await this.saveAsset({
            assetId: result.assetId || null,
            title: saveOptions.title || input.title || 'Untitled Model',
            description: saveOptions.description || '',
            modelUrl: result.modelUrl || null,
            previewImageUrl: result.previewImageUrl || null,
            modelType: result.modelType || input.modelType || 'auto',
            rigType: result.rigType || input.rigType || 'none',
            sourcePrompt: input.prompt || '',
            sourceImageDataUrl: input.imageDataUrl || null,
            tags: saveOptions.tags || input.tags || [],
            metadata: {
                generatedAt: new Date().toISOString(),
                style: input.style || 'stylized',
                autoRig: input.autoRig !== false
            }
        });

        return {
            generationJob: job,
            generationResult: result,
            savedAsset: saved
        };
    }

    /**
     * Full flow:
     * generate -> wait -> save -> send to dressing room
     */
    async generateSaveAndSendToDressingRoom(input = {}, saveOptions = {}, dressingOptions = {}, onProgress = null) {
        const bundle = await this.generateAndSave3D(input, saveOptions, onProgress);

        const assetId =
            bundle.savedAsset?.assetId ||
            bundle.generationResult?.assetId;

        if (!assetId) {
            throw new Error('No assetId available for dressing room handoff');
        }

        const dressing = await this.sendToDressingRoom(assetId, dressingOptions);

        return {
            ...bundle,
            dressingRoomResult: dressing
        };
    }
}

// Export singleton
const apiClient = new APIClient();

// Make available globally for non-module scripts
if (typeof window !== 'undefined') {
    window.apiClient = apiClient;
}

