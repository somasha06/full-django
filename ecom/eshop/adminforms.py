from django.forms import ModelForm
from .models import *

class Categoryform(ModelForm):
    class Meta:
        model=Category
        exclude = ("slug",)

class SubCategoryform(ModelForm):
    class Meta:
        model=SubCategory
        exclude = ("slug",)


class Productform(ModelForm):
    class Meta:
        model=Product
        exclude = ("seller","slug")
        
class Productvariantform(ModelForm):
    class Meta:
        model=ProductVariant
        fields="__all__"

class StoreProfileForm(ModelForm):
    class Meta:
        model=StoreProfile
        exclude = ("seller",)