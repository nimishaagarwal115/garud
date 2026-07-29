function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        const cookie = cookies.find(c => c.trim().startsWith(name + '='));
        if (cookie) {
            cookieValue = decodeURIComponent(cookie.trim().substring(name.length + 1));
        }
    }
    return cookieValue;
}

function sendAjaxRequest({ url, method = 'POST', data = {}, dataType = 'json', success = () => { }, error = () => { } }) {
    let isFormData = data instanceof FormData;

    // Inject CSRF token
    if (isFormData && !data.has('csrfmiddlewaretoken')) {
        data.append('csrfmiddlewaretoken', getCSRFToken());
    }

    $.ajax({
        url: url,
        type: method,
        data: isFormData ? data : JSON.stringify(data),
        dataType: dataType,
        processData: isFormData ? false : true,
        contentType: isFormData ? false : 'application/json',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        success: success,
        error: error
    });
}

// // Language preference form submission
// $(document).ready(function () {
//     $("#language-form").submit(function (e) {
//         e.preventDefault();
//         let formData = new FormData(this);

//         sendAjaxRequest({
//             url: "{% url 'language_preference_ajax' %}",
//             data: formData,
//             success: function (response) {
//                 if (response.success) {
//                     $("#cookieModal").modal("show");
//                 } else {
//                     console.error("Validation error: ", response.errors);
//                 }
//             },
//             error: function (xhr) {
//                 console.error("Server error: ", xhr.responseText);
//             }
//         });
//     });
// });

// // Cookie consent form submission
// $("#cookie-form").submit(function (e) {
//     e.preventDefault();
//     let formData = new FormData(this);

//     sendAjaxRequest({
//         url: "{% url 'cookie_consent_ajax' %}",
//         data: formData,
//         success: function (response) {
//             if (response.success) {
//                 window.location.href = "{% url 'phone_login' %}";
//             }
//         },
//         error: function (xhr) {
//             console.error("Cookie consent error: ", xhr.responseText);
//         }
//     });
// });


// $('#phone-login-form').on('submit', function (e) {
//     e.preventDefault();
//     let formData = new FormData(this);

//     sendAjaxRequest({
//         url: '/phone_login/',
//         data: formData,
//         success: function (response) {
//             if (response.success) {
//                 window.location.href = '/verify_otp/';
//             } else {
//                 showtoast('error', response.error || 'Failed to send OTP.');
//             }
//         },
//         error: function () {
//             showtoast('error', 'Error occurred while logging in.');
//         }
//     });
// });
