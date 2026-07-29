import uuid
import random
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from razorpay import Product
from django.views.decorators.csrf import csrf_exempt
from account.models import *
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
import json

from orders.models import *

def generate_random_cookie(length=16):
    characters = str(uuid.uuid4())
    cookie = "".join(random.choices(characters, k=length))
    return cookie



def setCookie(request):
    if request.method == "POST":
        response = JsonResponse({"status": True, "message": "Cookie set successfully!"})
        language = request.POST.get('garuda_language', 'Hindi')  # default 'hi'
        expiry_date = timezone.now() + timedelta(days=365 * 100)
        response.set_cookie("garuda_language", language, expires=expiry_date)
        return response
    else:
        return JsonResponse({"status": False, "message": "Invalid request method."})





@csrf_exempt
def create_order(request):
    cashfree_client_id = settings.CASHFREE_CLIENT_ID
    cashfree_client_secret_key = settings.CASHFREE_CLIENT_SECRET_KEY

    Cashfree.XClientId = str(cashfree_client_id)
    Cashfree.XClientSecret = str(cashfree_client_secret_key)
    Cashfree.XEnvironment = settings.CASHFREE_ENVIRONMENT
    print("environment-->", settings.CASHFREE_ENVIRONMENT)
    x_api_version = "2023-08-01"
    data = json.loads(request.body.decode('utf-8'))
    amount = data.get("cart_total", None)

    print("request.POST-->", request.POST)

    print("amount-->", amount)
    if not amount:
        print("in if")
        return JsonResponse({"status": "error", "message": "Invalid amount."})
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        print("in except")
        return JsonResponse({"status": "error", "message": "Invalid amount."})

    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User not authenticated."})

    modified_phone_number = str(getattr(request.user, 'mobile', '')).replace("+91", "").replace(" ", "")
    if not modified_phone_number:
        modified_phone_number = "9999999999" # Fallback if mobile is missing

    print("modified_phone_number-->", modified_phone_number)

    print("user id-->", request.user.id)

    user_id_str = str(request.user.id)
    if len(user_id_str) == 1:
        user_id_str = "00" + user_id_str
    elif len(user_id_str) == 2:
        user_id_str = "0" + user_id_str

    customerDetails = CustomerDetails(customer_id=str(user_id_str), customer_phone=modified_phone_number)
    createOrderRequest = CreateOrderRequest(order_amount=amount, order_currency="INR", customer_details=customerDetails)
    response_data = None
    try:
        api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
        print("done",api_response.data)
        print(type(api_response.data))

        # Convert response to dictionary format
        if hasattr(api_response.data, 'to_dict'):
            response_data = api_response.data.to_dict()
        elif isinstance(api_response.data, dict):
            response_data = api_response.data
        else:
            response_data = json.loads(str(api_response.data))
        print("------------------->",response_data)
    except Exception as e:
        print("error-->",e)
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status":'success',"api_response": response_data,"environment":settings.JAVASCRIPT_ENV})

def payment_confirmation(request):
    if request.method == "POST":
        try:
            response_data = json.loads(json.dumps(request.POST.get("api_response"), default=str))
            data = json.loads(request.body.decode('utf-8'))
            amount = data.get("cart_total", None)
            address_id = data.get("address_id")
            if amount is None:
                cart_items = CartItem.objects.filter(cart__user=request.user)
                amount = float(sum(item.total_price() for item in cart_items))
            else:
                try:
                    amount = float(amount)
                except (ValueError, TypeError):
                    cart_items = CartItem.objects.filter(cart__user=request.user)
                    amount = float(sum(item.total_price() for item in cart_items))

            # Save transaction
            transaction_instance = Transaction.objects.create(
                user=request.user,
                transaction_user=str(request.user.mobile),
                purpose="order",
                amount=amount,
                order_info=response_data,
                payment_status=True
            )
            transaction_instance.save()

            # Get pg_order_id and pg_order_status from Cashfree response
            pg_order_id = None
            pg_order_status = None
            if isinstance(response_data, dict):
                pg_order_id = response_data.get("order_id") or response_data.get("orderId")
                pg_order_status = response_data.get("order_status") or response_data.get("orderStatus")

            # Get address
            address = None
            if address_id:
                try:
                    from account.models import CustomerAddressModel
                    address = CustomerAddressModel.objects.get(id=address_id, user=request.user)
                except CustomerAddressModel.DoesNotExist:
                    address = None

            # Get cart and items
            cart = Cart.objects.filter(user=request.user).order_by('-created_at').first()
            cart_items = CartItem.objects.filter(cart=cart)

            # Save order summary (cart details)
            order_summary = {
                "items": [
                    {
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "price": float(item.product.price),
                        "total": float(amount),  # Use amount instead of item.total_price()
                    } for item in cart_items
                ],
                "subtotal": float(cart.subtotal()) if cart else 0,
                "total": float(amount),
            }

            # Save order
            order = OrderModel.objects.create(
                user=request.user,
                transaction=transaction_instance,
                pg_order_id=pg_order_id or str(uuid.uuid4()),
                pg_order_status=pg_order_status or "SUCCESS",
                address=address,
                order_summary=order_summary,
            )

            from orders.models import SellerOrderModel
            from communications.utils import create_seller_notification

            seller_orders = {}

            # Save order items and update stock
            for item in cart_items:
                seller = item.product.user
                if seller.id not in seller_orders:
                    seller_order = SellerOrderModel.objects.create(
                        order=order,
                        seller=seller,
                        status='PENDING'
                    )
                    seller_orders[seller.id] = seller_order
                    
                    try:
                        create_seller_notification(
                            seller=seller,
                            title="नया ऑर्डर प्राप्त हुआ",
                            message=f"आपको एक नया ऑर्डर प्राप्त हुआ है (ऑर्डर आईडी: {order.pg_order_id})।",
                            category="ORDER_UPDATE"
                        )
                    except Exception as e:
                        pass # avoid failing checkout if notification fails
                        
                OrderItemModel.objects.create(
                    order=order,
                    seller_order=seller_orders[seller.id],
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.offer_price if item.product.offer_price else item.product.price,  # Use actual item price
                )
                # Update product stock
                if item.product.stock_quantity is not None:
                    item.product.stock_quantity = max(0, item.product.stock_quantity - item.quantity)
                    item.product.save()

            # Clear cart
            cart_items.delete()
  
            return JsonResponse({
                "status": "Payment successful!",
                "pg_order_id": order.pg_order_id,
                "transaction_id": transaction_instance.id,
                "pg_order_status": order.pg_order_status
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)
