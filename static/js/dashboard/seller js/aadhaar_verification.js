
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  // Navigation buttons for stepper functionality
  const goBackBtn = document.getElementById("goBackBtn");
  const goForwardBtn = document.getElementById("goForwardBtn");
  const topBackBtn = document.getElementById("topBackBtn");

  // Top back button handler
  if (topBackBtn) {
    topBackBtn.addEventListener("click", function () {
      // Check if we're in the stepper context
      const currentUrl = window.location.href;
      if (currentUrl.includes('onboarding_stepper')) {
        // Navigate to previous step in stepper (phone)
        window.location.href = currentUrl.split('?')[0] + '?step=phone';
      } else {
        // Go back in browser history
        window.history.back();
      }
    });
  }

  // Back to Options buttons functionality
  const backToOptionsButtons = document.querySelectorAll('.back-to-options-btn');
  backToOptionsButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Show initial options and hide all verification sections
      document.getElementById("step1-options").style.display = "block";
      document.getElementById("step2-scan").style.display = "none";
      document.getElementById("step3-manual").style.display = "none";
      document.getElementById("step4-mobile").style.display = "none";
      
      // Show navigation buttons again
      const navButtons = document.querySelector('div[style*="position: fixed; bottom: 30px"]');
      if (navButtons) navButtons.style.display = "flex";
      
      // Stop camera stream if active
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
      }
      
      // Clear any status messages
      document.getElementById("statusMsg").textContent = "";
      document.getElementById("ocr-result").innerHTML = "";
      document.getElementById("manual-success-msg").style.display = "none";
      document.getElementById("mobile-success-msg").style.display = "none";
    });
  });


  // Go Forward button handler
  if (goForwardBtn) {
    goForwardBtn.addEventListener("click", function () {
      // Check if we're in the stepper context
      const currentUrl = window.location.href;
      if (currentUrl.includes('onboarding_stepper')) {
        // Navigate to next step in stepper (income)
        window.location.href = currentUrl.split('?')[0] + '?step=income';
      } else {
        // Navigate to annual income page
        window.location.href = '{% url "annual_income" %}';
      }
    });
  }

  document.getElementById("continueBtn").addEventListener("click", () => {
    const scanOption = document.getElementById("scan_aadhaar").checked;
    const mobileOption = document.getElementById("enter_mobile").checked;
    const manualOption = document.getElementById("manual_entry").checked;

    // Hide all
    document.getElementById("step1-options").style.display = "none";
    document.getElementById("step2-scan").style.display = "none";
    document.getElementById("step3-manual").style.display = "none";
    document.getElementById("step4-mobile").style.display = "none";
     
    // Hide navigation buttons during verification process
    const navButtons = document.querySelector('div[style*="position: fixed; bottom: 30px"]');
    if (navButtons) navButtons.style.display = "none";

    if (scanOption) {
      document.getElementById("step2-scan").style.display = "block";
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then((s) => {
          stream = s;
          video.srcObject = stream;
        });
      }
    } else if (manualOption) {
      document.getElementById("step3-manual").style.display = "block";
    } else if (mobileOption) {
      document.getElementById("step4-mobile").style.display = "block";
    }
  });

  let frontImageData = null;
  let backImageData = null;
  let stream = null;

  const video = document.getElementById('webcam');
  const canvas = document.getElementById('canvas');
  const captureFrontBtn = document.getElementById('captureFrontBtn');
  const captureBackBtn = document.getElementById('captureBackBtn');
  const uploadBtn = document.getElementById('uploadBtn');
  const photoPreview = document.getElementById('photoPreview');
  const statusMsg = document.getElementById('statusMsg');
  const ocrResult = document.getElementById('ocr-result');

  captureFrontBtn.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    frontImageData = canvas.toDataURL('image/png');
    photoPreview.innerHTML = `<b>Front Image:</b><br><img src="${frontImageData}" width="200"/><br>`;
    statusMsg.textContent = '✅ Front image captured. Now capture back image.';
    statusMsg.style.color = 'green';
    if (backImageData) uploadBtn.style.display = '';
  });

  captureBackBtn.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    backImageData = canvas.toDataURL('image/png');
    let html = `<b>Front Image:</b><br><img src="${frontImageData}" width="200"/><br>`;
    html += `<b>Back Image:</b><br><img src="${backImageData}" width="200"/><br>`;
    photoPreview.innerHTML = html;
    statusMsg.textContent = '✅ Back image captured. Now submit Aadhaar.';
    statusMsg.style.color = 'green';
    if (frontImageData) uploadBtn.style.display = '';
  });

  uploadBtn.addEventListener('click', () => {
    if (!frontImageData || !backImageData) {
      statusMsg.textContent = '❌ Please capture both front and back images.';
      statusMsg.style.color = 'red';
      return;
    }
    statusMsg.textContent = 'Processing...';
    statusMsg.style.color = 'orange';
    fetch("/aadhaar/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        option: "scan",
        front_image: frontImageData,
        back_image: backImageData,
      }),
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          const info = data.data;
          ocrResult.innerHTML = `
          <b>Name:</b> ${info.name || ''}<br>
          <b>DOB:</b> ${info.dob || ''}<br>
          <b>Gender:</b> ${info.gender || ''}<br>
          <b>Aadhaar Number:</b> ${info.aadhaar_number || ''}<br>
          <b>Address:</b> ${info.address || ''}
        `;
          statusMsg.textContent = '✅ Aadhaar details extracted and saved!';
          statusMsg.style.color = 'green';
          setTimeout(() => window.location.href = '/annual-income/', 3000);
        } else {
          statusMsg.textContent = data.error || "Something went wrong.";
          statusMsg.style.color = 'red';
        }
      });
  });

  // Manual submit
  document.getElementById("manualSubmitBtn").addEventListener("click", () => {
    const input = document.getElementById("aadhaarManualInput").value.trim();
    const msg = document.getElementById("manual-success-msg");
    if (/^\d{12}$/.test(input)) {
      msg.style.color = "green";
      msg.innerText = "✅ Aadhaar Number Submitted Successfully";
      msg.style.display = "block";
      fetch("/aadhaar/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          option: "manual",
          aadhaar_number: input,
        }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            window.location.href = "/annual-income/";
          }
        });
    } else {
      msg.style.color = "red";
      msg.innerText = "❌ Please enter a valid 12-digit Aadhaar number.";
      msg.style.display = "block";
    }
  });

  // Mobile number flow
  document.getElementById("mobileSubmitBtn").addEventListener("click", () => {
    const input = document.getElementById("aadhaarMobileInput").value.trim();
    const msg = document.getElementById("mobile-success-msg");
    if (/^\d{10}$/.test(input)) {
      msg.style.color = "green";
      msg.innerText = "✅ Mobile Number Submitted";
      msg.style.display = "block";
      fetch("/aadhaar/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          option: "mobile",
          mobile: input,
        }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            window.location.href = "/annual-income/";
          }
        });
    } 
    else {
      msg.style.color = "red";
      msg.innerText = "❌ Please enter a valid 10-digit mobile number.";
      msg.style.display = "block";
    }
  });





