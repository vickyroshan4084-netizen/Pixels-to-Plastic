import os
import django
import sys

# Set up Django environment
sys.path.append(r'c:\Users\vicky\OneDrive\Desktop\P2P\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vignesh3d.settings')
django.setup()

from products.models import PaymentMethod
from products.serializers import PaymentMethodSerializer

def verify():
    print("Verifying Payment Method Implementation...")
    
    # 1. Create a UPI Payment Method with QR
    pay, created = PaymentMethod.objects.get_or_create(
        name="GPay UPI",
        method_type="upi",
        upi_id="vickyroshan1995-1@okhdfcbank",
        instructions="Scan and pay, then share screenshot on WhatsApp",
        icon="📱"
    )
    if created:
        print(f"Created new payment method: {pay}")
    else:
        print(f"Using existing payment method: {pay}")

    # 2. Verify Serializer
    serializer = PaymentMethodSerializer(pay)
    print(f"Serialized Data: {serializer.data}")
    assert serializer.data['name'] == "GPay UPI"
    assert serializer.data['method_type'] == "upi"
    assert serializer.data['upi_id'] == "vickyroshan1995-1@okhdfcbank"

    print("Verification Successful!")

if __name__ == "__main__":
    verify()
