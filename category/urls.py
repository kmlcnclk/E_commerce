from django.urls import path
from .views import CreateView, GetView, UpdateView, DeleteView

urlpatterns = [
    path('create', CreateView.as_view(), name="create"),
    path('get', GetView.as_view(), name="get"),
    path('update/<str:pk>', UpdateView.as_view(), name="update"),
    path('delete/<str:pk>', DeleteView.as_view(), name="delete"),
]
