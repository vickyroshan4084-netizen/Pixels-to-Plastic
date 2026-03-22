from django.urls import path
from .views import CartDetailView, CartItemCreateView, CartItemUpdateView

urlpatterns = [
    path('',             CartDetailView.as_view()),
    path('items/',       CartItemCreateView.as_view()),
    path('items/<int:pk>/', CartItemUpdateView.as_view()),
]
