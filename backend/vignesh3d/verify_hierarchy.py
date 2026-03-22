import os
import django
import sys

# Set up Django environment
sys.path.append(r'c:\Users\vicky\OneDrive\Desktop\P2P\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vignesh3d.settings')
django.setup()

from products.models import MainCategory, ProductCategory, Product
from products.serializers import MainCategorySerializer, ProductCategorySerializer

def verify():
    print("Verifying Product Hierarchy Implementation...")
    
    # 1. Check MainCategory
    mc = MainCategory.objects.first()
    if mc:
        print(f"MainCategory: {mc.name}")
        serializer = MainCategorySerializer(mc)
        print(f"MC Serializer fields: {serializer.data.keys()}")
        assert 'image' in serializer.data
    else:
        print("No MainCategory found!")

    # 2. Check ProductCategory
    pc = ProductCategory.objects.first()
    if pc:
        print(f"ProductCategory: {pc.name}")
        serializer = ProductCategorySerializer(pc)
        print(f"PC Serializer fields: {serializer.data.keys()}")
        assert 'image' in serializer.data
        assert 'main_category' in serializer.data
    else:
        print("No ProductCategory found!")

    print("Verification Successful!")

if __name__ == "__main__":
    verify()
