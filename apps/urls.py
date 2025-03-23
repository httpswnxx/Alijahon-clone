from django.urls import path
from . import views
from templates import *
from .views import *

urlpatterns = [
    path('', CategoryListView.as_view(), name='home'),
    path("products/<str:slug>", ProductListView.as_view(), name="product_list"),
    path('login/', AuthFormView.as_view(), name='login'),
    path("logout/", CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileFormView.as_view(), name='profile'),
    path('profile/change-password/', PasswordChangeView.as_view(), name='change_password'),
    path("test/", a),
    path('districts_list/', district_list_view, name='districts_list'),
    path("wishlist/<int:product_id>", WishlistView.as_view(), name='wishlist'),
    path("product-detail/<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
    path('order/form', OrderView.as_view(), name='order'),
    path('order-list', OrderListView.as_view(), name='orders'),
    path('market', MarketView.as_view(), name='market'),
    path('wishlist', WishlistListView.as_view(), name='wishlist-page'),
]

urlpatterns += [
    path('stream-list/', StreamListView.as_view(), name='stream-list'),
    path('create-stream/', CreateStreamView.as_view(), name='create_stream'),
    path('admin_page/stats', StatsView.as_view(), name='stats'),
    path('konkurs/', CompetitionListView.as_view(), name='konkurs'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('diagrams', DiagramView.as_view(), name='diagrams'),
    path('operator-list/', OperatorListView.as_view(), name='operator_list'),
    path('create-operator-order/', CreateOperatorOrderView.as_view(), name='create_operator_order'),
    path('operator-detail/<int:pk>/', OperatorDetailView.as_view(), name='operator_detail'),
]
