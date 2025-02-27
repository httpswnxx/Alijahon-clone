import re

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, UpdateView

from apps.forms import AuthForm
from apps.models import User, Product, Category, Order


class CategoryListView(ListView):
    queryset = Product.objects.all().select_related('category')
    template_name = 'apps/home-page.html'
    context_object_name = 'products'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['categories'] = Category.objects.all()
        return data



class AuthFormView(FormView):
    form_class = AuthForm
    template_name = 'apps/auth/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        phone_number = form.cleaned_data.get("phone_number")
        password = form.cleaned_data.get("password")

        print(f"🔍 Checking user: {phone_number}")  # Debug log

        try:
            # Check if user exists
            user = User.objects.get(phone_number=phone_number)
            print("✅ User exists!")

            # Verify password
            if not user.check_password(password):
                print("❌ Wrong password!")
                messages.error(self.request, "Telefon nomer yoki parol xato!")
                return self.form_invalid(form)
        except User.DoesNotExist:
            # If user doesn't exist, create a new user
            print("🆕 User does not exist, creating new user...")
            user = User.objects.create_user(phone_number=phone_number, password=password)

        # Log in the user
        login(self.request, user)
        print("✅ Login successful!")
        return super().form_valid(form)



class ProductListView(ListView):
    model = Product
    template_name = 'apps/idk/product-list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset




class ProductDetailView(DetailView):
    model = Product
    template_name = 'apps/idk/product-detail.html'
    context_object_name = 'product'


class OrderListView(ListView):
    model = Order
    template_name = 'apps/idk/order-list.html'
    context_object_name = 'orders'


class CustomLogoutView(View):
    def get(self,request):
        logout(self.request)
        return redirect('home')


from apps.forms import ProfileUpdateForm, CustomPasswordChangeForm

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'apps/idk/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user  # Ensure user can only edit their own profile

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)


class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'apps/idk/profile.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, "Password changed successfully!")
        return super().form_valid(form)


def a(request):
    return render(request,'apps/idk/profile.html')
