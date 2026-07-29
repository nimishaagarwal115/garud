// ======= Cookie & Language Mapping =========
window.langMap = {
    'English': 'en-US',
    'Hindi': 'hi-IN',
    'Marathi': 'mr-IN',
    'Tamil': 'ta-IN',
    'Telugu': 'te-IN',
    'Gujarati': 'gu-IN',
    'Punjabi': 'pa-IN',
    'Bengali': 'bn-IN',
    'Urdu': 'ur-IN',
    'Kannada': 'kn-IN',
    'Malayalam': 'ml-IN'
};

function getCookie(name) {
    const value = "; " + document.cookie;
    const parts = value.split("; " + name + "=");
    if (parts.length === 2) return decodeURIComponent(parts.pop().split(";").shift());
    return null;
}

function applyLanguagePreference() {
    const userLangName = getCookie("garuda_language");
    let langCode = null;

    if (userLangName && window.langMap[userLangName]) {
        langCode = window.langMap[userLangName].split('-')[0];
        console.log("Using language from cookie:", langCode);
    } else {
        const browserLang = (navigator.language || navigator.userLanguage).split('-')[0];
        const foundEntry = Object.entries(window.langMap).find(([_, val]) => val.startsWith(browserLang));
        if (foundEntry) {
            langCode = foundEntry[1].split('-')[0];
            console.log("Using browser language:", langCode);
        } else {
            console.warn("No matching language found, defaulting to English.");
        }
    }

    if (langCode && langCode !== 'en') {
        const interval = setInterval(() => {
            const select = document.querySelector(".goog-te-combo");
            if (select) {
                select.value = langCode;
                select.dispatchEvent(new Event("change"));
                clearInterval(interval);
                console.log("Auto-translated to:", langCode);
            }
        }, 500);
    } else if (langCode === 'en') {
        // Clear Google Translate cookie for English to revert translation
        if (getCookie("googtrans")) {
            document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
            document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=" + document.domain;
            window.location.reload();
        }
    }
}

// Google Translate Widget Initialization
function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: Object.values(window.langMap).map(code => code.split('-')[0]).join(','),
        autoDisplay: false
    }, 'google_translate_element');

    setTimeout(applyLanguagePreference, 1500);
}

window.googleTranslateElementInit = googleTranslateElementInit;

const userLangName = getCookie("garuda_language") || "English";
window.USER_LANG_CODE = window.langMap?.[userLangName] || "en-IN";
