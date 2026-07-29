from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

class BaseTemplateView(TemplateView):
    """
    Base view for all template-based views.
    This class can be extended to create specific template views with common functionality.
    """
    template_name = 'base/base.html'


class AuthenticatedRedirectMixin(View):
    """
    Redirect authenticated users away from pages like login, signup, etc.
    """
    redirect_authenticated_url = 'onboarding_success'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.redirect_authenticated_url)
        return super().dispatch(request, *args, **kwargs)

class BaseDashboardView(LoginRequiredMixin, BaseTemplateView):
    """
    Base view for all dashboard pages.
    This class can be extended to create specific dashboard views with common functionality.
    """
    template_name = 'base/base_dashboard.html'
