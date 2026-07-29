document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.aadhaar-form');
    const submitBtn = document.getElementById('submitBtn');
    
    console.log('Annual Income & Occupation page loaded');
    
    form.addEventListener('submit', function(e) {
        console.log('Form submit triggered');
        
        const annualIncomeValue = document.getElementById('id_annual_income').value;
        const occupationValue = document.getElementById('id_occupation').value;
        
        console.log('Annual income value:', annualIncomeValue);
        console.log('Occupation value:', occupationValue);
        
        // Validate annual income
        if (!annualIncomeValue || annualIncomeValue.trim() === '') {
            e.preventDefault();
            alert('Please enter your annual income');
            return false;
        }
        
        if (isNaN(annualIncomeValue) || parseInt(annualIncomeValue) < 0) {
            e.preventDefault();
            alert('Please enter a valid annual income (positive number)');
            return false;
        }
        
      
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Processing...';
        
        console.log('Form validation passed, submitting...');
    });
});