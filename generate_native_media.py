import os
import re

html_path = r"c:\Users\agarw\OneDrive\Desktop\garud-app-garuda_backend-aba4bee89d84\templates\product_listing\upload_wizard.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the Bottom Sheet Modal HTML
modal_pattern = re.compile(r'<!-- Mobile Native Bottom Sheet -->.*?</div>\s*</div>\s*</div>', re.DOTALL)
content = modal_pattern.sub('', content)

# Also remove the old 4 inputs
inputs_pattern = re.compile(r'<!-- Hidden file inputs -->.*?<input type="file" id="input-upload-video" accept="video/\*" multiple style="display: none;">', re.DOTALL)

new_inputs = """<!-- Native file inputs -->
        <input type="file" id="input-native-photo" accept="image/*" multiple style="display: none;">
        <input type="file" id="input-native-video" accept="video/*" multiple style="display: none;">
        <!-- Input for adding both when clicking + -->
        <input type="file" id="input-native-any" accept="image/*,video/*" multiple style="display: none;">"""

content = inputs_pattern.sub(new_inputs, content)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated HTML.")

js_path = r"c:\Users\agarw\OneDrive\Desktop\garud-app-garuda_backend-aba4bee89d84\static\js\product_upload_wizard.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

# Rewrite the initEventListeners to use the native inputs
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
        const btnPhoto = document.getElementById('btn-show-options-photo');
        const btnVideo = document.getElementById('btn-show-options-video');
        const addMoreTile = document.getElementById('add-more-tile');
        
        const inPhoto = document.getElementById('input-native-photo');
        const inVideo = document.getElementById('input-native-video');
        const inAny = document.getElementById('input-native-any');
        
        if (btnPhoto && inPhoto) {
            btnPhoto.addEventListener('click', () => inPhoto.click());
        }
        
        if (btnVideo && inVideo) {
            btnVideo.addEventListener('click', () => inVideo.click());
        }
        
        if (addMoreTile && inAny) {
            addMoreTile.addEventListener('click', () => inAny.click());
        }
        
        // Generic change handler for all inputs
        const handleNativeInput = (e) => {
            const files = Array.from(e.target.files);
            files.forEach(file => {
                if (file.type.startsWith('image/')) {
                    this.convertToBase64(file, (base64) => {
                        this.uploadedImages.push(base64);
                        this.updateMediaPreview();
                    });
                } else if (file.type.startsWith('video/')) {
                    this.convertToBase64(file, (base64) => {
                        this.uploadedVideos.push(base64);
                        this.updateMediaPreview();
                    });
                }
            });
            e.target.value = ''; // Reset input
        };
        
        if (inPhoto) inPhoto.addEventListener('change', handleNativeInput);
        if (inVideo) inVideo.addEventListener('change', handleNativeInput);
        if (inAny) inAny.addEventListener('change', handleNativeInput);
        
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

with open(js_path, "w", encoding="utf-8") as f:
    f.write(new_js)
print("Updated JS.")
