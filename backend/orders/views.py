import hmac, hashlib
from django.conf import settings
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
import csv
from cart.views import get_or_create_cart
from cart.models import CartItem
from products.models import Product
from .models import Order, OrderItem
from .serializers import OrderSerializer

try:
    import razorpay
    rzp_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
except Exception:
    rzp_client = None


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.prefetch_related('items').all()


class CheckoutView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        data = request.data
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        # Build order
        subtotal  = float(cart.total)
        shipping  = 0 if subtotal >= 1000 else 99
        total     = subtotal + shipping

        order = Order.objects.create(
            user             = request.user if request.user.is_authenticated else None,
            guest_name       = data.get('name', ''),
            guest_email      = data.get('email', ''),
            guest_phone      = data.get('phone', ''),
            shipping_address = data.get('shipping_address', ''),
            city             = data.get('city', ''),
            state            = data.get('state', ''),
            pincode          = data.get('pincode', ''),
            payment_method   = data.get('payment_method', 'cod'),
            subtotal         = subtotal,
            shipping_charge  = shipping,
            total            = total,
            status           = 'pending',
        )

        # Copy cart items → order items, reduce stock
        for ci in cart.items.select_related('product'):
            OrderItem.objects.create(
                order      = order,
                product    = ci.product,
                title      = ci.product.title,
                unit_price = ci.product.final_price,
                quantity   = ci.quantity,
                line_total = ci.line_total,
            )
            # Reduce stock
            Product.objects.filter(id=ci.product.id).update(stock=ci.product.stock - ci.quantity)

        # Razorpay order
        response_data = OrderSerializer(order).data
        if order.payment_method == 'razorpay' and rzp_client:
            try:
                rzp_order = rzp_client.order.create({
                    'amount':   int(total * 100),
                    'currency': 'INR',
                    'receipt':  f'order_{order.id}',
                })
                order.razorpay_order_id = rzp_order['id']
                order.save()
                response_data['razorpay_order_id'] = rzp_order['id']
                response_data['razorpay_key_id']   = settings.RAZORPAY_KEY_ID
            except Exception as e:
                # Razorpay unavailable — fall back to COD
                pass

        # Google Pay — just return UPI VPA and amount, frontend builds deep-link
        if order.payment_method == 'gpay':
            response_data['gpay_upi_vpa']      = settings.GPAY_UPI_VPA
            response_data['gpay_merchant_name'] = settings.GPAY_MERCHANT_NAME
            response_data['gpay_amount']        = str(total)
            order.status = 'pending'
            order.save()

        # COD — mark pending, no payment needed
        if order.payment_method == 'cod':
            order.status = 'pending'
            order.save()

        # Clear cart
        cart.items.all().delete()

        return Response(response_data, status=201)


class PaymentVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        razorpay_order_id   = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature  = request.data.get('razorpay_signature')

        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        # Verify HMAC signature
        msg  = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
        key  = settings.RAZORPAY_KEY_SECRET.encode()
        computed = hmac.new(key, msg, hashlib.sha256).hexdigest()

        if computed == razorpay_signature:
            order.razorpay_payment_id = razorpay_payment_id
            order.payment_verified    = True
            order.status              = 'paid'
            order.save()
            return Response({'status': 'payment verified', 'order_id': order.id})

        return Response({'error': 'Payment verification failed'}, status=400)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class   = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.prefetch_related('items').all()


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        new_status = request.data.get('status')
        valid = [s[0] for s in Order.STATUS_CHOICES]
        if new_status not in valid:
            return Response({'error': f'Invalid status. Choose from: {valid}'}, status=400)
        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)


class ExportOrdersCSVView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="p2p_orders.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer Name', 'Email', 'Phone', 'Address', 'City', 'State', 'Pincode', 'Payment Method', 'Status', 'Total', 'Date'])
        for o in Order.objects.all().order_by('-created_at'):
            writer.writerow([
                o.id,
                o.guest_name,
                o.guest_email,
                o.guest_phone,
                o.shipping_address,
                o.city,
                o.state,
                o.pincode,
                o.payment_method,
                o.status,
                o.total,
                o.created_at.strftime('%d/%m/%Y %H:%M')
            ])
        return response
