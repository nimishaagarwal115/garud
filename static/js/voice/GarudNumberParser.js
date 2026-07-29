class GarudNumberParserModule {
    constructor() {
        this.wordToDigit = {
            // English
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            // Hindi (Transliterated)
            'shunya': '0', 'ek': '1', 'do': '2', 'teen': '3', 'char': '4', 'chaar': '4',
            'panch': '5', 'paanch': '5', 'chhah': '6', 'che': '6', 'saat': '7', 
            'aath': '8', 'nau': '9', 'no': '9',
            // Hindi (Devanagari script)
            'शून्य': '0', 'एक': '1', 'दो': '2', 'तीन': '3', 'चार': '4', 
            'पांच': '5', 'पाँच': '5', 'छह': '6', 'सात': '7', 'आठ': '8', 'नौ': '9'
        };

        this.multipliers = {
            'double': 2,
            'triple': 3,
            'डबल': 2,
            'ट्रिपल': 3
        };
    }

    normalizeDigit(char) {
        if (/[0-9]/.test(char)) return char;
        const code = char.charCodeAt(0);
        // Devanagari ०-९
        if (code >= 0x0966 && code <= 0x096F) return String(code - 0x0966);
        // Bengali ০-৯
        if (code >= 0x09E6 && code <= 0x09EF) return String(code - 0x09E6);
        // Gujarati ૦-૯
        if (code >= 0x0AE6 && code <= 0x0AEF) return String(code - 0x0AE6);
        // Tamil ௦-௯
        if (code >= 0x0BE6 && code <= 0x0BEF) return String(code - 0x0BE6);
        // Telugu ౦-౯
        if (code >= 0x0C66 && code <= 0x0C6F) return String(code - 0x0C66);
        // Kannada ೦-೯
        if (code >= 0x0CE6 && code <= 0x0CEF) return String(code - 0x0CE6);
        // Malayalam ൦-൯
        if (code >= 0x0D66 && code <= 0x0D6F) return String(code - 0x0D66);
        return null;
    }

    parse(transcript, fieldType) {
        if (!transcript) return "";
        
        let normalized = transcript.toLowerCase();
        console.log("Raw transcript: " + transcript);
        console.log("Normalized transcript: " + normalized);

        // Split by spaces to process word by word
        let words = normalized.split(/\s+/);
        let parsedChars = [];
        
        for (let i = 0; i < words.length; i++) {
            let word = words[i];
            
            // Check for multiplier (e.g. "double nine", "डबल नौ")
            if (this.multipliers[word] && i + 1 < words.length) {
                let count = this.multipliers[word];
                let nextWord = words[i + 1];
                let digit = this.wordToDigit[nextWord];
                
                // Also check if nextWord is directly an Indic digit like "९"
                if (!digit && nextWord.length === 1) {
                    digit = this.normalizeDigit(nextWord);
                }

                if (digit) {
                    for (let j = 0; j < count; j++) {
                        parsedChars.push(digit);
                    }
                    i++; // Skip the next word
                    continue;
                }
            }

            // Direct mapping
            if (this.wordToDigit[word]) {
                parsedChars.push(this.wordToDigit[word]);
            } else {
                // Parse characters one by one
                for (let char of word) {
                    let normDigit = this.normalizeDigit(char);
                    if (normDigit) {
                        parsedChars.push(normDigit);
                    } else if (/[a-z]/i.test(char)) {
                        parsedChars.push(char.toUpperCase());
                    }
                }
            }
        }

        let parsedString = parsedChars.join('');
        console.log("Parsed number (initial): " + parsedString);

        // Filter based on fieldType
        if (fieldType === 'mobile' || fieldType === 'aadhaar' || fieldType === 'account' || fieldType === 'pin') {
            // Strictly digits
            parsedString = parsedString.replace(/\D/g, '');
        } else if (fieldType === 'ifsc' || fieldType === 'gst') {
            // Alphanumeric
            parsedString = parsedString.replace(/[^A-Z0-9]/g, '');
        }

        console.log("Parsed number (final): " + parsedString);
        return parsedString;
    }
}

window.GarudNumberParser = new GarudNumberParserModule();
