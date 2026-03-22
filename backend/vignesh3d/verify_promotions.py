import os
import django
import sys

# Set up Django environment
sys.path.append(r'c:\Users\vicky\OneDrive\Desktop\P2P\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vignesh3d.settings')
django.setup()

from products.models import Promotion
from products.serializers import PromotionSerializer

def verify():
    print("Verifying Promotion Implementation...")
    
    # 1. Check if we can create a promotion
    promo, created = Promotion.objects.get_or_create(
        banner_text="Test Promotion | Free shipping above ₹500",
        shipping_threshold=500.00
    )
    if created:
        print(f"Created new promotion: {promo}")
    else:
        print(f"Using existing promotion: {promo}")

    # 2. Verify Serializer
    serializer = PromotionSerializer(promo)
    print(f"Serialized Data: {serializer.data}")
    assert serializer.data['banner_text'] == "Test Promotion | Free shipping above ₹500"
    assert float(serializer.data['shipping_threshold']) == 500.00

    print("Verification Successful!")

if __name__ == "__main__":
    verify()
