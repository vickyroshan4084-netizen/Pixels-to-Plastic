from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Merge guest cart if any
        sid = request.session.session_key
        if sid:
            try:
                guest = Cart.objects.get(session_id=sid, user=None)
                for item in guest.items.all():
                    ci, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
                    if not created:
                        ci.quantity += item.quantity
                        ci.save()
                guest.delete()
            except Cart.DoesNotExist:
                pass
        return cart
    # Guest cart via session
    if not request.session.session_key:
        request.session.create()
    sid = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_id=sid, user=None)
    return cart


class CartDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = get_or_create_cart(request)
        return Response(CartSerializer(cart).data)


class CartItemCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cart = get_or_create_cart(request)
        product_id = request.data.get('product_id')
        quantity   = int(request.data.get('quantity', 1))
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)
        if not product.in_stock:
            return Response({'error': 'Out of stock'}, status=400)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        return Response(CartSerializer(cart).data, status=201)


class CartItemUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    def patch(self, request, pk):
        cart = get_or_create_cart(request)
        try:
            item = CartItem.objects.get(id=pk, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)
        qty = int(request.data.get('quantity', item.quantity))
        if qty <= 0:
            item.delete()
        else:
            item.quantity = qty
            item.save()
        return Response(CartSerializer(cart).data)

    def delete(self, request, pk):
        cart = get_or_create_cart(request)
        CartItem.objects.filter(id=pk, cart=cart).delete()
        return Response(CartSerializer(cart).data)
