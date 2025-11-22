from .models import Product,Order,OrderItem,Favorite,UserProfile
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import OrderNotification


def home(request):
   return render(request, 'shop/home.html')

def about_us(request):
    context = {
        'text': """
Mirësevini në Pasticeri “Qershia mbi Tortë”  
Çdo ditë përgatisim ëmbëlsira dhe torta të freskëta, me përkushtim dhe dashuri, për t’i bërë momentet tuaja të veçanta edhe më të ëmbla.  

Historia jonë nisi me pasionin për ëmbëlsirat artizanale dhe dëshirën për të sjellë diçka ndryshe në tryezat e klientëve tanë. Duke përdorur përbërës të freskët dhe me cilësi të lartë, ne krijojmë torta unike, të përshtatura për çdo rast – nga festat familjare te eventet më të rëndësishme.  

Në ambientet tona moderne dhe mikpritëse, do të gjeni një gamë të gjerë produktesh, ku tradita dhe inovacioni bashkohen për të ofruar shije që mbeten gjatë në kujtesë.  

“Qershia mbi Tortë” është simboli i ëmbëlsisë, cilësisë dhe kujtimeve të bukura. Jemi këtu për t’ju shoqëruar në çdo moment të veçantë të jetës suaj!
        """
    }
    return render(request, 'shop/about_us.html', context)


def product_list(request):
    sort_by = request.GET.get('sort_by', 'name')
    allowed_sort_fields = ['name', '-name', 'price', '-price']
    if sort_by not in allowed_sort_fields:
        sort_by = '-name'
    products = Product.objects.all().order_by(sort_by)
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
    else:
        user_favorites = []
    return render(request, 'shop/product_list.html', {
        'products': products,
        'user_favorites': user_favorites
    })

def contact_us(request):
        context = {
            'tiktok_link': 'https://www.tiktok.com/@qershi_mbi_torte?_t=ZM-8zutlSB3KVE&_r=1',
            'instagram_link': 'https://www.instagram.com/qershi_mbi_torte/',
        }
        return render(request, 'shop/contact_us.html', context)


def register_view(request):
    if request.method == 'POST':
        # Merr fushat
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ky username ekziston tashmë.')
            return render(request, 'shop/login.html')

        if password != confirm_password:
            messages.error(request, 'Fjalëkalimet nuk përputhen.')
            return render(request, 'shop/login.html')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        UserProfile.objects.create(user=user, address=address, phone_number=phone_number)

        messages.success(request, 'Llogaria u krijua me sukses! Tani mund të kyçeni.')
        return redirect('client_login')

    return render(request, 'shop/login.html')

def client_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in!")
            return render(request, "shop/login.html")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "shop/login.html")



def client_logout(request):
    logout(request)
    messages.success(request, "You are now logged out.")
    return redirect('home')

@login_required
def add_to_cart(request, product_id):
    # Kontrollo login
    if not request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"redirect_url": "/client/login/"}, status=401)
        else:
            return redirect("client_login")

    cart = request.session.get("cart", {})
    product = get_object_or_404(Product, id=product_id)
    product_id_str = str(product.id)

    if product_id_str not in cart:
        cart[product_id_str] = {
            "quantity": 1,
            "price": float(product.price),
            "name": product.name,
            "image": product.image.url if product.image else "",
        }
    else:
        cart[product_id_str]["quantity"] += 1

    # rifresko totalin
    request.session["cart"] = cart
    request.session["cart_total_items"] = sum(item["quantity"] for item in cart.values())

    return JsonResponse({
        "success": True,
        "cart_count": request.session["cart_total_items"],
    })


@login_required
def cart_view(request):
    cart = request.session.get("cart", {})
    cart_items = []

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        cart_items.append({
            "product": product,
            "quantity": item["quantity"],
            "price": item["price"],
        })

    total = sum(item["price"] * item["quantity"] for item in cart_items)

    return render(request, "shop/cart.html", {
        "cart_items": cart_items,
        "total": total,
    })


@login_required
def update_cart(request, product_id):
    cart = request.session.get("cart", {})
    product = get_object_or_404(Product, id=product_id)
    product_id_str = str(product.id)

    if product_id_str in cart:
        action = request.GET.get("action")

        if action == "add":
            cart[product_id_str]["quantity"] += 1
        elif action == "remove":
            if cart[product_id_str]["quantity"] > 1:
                cart[product_id_str]["quantity"] -= 1
            else:
                del cart[product_id_str]

        request.session["cart"] = cart
        cart_total_items = sum(item["quantity"] for item in cart.values())
        request.session["cart_total_items"] = cart_total_items
        total = float(sum(item["price"] * item["quantity"] for item in cart.values()))

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "quantity": cart.get(product_id_str, {}).get("quantity", 0),
                "total": total,
                "cart_total_items": cart_total_items,
            })

    return redirect("cart")
@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    if str(product.id) in cart:
        del cart[str(product.id)]
        request.session['cart'] = cart
        total_items = sum(item["quantity"] for item in cart.values()) 
        request.session['cart_total_items'] = total_items
        messages.success(request, f"Produkti '{product.name}' u hoq nga shporta.")
    return redirect('cart')


#Konfrim i porosise
@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "bank":
            order.status = "pending_bank"
            order.save()
            # Shporta mbetet plot
            return render(request, "shop/bank_payment.html", {"order": order})

        elif payment_method == "cash":
            # pastro shportën
            if "cart" in request.session:
                del request.session["cart"]

                request.session["cart_total_items"] = 0
                request.session.modified = True

            return render(request, "shop/success.html", {"order": order})

        else:
            messages.error(request, "Ju lutem zgjidhni një mënyrë pagese.")
            return redirect("checkout", order.id)

    return render(request, "shop/checkout.html", {"order": order})


#Krijim i porosise
@login_required
def checkout_from_cart(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Shporta është bosh.")
        return redirect('cart')

    order = Order.objects.create(user=request.user, status='pending')

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
        )
    return redirect('checkout', order_id=order.id)



@login_required
def success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "shop/success.html", {"order": order})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    notifications = OrderNotification.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(request, "shop/my_orders.html", {"orders": orders, "notifications": notifications})
@login_required
def check_new_notifications(request):
    notifications = OrderNotification.objects.filter(
        user=request.user,
        read=False
    ).values("id", "message")
    return JsonResponse(list(notifications), safe=False)


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(OrderNotification, id=notif_id, user=request.user)
    notif.read = True
    notif.save()
    return JsonResponse({"status": "ok"})

@login_required
def all_notifications(request):
    notifications = OrderNotification.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "shop/notifications.html", {"notifications": notifications})

def product_search(request):
    q = request.GET.get("q", "")
    products = Product.objects.filter(name__icontains=q) if q else Product.objects.all()
    return render(request, "shop/search.html", {"products": products, "q": q})

@login_required(login_url="/client/login/")
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        fav.delete()
        is_favorite = False
    else:
        is_favorite = True

    # Nëse është AJAX kërkesë → kthe JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "is_favorite": is_favorite,
            "message": "Produkti u shtua te Favorites!" if is_favorite else "Produkti u hoq nga Favorites!"
        })

    # Nëse s’është AJAX (fallback) → redirect normal
    return redirect("favorite_list")


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related("product")
    return render(request, "shop/favorites.html", {"favorites": favorites})


@login_required
def move_favorite_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.filter(user=request.user, product=product).delete()
    cart = request.session.get("cart", {})

    # pastro vlera që nuk janë dict
    for key, val in list(cart.items()):
        if not isinstance(val, dict):
            cart[key] = {
                "quantity": 1,
                "price": 0,
                "name": "",
                "image": "",
            }

    product_id_str = str(product.id)

    if product_id_str not in cart:
        cart[product_id_str] = {
            "quantity": 1,
            "price": float(product.price),
            "name": product.name,
            "image": product.image.url if product.image else "",
        }
    else:
        cart[product_id_str]["quantity"] += 1

    # ruaj në sesion
    request.session["cart"] = cart
    request.session["cart_total_items"] = sum(
        item["quantity"] for item in cart.values() if isinstance(item, dict)
    )

    return JsonResponse({
        "success": True,
        "product_id": product.id,
        "cart_count": request.session["cart_total_items"],
        "fav_count": Favorite.objects.filter(user=request.user).count()
    })


@login_required
def remove_favorite(request, product_id):
    Favorite.objects.filter(user=request.user, product_id=product_id).delete()
    fav_count = Favorite.objects.filter(user=request.user).count()
    return JsonResponse({
        "success": True,
        "fav_count": fav_count
    })