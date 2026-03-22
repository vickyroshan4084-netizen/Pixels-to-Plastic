import os
import django
import sys
import getpass

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vignesh3d.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def create_vicky_superuser():
    print("=" * 60)
    print("   Pixels to Plastic (P2P) — Superuser Setup")
    print("=" * 60)
    
    email = "vickyroshan4084@gmail.com"
    username = "vickyroshan" # You can change this or keep it as vickyroshan
    
    print(f"\nTarget Email: {email}")
    
    # Check if user already exists
    existing_user = User.objects.filter(email=email).first()
    if existing_user:
        print(f"User with email {email} already exists (Username: {existing_user.username}).")
        choice = input("Do you want to reset the password and make them superuser? (y/n): ").lower()
        if choice != 'y':
            print("Operation cancelled.")
            return
        user = existing_user
    else:
        user = User(username=username, email=email)
        print(f"Creating new user: {username}")

    password = getpass.getpass("Enter New Password for Admin/Superuser: ")
    password_confirm = getpass.getpass("Confirm Password: ")

    if password != password_confirm:
        print("Error: Passwords do not match.")
        return

    if len(password) < 8:
        print("Error: Password must be at least 8 characters long.")
        return

    # Set password and privileges
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

    # Create/Update UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.role = 'admin'
    profile.save()

    print("\n" + "✓" * 60)
    print(f" SUCCESS: Superuser '{user.username}' ({email}) is ready!")
    print(" You can now log in at:")
    print(" 1. Django Admin: http://localhost:8000/admin/")
    print(" 2. Site Admin Login (using email): http://localhost:8000/admin-login.html")
    print("✓" * 60)

if __name__ == "__main__":
    try:
        create_vicky_superuser()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
