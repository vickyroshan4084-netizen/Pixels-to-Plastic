import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vignesh3d.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
import getpass

def create_admin():
    print("=" * 50)
    print("   Pixels to Plastic (P2P) — Admin Creator")
    print("=" * 50)
    print("\nThis script will create a new administrator account.\n")

    try:
        username = input("Enter Username: ").strip()
        if User.objects.filter(username=username).exists():
            print(f"Error: Username '{username}' already exists.")
            return

        email = input("Enter Email: ").strip()
        password = getpass.getpass("Enter Password: ")
        password_confirm = getpass.getpass("Confirm Password: ")

        if password != password_confirm:
            print("Error: Passwords do not match.")
            return

        if len(password) < 8:
            print("Error: Password must be at least 8 characters long.")
            return

        # Create the user
        print(f"\nCreating account for {username}...")
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        # Create/Update UserProfile
        # User.objects.create_superuser handles is_staff and is_superuser
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = 'admin'
        profile.save()

        print("\n" + "✓" * 50)
        print(" SUCCESS: Admin account created successfully!")
        print(" You can now log in at http://localhost:8000/admin-login.html")
        print("✓" * 50)

    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    create_admin()
