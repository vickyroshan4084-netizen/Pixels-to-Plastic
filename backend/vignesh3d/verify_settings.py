import os
import django
import sys

# Set up Django environment
sys.path.append(r'c:\Users\vicky\OneDrive\Desktop\P2P\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vignesh3d.settings')
django.setup()

from products.models import SiteSettings
from products.serializers import SiteSettingsSerializer

def verify():
    print("Verifying Site Settings Implementation...")
    
    # 1. Create Site Settings
    settings, created = SiteSettings.objects.get_or_create(
        about_title="About P2P",
        about_text="We print amazing 3D models.",
        contact_email="test@p2p.com",
        contact_phone="+91 11111 22222",
        contact_address="Test City, India",
        footer_copy="© 2026 P2P Test"
    )
    if created:
        print(f"Created new site settings: {settings}")
    else:
        print(f"Using existing site settings: {settings}")

    # 2. Verify Serializer
    serializer = SiteSettingsSerializer(settings)
    print(f"Serialized Data: {serializer.data}")
    assert serializer.data['about_title'] == "About P2P"
    assert serializer.data['contact_email'] == "test@p2p.com"

    print("Verification Successful!")

if __name__ == "__main__":
    verify()
