export const ALLOWED_FILE_TYPES = {
    single: ['application/json', 'text/xml', 'text/plain', 'application/xml'],
    zip: ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed']
};

export const FILE_SIZE_LIMITS = {
    single: 10 * 1024 * 1024, 
    zip: 50 * 1024 * 1024   
};

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

export const MODES = {
    PROMPT_CODEGEN: 'prompt-codegen',
    PROMPT: 'prompt',
    CODEGEN: 'codegen'
};


export const UI_CLASSES = {
    ACTIVE: 'active',
    BTN_PRIMARY: 'btn-primary',
    BTN_SECONDARY: 'btn-secondary',
    BTN_SUCCESS: 'btn-success',
    BTN_INFO: 'btn-info',
    BTN_WARNING: 'btn-warning',
    BTN_OUTLINE_PRIMARY: 'btn-outline-primary',
};
