import config from './config.js';

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

function getFileIcon(file) {
    if (file.isDir) return '📁';
    const ext = file.extension.toLowerCase();
    if (['.jpg', '.jpeg', '.png', '.gif'].includes(ext)) return '🖼️';
    if (['.pdf'].includes(ext)) return '📄';
    return '📝';
}

function getPreviewUrl(file) {
    return `${config.API_BASE_URL}/api/public/dl/${config.DEFAULT_SHARE}/${encodeURIComponent(file.name)}?inline=true`;
}

function renderFiles(files) {
    return files.map(file => {
        const isPreviewable = ['.jpg', '.jpeg', '.png', '.gif', '.pdf'].includes(file.extension.toLowerCase());
        return `
        <div class="file-item">
            <div class="file-icon">${getFileIcon(file)}</div>
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">
                    ${formatFileSize(file.size)} • 
                    ${formatDate(file.modified)}
                    ${file.resolution ? ` • ${file.resolution.width}×${file.resolution.height}` : ''}
                </div>
                ${isPreviewable ? `
                <div class="preview">
                    ${file.extension.toLowerCase() === '.pdf' ? `
                        <iframe src="${getPreviewUrl(file)}" class="preview-pdf" title="${file.name}"></iframe>
                    ` : `
                        <img src="${getPreviewUrl(file)}" alt="${file.name}" class="preview-image">
                    `}
                </div>
                ` : ''}
            </div>
        </div>
    `}).join('');
}

async function loadFiles() {
    const content = document.getElementById('content');
    try {
        const response = await fetch(`${config.API_BASE_URL}/api/public/share/${config.DEFAULT_SHARE}`);
        if (!response.ok) throw new Error('Failed to fetch files');
        
        const data = await response.json();
        content.innerHTML = renderFiles(data.items || []);
    } catch (error) {
        if (config.DEBUG) {
            console.error('Error loading files:', error);
        }
        content.innerHTML = `<div class="error">Error loading files: ${error.message}</div>`;
    }
}

// Load files when page loads
loadFiles();