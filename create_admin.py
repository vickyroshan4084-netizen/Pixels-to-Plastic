#!/usr/bin/env python
"""
create_admin.py  —  Easy Admin Creator for Pixels to Plastic
=============================================================
Place this file in your /backend/ folder.

Run:
    cd backend
    python create_admin.py

Or with flags (no prompts):
    python create_admin.py --username admin --password admin123 --email admin@p2p.com
"""
import os, sys, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vignesh3d.settings')

import django
django.setup()

from django.contrib.auth.models import User


def run(username=None, password=None, email=None):
    print()
    print("=" * 48)
    print("  Pixels to Plastic — Admin Account Creator")
    print("=" * 48)
    print()

    if not username:
        username = input("  Username  [admin]: ").strip() or "admin"
    if not email:
        email = input("  Email     [admin@p2p.com]: ").strip() or "admin@p2p.com"
    if not password:
        import getpass
        while True:
            pw  = getpass.getpass("  Password  (min 6 chars): ")
            pw2 = getpass.getpass("  Confirm   password: ")
            if pw != pw2:   print("  Passwords don't match. Try again.\n"); continue
            if len(pw) < 6: print("  Too short. Try again.\n");             continue
            password = pw; break

    print()

    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"  User '{username}' already exists.")
        ans = input("  Make this user an admin? [y/N]: ").strip().lower()
        if ans != 'y':
            print("  Cancelled."); return
        user.set_password(password)
        user.email        = email
        user.is_staff     = True
        user.is_superuser = True
        user.save()
        print(f"\n  '{username}' upgraded to admin!\n")
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"  Admin created!\n")
        print(f"  Username : {username}")
        print(f"  Email    : {email}")
        print(f"\n  Open frontend/admin-login.html")
        print(f"  Click the 'Admin' tab and sign in\n")


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Create P2P admin user')
    p.add_argument('--username'); p.add_argument('--password'); p.add_argument('--email')
    args = p.parse_args()
    try:
        run(args.username, args.password, args.email)
    except KeyboardInterrupt:
        print("\n\n  Cancelled.")
    except Exception as e:
        print(f"\n  Error: {e}"); sys.exit(1)
