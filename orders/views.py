from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Q
from .models import SellerOrderModel
from communications.utils import create_seller_notification
from catalogue.models import ProductReviewModel
import json

class SellerOrderListView(LoginRequiredMixin, ListView):
    model = SellerOrderModel
    template_name = 'seller/orders/list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        # Base query for logged in seller
        qs = SellerOrderModel.objects.filter(seller=self.request.user).order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.GET.get('status', 'ALL')
        if status_filter != 'ALL':
            qs = qs.filter(status=status_filter)
            
        # Search (Global)
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            qs = qs.filter(
                Q(order__pg_order_id__icontains=search_query) |
                Q(items__product__name__icontains=search_query) |
                Q(order__user__full_name__icontains=search_query) |
                Q(order__user__mobile__icontains=search_query)
            ).distinct()
            
        # Specific Order ID filter (from Filter modal)
        order_id_query = self.request.GET.get('order_id', '').strip()
        if order_id_query:
            qs = qs.filter(order__pg_order_id__icontains=order_id_query)
            
        # Date filters
        date_from = self.request.GET.get('date_from', '').strip()
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
            
        date_to = self.request.GET.get('date_to', '').strip()
        if date_to:
            # We append 23:59:59 to include the whole end day if they just send YYYY-MM-DD
            if len(date_to) == 10:
                qs = qs.filter(created_at__lte=f"{date_to} 23:59:59")
            else:
                qs = qs.filter(created_at__lte=date_to)
            
        return qs
        
class SellerOrderDetailView(LoginRequiredMixin, DetailView):
    model = SellerOrderModel
    template_name = 'seller/orders/detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return SellerOrderModel.objects.filter(seller=self.request.user)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate subtotal, discount, taxes. 
        # For now, we will sum up items.
        seller_order = self.get_object()
        items = seller_order.items.all()
        
        subtotal = sum(item.price * item.quantity for item in items)
        
        # Assuming no explicit discount or tax fields on OrderItemModel currently,
        # we just pass subtotal.
        context['subtotal'] = subtotal
        context['discount'] = 0
        context['taxes'] = 0
        context['grand_total'] = subtotal
        return context

class SellerOrderTrackingView(LoginRequiredMixin, DetailView):
    model = SellerOrderModel
    template_name = 'seller/orders/tracking.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return SellerOrderModel.objects.filter(seller=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller_order = self.get_object()
        
        # Get reviews for products in this order
        product_ids = seller_order.items.values_list('product_id', flat=True)
        reviews = ProductReviewModel.objects.filter(product_id__in=product_ids).order_by('-created_at')
        
        context['reviews'] = reviews
        return context

class SellerOrderStatusUpdateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        seller_order = get_object_or_404(SellerOrderModel, pk=pk, seller=request.user)
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            
            valid_statuses = [c[0] for c in SellerOrderModel.STATUS_CHOICES]
            if new_status in valid_statuses:
                seller_order.status = new_status
                seller_order.save()
                
                # Send notification
                status_messages = {
                    'CONFIRMED': "ऑर्डर कन्फर्म हो गया है।",
                    'PACKED': "ऑर्डर पैक हो गया है।",
                    'SHIPPED': "ऑर्डर शिप हो गया है।",
                    'DELIVERED': "ऑर्डर डिलीवर हो गया है।",
                    'CANCELLED': "ऑर्डर रद्द हो गया है।"
                }
                msg = status_messages.get(new_status, f"ऑर्डर का स्टेटस '{new_status}' में अपडेट हो गया है।")
                
                try:
                    create_seller_notification(
                        seller=request.user,
                        title="ऑर्डर स्टेटस अपडेट",
                        message=f"ऑर्डर {seller_order.order.pg_order_id}: {msg}",
                        category="ORDER_UPDATE"
                    )
                except Exception:
                    pass
                    
                # Notify Customer
                try:
                    from communications.utils import create_customer_notification
                    from django.urls import reverse
                    
                    customer = seller_order.order.user
                    cust_msg = ""
                    if new_status == 'CONFIRMED':
                        cust_msg = f"Your order #{seller_order.order.pg_order_id} has been <strong>confirmed</strong>."
                    elif new_status == 'PACKED':
                        cust_msg = f"Your order #{seller_order.order.pg_order_id} has been <strong>packed</strong>."
                    elif new_status == 'SHIPPED':
                        cust_msg = f"Your order #{seller_order.order.pg_order_id} has been <strong>shipped</strong>."
                    elif new_status == 'DELIVERED':
                        cust_msg = f"Package from your order <strong style='color:#b94a2c;'>#{seller_order.order.pg_order_id}</strong> has <strong>arrived</strong>."
                    elif new_status == 'CANCELLED':
                        cust_msg = f"Your order #{seller_order.order.pg_order_id} was <strong>cancelled</strong>."
                        
                    if cust_msg:
                        # Find the target URL for the customer order details
                        first_item = seller_order.items.first()
                        target_url = reverse('customer_order_info', args=[first_item.id]) if first_item else "#"
                        
                        # Use product image from first item if available
                        img = first_item.product.image if first_item and first_item.product.image else None
                        
                        create_customer_notification(
                            user=customer,
                            title="", # The prototype only shows text, we can put everything in message
                            message=cust_msg,
                            category="ORDER_UPDATE",
                            image=img,
                            target_url=target_url
                        )
                except Exception as e:
                    print("Error notifying customer:", e)

                return JsonResponse({'success': True, 'status': new_status})
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
