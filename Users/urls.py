from django.urls import path
from Users.views import RegisterView, LoginView, LogoutView, CartView, AddToCartView, IncreaseToCartView, DecreaseToCartView, DeleteToCartView, UserDelete

urlpatterns = [
    path('register', RegisterView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('delete', UserDelete.as_view(), name="delete"),
    path('cart/', CartView.as_view(), name="cart"),
    path('cart/add_to_cart', AddToCartView.as_view(), name="add_to_cart"),
    path('cart/increase_item_in_cart',
         IncreaseToCartView.as_view(), name="increase_to_cart"),
    path('cart/decrease_item_in_cart',
         DecreaseToCartView.as_view(), name="decrease_to_cart"),
    path('cart/delete_item_in_cart',
         DeleteToCartView.as_view(), name="delete_to_cart"),
]
