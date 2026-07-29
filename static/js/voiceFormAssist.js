// VoiceFormAssist class: Handles speech-based form interaction (TTS + STT)
class VoiceFormAssist {
    constructor(langCode = window.USER_LANG_CODE, useCloud = true) {
        // Set default language and speech recognition method (cloud-based or browser-based)
        this.langCode = langCode;
        this.useCloud = useCloud;
        this.recognition = null;
        this.isListening = false;
        this.isSpeaking = false;
        this.currentAudio = null;
        this.initRecognition(); // Initialize speech recognition engine (Web Speech API)
    }

    // Initialize browser-based speech recognition
    initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return; // Exit if browser doesn't support STT
        this.recognition = new SpeechRecognition();
        this.recognition.lang = this.langCode;
        this.recognition.interimResults = false; // Only final results
        this.recognition.maxAlternatives = 1; // Pick best match
    }

    // Stop any current speech or listening
    stopAll() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
        this.isSpeaking = false;
        this.isListening = false;
    }

    // Update language dynamically
    updateLanguage(newLangCode) {
        this.langCode = newLangCode;
        if (this.recognition) {
            this.recognition.lang = newLangCode;
        }
    }

    // Convert text to speech with faster processing
    speakText(text, onEndCallback = null) {
        if (!text.trim()) {
            if (onEndCallback) onEndCallback();
            return;
        }

        // Stop any current speech
        this.stopAll();
        this.isSpeaking = true;

        // Skip translation for faster response if text is short
        if (text.length < 50 && this.langCode.startsWith('en')) {
            // Direct TTS for short English text
            fetch(`/api/tts/?text=${encodeURIComponent(text)}&lang=${this.langCode}`)
                .then(res => {
                    if (!res.ok) throw new Error("TTS failed");
                    return res.blob();
                })
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    this.currentAudio = new Audio(url);
                    
                    this.currentAudio.onended = () => {
                        this.isSpeaking = false;
                        this.currentAudio = null;
                        if (onEndCallback) onEndCallback();
                    };
                    
                    this.currentAudio.onerror = () => {
                        this.isSpeaking = false;
                        this.currentAudio = null;
                        if (onEndCallback) onEndCallback();
                    };
                    
                    this.currentAudio.play();
                })
                .catch(err => {
                    this.isSpeaking = false;
                    if (onEndCallback) onEndCallback();
                });
        } else {
            // Full translation + TTS for longer text or non-English
            fetch(`/api/translate/?text=${encodeURIComponent(text)}&lang=${this.langCode}`)
                .then(res => {
                    if (!res.ok) throw new Error("Translation failed");
                    return res.json();
                })
                .then(data => {
                    const translatedText = data.translated_text;
                    return fetch(`/api/tts/?text=${encodeURIComponent(translatedText)}&lang=${this.langCode}`);
                })
                .then(res => {
                    if (!res.ok) throw new Error("TTS failed");
                    return res.blob();
                })
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    this.currentAudio = new Audio(url);
                    
                    this.currentAudio.onended = () => {
                        this.isSpeaking = false;
                        this.currentAudio = null;
                        if (onEndCallback) onEndCallback();
                    };
                    
                    this.currentAudio.onerror = () => {
                        this.isSpeaking = false;
                        this.currentAudio = null;
                        if (onEndCallback) onEndCallback();
                    };
                    
                    this.currentAudio.play();
                })
                .catch(err => {
                    this.isSpeaking = false;
                    if (onEndCallback) onEndCallback();
                });
        }
    }

    // Start speech recognition (cloud-based or fallback)
    startRecognition(callback) {
        if (this.isListening || this.isSpeaking) {
            console.warn("Already listening or speaking");
            return;
        }

        if (this.useCloud) {
            this._cloudSTT(callback); // Use custom STT API
        } else {
            this._browserSTT(callback); // Use browser fallback
        }
    }

    // Browser-based STT fallback
    _browserSTT(callback) {
        if (!this.recognition) {
            console.error("Speech recognition not supported");
            return;
        }

        this.isListening = true;

        this.recognition.onstart = () => {
            console.log("Speech recognition started");
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.isListening = false;
            callback(transcript);
        };

        this.recognition.onerror = (event) => {
            this.isListening = false;
            console.error("Speech recognition error:", event.error);
            callback("");
        };

        this.recognition.onend = () => {
            this.isListening = false;
        };

        this.recognition.start();
    }

    // Record shorter audio for faster processing
    async _cloudSTT(callback) {
        try {
            this.isListening = true;
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true}); 
            const recorder = new MediaRecorder(stream); 
            const chunks = [];

            recorder.ondataavailable = e => chunks.push(e.data);

            recorder.onstop = async () => {
                this.isListening = false;
                
                // Stop all tracks to free the microphone
                stream.getTracks().forEach(track => track.stop());
                
                try {
                    const blob = new Blob(chunks, { type: 'audio/webm' });
                    const arrayBuffer = await blob.arrayBuffer();
                    const audioData = await this._convertToPCM16(arrayBuffer);
                    
                    const res = await fetch(`/api/stt/?lang=${this.langCode}`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCSRFToken(),
                            'Content-Type': 'application/octet-stream'
                        },
                        body: audioData
                    });
                    const json = await res.json();
                    callback(json.transcript || "");
                } catch (err) {
                    console.error("STT processing error:", err);
                    callback("");
                }
            };

            recorder.start();
            // Reduced recording time from 5 seconds to 3 seconds for faster response
            setTimeout(() => {
                if (recorder.state === "recording") {
                    recorder.stop();
                }
            }, 3000);
        } catch (err) {
            this.isListening = false;
            console.warn("Cloud STT failed, falling back to browser STT:", err);
            this._browserSTT(callback);
        }
    }

    // Convert raw WebM buffer to 16-bit PCM format for cloud STT compatibility
    async _convertToPCM16(buffer) {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        const audioBuffer = await audioCtx.decodeAudioData(buffer); // Decode to audio buffer
        const raw = audioBuffer.getChannelData(0); // Get first channel
        const pcm = new Int16Array(raw.length); // Allocate space

        for (let i = 0; i < raw.length; i++) {
            pcm[i] = Math.max(-1, Math.min(1, raw[i])) * 0x7FFF; // Convert float [-1,1] to Int16
        }

        return new Blob([pcm.buffer], { type: 'application/octet-stream' });
    }

    // Specialized OTP input using voice – listens to 6-digit code
    startOtpVoiceInput({ formSelector = "#otp-verification-form", lang = this.langCode } = {}) {
        const form = document.querySelector(formSelector);
        const fields = Array.from(form.querySelectorAll('.otp-field'));
        const self = this;

        this.speakText("Please say your six digit one time password now.", () => {
            self.startRecognition((transcript) => {
                const digits = transcript.replace(/\D/g, ''); // Extract only digits

                // Retry if incomplete OTP
                if (digits.length < fields.length) {
                    self.speakText("Incomplete OTP. Please repeat all six digits.", () => {
                        self.startOtpVoiceInput({ formSelector, lang }); // Retry
                    });
                    return;
                }

                // Fill OTP fields
                fields.forEach((field, idx) => field.value = digits[idx] || '');
                self.speakText("OTP entered successfully. Please check your inputs before submitting.");
            });
        });
    }

    // Full voice-driven form filling
    startVoiceFormFilling({ form, introPrompt = "Please fill the form using your voice.", onComplete = null } = {}) {
        if (!form) return;

        // Filter valid interactive fields
        const formFields = Array.from(form.elements).filter(el =>
            ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName) &&
            !['hidden', 'submit', 'button', 'file', 'password'].includes(el.type) &&
            !el.disabled
        );

        let currentIndex = 0; // Track progress field-wise

        // Try to get human-readable field label
        const getFieldLabel = (field) => {
            const label = form.querySelector(`label[for="${field.id}"]`);
            return label ? label.innerText :
                field.getAttribute("aria-label") ||
                field.getAttribute("placeholder") ||
                field.name.replace(/_/g, ' ') ||
                `field ${currentIndex + 1}`;
        };

        // Handle each field sequentially
        const handleNextField = () => {
            if (currentIndex >= formFields.length) {
                // Done with all fields
                this.speakText("Form completed. Please review your inputs before submitting.", () => {
                    if (typeof onComplete === "function") onComplete();
                });
                return;
            }

            const field = formFields[currentIndex];
            const label = getFieldLabel(field);

            // For checkbox fields
            if (field.type === "checkbox") {
                this.stopAll(); // Stop any previous voice instructions
                this.speakText(`Would you like to check the ${label}? Say yes or no.`, () => {
                    this.startRecognition((transcript) => {
                        field.checked = transcript.toLowerCase().includes("yes");
                        currentIndex++;
                        handleNextField();
                    });
                });

            // For radio groups
            } else if (field.type === "radio") {
                this.stopAll(); // Stop any previous voice instructions
                const radios = form.querySelectorAll(`input[name="${field.name}"]`);
                const options = Array.from(radios).map(radio => {
                    const lbl = form.querySelector(`label[for="${radio.id}"]`);
                    return lbl ? lbl.innerText : radio.value;
                }).join(", ");
                this.speakText(`Please choose one option for ${label}: ${options}.`, () => {
                    this.startRecognition((transcript) => {
                        const choice = transcript.toLowerCase();
                        radios.forEach(radio => {
                            const lbl = form.querySelector(`label[for="${radio.id}"]`);
                            const text = lbl?.innerText.toLowerCase() || radio.value.toLowerCase();
                            if (text.includes(choice)) radio.checked = true;
                        });
                        currentIndex += radios.length;
                        handleNextField();
                    });
                });

            // For dropdown selects
            } else if (field.tagName === "SELECT") {
                this.stopAll(); // Stop any previous voice instructions
                const options = Array.from(field.options).filter(o => o.value).map(o => o.text).join(", ");
                this.speakText(`Please select a value for ${label}. Your options are: ${options}.`, () => {
                    this.startRecognition((transcript) => {
                        const choice = transcript.toLowerCase();
                        for (let option of field.options) {
                            if (option.text.toLowerCase().includes(choice)) {
                                field.value = option.value;
                                break;
                            }
                        }
                        currentIndex++;
                        handleNextField();
                    });
                });

            // For text, number, email, etc.
            } else {
                this.stopAll(); // Stop any previous voice instructions
                this.speakText(`Please enter your ${label}.`, () => {
                    this.startRecognition((transcript) => {
                        field.value = transcript.trim();
                        field.focus();
                        currentIndex++;
                        handleNextField();
                    });
                });
            }
        };

        // Start form interaction
        this.speakText(introPrompt, () => handleNextField());
    }
}

// Export globally for external use
window.voiceFormAssist = new VoiceFormAssist(window.USER_LANG_CODE, true);
