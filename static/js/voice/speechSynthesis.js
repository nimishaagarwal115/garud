export class CustomSpeechSynthesis {
    constructor() {
        this.synth = window.speechSynthesis;
        this.supported = !!this.synth;
    }

    speak(text, lang, onEnd) {
        if (!this.supported) return;
        
        this.synth.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang || "en-IN";
        
        if (onEnd) {
            utterance.onend = onEnd;
        }
        
        this.synth.speak(utterance);
    }
    
    stop() {
        if (this.supported) {
            this.synth.cancel();
        }
    }
}
