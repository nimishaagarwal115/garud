export class CustomSpeechRecognition {
    constructor() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error("Speech Recognition API not supported in this browser.");
            this.supported = false;
            return;
        }
        this.supported = true;
        this.recognition = new SpeechRecognition();
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;
    }

    start(lang, onResult, onError, onEnd) {
        if (!this.supported) return;
        this.recognition.lang = lang || "en-IN";
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            if (onResult) onResult(transcript);
        };
        
        this.recognition.onerror = (event) => {
            if (onError) onError(event.error);
        };
        
        this.recognition.onend = () => {
            if (onEnd) onEnd();
        };
        
        try {
            this.recognition.start();
        } catch (e) {
            console.error("Speech recognition already started or error:", e);
        }
    }

    stop() {
        if (this.supported) {
            this.recognition.stop();
        }
    }
}
