/**
 * GarudAddressParser
 * Intelligently parses spoken addresses into constituent components.
 */

window.GarudAddressParser = {
    async parse(transcript) {
        let result = {
            pincode: "",
            state: "",
            district: "",
            city: "",
            building: ""
        };

        // Normalize text
        let text = transcript.trim();
        
        // 1. Extract PIN Code (6 digits)
        const pinMatch = text.match(/\b\d{6}\b/);
        if (pinMatch) {
            result.pincode = pinMatch[0];
            text = text.replace(pinMatch[0], ""); // Remove pin from text
            
            // Try fetching data from API
            try {
                const res = await fetch(`https://api.postalpincode.in/pincode/${result.pincode}`);
                const data = await res.json();
                
                if (data && data[0] && data[0].Status === "Success") {
                    const postOffice = data[0].PostOffice[0];
                    result.state = postOffice.State || "";
                    result.district = postOffice.District || "";
                    // Block can be City sometimes, but District is safer. 
                    // Let's set City to District if not explicitly available, or use Block/Region.
                    result.city = postOffice.Block || postOffice.District || "";
                    
                    // Remove these discovered words from the building address to avoid duplication
                    const removeWords = [result.state, result.district, result.city];
                    removeWords.forEach(word => {
                        if(word) {
                            const regex = new RegExp(`\\b${word}\\b`, "gi");
                            text = text.replace(regex, "");
                        }
                    });
                }
            } catch (err) {
                console.error("Failed to fetch pin code data:", err);
            }
        }

        // Cleanup filler words like "pin code", "house number", "building" if they are standalone
        // Actually, "House number 45" is useful. We should only remove "pin code" or "pincode"
        text = text.replace(/\bpin code\b/gi, "");
        text = text.replace(/\bpincode\b/gi, "");
        text = text.replace(/\bpin\b/gi, "");
        
        // Custom lookups for common states/cities if PIN wasn't found or API failed
        if (!result.state) {
            const states = ["Rajasthan", "Maharashtra", "Gujarat", "Delhi", "Punjab", "Haryana", "UP", "Uttar Pradesh", "MP", "Madhya Pradesh", "Bihar", "Bengal"];
            for (let s of states) {
                if (new RegExp(`\\b${s}\\b`, "i").test(text)) {
                    result.state = s;
                    text = text.replace(new RegExp(`\\b${s}\\b`, "gi"), "");
                    break;
                }
            }
        }

        if (!result.city) {
            const cities = ["Jaipur", "Kota", "Mumbai", "Pune", "Surat", "Ahmedabad", "Delhi", "Chandigarh", "Ludhiana", "Amritsar", "Agra", "Lucknow", "Indore", "Bhopal", "Patna"];
            for (let c of cities) {
                if (new RegExp(`\\b${c}\\b`, "i").test(text)) {
                    result.city = c;
                    // Usually district is same as major city for simplicity if not found via API
                    if (!result.district) result.district = c;
                    text = text.replace(new RegExp(`\\b${c}\\b`, "gi"), "");
                    break;
                }
            }
        }

        // Clean up punctuation and multiple spaces
        text = text.replace(/[,.-]+/g, " ");
        text = text.replace(/\s+/g, " ").trim();

        result.building = text;

        return result;
    }
};
