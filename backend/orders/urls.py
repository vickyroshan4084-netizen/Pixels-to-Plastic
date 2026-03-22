from django.urls import path
from .views import OrderListView, CheckoutView, PaymentVerifyView, OrderDetailView, OrderStatusUpdateView

urlpatterns = [
    path('',                      OrderListView.as_view()),
    path('checkout/',             CheckoutView.as_view()),
    path('payment/verify/',       PaymentVerifyView.as_view()),
    path('<int:pk>/',             OrderDetailView.as_view()),
    path('<int:pk>/status/',      OrderStatusUpdateView.as_view()),
]
from .export_views import export_orders_excel
path('export/excel/', export_orders_excel, name='export-orders'),