from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView



class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = 'costuner_flow/wishlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wishlist = getattr(self.request.user, 'wishlist', None)
        items = wishlist.items.select_related('product') if wishlist else []
        context['wishlist_items'] = items
        return context