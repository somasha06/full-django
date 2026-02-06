"""
URL configuration for ecom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from eshop.views import *
from eshop.adminviews import *
from eshop.customerviews import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('superadmin/', admin.site.urls),
    path("",home,name="homepage"),
    path("about/",about, name="about"),
    path("login/", login_view, name="login"),
    path("signup/", customer_signup, name="signup"),
    path("logout/", logout_view, name="logout"),

    path("admin/",admindashboard,name="dashboardpage"),
    path("admin/storeprofile",storeprofile,name="storeprofile"),

    path("admin/managecategory/",managecategory,name="managecategory"),
    path("admin/managecategory/<int:id>/delete",deletecategory,name="deletecategory"),
    path("admin/managecategory/<int:id>/edit",editcategory,name="editcategory"),

    path("admin/managesubcategory",managesubcategory,name="managesubcategory"),
    path("admin/managesubcategory/<int:id>/delete",deletesubcategory,name="deletesubcategory"),
    path("admin/managesubcategory/<int:id>/edit",editsubcategory,name="editsubcategory"),

    path("admin/manageproduct",manageproduct,name="manageproduct"),
    path("admin/insertproduct",insertproduct,name="insertproduct"),
    path("admin/deleteproduct/<int:id>/delete",deleteproduct,name="deleteproduct"),
    path("admin/editproduct/<int:id>/edit",editproduct,name="editproduct"),
    path("p/<int:id>/",viewproduct,name="viewproduct"),
    path("admin/deleteproductimage/<int:image_id>/",delete_product_image,name="delete_product_image"),

    path("admin/insertproductvariant",insertproductvariant,name="insertproductvariant"),
    path("admin/manageproductvariant",manageproductvariant,name="manageproductvariant"),
    path("admin/productvariant/<int:id>/edit/", editproductvariant, name="editproductvariant"),
    path("admin/productvariant/<int:id>/",deleteproductvariant,name="deleteproductvariant"),
    

    path("admin/allcustomer", allcustomer, name="allcustomer"),
    path("admin/customer/<int:id>/",viewcustomerprofile,name="viewcustomerprofile"),
    path("admin/customer/<int:id>/wishlist/",viewcustomerwishlist, name="viewcustomerwishlist"),
    path("admin/customer/<int:id>/cart/",viewcustomercart, name="viewcustomercart"),
    path("admin/customer/<int:id>/orders/",viewcustomerorder, name="viewcustomerorder"),
    path("admin/customerorder/<int:id>/items/",viewcustomerorderitems,name="viewcustomerorderitems"),
    path("admin/customerorders/totalorders/",totalorders, name="totalorders"),


    #Customer
    path("customer/",customerhome,name="customerpage"),

    path("wishlist/",viewwishlist, name="viewwishlist"),
    path("wishlist/add/<int:id>/",addtowishlist, name="addtowishlist"),
    path("wishlist/remove/<int:id>/",removefromwishlist, name="removefromwishlist"),

    path("addtocart/<int:id>",addtocart,name="addtocart"),
    path("viewcart",viewcart,name="viewcart"),
    path("viewcart/increase/<int:id>/",increaseqty, name="increaseqty"),
    path("viewcart/decrease/<int:id>/",decreaseqty, name="decreaseqty"),
    # path("apply_coupon/",apply_coupon,name="apply_coupon"),

    path("search/",search,name="search"),
    path("filter/<int:id>/",filterproduct,name="filter"),

    path("address/delete/<int:id>/", deleteaddress, name="deleteaddress"),
    path("address/edit/<int:id>/", editaddress, name="editaddress"),
   

    path("checkout/", checkout, name="checkout"),
    path("place-order/", place_order, name="place_order"),
    path("verify-payment/", verify_payment, name="verify_payment"),
    path("cod-order/", cod_order, name="cod_order"),
    path("order-success/", order_success, name="order_success"),

    path("customer/profile/",profile_dashboard,name="profile"),
    path("customer/my_orders/",my_orders,name="my_orders"),
    path("customer/my_addresses/",my_addresses,name="my_addresses"),
    path("customer/myorder_detail/<int:id>/",myorder_detail,name="myorder_detail"),

]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

