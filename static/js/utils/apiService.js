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

        // 添加请求拦截器
        this.axios.interceptors.request.use(
            config => {
                // 在发送请求之前做些什么
                return config;
            },
            error => {
                return Promise.reject(error);
            }
        );

        // 添加响应拦截器
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
            // 服务器响应出错
            return {
                message: error.response.data.message || '服务器错误',
                status: error.response.status
            };
        } else if (error.request) {
            // 请求未收到响应
            return {
                message: '网络错误，请检查您的网络连接',
                status: 0
            };
        } else {
            // 请求配置出错
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
