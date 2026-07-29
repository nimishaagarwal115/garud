export class VoiceAnimations {
    static startListening(buttonElement) {
        if (!buttonElement) return;
        buttonElement.classList.add("listening-active");
        
        // Add pulsating effect or text change if it's a Garud typical button
        const icon = buttonElement.querySelector("i");
        if (icon) {
            icon.classList.remove("bi-mic");
            icon.classList.add("bi-mic-fill", "text-danger");
        }
        
        // Add inline style or rely on CSS class 'pulse-anim'
        buttonElement.style.transform = "scale(1.1)";
        buttonElement.style.transition = "transform 0.3s";
        
        // Update any text inside the button if it has a specific span
        const textSpan = buttonElement.querySelector(".btn-text");
        if (textSpan) {
            textSpan.dataset.originalText = textSpan.innerText;
            textSpan.innerText = "Listening...";
        }
    }

    static stopListening(buttonElement) {
        if (!buttonElement) return;
        buttonElement.classList.remove("listening-active");
        
        const icon = buttonElement.querySelector("i");
        if (icon) {
            icon.classList.remove("bi-mic-fill", "text-danger");
            icon.classList.add("bi-mic");
        }
        
        buttonElement.style.transform = "scale(1)";
        
        const textSpan = buttonElement.querySelector(".btn-text");
        if (textSpan && textSpan.dataset.originalText) {
            textSpan.innerText = textSpan.dataset.originalText;
        }
    }
}
