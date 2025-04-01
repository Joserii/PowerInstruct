import { API_ENDPOINTS } from '../config/constants.js';

const axios = window.axios;

export class APIService {
    constructor() {
        this.axios = axios.create({
            timeout: 100000,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        this.axios.interceptors.request.use(
            config => {
                return config;
            },
            error => {
                return Promise.reject(error);
            }
        );

        this.axios.interceptors.response.use(
            response => {
                return response;
            },
            error => {
                return Promise.reject(this.handleError(error));
            }
        );
    }

    handleError(error) {
        if (error.response) {
            return {
                message: error.response.data.message || 'Server Error',
                status: error.response.status
            };
        } else if (error.request) {
            return {
                message: 'Network error, please check your network connection',
                status: 0
            };
        } else {
            return {
                message: error.message,
                status: -1
            };
        }
    }

    async uploadFile(formData, onProgress) {
        return this.axios.post(API_ENDPOINTS.UPLOAD, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: onProgress
        });
    }

    async deleteFile(filePath) {
        return this.axios.delete(`${API_ENDPOINTS.DELETE_FILE}/${encodeURIComponent(filePath)}`);
    }

    async uploadZipFile(formData, onProgress) {
        return this.axios.post(API_ENDPOINTS.UPLOAD_ZIP, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: onProgress
        });
    }

    async fetchTemplates() {
        return this.axios.get(API_ENDPOINTS.TEMPLATES);
    }

    async fetchJsonContent(filePath) {
        return await axios.get(`/api/json-content?path=${encodeURIComponent(filePath)}`);
    }

    async saveTemplate(templateData) {
        return this.axios.post(API_ENDPOINTS.SAVE_TEMPLATE, templateData);
    }

    async analyzeFile(analyzeData) {
        return this.axios.post(API_ENDPOINTS.ANALYZE, analyzeData);
    }

    async executeCode(codeData) {
        return this.axios.post(API_ENDPOINTS.EXECUTE, codeData);
    }

    async mergeTemplate(data) {
        try {
            const response = await axios.post(API_ENDPOINTS.MERGE_TEMPLATE, data);
            return response;
        } catch (error) {
            throw this.handleApiError(error);
        }
    }
}

export const apiService = new APIService();
