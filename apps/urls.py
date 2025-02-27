from django.urls import path
from . import views
from templates import *
from .views import *

urlpatterns = [
    path('', CategoryListView.as_view(), name='home'),
    path('product-list/', ProductListView.as_view(), name='product_list'),
    path('order-list/', OrderListView.as_view(), name='order-list'),
    path('login/', AuthFormView.as_view(), name='login'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path("logout/", CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('profile/change-password/', PasswordChangeView.as_view(), name='change_password'),
    path("test/",a)

]
