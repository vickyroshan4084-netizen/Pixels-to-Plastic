from django.urls import path
from .views import OrderListView, CheckoutView, PaymentVerifyView, OrderDetailView, OrderStatusUpdateView, ExportOrdersCSVView

urlpatterns = [
    path('',                      OrderListView.as_view()),
    path('checkout/',             CheckoutView.as_view()),
    path('payment/verify/',       PaymentVerifyView.as_view()),
    path('export_csv/',           ExportOrdersCSVView.as_view(), name='export-orders-csv'),
    path('<int:pk>/',             OrderDetailView.as_view()),
    path('<int:pk>/status/',      OrderStatusUpdateView.as_view()),
]
from .export_views import export_orders_excel
path('export/excel/', export_orders_excel, name='export-orders'),