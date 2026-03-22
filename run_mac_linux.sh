#!/bin/bash
echo "================================================"
echo "  Pixels to Plastic (P2P) — Local Setup"
echo "================================================"
echo

cd backend

echo "[1] Installing packages..."
pip install -r requirements.txt
echo

echo "[2] Creating database tables..."
python manage.py makemigrations accounts products cart orders
python manage.py migrate
echo

echo "[3] Seeding sample categories..."
python manage.py shell -c "
from products.models import MainCategory, ProductCategory
m1,_ = MainCategory.objects.get_or_create(name='Miniatures', defaults={'icon':'⚔️'})
m2,_ = MainCategory.objects.get_or_create(name='Tools',      defaults={'icon':'🔧'})
m3,_ = MainCategory.objects.get_or_create(name='Home Decor', defaults={'icon':'🏮'})
ProductCategory.objects.get_or_create(main_category=m1, name='Warriors and Soldiers', defaults={'base_price':800})
ProductCategory.objects.get_or_create(main_category=m1, name='Fantasy Creatures',    defaults={'base_price':1200})
ProductCategory.objects.get_or_create(main_category=m2, name='Workshop Tools',       defaults={'base_price':600})
ProductCategory.objects.get_or_create(main_category=m3, name='Table Decor',          defaults={'base_price':900})
print('Categories seeded!')
"
echo

echo "[4] Creating admin user (enter username + password)..."
python manage.py createsuperuser
echo

echo "================================================"
echo " Starting server: http://localhost:8000"
echo " Open frontend/index.html in your browser"
echo "================================================"
python manage.py runserver
