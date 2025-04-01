import { ALLOWED_FILE_TYPES, FILE_SIZE_LIMITS } from '../config/constants.js';

export class FileValidator {
    static validateSingleFile(file) {
        if (!file) {
            throw new Error('No file selected');
        }

        if (!ALLOWED_FILE_TYPES.single.includes(file.type)) {
            throw new Error('Invalid file type. Please upload JSON, XML, or TXT files.');
        }

        if (file.size > FILE_SIZE_LIMITS.single) {
            throw new Error('File size exceeds 10MB limit.');
        }

        return true;
    }

    static validateZipFile(file) {
        if (!file) {
            throw new Error('No file selected');
        }

        if (!ALLOWED_FILE_TYPES.zip.includes(file.type)) {
            throw new Error('Invalid archive type. Please upload ZIP, RAR, or 7Z files.');
        }

        if (file.size > FILE_SIZE_LIMITS.zip) {
            throw new Error('File size exceeds 50MB limit.');
        }

        return true;
    }

    static validateTemplateContent(content) {
        if (!content || content.trim().length === 0) {
            throw new Error('Template content cannot be empty');
        }
        return true;
    }

    static validateAnalyzeData(data) {
        const requiredFields = ['filename', 'filepath', 'mode', 'model_id', 'template'];
        for (const field of requiredFields) {
            if (!data[field]) {
                throw new Error(`Missing required field: ${field}`);
            }
        }
        return true;
    }
}
