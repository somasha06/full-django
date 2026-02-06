from django.shortcuts import render,redirect,get_object_or_404
from .models import *
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.urls import reverse


def customerhome(request):
    subcategories=SubCategory.objects.all()
    products=Product.objects.all()
    return render(request,"customer/customerhome.html",{"products":products,"subcategories":subcategories})

def addtowishlist(request,id):
    variant=get_object_or_404(ProductVariant,id=id)
    wishlist,created=Wishlist.objects.get_or_create(user=request.user)
    WishlistItem.objects.get_or_create(wishlist=wishlist,product_variant=variant)
    return redirect(viewwishlist)

def viewwishlist(request):
    wishlist=Wishlist.objects.filter(user=request.user).first()
    items=WishlistItem.objects.all() if wishlist else []
    return render(request,"customer/wishlist.html",{"items":items})

def removefromwishlist(request,id):
    wishlist=get_object_or_404(Wishlist,user=request.user)
    item=get_object_or_404(WishlistItem,wishlist=wishlist,id=id)
    item.delete()
    return redirect("viewwishlist")

def filterproduct(request,id):
    subcategories=SubCategory.objects.all()
    products=Product.objects.filter(subcategory__id=id)
    return render(request,"customer/customerhome.html",{"subcategories":subcategories,"products":products})


def addtocart(request,id):
    variant=get_object_or_404(ProductVariant,id=id)
    cart,created=Cart.objects.get_or_create(user=request.user)
    cartitem,created=CartItem.objects.get_or_create(cart=cart,product_variant=variant)

    if not created:
        cartitem.quantity+=1
        cartitem.save()

    return redirect("viewcart")

def viewcart(request):
    cart=Cart.objects.filter(user=request.user).first()
    items=cart.items.all() if cart else []
    total=sum(item.total_price for item in items)
    return render(request,"customer/cart.html",{"cart": cart,"items": items,"total": total})

def increaseqty(request,id):
    item=get_object_or_404(CartItem,id=id,cart__user=request.user)
    item.quantity+=1
    item.save()
    return redirect(viewcart)

def decreaseqty(request,id):
    item=get_object_or_404(CartItem,id=id,cart__user=request.user)
    if item.quantity>1:
        item.quantity-=1
        item.save()
    else:
        item.delete()
    return redirect(viewcart)

def deleteaddress(request,id):
    address=get_object_or_404(Address,id=id,user=request.user)
    address.delete()
    return redirect(checkout)

def editaddress(request,id):
    address=get_object_or_404(Address,id=id,user=request.user)
    if request.method=="POST":
        address.fullname = request.POST["fullname"]
        address.phone = request.POST["phone"]
        address.address = request.POST["address"]
        address.city = request.POST["city"]
        address.pincode = request.POST["pincode"]
        address.save()
        return redirect(checkout)
    return redirect(request,"editaddress.html",{"address":address})

def checkout(request):
    cart=Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        return redirect("viewcart")

    items=cart.items.all()
    total=sum(item.total_price for item in items)
    addresses=Address.objects.filter(user=request.user)

    return render(request,"customer/checkout.html",{"items":items,"total":total,"addresses":addresses})


def place_order(request):
    if request.method != "POST":
        return redirect("checkout")

    cart = Cart.objects.get(user=request.user)
    items = cart.items.all()

    if not items.exists():
        return redirect("viewcart")

    address_id = request.POST.get("address_id")

    if address_id:
        address = Address.objects.get(
            id=address_id,
            user=request.user
        )


    else:
       address, created = Address.objects.get_or_create(
    user=request.user,
    street=request.POST.get("address"),
    city=request.POST.get("city"),
    pin_code=request.POST.get("pincode"),
    defaults={
        "name": request.POST.get("fullname"),
        "phone": request.POST.get("phone"),
        "state": request.POST.get("state", ""),
        "country": "India"
    }
)

    total = sum(item.total_price for item in items)

    payment_method = request.POST.get("payment_method", "ONLINE")


    order = Order.objects.create(
        user=request.user,
        address=address,
        total_price=total,
        final_price=total,
        status="pending"
    )

    if payment_method == "COD":

        for item in items:
            OrderItem.objects.create(
                order=order,
                product_variant=item.product_variant,
                quantity=item.quantity,
                price=item.product_variant.discount_price or item.product_variant.price
            )

        cart.items.all().delete()

        request.session["order_id"] = order.id
        return redirect("order_success")


    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(total * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    order.razorpay_order_id = razorpay_order["id"]
    order.save()

    return render(request, "customer/payment.html", {
        "order": order,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": int(order.final_price * 100),
    })


@csrf_exempt
def verify_payment(request):
    import json
    data = json.loads(request.body)

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"]
        })

        order = Order.objects.get(razorpay_order_id=data["razorpay_order_id"])
        order.payment_method = "ONLINE"
        order.status = "paid"
        order.razorpay_payment_id = data["razorpay_payment_id"]
        order.save()

        cart = Cart.objects.get(user=order.user)

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_variant=item.product_variant,
                quantity=item.quantity,
                price=item.unit_price
            )

        cart.items.all().delete()

        request.session["order_id"] = order.id
        request.session.modified = True

        return JsonResponse({"status": "success","redirect_url": "/order-success/"})

    except:
        return JsonResponse({"status": "failed"})
    

@csrf_exempt
def cod_order(request):
    if request.method != "POST":
        return JsonResponse({"status": "invalid"}, status=400)

    data = json.loads(request.body)

    order = Order.objects.get(id=data["order_id"])

    # ✅ Update order
    order.payment_method = "COD"
    order.status = "pending"
    order.save()

    # ✅ CREATE ORDER ITEMS (THIS WAS MISSING)
    cart = Cart.objects.get(user=order.user)

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product_variant=item.product_variant,
            quantity=item.quantity,
            price=item.unit_price
        )

    # ✅ CLEAR CART
    cart.items.all().delete()

    # ✅ Store for success page
    request.session["order_id"] = order.id

    return JsonResponse({
        "status": "success",
        "redirect_url": reverse("order_success")
    })




def order_success(request):
    order_id=request.session.get("order_id")
    if not order_id:
        return redirect("customerpage")
    order=Order.objects.get(id=order_id)
    order_items=OrderItem.objects.filter(order=order)
    del request.session["order_id"]

    return render(request, "customer/order_success.html",{"order":order,"order_items":order_items})



def profile_dashboard(request):
    orders=Order.objects.filter(user=request.user).order_by("-id")
    addresses=Address.objects.filter(user=request.user)
    return render(request,"customer/profile/mydashboard.html",{"orders":orders,"addresses":addresses})

def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-id")
    return render(request,"customer/profile/my_orders.html",{"orders":orders})

def myorder_detail(request,id):
    order=Order.objects.get(id=id,user=request.user)
    return render(request,"customer/profile/myorderdetails.html",{"order":order})

def my_addresses(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, "customer/profile/my_addresses.html", {
        "addresses": addresses
    })


def search(request):
    query = request.GET.get("product","")
    if query:
        products = Product.objects.filter(Q(name__icontains=query)|Q(description__icontains= query))
    else:
        products=Product.objects.all()
    return render(request,"customer/customerhome.html",{"products":products,"query":query})


def add_review(request, order_item_id):
    item = get_object_or_404(
        OrderItem,
        id=order_item_id,
        order__user=request.user,
        order__status="delivered"
    )

    product = item.product_variant.product
    review = Review.objects.filter(order_item=item).first()

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if review:
            review.rating = rating
            review.comment = comment
            review.save()
        else:
            Review.objects.create(
                user=request.user,
                product=product,
                order_item=item,
                rating=rating,
                comment=comment
            )

        return redirect("my_orders")

    return render(request, "customer/add_review.html", {
        "item": item,
        "review": review
    })

