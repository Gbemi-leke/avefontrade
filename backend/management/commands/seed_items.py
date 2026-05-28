from django.core.management.base import BaseCommand
from backend.models import BuyingItem

ITEMS = [
    ("Men's Ankara Long Sleeve Shirts",     'mens',        35,  'piece', 20,  'URGENT', 78),
    ("Women's Kaba & Slit Sets",            'womens',      80,  'set',   1,   'HOT',    62),
    ('Authentic Kente Strip Cloth',          'kente',       120, 'yard',  10,  'URGENT', 45),
    ('Ankara / Holland Wax Print 6-Yard',    'fabric',      55,  '6yds',  1,   '',       55),
    ("Men's Casual Linen Shorts (Bulk)",     'mens',        22,  'piece', 50,  '',       80),
    ("Women's Wrap Dashiki Dress",           'womens',      45,  'piece', 1,   'HOT',    70),
    ('Northern Smock / Fugu Fabric',         'fabric',      40,  'yard',  1,   'NEW',    40),
    ('Kente Accessories — Bags & Hats',      'kente',       25,  'piece', 1,   '',       50),
    ("Men's Batik Short Sleeve Shirts",      'mens',        28,  'piece', 30,  '',       65),
    ("Women's Batik Skirt & Blouse Set",     'womens',      55,  'set',   1,   'NEW',    48),
    ('Polyester Chiffon Fabric (Wholesale)', 'fabric',      18,  'yard',  20,  '',       55),
    ('Royal Kente Cloth — Full Piece',       'kente',       350, 'piece', 1,   'URGENT', 20),
    ("Men's Plain Cotton T-Shirts (Bulk)",   'mens',        12,  'piece', 100, '',       90),
    ("Women's Ankara Headwraps (Gele)",      'womens',      15,  'piece', 1,   'HOT',    85),
    ('Pure Cotton Fabric Roll (Wholesale)',  'fabric',      30,  'yard',  50,  'NEW',    35),
    ('Kente Strip — Ashanti Royal Pattern',  'kente',       180, 'yard',  1,   'URGENT', 30),
]

class Command(BaseCommand):
    help = 'Seed buying items into the database'

    def handle(self, *args, **kwargs):
        created = 0
        for name, cat, price, unit, min_qty, badge, pct in ITEMS:
            obj, was_created = BuyingItem.objects.get_or_create(
                name=name,
                defaults=dict(category=cat, price=price, unit=unit,
                              min_qty=min_qty, badge=badge, pct_filled=pct, is_active=True)
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'✅ Seeded {created} items ({BuyingItem.objects.count()} total)'))
