from datetime import timedelta, datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.forms import ModelForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, FormView, TemplateView, DetailView, UpdateView
from apps.forms import AuthForm, ProfileUpdateForm, CustomPasswordChangeForm, OrderForm, StreamForm, WithdrawForm, \
    OrderModelForm
from apps.models import User, Product, Category, District, Region, Wishlist, Order, Stream, AdminSetting, Withdraw


class CategoryListView(LoginRequiredMixin, ListView):
    queryset = Category.objects.all()
    template_name = "apps/home-page.html"
    context_object_name = "categories"
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['products'] = Product.objects.all()
        return data


class AuthFormView(FormView):
    form_class = AuthForm
    template_name = 'apps/auth/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        phone_number = form.cleaned_data.get("phone_number")
        password = form.cleaned_data.get("password")

        print(f"🔍 Checking user: {phone_number}")

        try:
            user = User.objects.get(phone_number=phone_number)
            print("✅ User exists!")

            if not user.check_password(password):
                print("❌ Wrong password!")
                messages.error(self.request, "Telefon nomer yoki parol xato!")
                return self.form_invalid(form)
        except User.DoesNotExist:
            print("🆕 User does not exist, creating new user...")
            user = User.objects.create_user(phone_number=phone_number, password=password)

        login(self.request, user)
        print("✅ Login successful!")
        return super().form_valid(form)


class CustomLogoutView(View):
    def get(self, request):
        logout(self.request)
        return redirect('home')


class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'apps/idk/profile.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        user = self.request.user
        old_password = form.cleaned_data.get('old')

        if not check_password(old_password, user.password):
            messages.error(self.request, "Eski parol noto‘g‘ri!")
            return self.form_invalid(form)

        form.save(user)
        messages.success(self.request, "Parol muvaffaqiyatli yangilandi! Iltimos, qayta kirish qiling.")
        logout(self.request)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f"Xatolik yuz berdi: {form.errors}")
        return super().form_invalid(form)


def district_list_view(request):
    region_id = request.GET.get('region_id')
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)


def a(request):
    return render(request, 'apps/idk/competition.html')


def order_success(request):
    order_id = request.session.get('last_order_id')

    if not order_id:
        messages.error(request, "Order topilmadi.")
        return redirect('order')
    order = Order.objects.get(id=order_id)
    deliver_price = AdminSetting.objects.first().deliver_price

    return render(request, 'apps/idk/order-successful.html', {'order': order, 'deliver_price': deliver_price})


def user_orders(request):
    orders = Order.objects.filter(owner=request.user).order_by('-ordered_at')

    return render(request, 'apps/idk/order.html', {'orders': orders})


class OrderFormView(FormView):
    form_class = OrderForm
    success_url = reverse_lazy('order-success')

    def form_valid(self, form):
        order = form.save(self.request.user)
        self.request.session['last_order_id'] = order.id

        return redirect('order-success')


class ProfileFormView(LoginRequiredMixin, FormView):
    template_name = 'apps/idk/profile.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = Region.objects.all()
        return context

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        district_id = form.cleaned_data['district_id']
        if district_id:
            user.district = get_object_or_404(District, id=district_id)
        else:
            user.district = None
        user.address = form.cleaned_data['address']
        user.telegram_id = form.cleaned_data['telegram_id']
        user.about = form.cleaned_data['about']
        user.save()
        messages.success(self.request, "Profil muvaffaqiyatli yangilandi!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f"Xatolik yuz berdi: {form.errors}")
        return super().form_invalid(form)


class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = "apps/idk/product-list.html"
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        slug_name = self.kwargs.get('slug')
        category = Category.objects.filter(slug=slug_name).first()

        products = Product.objects.all()

        if slug_name != 'all' and category:
            products = products.filter(category=category)

        query = self.request.GET.get("query")
        if query:
            products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

        data["products"] = products
        data["categories"] = Category.objects.all()
        data['session_category'] = category

        if self.request.user.is_authenticated:
            liked_products = Wishlist.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            data["liked_products_id"] = list(liked_products)
        else:
            data["liked_products_id"] = []

        return data


class WishlistView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request, product_id):
        liked = True
        like = Wishlist.objects.filter(product_id=product_id, user=self.request.user)
        if like.exists():
            like.delete()
            liked = False
        else:
            Wishlist.objects.create(product_id=product_id, user=self.request.user)

        return JsonResponse({'liked': liked})


class ProductDetailView(DetailView):
    model = Product
    template_name = "apps/idk/product-detail.html"
    context_object_name = "product"

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["liked_products_id"] = Wishlist.objects.filter(user=self.request.user).values_list("product_id",
                                                                                                   flat=True) if self.request.user.is_authenticated else []
        return context


class OrderView(FormView):
    form_class = OrderForm
    template_name = "apps/idk/order.html"
    success_url = reverse_lazy('order')

    def form_valid(self, form):
        order = form.save(self.request.user)
        return render(self.request, 'apps/idk/order-successful.html', {'order': order})


class OrderListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    queryset = Order.objects.all()
    template_name = "apps/idk/order-list.html"
    context_object_name = "orders"

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)
        data["orders"] = data.get("orders").filter(owner=self.request.user)
        return data


class WishlistListView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = "apps/wishlist.html"
    context_object_name = "wishlists"
    login_url = reverse_lazy("login")
    paginate_by = 6

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["categories"] = Category.objects.all()
        return data


class MarketView(ListView):
    queryset = Product.objects.all()
    template_name = "apps/idk/market-list.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.request.GET.get("category")
        query = self.request.GET.get("query")
        if category_slug:
            category = Category.objects.filter(slug=category_slug).first()
            if category:
                queryset = queryset.filter(category=category)
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["categories"] = Category.objects.all()
        data["query"] = self.request.GET.get("query", "")
        return data


class StreamListView(ListView):
    queryset = Stream.objects.all()
    template_name = 'apps/thread/stream-list.html'
    context_object_name = 'threads'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class CreateStreamView(LoginRequiredMixin, View):
    template_name = 'apps/idk/market-list.html'
    login_url = reverse_lazy('login')

    def get(self, request):
        return redirect('market')

    def post(self, request):
        form = StreamForm(request.POST)
        if form.is_valid():
            stream = form.save(commit=False)
            stream.owner = self.request.user
            stream.save()
            messages.success(request, "Oqim muvaffaqiyatli yaratildi!")
            return redirect('stream-list')
        else:
            messages.error(request, "Forma to‘ldirishda xatolik yuz berdi: " + str(form.errors))
            return redirect('market')


class StatsView(TemplateView):
    template_name = "apps/thread/stream-statistics.html"

    def get_context_data(self, **kwargs):
        global end_date
        context = super().get_context_data(**kwargs)
        streams = Stream.objects.all()
        period = self.request.GET.get('period', 'all')

        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'last_day':
            start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif period == 'weekly':
            start_date = now - timedelta(days=7)
        elif period == 'monthly':
            start_date = now - timedelta(days=30)
        else:
            start_date = None

        for stream in streams:
            orders = Order.objects.filter(thread__id=stream.id)
            if start_date:
                if period == 'last_day':
                    orders = orders.filter(ordered_at__range=[start_date, end_date])
                else:
                    orders = orders.filter(ordered_at__gte=start_date)

            stream.count = orders.count()
            stream.new_count = orders.filter(status=Order.StatusType.NEW).count()
            stream.ready_count = orders.filter(status=Order.StatusType.READY_TO_ORDER).count()
            stream.deliver_count = orders.filter(status=Order.StatusType.DELIVERING).count()
            stream.delivered_count = orders.filter(status=Order.StatusType.DELIVERED).count()
            stream.cant_phone_count = orders.filter(status=Order.StatusType.NOT_PICK_UP).count()
            stream.canceled_count = orders.filter(status=Order.StatusType.CANCELED).count()
            stream.archived_count = 0

        all_orders = Order.objects.all()
        if start_date:
            if period == 'last_day':
                all_orders = all_orders.filter(ordered_at__range=[start_date, end_date])
            else:
                all_orders = all_orders.filter(ordered_at__gte=start_date)

        context['streams'] = streams
        context['all_count'] = all_orders.count()
        context['all_new'] = all_orders.filter(status=Order.StatusType.NEW).count()
        context['all_ready'] = all_orders.filter(status=Order.StatusType.READY_TO_ORDER).count()
        context['all_deliver'] = all_orders.filter(status=Order.StatusType.DELIVERING).count()
        context['all_delivered'] = all_orders.filter(status=Order.StatusType.DELIVERED).count()
        context['all_cant_phone'] = all_orders.filter(status=Order.StatusType.NOT_PICK_UP).count()
        context['all_canceled'] = all_orders.filter(status=Order.StatusType.CANCELED).count()
        context['all_archived'] = 0

        return context


class CompetitionListView(ListView):
    template_name = 'apps/idk/competition.html'
    context_object_name = "users"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['site'] = AdminSetting.objects.first()
        return data

    def get_queryset(self):
        start_date = datetime(2024, 9, 20, tzinfo=timezone.get_current_timezone())
        end_date = datetime(2025, 3, 20, tzinfo=timezone.get_current_timezone())

        query = User.objects.all()
        query = query.annotate(
            order_count=Count(
                'order',
                filter=Q(
                    order__status=Order.StatusType.COMPLETED,
                    order__ordered_at__range=[start_date, end_date]
                )
            )
        ).order_by('-order_count').only('first_name', 'full_name', 'phone_number')

        ranked_users = []
        for rank, user in enumerate(query, start=1):
            if user.order_count > 0:
                ranked_users.append({
                    'rank': rank,
                    'first_name': user.first_name or user.full_name or user.phone_number,
                    'order_count': user.order_count
                })
        return ranked_users


class WithdrawView(LoginRequiredMixin, FormView):
    template_name = "apps/idk/withdraw.html"
    form_class = WithdrawForm
    success_url = reverse_lazy('withdraw')
    login_url = reverse_lazy("login")

    def form_valid(self, form):
        withdraw = form.save(commit=False)
        user = self.request.user
        request_amounted=withdraw.amount

        if user.balance < request_amounted:
            messages.error(self.request,"Balansingizda hisob yetarli emas")
            return self.form_invalid(form)
        withdraw.user = user
        withdraw.save()
        messages.success(self.request,"Sorov yuborildi ! ")
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["user"] = self.request.user
        data["withdraws"] = Withdraw.objects.filter(user=self.request.user).order_by('-created_at')
        return data




class OperatorTemplateView(TemplateView):
    template_name = "apps/operator/operator-page.html"

    def post(self, request):
        context = self.get_context_data()
        return render(request, 'apps/operator/operator-page.html', context)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        status = self.request.GET.get('status')

        category_id = self.request.POST.get('category_id')
        district_id = self.request.POST.get('district_id')
        data['status'] = Order.StatusType.values
        data['categories'] = Category.objects.all()
        data['regions'] = Region.objects.all()
        orders = Order.objects.filter(status=Order.StatusType.NEW)
        if status:
            orders = Order.objects.filter(status=status)
        if category_id:
            orders = orders.filter(product__category_id=category_id)
        if district_id:
            orders = orders.filter(district_id=district_id)
        data['orders'] = orders
        return data


class OperatorOrderChangeDetailView(DetailView):
    queryset = Order.objects.all()
    template_name = 'apps/operator/order-change.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['regions'] = Region.objects.all()
        return data


class OrderUpdateView(UpdateView):
    queryset = Order.objects.all()
    form_class = OrderModelForm
    template_name = 'apps/operator/order-change.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('operator')


class CoinView(View):
    template_name = 'apps/coin/coin.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter().order_by('id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
