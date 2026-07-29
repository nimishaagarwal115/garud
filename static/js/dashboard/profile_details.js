window.addEventListener("load", () => {
    // Cancel any ongoing speech synthesis when page loads
    window.speechSynthesis.cancel();

    // Filter form fields: exclude image fields and date inputs here before passing to voice assist
    const form = document.querySelector("form");
    const filteredFields = Array.from(form.elements).filter(el => {
        if (['hidden', 'submit', 'button', 'file', 'password'].includes(el.type)) return false;
        if (el.type === "date") return false;  // skip date fields
        if (el.tagName === "INPUT" && el.getAttribute("type") === "file") return false;  // skip image fields
        return ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName) && !el.disabled;
    });

    // Custom workflow for filtered fields
    let currentIndex = 0;

    const getFieldLabel = (field) => {
        const label = form.querySelector(`label[for="${field.id}"]`);
        return label ? label.innerText :
               field.getAttribute("aria-label") ||
               field.getAttribute("placeholder") ||
               field.name.replace(/_/g, ' ') ||
               `field ${currentIndex + 1}`;
    };

    const handleNextField = () => {
        if (currentIndex >= filteredFields.length) {
            voiceFormAssist.speakText("Form completed. Please review your inputs before submitting.");
            return;
        }

        const field = filteredFields[currentIndex];
        const label = getFieldLabel(field);

        if (field.tagName === "SELECT") {
            const optionsText = Array.from(field.options)
                .filter(o => o.value)
                .map(o => o.text)
                .join(", ");
            voiceFormAssist.speakText(`Please select your ${label}. Options are: ${optionsText}.`, () => {
                voiceFormAssist.startRecognition((transcript) => {
                    const choice = transcript.toLowerCase();
                    for (let option of field.options) {
                        if (option.text.toLowerCase().includes(choice)) {
                            field.value = option.value;
                            break;
                        }
                    }
                    currentIndex++;
                    setTimeout(handleNextField, 500);
                });
            });

        } else {
            voiceFormAssist.speakText(`Please enter your ${label}.`, () => {
                voiceFormAssist.startRecognition((transcript) => {
                    field.value = transcript.trim();
                    field.focus();
                    currentIndex++;
                    setTimeout(handleNextField, 500);
                });
            });
        }
    };

    // Start form filling process
    voiceFormAssist.speakText("Please fill your profile form using your voice.", () => {
        setTimeout(handleNextField, 500);
    });

});

document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("id_profile_picture");
    const previewImg = document.getElementById("profile-preview");

    fileInput.addEventListener("change", function (e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                previewImg.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
});