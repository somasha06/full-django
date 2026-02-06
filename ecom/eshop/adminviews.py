from django.shortcuts import render,redirect
from .models import *
from .adminforms import *
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.db.models import Count, Sum, Max



def admindashboard(request):
    return render(request,"admin/admindashboard.html")

def managecategory(request):
    form=Categoryform(request.POST or None ,request.FILES or None)
    categories=Category.objects.all()
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(managecategory)
    return render(request,"admin/managecategory.html",{"form":form,"categories":categories})

def deletecategory(request,id):
    deletedcategory=Category.objects.get(id=id)
    deletedcategory.delete()
    return redirect(managecategory)

def editcategory(request,id):
    category=Category.objects.get(id=id)
    form=Categoryform(request.POST or None,request.FILES or None,instance=category)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(managecategory)
    return render(request,"admin/editcategory.html",{"category": category,"form": form})

def managesubcategory(request):
    form=SubCategoryform(request.POST or None,request.FILES or None)
    subcategories=SubCategory.objects.all()
    if form.is_valid():
        form.save()
        return redirect(managesubcategory)
    return render(request,"admin/managesubcategory.html",{"form":form,"subcategories":subcategories})

def editsubcategory(request,id):
    subcategory=SubCategory.objects.get(id=id)
    form=SubCategoryform(request.POST or None,request.FILES or None,instance=subcategory)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(managesubcategory)
    return render(request,"admin/editsubcategory.html",{"form":form,"subcategory":subcategory})
    
def deletesubcategory(request,id):
    deletedsubcategory=SubCategory.objects.get(id=id)
    deletedsubcategory.delete()
    return redirect(managesubcategory)

def insertproduct(request):
    storeprofile=get_object_or_404(StoreProfile)
    form=Productform(request.POST or None,request.FILES or None)
    if request.method=="POST":
        if form.is_valid():
            product=form.save(commit=False)

            product.seller=storeprofile.seller

            product.save()
            images = request.FILES.getlist("productimages")
            for img in images:
                Productimage.objects.create(
                    product=product,
                    productimages=img
            )
            return redirect(manageproduct)
    return render(request,"admin/insertproduct.html",{"form":form})

def manageproduct(request):
    products=Product.objects.all()
    return render(request,"admin/manageproduct.html",{"products":products})

def deleteproduct(request,id):
    deletedproduct=Product.objects.get(id=id)
    deletedproduct.delete()
    return redirect(manageproduct)

def editproduct(request,id):
    storeprofile=get_object_or_404(StoreProfile)

    product=Product.objects.get(id=id)
    form=Productform(request.POST or None , request.FILES or None,instance=product)
    if request.method=="POST":
        if form.is_valid():
            product=form.save(commit=False)
            product.seller=storeprofile.seller
            product.save()

            # images = request.FILES.getlist("productimages")
            for img in request.FILES.getlist("productimages"):
                Productimage.objects.create(
                    product=product,
                    productimages=img
            )

            return redirect(manageproduct)
    return render(request,"admin/editproduct.html",{"form":form,"product":product})

def viewproduct(request):

    return render(request,"viewproduct.html")

def insertproductvariant(request):
    form=Productvariantform(request.POST or None, request.FILES or None)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(manageproductvariant)
    return render(request,"admin/insertproductvariant.html",{"form":form})

def manageproductvariant(request):
    variants=ProductVariant.objects.all()
    return render(request,"admin/manageproductvariant.html",{"variants":variants})

def deleteproductvariant(request,id):
    remove=ProductVariant.objects.get(id=id)
    remove.delete()
    return redirect(manageproductvariant)

def editproductvariant(request,id):
    productvariant=ProductVariant.objects.get(id=id)
    form=Productvariantform(request.POST or None,request.FILES or None,instance=productvariant)
    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect(manageproductvariant)
    return render(request,"admin/editproductvariant.html",{"productvariant":productvariant,"form":form})

def storeprofile(request):
    seller_user=get_object_or_404(User,username="Asha")
    profile,created=StoreProfile.objects.get_or_create(seller=seller_user)
    
    if created:
        seller_group = Group.objects.get(name="Seller")
        seller_user.groups.add(seller_group)

    form=StoreProfileForm(request.POST or None,request.FILES or None,instance=profile)

    if request.method=="POST":
        if form.is_valid():
            form.save()
            return redirect("storeprofile")
        
    return render(request,"admin/storeprofile.html",{"form":form,"profile":profile})

def viewproduct(request,id):
    product=Product.objects.get(id=id)
    productvariants=product.productvariants.filter(is_active=True)
    default_variant = productvariants.first()
    profile = StoreProfile.objects.first()
    images = product.images.all()   
    subcategories=SubCategory.objects.all()
    return render(request,"viewproduct.html",{"product":product,"subcategories":subcategories,"productvariants":productvariants,"default_variant":default_variant,"profile":profile,"images":images})

def delete_product_image(request, image_id):
    image = get_object_or_404(Productimage, id=image_id)
    product_id = image.product.id

    image.productimages.delete(save=False)  # delete file
    image.delete()                           # delete DB row

    return redirect("editproduct", id=product_id)

def allcustomer(request):
    customers=Role.objects.filter(role=Role.CUSTOMER).select_related("user").annotate(order_count=Count("user__orders", distinct=True),total_spent=Sum("user__orders__total_price"),last_order=Max("user__orders__created_at"),)
    return render(request,"admin/viewcustomer.html",{"customers":customers})

def viewcustomerprofile(request,id):
    user=get_object_or_404(User,id=id)
    orders=Order.objects.filter(user=user)
    wishlistitem=WishlistItem.objects.filter(wishlist__user=user)
    cartitem=CartItem.objects.filter(cart__user=user)
    addresses=user.address.all()

    context={"customer":user,"ordercount":orders.count(),"wishlistcount":wishlistitem.count(),"cartcount":cartitem.count(),"addresses":addresses}
    return render(request,"admin/viewcustomerprofile.html",context)

def viewcustomerwishlist(request,id):
    user=get_object_or_404(User,id=id)
    wishlistitem=WishlistItem.objects.filter(wishlist__user=user).select_related("product_variant","product_variant__product")
    return render(request,"admin/viewcustomerwishlist.html",{"user":user,"wishlistitem":wishlistitem})

def viewcustomercart(request,id):
    user=get_object_or_404(User,id=id)
    cartitem=CartItem.objects.filter(cart__user=user).select_related("product_variant","product_variant__product")
    return render(request,"admin/viewcustomercart.html",{"user":user,"cartitem":cartitem})


def viewcustomerorder(request,id):
    user=get_object_or_404(User,id=id)
    orders=Order.objects.filter(user=user).select_related("user").order_by("-created_at")
    return render(request,"admin/viewcustomerorder.html",{"user":user,"orders":orders})

def viewcustomerorderitems(request,id):
    order=get_object_or_404(Order,id=id)

    items=OrderItem.objects.filter(order=order).select_related("product_variant","product_variant__product")
    return render(request,"admin/viewcustomerorderitems.html",{"order":order,"items":items})

def totalorders(request):
    
    paidorders=Order.objects.filter(status="success").order_by("-created_at")
    pendingorders=Order.objects.filter(status="pending").order_by("-created_at")
    failedorders=Order.objects.filter(status="failed").order_by("-created_at")

    return render(request,"admin/totalorder.html",{"paidorders":paidorders,"pendingorders":pendingorders,"failedorders":failedorders})