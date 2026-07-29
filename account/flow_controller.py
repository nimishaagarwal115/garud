from django.shortcuts import redirect
from django.views import View
from account.models import GovernmentDetailsModel

class CentralFlowControllerView(View):
    def get(self, request, *args, **kwargs):
        # 1. Check if language is selected (cookie: garuda_language)
        if not request.COOKIES.get('garuda_language'):
            return redirect('language_preference_ajax')
            
        # 2. Check if authenticated
        if not request.user.is_authenticated:
            # Not authenticated but language is set -> Role Selection
            return redirect('role_selection')
            
        # 3. Authenticated -> Check Role
        role_name = request.user.roles.name if request.user.roles else 'Customer'
        
        if role_name == 'Customer':
            return redirect('customer_home')
            
        elif role_name == 'Seller':
            # Check seller onboarding status
            gov_details = GovernmentDetailsModel.objects.filter(user=request.user).first()
            
            # If status is UPLOADED, VERIFIED, or ONBOARDING_COMPLETED -> Dashboard
            if gov_details and gov_details.overall_status in ['UPLOADED', 'VERIFIED', 'ONBOARDING_COMPLETED']:
                return redirect('upload_wizard')
            else:
                # Not started or incomplete -> Direct to Onboarding Step 1 (Upload Picture)
                return redirect('seller_onboarding_step', step=1)
                
        # Fallback
        return redirect('role_selection')
