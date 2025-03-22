const config = {
    API_BASE_URL: 'http://pind.mooo.com:8000/files',  
    USER: 'plansky',
    PASSWORD: 'plan23',
    DEFAULT_DIRECTORY: 'beispiele',
    DEFAULT_SHARE: 'MOKqe_oD',
    DEBUG: true  // Enable debug logging
};

// Add debug logging if enabled
if (config.DEBUG) {
    window.onerror = function(msg, url, lineNo, columnNo, error) {
        console.error('Window Error: ', {msg, url, lineNo, columnNo, error});
        return false;
    };
}

export default config;

