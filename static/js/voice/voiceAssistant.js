import { CustomSpeechRecognition } from './speechRecognition.js';
import { CustomSpeechSynthesis } from './speechSynthesis.js';
import { VoiceAnimations } from './voiceAnimations.js';

export class VoiceAssistant {
    constructor() {
        this.recognition = new CustomSpeechRecognition();
        this.synthesis = new CustomSpeechSynthesis();
        this.isListening = false;
    }

    getLangCode() {
        const match = document.cookie.match(new RegExp('(^| )garuda_language=([^;]+)'));
        const langMap = {
            'Hindi': 'hi-IN',
            'English': 'en-IN',
            'Marathi': 'mr-IN',
            'Bengali': 'bn-IN',
            'Tamil': 'ta-IN',
            'Gujarati': 'gu-IN',
            'Telugu': 'te-IN'
        };
        if (match) {
            return langMap[match[2]] || 'hi-IN';
        }
        return 'hi-IN'; // Default
    }

    start(inputFieldId, promptText, buttonId = null, onComplete = null) {
        const inputField = typeof inputFieldId === 'string' ? document.getElementById(inputFieldId) : inputFieldId;
        const button = typeof buttonId === 'string' ? document.getElementById(buttonId) : buttonId;
        const lang = this.getLangCode();

        if (this.isListening) {
            this.stop(button);
            return;
        }

        if (promptText) {
            VoiceAnimations.startListening(button);
            this.synthesis.speak(promptText, lang, () => {
                this._startListening(inputField, button, lang, onComplete);
            });
        } else {
            this._startListening(inputField, button, lang, onComplete);
        }
    }

    _startListening(inputField, button, lang, onComplete) {
        this.isListening = true;
        VoiceAnimations.startListening(button);
        
        this.recognition.start(
            lang,
            (transcript) => {
                if (inputField) {
                    inputField.value = transcript;
                    inputField.dispatchEvent(new Event('input', { bubbles: true }));
                    inputField.dispatchEvent(new Event('change', { bubbles: true }));
                }
                this.isListening = false;
                VoiceAnimations.stopListening(button);
                if (onComplete) onComplete(transcript);
            },
            (error) => {
                console.error("Voice Error:", error);
                this.isListening = false;
                VoiceAnimations.stopListening(button);
            },
            () => {
                this.isListening = false;
                VoiceAnimations.stopListening(button);
            }
        );
    }
    
    stop(button = null) {
        this.recognition.stop();
        this.synthesis.stop();
        this.isListening = false;
        if (button) VoiceAnimations.stopListening(button);
    }
    
    speakOnly(text) {
        this.synthesis.speak(text, this.getLangCode());
    }
}

// Global expose
window.GarudVoiceAssistant = new VoiceAssistant();
