from django.urls import path
from .views import CreateView, GetView, UpdateView, DeleteView, LikeView, UnlikeView, GetProductsView

urlpatterns = [
    path('create', CreateView.as_view(), name="create"),
    path('get/<str:pk>', GetView.as_view(), name="get"),
    path('update/<str:pk>', UpdateView.as_view(), name="update"),
    path('delete/<str:pk>', DeleteView.as_view(), name="delete"),
    path('like/<str:pk>', LikeView.as_view(), name="like"),
    path('unlike/<str:pk>', UnlikeView.as_view(), name="unlike"),
    path('a', GetProductsView.as_view(), name="unlike"),
]
