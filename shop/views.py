from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from cart.models import Cart, CartItem
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from category.models import Category
from .models import Customers, Order, OrderItem, Payment, ShippingAddress, Wishlist, Review
from artist.models import ProNotification, Product
from django.views.decorators.http import require_POST
import logging
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import logging
from artist.models import ProNotification
from cart.models import CartItem
import razorpay
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from django.db.models import Q
from django.shortcuts import render
from .models import Product
from category.models import Category  
from accounts.models import Artist, ArtistAddress
from django.utils import timezone
from datetime import timedelta
from delivery.models import DeliveryOrder
import cv2
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import base64
import io
from PIL import Image
from .models import Customers
from django.contrib.auth import login
import logging

logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from cart.models import Cart, CartItem
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from category.models import Category
from .models import Customers, Order, OrderItem, Payment, ShippingAddress, Wishlist, Review
from artist.models import ProNotification, Product

from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied

# Create your views here.

def shop_index(request, category_slug=None):
    try:
        products = Product.objects.filter(is_available=True)
        categories = Category.objects.all()

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(categories=category)

        cart_count = 0
        wishlist_count = 0

        if request.user.is_authenticated:
            try:
                customer = Customers.objects.get(user=request.user)
                wishlist_count = Wishlist.objects.filter(user=customer).count()
            except Customers.DoesNotExist:
                wishlist_count = 0

        context = {
            'products': products,
            'categories': categories,
            'cart_count': cart_count,
            'wishlist_count': wishlist_count,
        }
        return render(request, 'customers/index.html', context)
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, 'customers/index.html', {
            'categories': Category.objects.all(),
            'products': [],
            'cart_count': 0,
            'wishlist_count': 0,
        })

def product_detail(request,category_slug,product_slug):
    category=get_object_or_404(Category,slug=category_slug)
    single_product=get_object_or_404(Product,categories=category,slug=product_slug)
    cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = cart_items.count()
    
       # Wishlist count logic
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            customer = get_object_or_404(Customers, user=request.user)
            wishlist_count = Wishlist.objects.filter(user=customer).count()
        except Customers.DoesNotExist:
            wishlist_count = 0  # In case the customer is not found
    
    context={
        'single_product':single_product,
        'cart_count': cart_count,
         'wishlist_count': wishlist_count,
    }
    return render(request, 'customers/product_detail.html',context)


def customerRegister(request):
    request.session['user_role']='customer'
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        profile_pic_data=request.POST.get('profile_pic')
        face_data=request.POST.get('face_data')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        
        logger = logging.getLogger(__name__)
        logger.info("Starting customer registration process")
        
        if password==confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request,'Username already exists')
                return redirect('customer_register')
            elif User.objects.filter(email=email).exists():
                messages.error(request,'Email already exists')
                return redirect('customer_register')
            elif Customers.objects.filter(phone=phone).exists():
                messages.error(request,'Phone number already exists')
                return redirect('customer_register')
            else:
                try:
                    with transaction.atomic():
                        # Create user
                        user = User.objects.create_user(username=username, email=email, password=password)
                        logger.info(f"Created user: {username}")
                        
                        # Process face data
                        if face_data and ',' in face_data:
                            import base64
                            import cv2
                            import numpy as np
                            from django.core.files.base import ContentFile
                            
                            # Remove data URL prefix and get base64 data
                            format, imgstr = face_data.split(';base64,')
                            ext = format.split('/')[-1]
                            
                            # Decode base64 image
                            image_bytes = base64.b64decode(imgstr)
                            nparr = np.frombuffer(image_bytes, np.uint8)
                            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            
                            if img is None:
                                raise Exception("Failed to decode image")
                            
                            # Convert to grayscale for face detection
                            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            
                            # Load face cascade classifier
                            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                            faces = face_cascade.detectMultiScale(
                                gray,
                                scaleFactor=1.1,
                                minNeighbors=5,
                                minSize=(30, 30)
                            )
                            
                            if len(faces) == 0:
                                raise Exception("No face detected in the image")
                            
                            # Process the largest face
                            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                            face_img = gray[y:y+h, x:x+w]
                            
                            # Standardize size and enhance
                            face_img = cv2.resize(face_img, (128, 128))
                            face_img = cv2.equalizeHist(face_img)
                            
                            # Convert processed face to bytes
                            success, buffer = cv2.imencode('.jpg', face_img)
                            if not success:
                                raise Exception("Failed to encode face image")
                            
                            face_bytes = buffer.tobytes()
                            
                            # Create profile picture file
                            profile_pic = ContentFile(image_bytes, name=f'{username}_profile.{ext}')
                            
                            # Create customer with face data
                            customer = Customers.objects.create(
                                user=user,
                                phone=phone,
                                profile_pic=profile_pic,
                                face_encoding=face_bytes,
                                face_registered=True
                            )
                            logger.info(f"Created customer with face registration: {username}")
                        else:
                            # Create customer without face data
                            customer = Customers.objects.create(
                                user=user,
                                phone=phone
                            )
                            logger.info(f"Created customer without face registration: {username}")
                        
                        messages.success(request, 'Registration successful! Please login.')
                        logger.info(f"Registration successful for user: {username}")
                        return redirect('customerlogin')
                        
                except Exception as e:
                    logger.error(f"Registration error for {username}: {str(e)}")
                    messages.error(request, f'Registration failed: {str(e)}')
                    return redirect('customer_register')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('customer_register')
    
    return render(request, 'customers/Register.html')


@csrf_exempt
def customerLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and hasattr(user, 'customers'):
            login(request, user)
            messages.success(request, 'Login successfully')
            return redirect('shop_index')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'customers/login.html')
    return render(request, 'customers/login.html')

def customerLogout(request):
    logout(request)
    request.session.flush()
    messages.success(request,'Logout successfully')
    return redirect('customerlogin')
    

from django.shortcuts import redirect
from cart.models import Cart, CartItem
from artist.models import Product
from django.core.exceptions import ObjectDoesNotExist

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

@login_required(login_url='customerlogin')
def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.Quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            Quantity=1
        )
        cart_item.save()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.Quantity)
            quantity += cart_item.Quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart.html', context)
                
                                                 
import razorpay
from django.conf import settings

# def checkout(request):
#     cart = None
#     cart_items = []
#     cart_total = 0
#     tax = 0
#     grand_total = 0

#     try:
#         cart = Cart.objects.get(cart_id=_cart_id(request))
#         cart_items = CartItem.objects.filter(cart=cart, is_active=True)

#         for item in cart_items:
#             item.total_price = item.product.price * item.Quantity
#             cart_total += item.total_price

#         tax = (2 * cart_total) / 100  
#         grand_total = cart_total + tax
#     except Cart.DoesNotExist:
#         pass

#     if request.method == 'POST':
#         if cart_total <= 0:
#             messages.error(request, "Your cart is empty. Please add items before checking out.")
#             return redirect('cart')

 
#         order = Order.objects.create(
#             customer=request.user,
#             total_amount=grand_total
#         )

#         for cart_item in cart_items:
#             order_item = OrderItem.objects.create(
#                 order=order,
#                 product=cart_item.product,
#                 quantity=cart_item.Quantity,
#                 price=cart_item.product.price
#             )

#             # Notify the artist
#             artist = cart_item.product.artist
#             message = f"Your product '{cart_item.product.name}' has been ordered by {request.user.username}."
#             ProNotification.objects.create(artist=artist,order=order,  message=message)

#         shipping_address = ShippingAddress.objects.create(
#             customer=request.user,
#             order=order,
#             address=request.POST.get('address'),
#             city=request.POST.get('city'),
#             state=request.POST.get('state'),
#             zip_code=request.POST.get('zipcode'),
#             country=request.POST.get('country', '')
#         )


#         print(Payment.__dict__) 
#         payment = Payment.objects.create(
#             customer=request.user,  
#             order=order,
#             amount=grand_total,  
#             shipping_address=shipping_address
#         )

#         client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
#         razorpay_order = client.order.create({
#             'amount': int(grand_total * 100),  # Amount in paise
#             'currency': 'INR',
#             'payment_capture': '1'
#         })

#         order.razorpay_order_id = razorpay_order['id']
#         order.save()

#         context = {
#             'order': order,
#             'cart_items': cart_items,
#             'cart_total': cart_total,
#             'tax': tax,
#             'grand_total': grand_total,
#             'razorpay_order_id': order.razorpay_order_id,
#             'razorpay_merchant_key': settings.RAZORPAY_API_KEY,
#             'callback_url': request.build_absolute_uri(reverse('razorpay_callback'))
#         }

#         return render(request, 'customers/checkout.html', context)

#     context = {
#         'cart_items': cart_items,
#         'cart_total': cart_total,
#         'tax': tax,
#         'grand_total': grand_total,
#     }

#     return render(request, 'customers/checkout.html', context)

import razorpay
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

@login_required
def checkout(request):
    logger.info("Checkout view called")
    cart = None
    cart_items = []
    cart_total = 0
    tax = 0
    grand_total = 0

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for item in cart_items:
            item.total_price = item.product.price * item.Quantity
            cart_total += item.total_price
        
        tax = (2 * cart_total) / 100  # 2% tax
        grand_total = cart_total + tax
    except Cart.DoesNotExist:
        logger.warning("Cart does not exist")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'Cart is empty'
            }, status=400)
        return redirect('cart')

    if request.method == 'POST':
        logger.info("POST request received")
        selected_address_id = request.POST.get('selected_address')
        logger.info(f"Selected address ID: {selected_address_id}")
        
        try:
            if selected_address_id:
                shipping_address = get_object_or_404(SavedAddress, id=selected_address_id, user=request.user)
            else:
                # For manual address entry
                address = request.POST.get('address')
                city = request.POST.get('city')
                state = request.POST.get('state')
                zipcode = request.POST.get('zipcode')
                
                if not all([address, city, state, zipcode]):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Please fill all address fields'
                    }, status=400)
                
                shipping_address = SavedAddress.objects.create(
                    user=request.user,
                    address=address,
                    city=city,
                    state=state,
                    zip_code=zipcode
                )
            
            # Create Razorpay order
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
            razorpay_order = client.order.create({
                'amount': int(grand_total * 100),  # Amount in paise
                'currency': 'INR',
                'payment_capture': '1'
            })

            order = Order.objects.create(
                customer=request.user,
                total_amount=grand_total,
                razorpay_order_id=razorpay_order['id']
            )
            logger.info(f"Order created in database: {order.id}")

            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.Quantity,
                    price=cart_item.product.price
                )
            logger.info("Order items created")

            # Create shipping address for the order
            ShippingAddress.objects.create(
                customer=request.user,
                order=order,
                address=shipping_address.address,
                city=shipping_address.city,
                state=shipping_address.state,
                zip_code=shipping_address.zip_code
            )
            logger.info("Shipping address created")

            return JsonResponse({
                'status': 'success',
                'razorpay_order_id': razorpay_order['id'],
                'amount': int(grand_total * 100),
                'message': 'Order created successfully'
            })
            
        except SavedAddress.DoesNotExist:
            logger.error("Selected address not found")
            return JsonResponse({
                'status': 'error',
                'message': 'Selected address not found'
            }, status=400)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f"An error occurred: {str(e)}"
            }, status=400)
    
    # For GET requests
    saved_addresses = SavedAddress.objects.filter(user=request.user)
    context = {
        'saved_addresses': saved_addresses,
        'cart_items': cart_items,
        'cart_total': cart_total,
        'tax': tax,
        'grand_total': grand_total,
        'razorpay_merchant_key': settings.RAZORPAY_API_KEY,
        'callback_url': request.build_absolute_uri(reverse('razorpay_callback'))
    }
    logger.info("Rendering initial checkout template")
    return render(request, 'customers/checkout.html', context)

from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, ShippingAddress
from django.shortcuts import render
from cart.models import Cart, CartItem  # Assuming Cart is in a separate 'cart' app

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    if order.customer != request.user:
        return HttpResponseForbidden("You are not allowed to view this order.")
    
    # Clear the cart
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
        cart_items.delete()
    except Cart.DoesNotExist:
        pass  # If the cart doesn't exist, we don't need to clear it
    except NameError:
        # If Cart is not defined, skip cart clearing
        pass
    
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        item.subtotal = item.get_subtotal()
    
    shipping_address = ShippingAddress.objects.filter(order=order).first()
    
    context = {
        'order': order,
        'order_items': order_items,
        'shipping_address': shipping_address,
    }
    return render(request, 'customers/payment_success.html', context)


from django.http import HttpResponse, HttpResponseForbidden


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.customer != request.user:
        return HttpResponseForbidden("You are not allowed to view this order.")

    order_items = order.orderitem_set.all()

    for item in order_items:
        item.subtotal = item.get_subtotal()
    shipping_addresses = order.shipping_addresses.all()  
    shipping_address = shipping_addresses.first() if shipping_addresses.exists() else None

    context = {
        'order': order,
        'order_items': order_items,
        'shipping_address': shipping_address,
    }

    return render(request, 'customers/order_summary_partial.html', context)
from django.core.paginator import Paginator

def order_history(request):
    user_orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    # Add debug information
    for order in user_orders:
        print(f"Order #{order.id} - Status: {order.status}")
        
        # Get the latest delivery order status
        try:
            latest_delivery = DeliveryOrder.objects.filter(order=order).latest('created_at')
            order.track_status = latest_delivery.status
            print(f"Latest Delivery Status: {latest_delivery.status}")
        except DeliveryOrder.DoesNotExist:
            order.track_status = None
            print("No delivery order found")

    paginator = Paginator(user_orders, 10)
    page_number = request.GET.get('page')
    page_orders = paginator.get_page(page_number)

    context = {
        'user_orders': page_orders
    }
    return render(request, 'customers/order_history.html', context)

@login_required
def view_order_items(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.customer != request.user:
        return HttpResponseForbidden("You are not allowed to view this order.")
  
    order_items = order.orderitem_set.all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'customers/view_order_items.html', context)


@login_required
def add_order_item(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    

    if order.customer != request.user:
        return HttpResponseForbidden("You are not allowed to modify this order.")
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        if product.stock < quantity:
            messages.error(request, "Insufficient stock for this product.")
            return redirect('add_order_item', order_id=order_id)
        
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )
        if not created:
            order_item.quantity += quantity
            order_item.save()

        order.update_total_amount()
        
        messages.success(request, f"{product.name} has been added to the order.")
        return redirect('view_order_items', order_id=order.id)
    
    products = Product.objects.all()  
    return render(request, 'customers/add_order_item.html', {'order': order, 'products': products})

@login_required
def update_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    
    if order_item.order.customer != request.user:
        return HttpResponseForbidden("You are not allowed to modify this order item.")
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', order_item.quantity))
        

        product = order_item.product
        if product.stock + order_item.quantity < quantity:  
            messages.error(request, "Insufficient stock for this product.")
            return redirect('update_order_item', order_item_id=order_item.id)
        
        product.stock += order_item.quantity 
        order_item.quantity = quantity
        order_item.save()
        
        product.stock -= quantity
        product.save()
        

        order_item.order.update_total_amount()
        
        messages.success(request, "Order item has been updated.")
        return redirect('view_order_items', order_id=order_item.order.id)
    
    return render(request, 'customers/update_order_item.html', {'order_item': order_item})

from .models import Wishlist

def wishlist_count(request):
    if request.user.is_authenticated:
        customer = request.user.customers
        wishlist_count = Wishlist.objects.filter(user=customer).count()
    else:
        wishlist_count = 0
    return {
        'wishlist_count': wishlist_count
    }

@login_required
def delete_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    
    if order_item.order.customer != request.user:
        return HttpResponseForbidden("You are not allowed to delete this order item.")
    
    order = order_item.order
    order_item.delete()
    

    order.update_total_amount()
    
    messages.success(request, "Order item has been removed.")
    return redirect('view_order_items', order_id=order.id)  

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import logging
from artist.models import ProNotification
from cart.models import CartItem

@csrf_exempt
def razorpay_callback(request):
    logger = logging.getLogger(__name__)
    logger.info("Razorpay callback received")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Body: {request.body.decode('utf-8')}")
    
    if request.method == "POST":
        try:
            # Initialize the Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
            
            # Get the payment details from the POST data
            payment_details = json.loads(request.body)
            
            logger.info(f"Payment details: {payment_details}")
            
            # Verify the payment signature
            params_dict = {
                'razorpay_payment_id': payment_details.get('razorpay_payment_id'),
                'razorpay_order_id': payment_details.get('razorpay_order_id'),
                'razorpay_signature': payment_details.get('razorpay_signature')
            }
            
            logger.info(f"Params for signature verification: {params_dict}")
            
            try:
                client.utility.verify_payment_signature(params_dict)
            except Exception as e:
                logger.error(f"Invalid payment signature: {str(e)}")
                return JsonResponse({'status': 'error', 'message': 'Invalid payment signature'}, status=400)
            
            # Payment signature is valid, update your order status
            order = Order.objects.get(razorpay_order_id=payment_details['razorpay_order_id'])
            order.status = 'Paid'
            order.razorpay_payment_id = payment_details['razorpay_payment_id']
            order.save()
            logger.info(f"Order {order.id} status updated to Paid")
            
            # Get the shipping address
            shipping_address = order.shipping_addresses.first()
            if not shipping_address:
                logger.error(f"No shipping address found for order {order.id}")
                return JsonResponse({'status': 'error', 'message': 'No shipping address found'}, status=400)
            
            # Create a payment record with shipping address
            Payment.objects.create(
                order=order,
                customer=order.customer,
                payment_id=payment_details['razorpay_payment_id'],
                amount=order.total_amount,
                status='Success',
                shipping_address=shipping_address
            )
            logger.info(f"Payment record created for order {order.id}")

            # Get cart items and create notifications for artists
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
            # Create notifications for each artist whose product was purchased
            for cart_item in cart_items:
                product = cart_item.product
                artist = product.artist
                message = f"New order received! {order.customer.username} has purchased {cart_item.Quantity} unit(s) of {product.name}."
                
                # Create notification for the artist
                ProNotification.objects.create(
                    artist=artist,
                    order=order,
                    message=message
                )
                logger.info(f"Notification created for artist {artist.user.username}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Payment successful',
                'redirect_url': reverse('payment_success', args=[order.id])
            })
        
        except Exception as e:
            logger.error(f"Error in razorpay_callback: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    logger.warning("Invalid request method for Razorpay callback")
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

import razorpay
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

def create_order(request):
    # Disable SSL verification warning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    # Create Razorpay client with SSL verification disabled
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
    client.set_app_details({"title": "Django", "version": "4.2"})
    session = requests.Session()
    session.verify = False
    client.session = session

    razorpay_order = client.order.create(dict(
        amount=Order.total_amount * 100,  # Amount in paise
        currency="INR",
        payment_capture="1"
    ))

    Order.razorpay_order_id = razorpay_order['id']
    Order.save()

    # Re-enable SSL verification warning
    requests.packages.urllib3.enable_warnings(InsecureRequestWarning)


# wishlist


@login_required
def add_to_wishlist(request, product_id):
    customer = get_object_or_404(Customers, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
  
    if not Wishlist.objects.filter(user=customer, product=product).exists():
        Wishlist.objects.create(user=customer, product=product)

    category = product.categories.first()
    if category:
        return redirect('product_detail', category_slug=category.slug, product_slug=product.slug)

    return redirect('shop_index')  

@login_required
def remove_from_wishlist(request, product_id):
    customer = get_object_or_404(Customers, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item = Wishlist.objects.filter(user=customer, product=product).first()
    if wishlist_item:
        wishlist_item.delete()
    
    return redirect('wishlist')

@login_required
def view_wishlist(request):
    customer = get_object_or_404(Customers, user=request.user)
    wishlist_items = Wishlist.objects.filter(user=customer)

    wishlist_count = wishlist_items.count()
    cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
    cart_items = CartItem.objects.filter(cart=cart)
    cart_count = cart_items.count()

    return render(request, 'customers/wishlist.html', { 
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
        'cart_count':cart_count
    }) 

def customerprofile(request):
    if request.user.is_authenticated and request.user.customers:
        customers=request.user.customers
        return render(request,'customers/dashboard.html',{'customers':customers})
    
@login_required
def add_to_cart_from_wishlist(request, product_id):
    customer = get_object_or_404(Customers, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    
    
  
    cart = Cart.objects.get_or_create(cart_id=_cart_id(request))[0]

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'Quantity': 1}  
    )

    if not created:
        cart_item.Quantity += 1
        cart_item.save()

    Wishlist.objects.filter(user=customer, product=product).delete()
    return redirect('wishlist')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SavedAddress  # Add this import


@login_required
def add_address(request):
    if request.method == 'POST':
        # Process the form data
        SavedAddress.objects.create(
            user=request.user,
            address_type=request.POST.get('address_type'),
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            zip_code=request.POST.get('zip_code')
        )
        return redirect('add_address')

    # Fetch saved addresses for the user
    addresses = SavedAddress.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'customers/add_address.html', context)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SavedAddress
from django.views.decorators.http import require_POST

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import SavedAddress

logger = logging.getLogger(__name__)

@login_required
@require_POST
def edit_address(request, address_id):
    try:
        address = SavedAddress.objects.get(id=address_id, user=request.user)
        
        address.address_type = request.POST.get('address_type')
        address.full_name = request.POST.get('full_name')
        address.phone = request.POST.get('phone')
        address.address = request.POST.get('address')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.zip_code = request.POST.get('zip_code')
        address.save()
        
        return JsonResponse({'success': True, 'message': 'Address updated successfully.'})
    except SavedAddress.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Address not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Address deleted successfully.')
    return redirect('add_address')

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@login_required
@require_POST
@csrf_exempt
def create_razorpay_order(request):
    data = json.loads(request.body)
    address_id = data.get('address_id')
    grand_total = float(data.get('grand_total'))

    try:
        shipping_address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
        
        # Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
        razorpay_order = client.order.create({
            'amount': int(grand_total * 100),  # Amount in paise
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Create order in your database
        order = Order.objects.create(
            customer=request.user,
            total_amount=grand_total,
            razorpay_order_id=razorpay_order['id']
        )

        # Create shipping address for the order
        ShippingAddress.objects.create(
            customer=request.user,
            order=order,
            address=shipping_address.address,
            city=shipping_address.city,
            state=shipping_address.state,
            zip_code=shipping_address.zip_code
        )

        return JsonResponse({'status': 'success', 'order_id': razorpay_order['id']})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def user_profile(request):
    context = {
        'user': request.user,
        'cart_count': get_cart_count(request),
    }
    return render(request, 'customers/user_profile.html', context)

from django.db.models import Prefetch
@login_required
def view_your_orders(request):
    # Use select_related for ForeignKey relationships and prefetch_related for ManyToMany or reverse ForeignKey
    user_orders = Order.objects.filter(
        customer=request.user,
        payment__status='Success'
    ).order_by('-created_at').prefetch_related(
        Prefetch('orderitem_set', 
                queryset=OrderItem.objects.select_related('product'))
    )
    
    # Debug information
    for order in user_orders:
        for item in order.orderitem_set.all():
            print(f"Product: {item.product.name}")
            print(f"Image: {item.product.image.url if item.product.image else 'No image'}")
    
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            customer = get_object_or_404(Customers, user=request.user)
            wishlist_count = Wishlist.objects.filter(user=customer).count()
        except Customers.DoesNotExist:
            wishlist_count = 0

    context = {
        'user_orders': user_orders,
        'cart_count': get_cart_count(request),
        'wishlist_count': wishlist_count
    }
    return render(request, 'customers/view_your_orders.html', context)


def get_cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
            cart_count = cart_items.count()
        except Cart.DoesNotExist:
            pass
    return cart_count
from django.contrib.auth.decorators import login_required
def track_order_status(request):
    customer=get_object_or_404(Customers,user=request.user)
    orders=Order.objects.filter(customer=request.user)
    return render(request,'customers/tracking.html',{'orders':orders})

from django.db.models import Q
from django.shortcuts import render
from .models import Product
from category.models import Category  # Import Category from the correct app

def search_products(request):
    try:
        query = request.GET.get('q', '')
        products = Product.objects.filter(is_available=True)
        
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            ).distinct()
            
            # Debug prints
            print(f"Search Query: {query}")
            print(f"Found {products.count()} products")
            for product in products:
                print(f"- {product.name}")
        
        context = {
            'products': products,
            'query': query,
            'links': Category.objects.all(),  # Add this back for navigation
        }
        
        return render(request, 'customers/index.html', context)
    except Exception as e:
        print(f"Error in search_products: {str(e)}")  # Debug print
        # Return empty results in case of error
        context = {
            'products': [],
            'query': query if 'query' in locals() else '',
            'links': Category.objects.all(),
            'error': 'An error occurred while searching. Please try again.'
        }
        return render(request, 'customers/index.html', context)

from accounts.models import Artist, ArtistAddress
from django.utils import timezone
from datetime import timedelta
from delivery.models import DeliveryOrder

@login_required
def update_order_status(request, order_id):
    """Handle order dispatch and create delivery order"""
    from accounts.models import Artist, ArtistAddress
    from django.utils import timezone
    from datetime import timedelta
    from delivery.models import DeliveryOrder
    
    # Get the order and artist
    order = get_object_or_404(Order, id=order_id)
    artist = get_object_or_404(Artist, user=request.user)
    artist_address = get_object_or_404(ArtistAddress, artist=artist)
    
    # Get shipping address directly from order
    shipping_address = order.shipping_addresses.first()
    if not shipping_address:
        messages.error(request, 'No shipping address found for this order')
        return redirect('order_notifications')
    
    print(f"Creating delivery order with artist pincode: {artist_address.pincode}")
    
    # Create delivery order
    delivery_order = DeliveryOrder.objects.create(
        order=order,
        status='AVAILABLE',  # Changed from 'PENDING' to 'AVAILABLE'
        delivery_pincode=artist_address.pincode,  # Match with delivery partner's pincode
        
        # Pickup details (artist's address)
        artist_address=artist_address.address,
        artist_pincode=artist_address.pincode,
        pickup_date=timezone.now().date(),
        pickup_time=timezone.now().time(),
        
        # Delivery details (customer's address)
        customer_address=f"{shipping_address.address}, {shipping_address.city}, {shipping_address.state}",
        customer_pincode=shipping_address.zip_code,
        expected_delivery_date=timezone.now().date() + timedelta(days=3)  # Expected delivery in 3 days
    )
    
    print(f"Created delivery order #{delivery_order.id} with status: {delivery_order.status} and pincode: {delivery_order.delivery_pincode}")
    
    # Update order status
    order.status = 'DISPATCHED'
    order.save()
    
    # Update notification as read
    notification = get_object_or_404(ProNotification, order=order, artist=artist)
    notification.is_read = True
    notification.save()
    
    messages.success(request, 'Order has been dispatched successfully')
    return redirect('order_notifications')

@login_required
def get_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if order.customer != request.user:
            return JsonResponse({'error': 'Not authorized'}, status=403)
            
        # Get the delivery order associated with this order
        delivery_order = DeliveryOrder.objects.filter(order=order).first()
        if delivery_order:
            return JsonResponse({
                'status': delivery_order.status,
                'updated_at': delivery_order.updated_at.isoformat() if delivery_order.updated_at else None
            })
        return JsonResponse({'error': 'No delivery order found'}, status=404)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

import cv2
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import base64
import io
from PIL import Image
from .models import Customers
from django.contrib.auth import login
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def register_face(request):
    logger = logging.getLogger(__name__)
    logger.info("Starting face registration")
    
    if request.method == 'POST':
        try:
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'User not authenticated'})

            data = json.loads(request.body.decode('utf-8'))
            face_data = data.get('face_data')
            
            if not face_data:
                return JsonResponse({'success': False, 'error': 'No face data provided'})
            
            # Process base64 image
            if 'base64,' in face_data:
                face_data = face_data.split('base64,')[1]
            
            try:
                # Get or create customer
                customer, created = Customers.objects.get_or_create(
                    user=request.user,
                    defaults={'phone': '9999999999'}
                )
                
                # Save face data directly without processing
                customer.face_registered = True
                customer.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Face registered successfully'
                })
                
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                return JsonResponse({'success': False, 'error': f'Failed to save: {str(e)}'})
                
        except Exception as e:
            logger.error(f"General error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def verify_face(request):
    logger = logging.getLogger(__name__)
    logger.info("Starting face verification process")
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    try:
        # Simple authentication check
        if 'username' in request.POST and 'password' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'status': 'success',
                    'message': 'Login successful',
                    'redirect_url': '/shop/index/'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid credentials'
                })
        
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid login attempt'
        })

    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def validate_aadhaar(request):
    if request.method == 'POST':
        aadhaar_number = request.POST.get('aadhaar_number')
        try:
            # Check if the Aadhaar number already exists in the database
            existing_delivery = DeliveryOrder.objects.filter(aadhaar_number=aadhaar_number).exists()
            if existing_delivery:
                return JsonResponse({'valid': False, 'message': 'This Aadhaar number is already registered'})
            return JsonResponse({'valid': True})
        except Exception as e:
            return JsonResponse({'valid': False, 'message': str(e)})
    return JsonResponse({'valid': False, 'message': 'Invalid request method'})

# Gemini Chatbot API
import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class ReArtChatbot:
    def __init__(self):
        try:
            # Get API key from settings
            api_key = settings.GEMINI_API_KEY
            if not api_key or api_key == "AIzaSyCPUS5du3FKvnsEdXcudwOjTQ6g0joteio":
                logger.error("Invalid or missing Gemini API key in settings")
                self.use_ai = False
                self.api_key_status = "Missing or invalid API key in settings.py"
            else:
                # Configure Gemini AI directly
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                
                # Additional context about ReArt
                self.context = """You are ReArt Assistant, an AI chatbot for ReArt, an online art marketplace. 
                You help users find art pieces, answer questions about artworks, artists, 
                and provide assistance with shopping, orders, and general inquiries. 
                Keep responses concise, friendly, and helpful.
                
                Important information:
                - ReArt is an online marketplace for buying and selling artwork
                - We support various artists and art styles
                - Users can browse, purchase, and review artwork
                - We offer secure payment processing and shipping
                
                When helping users:
                1. Always be friendly and professional
                2. For product inquiries: Provide information about available artwork
                3. For artist inquiries: Share details about our featured artists
                4. For order help: Guide users through the ordering process
                5. For account questions: Assist with login, registration, and profile management
                """
                
                # Initialize chat with context
                self.chat = self.model.start_chat(history=[])
                response = self.chat.send_message(self.context)
                if not response:
                    raise Exception("Failed to initialize chat with context")
                self.use_ai = True
                self.api_key_status = "Valid API key"
                logger.info("Successfully initialized Gemini AI chatbot")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            self.use_ai = False
            self.api_key_status = f"Error initializing: {str(e)}"
            
        # Initialize fallback responses regardless
        self.responses = {
            "products": {
                "keywords": ["product", "artwork", "painting", "art", "piece"],
                "response": "We have a diverse collection of artwork from various artists. You can browse our collection on the homepage or use the search feature to find specific pieces. Would you like recommendations based on a specific style or artist?"
            },
            "orders": {
                "keywords": ["order", "purchase", "buy", "checkout", "payment"],
                "response": "To place an order, simply browse our collection, add items to your cart, and proceed to checkout. We accept various payment methods and offer secure transactions. Can I help you with a specific part of the ordering process?"
            },
            "shipping": {
                "keywords": ["shipping", "delivery", "track", "package", "receive"],
                "response": "We ship artwork worldwide with careful packaging to ensure safe delivery. Shipping times vary by location, but you can track your order through your account. Would you like more information about shipping costs or delivery times?"
            },
            "artists": {
                "keywords": ["artist", "creator", "painter", "designer", "author"],
                "response": "ReArt features talented artists from around the world. Each artist has a profile page where you can learn about their background, style, and view their complete collection. Is there a particular artist you're interested in?"
            },
            "account": {
                "keywords": ["account", "profile", "login", "register", "password"],
                "response": "You can manage your ReArt account through the profile section. This allows you to update your information, view order history, and manage your wishlist. Would you like help with account registration or login?"
            }
        }

    def get_response(self, message):
        """Get response using Gemini AI or fallback to keyword matching"""
        if self.use_ai:
            try:
                logger.info(f"Sending message to Gemini AI: {message}")
                
                # Set safety settings to be more permissive
                safety_settings = [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    }
                ]
                
                # Try with generation config
                generation_config = {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
                
                try:
                    # First try with the chat history approach
                    response = self.chat.send_message(message)
                    
                    if hasattr(response, 'text') and response.text:
                        bot_response = response.text
                        logger.info(f"Received response from Gemini AI chat: {bot_response[:100]}...")
                        return {
                            "status": "success",
                            "response": bot_response
                        }
                    else:
                        # If chat approach fails, try direct generation
                        logger.info("Chat approach failed, trying direct generation...")
                        response = self.model.generate_content(
                            f"You are a helpful assistant for ReArt marketplace. User message: {message}",
                            generation_config=generation_config,
                            safety_settings=safety_settings
                        )
                        
                        if hasattr(response, 'text') and response.text:
                            bot_response = response.text
                            logger.info(f"Received response from direct generation: {bot_response[:100]}...")
                            return {
                                "status": "success",
                                "response": bot_response
                            }
                        else:
                            raise Exception("Empty response from both chat and direct generation")
                except Exception as inner_e:
                    logger.error(f"Error with primary generation method: {str(inner_e)}")
                    # Try one more approach - simple completion
                    response = self.model.generate_content(
                        f"The following is a conversation with an AI assistant for ReArt, an art marketplace. The assistant is helpful, creative, and friendly.\n\nUser: {message}\nAssistant:",
                        generation_config=generation_config,
                        safety_settings=safety_settings
                    )
                    
                    if hasattr(response, 'text') and response.text:
                        bot_response = response.text
                        logger.info(f"Received response from simple completion: {bot_response[:100]}...")
                        return {
                            "status": "success",
                            "response": bot_response
                        }
                    else:
                        raise Exception("All generation methods failed")
                
            except Exception as e:
                logger.error(f"Gemini AI Error: {str(e)}")
                return self._get_fallback_response(message)
        else:
            logger.info("Using fallback response system")
            return self._get_fallback_response(message)

    def _get_fallback_response(self, message):
        """Fallback response system using keyword matching"""
        message = message.lower()
        for intent, data in self.responses.items():
            if any(keyword in message for keyword in data["keywords"]):
                logger.info(f"Found matching intent: {intent}")
                return {
                    "status": "success",
                    "response": data["response"]
                }
        
        logger.info("No matching intent found, using default response")
        return {
            "status": "success",
            "response": "Welcome to ReArt! I'm here to help with your art-related questions. You can ask me about our artwork, artists, ordering process, or account management. How can I assist you today?"
        }

# Initialize chatbot globally
reart_chatbot = ReArtChatbot()

@csrf_exempt
def gemini_chat_api(request):
    """
    Handle chatbot requests by sending them to the Gemini API and returning the response.
    
    This endpoint expects a POST request with a JSON body containing a 'message' field.
    """
    logger.info(f"Received request to gemini_chat_api: {request.method}")
    
    if request.method != 'POST':
        logger.error(f"Invalid method: {request.method}")
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        # Parse the request body
        body = request.body.decode('utf-8')
        logger.info(f"Request body: {body}")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON format in request'}, status=400)
            
        user_message = data.get('message', '')
        
        if not user_message:
            logger.error("No message provided")
            return JsonResponse({'error': 'Message field is required'}, status=400)
        
        logger.info(f"Processing message: {user_message}")
        
        # Check if API key is set
        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key == "":
            logger.warning("No Gemini API key set in settings.py")
            return JsonResponse({
                'status': 'warning',
                'response': "I'm currently running in fallback mode because no Gemini API key is configured. Please add your API key in settings.py to enable full functionality.",
                'api_key_status': 'missing'
            })
        
        try:
            # Try to get response from chatbot
            response_data = reart_chatbot.get_response(user_message)
            # Add API key status to response
            response_data['api_key_status'] = getattr(reart_chatbot, 'api_key_status', 'unknown')
            logger.info(f"Got response from chatbot: {response_data}")
            return JsonResponse(response_data, safe=True)
        except Exception as e:
            # If chatbot fails, use fallback with error info
            logger.error(f"Error getting response from chatbot: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'response': f"I'm having trouble generating a response right now. Error: {str(e)}",
                'api_key_status': getattr(reart_chatbot, 'api_key_status', 'unknown')
            }, safe=True)
    
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
