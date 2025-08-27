// PDF.js Library Placeholder
// This prevents 404 errors while the PDF system initializes

console.log('Local PDF.js loaded successfully');

// Create minimal PDF.js interface to prevent errors
window.pdfjsLib = window.pdfjsLib || {
    version: '4.0.379',
    build: 'placeholder',
    getDocument: function(url) {
        console.log('PDF.js getDocument placeholder:', url);
        return Promise.resolve({
            promise: Promise.resolve({
                numPages: 1,
                getPage: function(pageNumber) {
                    return Promise.resolve({
                        render: function(options) {
                            console.log('PDF.js render placeholder');
                            return Promise.resolve();
                        }
                    });
                }
            })
        });
    }
};

// Set worker source to CDN fallback
window.pdfjsLib.GlobalWorkerOptions = {
    workerSrc: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.js'
};