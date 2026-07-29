


  document.addEventListener("DOMContentLoaded", function () {
    const radioOptions = document.querySelectorAll(".form-check[data-value]");
    const newPhoneGroup = document.getElementById("newPhoneGroup");
    const form = document.getElementById("phoneConfirmationForm");
    const continueBtn = document.getElementById("continueBtn");             

    // Toggle styles + show/hide input
    radioOptions.forEach((option) => {
      option.addEventListener("click", function () {
        const radio = this.querySelector('input[type="radio"]');
        radio.checked = true;

        radioOptions.forEach((opt) => {
          opt.style.borderColor = "#e9ecef";
          opt.style.background = "#f8f9fa";
          opt.style.boxShadow = "none";
        });

        this.style.borderColor = "#dc3545";
        this.style.background = "#fff5f5";
        this.style.boxShadow = "0 2px 8px rgba(220, 53, 69, 0.2)";

        if (radio.value === "change") {
          newPhoneGroup.style.display = "block";
        } else {
          newPhoneGroup.style.display = "none";
        }
      });
    });

    // Submit handler
    continueBtn.addEventListener("click", function () {
      const selected = document.querySelector('input[name="action"]:checked');
      if (!selected) {
        alert("Please select an option to continue.");
        return;
      }

      if (selected.value === "change") {
        const newPhone = document.getElementById("new_phone_number");
        if (!newPhone.value.trim()) {
          alert("Please enter a new phone number.");
          newPhone.focus();
          return;
        }
      }

      this.disabled = true;
      this.innerText = "Processing...";
      form.submit();
    });

    // Format input
    const phoneInput = document.getElementById("new_phone_number");
    phoneInput.addEventListener("input", function () {
      this.value = this.value.replace(/\D/g, "");
    });

    phoneInput.addEventListener("focus", function () {
      this.style.borderColor = "#dc3545";
      this.style.boxShadow = "0 0 0 3px rgba(220, 53, 69, 0.1)";
    });

    phoneInput.addEventListener("blur", function () {
      this.style.borderColor = "#e9ecef";
      this.style.boxShadow = "none";
    });
  });