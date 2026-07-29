function clearLanguageCookies() {
    document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/";
    document.cookie = "garuda_language=; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/";
    console.log("Cleared language-related cookies.");
}

function initLanguagePreference() {
    clearLanguageCookies();

    // Trigger on radio button change
    $("input[name='language']").on("change", function () {
        const selectedLanguage = $(this).val();
        if (!selectedLanguage) return;

        // Automatically translate via Google Translate if available
        // Usually, setting the cookie and reloading/redirecting is enough for Google Translate.
        // We will set the garuda_language cookie and then redirect to role selection.

        const formData = new FormData(document.getElementById("language-form"));
        formData.append("garuda_language", selectedLanguage);

        // We use the 'set-cookie' endpoint directly since we removed the modal
        sendAjaxRequest({
            url: "/set_cookie/", // Use the global set-cookie url
            data: formData,
            success: (response) => {
                if (response.status || response.success) {
                    // Redirect to Role Selection
                    window.location.href = "/role-selection/";
                } else {
                    console.error("Error saving language:", response.message);
                    window.location.href = "/role-selection/"; // fallback
                }
            },
            error: (xhr) => {
                console.error("Language save error: ", xhr.responseText);
                window.location.href = "/role-selection/"; // fallback
            },
        });
    });
}
