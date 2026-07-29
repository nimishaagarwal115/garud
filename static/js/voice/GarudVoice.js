/**
 * GarudVoice - Reusable Voice Module for Onboarding and Forms
 */
class GarudVoiceModule {
    constructor() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            this.supported = false;
            console.error("Speech Recognition API not supported in this browser.");
            return;
        }
        this.supported = true;
        this.recognition = new SpeechRecognition();
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;
        this.isListening = false;
        
        // CSS for pulsing animation
        this.injectStyles();
    }

    injectStyles() {
        if (!document.getElementById('garud-voice-styles')) {
            const style = document.createElement('style');
            style.id = 'garud-voice-styles';
            style.innerHTML = `
                @keyframes garudVoicePulse {
                    0% {
                        box-shadow: 0 0 0 0 rgba(199, 59, 39, 0.7),
                                    0 0 0 0 rgba(199, 59, 39, 0.5),
                                    0 0 0 0 rgba(199, 59, 39, 0.3);
                    }
                    50% {
                        box-shadow: 0 0 0 15px rgba(199, 59, 39, 0.3),
                                    0 0 0 30px rgba(199, 59, 39, 0.15),
                                    0 0 0 45px rgba(199, 59, 39, 0.05);
                    }
                    100% {
                        box-shadow: 0 0 0 30px rgba(199, 59, 39, 0),
                                    0 0 0 60px rgba(199, 59, 39, 0),
                                    0 0 0 90px rgba(199, 59, 39, 0);
                    }
                }
                .garud-voice-listening {
                    animation: garudVoicePulse 1.5s linear infinite;
                    background-color: #C73B27 !important;
                }
                .garud-voice-listening i {
                    color: white !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    getLangCode() {
        if (window.USER_LANG_CODE) {
            console.log("GarudVoice using window.USER_LANG_CODE:", window.USER_LANG_CODE);
            return window.USER_LANG_CODE;
        }
        
        let langName = this._getCookie('garuda_language');
        
        // If not found, try googtrans
        if (!langName) {
            const googtrans = this._getCookie('googtrans');
            if (googtrans) {
                const parts = googtrans.split('/');
                const code = parts[parts.length - 1]; // e.g. 'hi'
                const revMap = {
                    'en': 'English', 'hi': 'Hindi', 'mr': 'Marathi',
                    'ta': 'Tamil', 'te': 'Telugu', 'gu': 'Gujarati',
                    'pa': 'Punjabi', 'bn': 'Bengali', 'ur': 'Urdu',
                    'ml': 'Malayalam', 'kn': 'Kannada'
                };
                langName = revMap[code];
            }
        }
        
        if (langName) langName = langName.toLowerCase();

        const langMap = {
            'hindi': 'hi-IN',
            'english': 'en-IN',
            'marathi': 'mr-IN',
            'bengali': 'bn-IN',
            'tamil': 'ta-IN',
            'gujarati': 'gu-IN',
            'punjabi': 'pa-IN',
            'telugu': 'te-IN',
            'urdu': 'ur-IN',
            'malayalam': 'ml-IN',
            'kannada': 'kn-IN'
        };

        const finalLang = langMap[langName] || 'hi-IN';
        console.log("GarudVoice derived lang:", finalLang);
        return finalLang; // Default to Hindi
    }

    _getCookie(name) {
        const value = "; " + document.cookie;
        const parts = value.split("; " + name + "=");
        if (parts.length === 2) return decodeURIComponent(parts.pop().split(";").shift());
        return null;
    }

    /**
     * Start listening and map output to input field.
     * @param {string} inputElementId - The ID of the input field to populate.
     * @param {string} micButtonId - The ID of the microphone button.
     * @param {string} statusElementId - The ID of the status text element (optional).
     * @param {string} fieldType - The type of field (text, mobile, aadhaar, gst, ifsc, account)
     * @param {function} onSuccessCallback - Callback executed when recognition and validation succeed
     */
    start(inputElementId, micButtonId, statusElementId = null, fieldType = 'text', onSuccessCallback = null) {
        if (!this.supported) {
            alert("Your browser does not support Voice Input. Please type manually.");
            return;
        }

        if (this.isListening) {
            this.stop();
            return;
        }

        const inputField = document.getElementById(inputElementId);
        const micBtn = document.getElementById(micButtonId);
        const statusEl = statusElementId ? document.getElementById(statusElementId) : null;

        if (!inputField || !micBtn) {
            console.error("GarudVoice: Target elements not found.");
            return;
        }

        const lang = this.getLangCode();
        this.recognition.lang = lang;

        this._setUIListening(micBtn, statusEl, "Listening...");

        this.recognition.onresult = (event) => {
            const rawTranscript = event.results[0][0].transcript;
            
            let finalValue = rawTranscript;
            
            // Apply Number Parser if required
            if (fieldType !== 'text' && window.GarudNumberParser) {
                finalValue = window.GarudNumberParser.parse(rawTranscript, fieldType);
            }

            // Validation Rules
            let isValid = true;
            let errorMsg = "";

            if (fieldType === 'mobile' && finalValue.length !== 10) {
                isValid = false;
                errorMsg = "Mobile must be 10 digits. Tap mic to retry.";
            } else if (fieldType === 'aadhaar' && finalValue.length !== 12) {
                isValid = false;
                errorMsg = "Aadhaar must be 12 digits. Tap mic to retry.";
            }

            if (isValid) {
                inputField.value = finalValue;
                inputField.dispatchEvent(new Event('input', { bubbles: true }));
                inputField.dispatchEvent(new Event('change', { bubbles: true }));
                console.log("Final value inserted: " + finalValue);
                this._setUIStopped(micBtn, statusEl, "");
                
                // Trigger callback if provided
                if (onSuccessCallback && typeof onSuccessCallback === 'function') {
                    onSuccessCallback(finalValue);
                }
            } else {
                console.error("Validation failed: " + errorMsg);
                this._setUIStopped(micBtn, statusEl, errorMsg);
            }
            
            this.isListening = false;
        };

        this.recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            this._setUIStopped(micBtn, statusEl, "I couldn't understand. Please try again.");
            this.isListening = false;
        };

        this.recognition.onend = () => {
            if (this.isListening) {
                // If it ends without result or error
                this._setUIStopped(micBtn, statusEl, "");
                this.isListening = false;
            }
        };

        try {
            this.recognition.start();
            this.isListening = true;
        } catch (e) {
            console.error("Failed to start speech recognition:", e);
            this._setUIStopped(micBtn, statusEl, "Failed to start microphone.");
            this.isListening = false;
        }
    }

    stop() {
        if (this.supported && this.isListening) {
            this.recognition.stop();
            this.isListening = false;
        }
    }

    _setUIListening(micBtn, statusEl, message) {
        if (micBtn) {
            micBtn.classList.add('garud-voice-listening');
        }
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.classList.remove('text-danger');
            statusEl.classList.add('text-muted');
        }
    }

    _setUIStopped(micBtn, statusEl, message) {
        if (micBtn) {
            micBtn.classList.remove('garud-voice-listening');
        }
        if (statusEl) {
            statusEl.textContent = message;
            if (message && message !== "Listening...") {
                statusEl.classList.remove('text-muted');
                statusEl.classList.add('text-danger');
            }
        }
    }
}

window.GarudVoice = new GarudVoiceModule();
