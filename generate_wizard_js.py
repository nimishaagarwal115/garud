import os

file_path = r"c:\Users\agarw\OneDrive\Desktop\garud-app-garuda_backend-aba4bee89d84\static\js\product_upload_wizard.js"

new_js = """/**
 * Product Upload Wizard JavaScript
 * Handles the simplified 5-screen AI product upload flow
 */

class ProductUploadWizard {
    constructor() {
        this.uploadedImages = [];
        this.uploadedVideos = [];
        this.productData = {};
        
        // Expose instance globally
        window.wizard = this;

        this.initEventListeners();
    }
    
    // Helper to get CSRF token
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Base64 converter
    convertToBase64(file, callback) {
        const reader = new FileReader();
        reader.onloadend = () => callback(reader.result);
        reader.readAsDataURL(file);
    }
    
    initEventListeners() {
        // Bottom Sheet Elements
        const modal = document.getElementById('media-options-modal');
        const closeBtn = document.getElementById('close-options-btn');
        const sheetTitle = document.getElementById('sheet-title');
        
        const photoOptions = document.getElementById('photo-options');
        const videoOptions = document.getElementById('video-options');
        const addMoreOptions = document.getElementById('add-more-options');
        
        const hideAllSheetContent = () => {
            if(photoOptions) photoOptions.style.display = 'none';
            if(videoOptions) videoOptions.style.display = 'none';
            if(addMoreOptions) addMoreOptions.style.display = 'none';
        };

        const openModal = () => { if (modal) modal.style.display = 'flex'; };
        const closeModal = () => { if (modal) modal.style.display = 'none'; };
        
        if (closeBtn) closeBtn.addEventListener('click', closeModal);
        
        // Triggers
        const btnPhoto = document.getElementById('btn-show-options-photo');
        const btnVideo = document.getElementById('btn-show-options-video');
        const addMoreTile = document.getElementById('add-more-tile');
        
        if (btnPhoto) {
            btnPhoto.addEventListener('click', () => {
                hideAllSheetContent();
                if(photoOptions) photoOptions.style.display = 'block';
                if(sheetTitle) sheetTitle.textContent = 'Photo Options';
                openModal();
            });
        }
        
        if (btnVideo) {
            btnVideo.addEventListener('click', () => {
                hideAllSheetContent();
                if(videoOptions) videoOptions.style.display = 'block';
                if(sheetTitle) sheetTitle.textContent = 'Video Options';
                openModal();
            });
        }
        
        if (addMoreTile) {
            addMoreTile.addEventListener('click', () => {
                hideAllSheetContent();
                if(addMoreOptions) addMoreOptions.style.display = 'block';
                if(sheetTitle) sheetTitle.textContent = 'What would you like to add?';
                openModal();
            });
        }
        
        // Add More Sub-options
        const btnChoosePhoto = document.getElementById('btn-choose-photo');
        const btnChooseVideo = document.getElementById('btn-choose-video');
        
        if (btnChoosePhoto) {
            btnChoosePhoto.addEventListener('click', () => {
                hideAllSheetContent();
                if(photoOptions) photoOptions.style.display = 'block';
                if(sheetTitle) sheetTitle.textContent = 'Photo Options';
            });
        }
        
        if (btnChooseVideo) {
            btnChooseVideo.addEventListener('click', () => {
                hideAllSheetContent();
                if(videoOptions) videoOptions.style.display = 'block';
                if(sheetTitle) sheetTitle.textContent = 'Video Options';
            });
        }
        
        // The 4 Option Buttons -> Hidden Inputs
        const btnCapPhoto = document.getElementById('btn-capture-photo');
        const btnCapVideo = document.getElementById('btn-capture-video');
        const btnUpPhoto = document.getElementById('btn-upload-photo');
        const btnUpVideo = document.getElementById('btn-upload-video');
        
        const inCapPhoto = document.getElementById('input-capture-photo');
        const inCapVideo = document.getElementById('input-capture-video');
        const inUpPhoto = document.getElementById('input-upload-photo');
        const inUpVideo = document.getElementById('input-upload-video');
        
        if(btnCapPhoto) btnCapPhoto.addEventListener('click', () => { closeModal(); inCapPhoto.click(); });
        if(btnCapVideo) btnCapVideo.addEventListener('click', () => { closeModal(); inCapVideo.click(); });
        if(btnUpPhoto) btnUpPhoto.addEventListener('click', () => { closeModal(); inUpPhoto.click(); });
        if(btnUpVideo) btnUpVideo.addEventListener('click', () => { closeModal(); inUpVideo.click(); });
        
        // Input Change Listeners
        const handleImg = (e) => this.handleImageUpload(e);
        const handleVid = (e) => this.handleVideoUpload(e);
        
        if(inCapPhoto) inCapPhoto.addEventListener('change', handleImg);
        if(inUpPhoto) inUpPhoto.addEventListener('change', handleImg);
        if(inCapVideo) inCapVideo.addEventListener('change', handleVid);
        if(inUpVideo) inUpVideo.addEventListener('change', handleVid);
        
        // Proceed to AI button
        const btnProceed = document.getElementById('proceed-to-ai');
        if (btnProceed) {
            btnProceed.addEventListener('click', () => this.startAiProcessing());
        }
        
        // Back from Details to Media
        const backToMedia = document.getElementById('back-to-media');
        if (backToMedia) {
            backToMedia.addEventListener('click', (e) => {
                e.preventDefault();
                this.showScreen('screen-media');
            });
        }
        
        // Form Submission
        const form = document.getElementById('product-details-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFinalSubmission(e));
        }
    }
    
    handleImageUpload(event) {
        const files = Array.from(event.target.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                this.convertToBase64(file, (base64) => {
                    this.uploadedImages.push(base64);
                    this.updateMediaPreview();
                });
            }
        });
        event.target.value = ''; // Reset input
    }
    
    handleVideoUpload(event) {
        const files = Array.from(event.target.files);
        files.forEach(file => {
            if (file.type.startsWith('video/')) {
                this.convertToBase64(file, (base64) => {
                    this.uploadedVideos.push(base64);
                    this.updateMediaPreview();
                });
            }
        });
        event.target.value = ''; // Reset input
    }
    
    removeMedia(type, index) {
        if (type === 'image') {
            this.uploadedImages.splice(index, 1);
        } else {
            this.uploadedVideos.splice(index, 1);
        }
        this.updateMediaPreview();
    }
    
    updateMediaPreview() {
        const containers = [
            document.getElementById('media-preview'),
            document.getElementById('details-media-preview')
        ];
        const proceedBtn = document.getElementById('proceed-to-ai');
        
        const totalMedia = this.uploadedImages.length + this.uploadedVideos.length;
        
        // Toggle empty state vs preview state in Screen 1
        const emptyState = document.getElementById('screen1-empty-content');
        const selectedState = document.getElementById('screen2-media-content');
        const mediaSubtext = document.getElementById('media-subtext');
        const previewContainer = document.getElementById('media-preview');
        
        if (totalMedia > 0) {
            if(emptyState) emptyState.style.display = 'none';
            if(selectedState) selectedState.style.display = 'block';
            if(mediaSubtext) mediaSubtext.style.display = 'block';
            if(previewContainer) previewContainer.style.display = 'flex';
            if(proceedBtn) proceedBtn.disabled = false;
        } else {
            if(emptyState) emptyState.style.display = 'block';
            if(selectedState) selectedState.style.display = 'none';
            if(mediaSubtext) mediaSubtext.style.display = 'none';
            if(previewContainer) previewContainer.style.display = 'none';
            if(proceedBtn) proceedBtn.disabled = true;
        }
        
        // Re-render thumbnails in both containers
        containers.forEach(container => {
            if (!container) return;
            
            // Clear current items (except add-more tile if it exists in this container)
            Array.from(container.children).forEach(child => {
                if (child.id !== 'add-more-tile') {
                    child.remove();
                }
            });
            
            const addMoreTile = container.querySelector('#add-more-tile');
            
            this.uploadedImages.forEach((base64, index) => {
                const item = this.createMediaItem('image', base64, index);
                if (addMoreTile) {
                    container.insertBefore(item, addMoreTile);
                } else {
                    container.appendChild(item);
                }
            });
            
            this.uploadedVideos.forEach((base64, index) => {
                const item = this.createMediaItem('video', base64, index);
                if (addMoreTile) {
                    container.insertBefore(item, addMoreTile);
                } else {
                    container.appendChild(item);
                }
            });
        });
    }
    
    createMediaItem(type, base64, index) {
        const div = document.createElement('div');
        div.className = 'media-item';
        
        const removeBtn = `
            <button class="remove-btn" onclick="window.wizard.removeMedia('${type}', ${index}); event.stopPropagation();">
                &times;
            </button>
        `;
        
        if (type === 'image') {
            div.innerHTML = `
                <img src="${base64}" alt="Product Image">
                ${removeBtn}
            `;
        } else {
            div.innerHTML = `
                <video src="${base64}#t=0.1" preload="metadata"></video>
                <div class="video-indicator">Video</div>
                <div class="play-icon">▶</div>
                ${removeBtn}
            `;
        }
        
        return div;
    }
    
    showScreen(screenId) {
        const screens = ['screen-media', 'screen-loading', 'screen-details', 'screen-success'];
        screens.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.style.display = (id === screenId) ? 'block' : 'none';
            }
        });
        window.scrollTo(0, 0);
    }
    
    startAiProcessing() {
        if (this.uploadedImages.length === 0 && this.uploadedVideos.length === 0) {
            alert('Please upload media to continue');
            return;
        }
        
        this.showScreen('screen-loading');
        
        const formData = new FormData();
        formData.append('step', '1');
        this.uploadedImages.forEach(image => formData.append('images', image));
        this.uploadedVideos.forEach(video => formData.append('videos', video));
        
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': this.getCsrfToken() }
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.success) {
                this.productData = data.ai_content || {};
                this.populateDetailsForm();
                this.showScreen('screen-details');
            } else {
                alert(data.error || 'Failed to generate product details');
                this.showScreen('screen-media');
            }
        })
        .catch(error => {
            alert(`An error occurred: ${error.message}`);
            this.showScreen('screen-media');
        });
    }
    
    populateDetailsForm() {
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if(el) el.value = val || '';
        };
        
        setVal('field-title', this.productData.name);
        setVal('field-description', this.productData.description);
        
        // Quantity default to 1 if empty
        const qty = this.productData.stockQuantity || 1;
        setVal('field-quantity', qty);
        
        // Calculate offer % if possible, or leave empty
        let offerStr = '';
        if (this.productData.price && this.productData.offer_price) {
            const perc = Math.round((1 - (this.productData.offer_price / this.productData.price)) * 100);
            if (perc > 0) offerStr = perc + '%';
        }
        setVal('field-offer', offerStr);
        setVal('field-price', this.productData.price);
        
        // Make sure thumbnails are mirrored exactly
        this.updateMediaPreview();
    }
    
    handleFinalSubmission(event) {
        event.preventDefault();
        
        const btn = document.querySelector('#product-details-form button[type="submit"]');
        if(btn) {
            btn.disabled = true;
            btn.textContent = 'प्रतीक्षा करें...';
        }
        
        const formData = new FormData(event.target);
        // Include category id if it was generated (the backend might need it)
        if (this.productData.suggestedCategoryId || this.productData.suggested_category_id) {
            formData.append('category', this.productData.suggestedCategoryId || this.productData.suggested_category_id);
        }
        
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': this.getCsrfToken() }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showScreen('screen-success');
            } else {
                alert(data.error || 'Failed to save product');
                if(btn) {
                    btn.disabled = false;
                    btn.textContent = 'सहेजें';
                }
            }
        })
        .catch(error => {
            alert(`An error occurred: ${error.message}`);
            if(btn) {
                btn.disabled = false;
                btn.textContent = 'सहेजें';
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProductUploadWizard();
});
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_js)
print("Updated product_upload_wizard.js successfully.")
