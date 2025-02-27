from django.contrib import admin
from .models import User, Region, District, Category, Product, Wishlist, Thread, Order, Payment



admin.site.register(Region)
admin.site.register(District)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Wishlist)
admin.site.register(Thread)
admin.site.register(Order)
admin.site.register(Payment)
