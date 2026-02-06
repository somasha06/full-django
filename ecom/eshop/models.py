from django.db import models
import uuid
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.db.models import Avg

class User(AbstractUser):
    email=models.EmailField(unique=True)
    mobile_no=models.CharField(max_length=10,unique=True,null=True,blank=True)
    profile_pic = models.ImageField(upload_to="profile_pic/", null=True, blank=True)

    def __str__(self):
        return self.username
    
class PendingUser(models.Model):
    session_id=models.UUIDField(default=uuid.uuid4,unique=True) #uuid4=random unique ID
    email=models.EmailField(null=True,blank=True)
    mobile_no=models.CharField(max_length=10,null=True,blank=True)
    otp=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(days=365)
    
    def __str__(self):
        return self.email or self.mobile_no or str(self.session_id)
    
class Role(models.Model):
    ADMIN="admin"
    SELLER="seller"
    CUSTOMER="customer"

    ROLE_CHOICES =[
        (ADMIN, "Admin"),
        (SELLER, "Seller"),
        (CUSTOMER, "Customer"),
    ]

    role=models.CharField(max_length=20,choices=ROLE_CHOICES)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="roles")
    active=models.BooleanField(default=True)

    class Meta:
        unique_together=("user","role")

    def __str__(self):
        return f"{self.user.username}-{self.role}"
    
class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="address")
    name=models.CharField(max_length=100,null=True,blank=True)
    phone=models.CharField(max_length=10,null=True,blank=True)
    street=models.TextField(null=True,blank=True)
    city=models.CharField(max_length=100,null=True,blank=True)
    pin_code=models.CharField(max_length=6,null=True,blank=True)
    state=models.CharField(max_length=100,null=True,blank=True)
    country=models.CharField(max_length=100,null=True,blank=True)
    ADDRESS_CHOICES=(
        ("home","Home"),
        ("work","Work"),
    )
    address_type=models.CharField(max_length=10,choices=ADDRESS_CHOICES,default="home")
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}-name"


class Category(models.Model):
    name=models.CharField(max_length=200)
    is_active=models.BooleanField(default=True)
    slug=models.SlugField(unique=True,blank=True)
    image=models.ImageField(upload_to="categoriesimage/")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name,allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    category=models.ForeignKey(Category,related_name="subcategory",on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    slug = models.SlugField(unique=True,blank=True)
    image=models.ImageField(upload_to="subcategories/", null=True, blank=True)

    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    subcategory=models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    description=models.CharField(max_length=500)
    seller=models.ForeignKey(User,on_delete=models.CASCADE,related_name="products")
    created_at=models.DateField(auto_now_add=True)
    starting_from=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    updated_at=models.DateField(auto_now=True)
    is_active=models.BooleanField(default=False)
    slug = models.SlugField(unique=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 1) if avg else 5
    
    @property
    def total_reviews(self):
        return self.reviews.count()

    def __str__(self):
        return self.name
    
class Productimage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="images")
    productimages=models.ImageField(upload_to="productimages/")

    def __str__(self):
        return f"Image of {self.product.name}"
    
class ProductVariant(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="productvariants")
    weight=models.CharField(max_length=200)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    discount_price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    stock=models.PositiveIntegerField()
    sku=models.PositiveIntegerField()
    is_active=models.BooleanField(default=True)

    

    def __str__(self):
        return f"{self.product.name} - {self.weight}"
    
class Wishlist(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="wishlist")
    # product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="wishlistby",null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist"

class WishlistItem(models.Model):
    wishlist=models.ForeignKey(Wishlist,on_delete=models.CASCADE,related_name="wishlistitem",null=True,blank=True)
    product_variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE,null=True,blank=True)
    added_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=["wishlist","product_variant"]
        pass

    def __str__(self):
        return f"{self.product_variant.name} in {self.wishlist.user.username}'s wishlist"
    

class Cart(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="cart")
    coupon=models.ForeignKey("eshop.Coupon",on_delete=models.SET_NULL,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s cart"
    
class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    product_variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    added_at=models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.product_variant.discount_price * self.quantity
    

    class Meta:
        constraints=[models.UniqueConstraint(fields=["cart","product_variant"],name="unique_cart_product")]
    
    @property
    def unit_price(self):
        return self.product_variant.discount_price or self.product_variant.price

    def __str__(self):
        return f"{self.product_variant} x {self.quantity}"
    
class Coupon(models.Model):
    code=models.CharField(max_length=50,unique=True)

    DISCOUNT_TYPE_CHOICES=(
        ("flat","Flat Discount"),
        ("percent","Percentage Discount")
    )
    discount_type=models.CharField(max_length=10,choices=DISCOUNT_TYPE_CHOICES,default="percent")
    min_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    max_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    discount_amount=models.PositiveIntegerField(null=True,blank=True)
    expires_at=models.DateField()
    usage_limit=models.IntegerField(default=5)
    used_count=models.IntegerField(default=0)
    active=models.BooleanField(default=True)

    def is_valid(self):
        now=timezone.now().date()

        return(
            self.active
            and now <= self.expires_at
            and self.used_count < self.usage_limit
        )
    
    def __str__(self):
        return self.code
    
class StoreProfile(models.Model):
    seller = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=100)   # Your mother
    description = models.TextField()
    phone = models.CharField(max_length=10)
    email = models.EmailField()
    address = models.TextField()
    gst_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="GSTIN (15 characters)"
    )

    fssai_number = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        help_text="FSSAI License Number"
    )
    profile = models.ImageField(upload_to="store/", null=True, blank=True)

    def __str__(self):
        return self.store_name
    
class Order(models.Model):
    STATUS_CHOICES=[
        ("pending","Pending"),
        ("paid","Paid"),
        ("shipped","Shipped"),
        ("delivered","Delivered"),
        ("cancelled","Cancelled"),
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="orders")
    address=models.ForeignKey(Address,on_delete=models.SET_NULL,null=True,blank=True,related_name="orders")
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending")
    total_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    discount_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    final_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)

    created_at=models.DateTimeField(auto_now_add=True)

    razorpay_order_id=models.CharField(max_length=255,blank=True,null=True)
    razorpay_payment_id=models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user}"


class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    product_variant=models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    price=models.DecimalField(max_digits=10,decimal_places=2)

    @property
    def review(self):
        return Review.objects.filter(order_item=self).first()

    @property
    def __str__(self):
        return f"{self.product_variant.price} x {self.quantity}"
    
    

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    order_item = models.ForeignKey("OrderItem", on_delete=models.CASCADE,null=True,blank=True)
    rating = models.PositiveIntegerField(choices=[
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product", "order_item")

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐"

