import { apiService } from '../utils/apiService.js'; 

export class UIHelper {
    static showProgress(previewArea) {
        previewArea.innerHTML = `
            <div class="progress mb-3">
                <div class="progress-bar" role="progressbar" style="width: 0%">
                    <span class="progress-text">0%</span>
                </div>
            </div>
            <div class="upload-status">Ready to upload...</div>
        `;
    }

    static updateProgress(progressEvent, previewArea) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        const progressBar = previewArea.querySelector('.progress-bar');
        const statusDiv = previewArea.querySelector('.upload-status');
        
        if (progressBar && statusDiv) {
            progressBar.style.width = `${percentCompleted}%`;
            progressBar.querySelector('.progress-text').textContent = `${percentCompleted}%`;
            statusDiv.textContent = 'Uploading...';
        }
    }

    static showSuccess(fileData, container) {
        // Convert the file size to a readable format
        const formatFileSize = (bytes) => {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        };
        // Get the file extension
        const getFileExtension = (filename) => {
            return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2);
        };
        // Create HTML with detailed information
        const infoHtml = `
            <div class="card mt-3">
                <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                    <span>File uploaded successfully</span>
                    <button type="button" class="btn btn-sm btn-danger delete-single-file" data-path="${fileData.save_path}">
                        Deleting file
                    </button>
                </div>
                <div class="card-body">
                    <table class="table table-sm mb-0">
                        <tbody>
                            <tr>
                                <th scope="row" style="width: 140px;">File name</th>
                                <td>${fileData.original_filename}</td>
                            </tr>
                            <tr>
                                <th scope="row">File size</th>
                                <td>${formatFileSize(fileData.file_size)}</td>
                            </tr>
                            <tr>
                                <th scope="row">File Type</th>
                                <td>${getFileExtension(fileData.original_filename).toUpperCase()}</td>
                            </tr>
                            <tr>
                                <th scope="row">Save Path</th>
                                <td><small class="text-muted">${fileData.save_path}</small></td>
                            </tr>
                            <tr>
                                <th scope="row">Unique file name</th>
                                <td><small class="text-muted">${fileData.unique_filename}</small></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        container.innerHTML = infoHtml;
    }

    static showError(message, element) {
        element.innerHTML = `
            <div class="alert alert-danger">
                ${message}
            </div>
        `;
    }

    static showLoading(element, message = 'Loading...') {
        let dots = '';
        const loadingInterval = setInterval(() => {
            dots = dots.length >= 3 ? '' : dots + '.';
            element.textContent = message + dots;
        }, 500);
        return loadingInterval;
    }

    static clearLoading(interval) {
        if (interval) {
            clearInterval(interval);
        }
    }

    static toggleButtons(buttons, disabled) {
        buttons.forEach(button => {
            button.disabled = disabled;
        });
    }


    static updateSingleFile(fileData, container, onDelete) {
        this.showSuccess(fileData, container);

        const deleteButton = container.querySelector('.delete-single-file');
        if (deleteButton) {
            deleteButton.addEventListener('click', async (e) => {
                const filePath = e.target.dataset.path;
                try {
                    const response = await apiService.deleteFile(filePath);
                    if (response.status === 200) {
                        container.innerHTML = '';
                        container.innerHTML = `
                            <div class="alert alert-success alert-dismissible fade show" role="alert">
                                File successfully deleted
                            </div>
                            <div class="text-center">
                                <label for="file-input" class="btn btn-primary">
                                    Re-upload the file again
                                    <input type="file" id="file-input" class="d-none" accept=".txt,.xml,.json">
                                </label>
                            </div>
                        `;


                        // Add event listener for new file input
                        const fileInput = container.querySelector('#file-input');
                        if (fileInput) {
                            fileInput.addEventListener('change', async (event) => {
                                const file = event.target.files[0];
                                if (file) {
                                    // Create a FormData object
                                    const formData = new FormData();
                                    formData.append('file', file);

                                    try {
                                        // Display upload progress
                                        UIHelper.showProgress(container);

                                        // Use apiService to upload files
                                        const uploadResponse = await apiService.uploadFile(formData, (progressEvent) => {
                                            UIHelper.updateProgress(progressEvent, container);
                                        });

                                        if (uploadResponse.status === 200) {
                                            // Call success callback (if any)
                                            if (typeof onDelete === 'function') {
                                                onDelete(filePath, uploadResponse.data);
                                            }
                                        }
                                    } catch (uploadError) {
                                        console.error('Error uploading file:', uploadError);
                                        this.showError(uploadError.message || 'File upload failed, please try again', container);
                                    }
                                }
                            });
                        }
                        
                        // If a delete callback is provided, call it
                        if (typeof onDelete === 'function') {
                            onDelete(filePath);
                        }
                    }
                } catch (error) {
                    console.error('Error deleting file:', error);
                    this.showError(error.message || 'Failed to delete the file, please try again', container);
                }
            });
        }
    }

    static updateFileList(files, container) {
        const fileListHtml = files.map(file => `
            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                <span class="file-name">${file.name}</span>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="file-list mt-3">
                <h6>List of unzipped files:</h6>
                <div class="list-group">
                    ${fileListHtml}
                </div>
            </div>
        `;
        // Add a click event listener for the delete button
        container.querySelectorAll('.delete-file').forEach(button => {
            button.addEventListener('click', async (e) => {
                const filePath = e.target.dataset.path;
                try {
                    // Use apiService to send a delete request
                    const response = await apiService.deleteFile(filePath);
                    if (response.status === 200) {
                        // Remove the file item from the DOM
                        const fileItem = e.target.closest('.list-group-item');
                        fileItem.remove();
                        
                        // Remove the file from the files array
                        const fileIndex = files.findIndex(f => f.path === filePath);
                        if (fileIndex !== -1) {
                            files.splice(fileIndex, 1);
                        }
                    }
                } catch (error) {
                    console.error('Error deleting file:', error);
                    alert(error.message || 'Failed to delete the file, please try again');
                }
            });
        });
    }
}
