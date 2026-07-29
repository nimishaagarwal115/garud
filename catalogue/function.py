from django.http import JsonResponse
from catalogue.models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST



@require_POST
@login_required
def add_to_wishlist(request):
    product_id = request.POST.get('product_id')
    try:
        product = ProductModel.objects.get(pk=product_id)
    except ProductModel.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found.'})

    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
    if not created:
        return JsonResponse({'success': False, 'message': 'Already in Wishlist.'})
    return JsonResponse({'success': True, 'message': 'Added to Wishlist.'})



@require_POST
@login_required
def remove_from_wishlist(request):
    product_id = request.POST.get('product_id')
    try:
        product = ProductModel.objects.get(pk=product_id)
        wishlist = Wishlist.objects.get(user=request.user)
        item = WishlistItem.objects.get(wishlist=wishlist, product=product)
        item.delete()
        return JsonResponse({'success': True, 'message': 'Removed from Wishlist.'})
    except (ProductModel.DoesNotExist, Wishlist.DoesNotExist, WishlistItem.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Item not found in Wishlist.'})