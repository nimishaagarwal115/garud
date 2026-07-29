document.addEventListener('DOMContentLoaded', function() {
    const continueBtn = document.getElementById('continueBtn');
    const manualSubmitBtn = document.getElementById('manualSubmitBtn');
    const tryAgainBtn = document.getElementById('tryAgainBtn');
    const tryAgainBtn2 = document.getElementById('tryAgainBtn2');
    
    // Function to reset to initial state
    function resetToInitialState() {
        // Reset to initial state
        document.getElementById('step1-options').style.display = 'block';
        document.getElementById('continueBtn').style.display = 'inline-block';
        document.getElementById('step2-scan').style.display = 'none';
        document.getElementById('step3-manual').style.display = 'none';
        
        // Reset form inputs
        document.getElementById('panManualInput').value = '';
        document.getElementById('manual-success-msg').style.display = 'none';
        document.getElementById('statusMsg').textContent = '';
        document.getElementById('ocr-result').innerHTML = '';
        document.getElementById('photoPreview').innerHTML = '';
        document.getElementById('loader').style.display = 'none';
        document.getElementById('uploadBtn').style.display = 'none';
        
        // Reset webcam data
        frontImageData = null;
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        
        // Reset manual submit button
        document.getElementById('manualSubmitBtn').disabled = false;
        document.getElementById('manualSubmitBtn').innerHTML = 'Submit';
    }
    
    // Handle continue button click
    continueBtn.addEventListener('click', function() {
        const selectedOption = document.querySelector('input[name="pan_option"]:checked').value;
        
        // Hide all sections first
        document.getElementById('step1-options').style.display = 'none';
        document.getElementById('continueBtn').style.display = 'none';
        document.getElementById('step2-scan').style.display = 'none';
        document.getElementById('step3-manual').style.display = 'none';
        
        // Show relevant section
        if (selectedOption === 'scan') {
            document.getElementById('step2-scan').style.display = 'block';
            // Initialize webcam for PAN card scanning
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia({ video: true }).then((s) => {
                    stream = s;
                    video.srcObject = stream;
                });
            }
        } else if (selectedOption === 'manual') {
            document.getElementById('step3-manual').style.display = 'block';
        }
    });
    
    // Handle try again button clicks (both buttons)
    if (tryAgainBtn) {
        tryAgainBtn.addEventListener('click', resetToInitialState);
    }
    if (tryAgainBtn2) {
        tryAgainBtn2.addEventListener('click', resetToInitialState);
    }
    
    // Handle manual PAN submission
    if (manualSubmitBtn) {
        manualSubmitBtn.addEventListener('click', function() {
            const panInput = document.getElementById('panManualInput');
            const panNumber = panInput.value.trim().toUpperCase();
            
            if (!panNumber) {
                alert('Please enter PAN card number');
                return;
            }
            
            // Validate PAN format (5 letters, 4 digits, 1 letter)
            const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
            if (!panRegex.test(panNumber)) {
                alert('Please enter a valid PAN card number (Example: ABCDE1234F)');
                return;
            }
            
            // Submit PAN via AJAX (similar to Aadhaar manual submission)
            submitPANManually(panNumber);
        });
    }
});

// PAN Card webcam scanning variables and functions
let frontImageData = null;
let stream = null;

const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const captureFrontBtn = document.getElementById('captureFrontBtn');
const uploadBtn = document.getElementById('uploadBtn');
const photoPreview = document.getElementById('photoPreview');
const statusMsg = document.getElementById('statusMsg');
const ocrResult = document.getElementById('ocr-result');

// Capture front image
captureFrontBtn.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    frontImageData = canvas.toDataURL('image/png');
    photoPreview.innerHTML = `<b>PAN Card Image:</b><br><img src="${frontImageData}" width="250" style="border-radius: 8px; margin: 10px 0;"/><br>`;
    statusMsg.textContent = '✅ PAN card image captured. Click Submit to process.';
    statusMsg.style.color = 'green';
    uploadBtn.style.display = 'inline-block';
});

// Upload and process PAN card image
uploadBtn.addEventListener('click', () => {
    if (!frontImageData) {
        statusMsg.textContent = '❌ Please capture PAN card image first.';
        statusMsg.style.color = 'red';
        return;
    }
    
    statusMsg.textContent = 'Processing PAN card image...';
    statusMsg.style.color = 'orange';
    document.getElementById('loader').style.display = 'block';
    
    // Create form data for PAN card submission
    const formData = new FormData();
    formData.append('front_image', frontImageData);
    formData.append('scan_option', 'scan');
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
    
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loader').style.display = 'none';
        if (data.success) {
            const info = data.data || {};
            ocrResult.innerHTML = `
                <b>PAN Number:</b> ${info.pan_number || 'Extracted'}<br>
                <b>Name:</b> ${info.name || 'Extracted'}<br>
                <b>Father's Name:</b> ${info.father_name || 'Extracted'}<br>
                <b>Date of Birth:</b> ${info.dob || 'Extracted'}
            `;
            statusMsg.textContent = '✅ PAN card details extracted and saved!';
            statusMsg.style.color = 'green';
            
            // Redirect to next step after success
            setTimeout(() => {
                window.location.href = '{% url "success_page" %}';
            }, 3000);
        } else {
            statusMsg.textContent = data.error || 'Something went wrong with PAN card processing.';
            statusMsg.style.color = 'red';
        }
    })
    .catch(error => {
        document.getElementById('loader').style.display = 'none';
        console.error('Error:', error);
        statusMsg.textContent = 'Error processing PAN card. Please try again.';
        statusMsg.style.color = 'red';
    });
});

function submitPANManually(panNumber) {
    // Create form data
    const formData = new FormData();
    formData.append('pan_card_number', panNumber);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
    
    // Show loading state
    document.getElementById('manualSubmitBtn').disabled = true;
    document.getElementById('manualSubmitBtn').innerHTML = 'Processing...';
    
    // Submit form
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => {
        if (response.ok) {
            // Success - redirect to next step
            document.getElementById('manual-success-msg').innerHTML = 'PAN card number saved successfully!';
            document.getElementById('manual-success-msg').style.display = 'block';
            
            // Redirect after a short delay
            setTimeout(function() {
                window.location.href = '{% url "success_page" %}';
            }, 1500);
        } else {
            throw new Error('Server error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving PAN card number. Please try again.');
        
        // Reset button
        document.getElementById('manualSubmitBtn').disabled = false;
        document.getElementById('manualSubmitBtn').innerHTML = 'Submit';
    });
}