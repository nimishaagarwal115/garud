from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class RoleRequiredMixin(AccessMixin):
    """
    Abstract mixin that checks if the user has a specific role.
    """
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        user_role = request.user.roles.name if request.user.roles else 'Customer'
        if user_role != self.required_role:
            return redirect('central_controller')
            
        return super().dispatch(request, *args, **kwargs)

class CustomerRequiredMixin(RoleRequiredMixin):
    required_role = 'Customer'

class SellerRequiredMixin(RoleRequiredMixin):
    required_role = 'Seller'
