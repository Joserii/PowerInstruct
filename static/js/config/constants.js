// 文件类型常量
export const ALLOWED_FILE_TYPES = {
    single: ['application/json', 'text/xml', 'text/plain', 'application/xml'],
    zip: ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed']
};

// 文件大小限制
export const FILE_SIZE_LIMITS = {
    single: 10 * 1024 * 1024, // 10MB
    zip: 50 * 1024 * 1024     // 50MB
};

// API 端点
export const API_ENDPOINTS = {
    UPLOAD: '/upload',
    UPLOAD_ZIP: '/upload_zip',
    TEMPLATES: '/templates',
    SAVE_TEMPLATE: '/save_template',
    ANALYZE: '/analyze',
    EXECUTE: '/execute',
    DELETE_FILE: '/delete_file',
    MERGE_TEMPLATE: '/merge_template'
};

// 模式类型
export const MODES = {
    PROMPT_CODEGEN: 'prompt-codegen',
    PROMPT: 'prompt',
    CODEGEN: 'codegen'
};

// UI相关常量
export const UI_CLASSES = {
    ACTIVE: 'active',
    BTN_PRIMARY: 'btn-primary',
    BTN_SECONDARY: 'btn-secondary',
    BTN_SUCCESS: 'btn-success',
    BTN_INFO: 'btn-info',
    BTN_WARNING: 'btn-warning',
    BTN_OUTLINE_PRIMARY: 'btn-outline-primary',
    // ... 其他UI类名
};
