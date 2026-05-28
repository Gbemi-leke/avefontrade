from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


# ── BUYING ITEM ───────────────────────────────────────────────
class BuyingItem(models.Model):
    CATEGORIES = [
        ('mens',         "Men's Wear"),
        ('womens',       "Women's Clothing"),
        ('kente',        'Kente & Traditional'),
        ('fabric',       'Fabrics & Textiles'),
        ('accessories',  'Accessories'),
        ('wholesale',    'Wholesale Lots'),
        ('traditional',  'Traditional Wear'),
        ('smock',        'Smock & Fugu'),
    ]
    BADGES = [('', 'None'), ('URGENT', '🔥 Urgent'), ('HOT', '⭐ Hot'), ('NEW', '✨ New')]
    EMOJIS = {
        'mens': '👔', 'womens': '👗', 'kente': '🧣',
        'fabric': '🧵', 'accessories': '👜', 'wholesale': '📦',
        'traditional': '🏵', 'smock': '🪡',
    }
    BG_COLORS = {
        'mens': '#EEF1FB', 'womens': '#FDE8F5', 'kente': '#FDF6DC',
        'fabric': '#EEF1FB', 'accessories': '#FDF6DC', 'wholesale': '#E8F5E9',
        'traditional': '#FDF6DC', 'smock': '#EEF1FB',
    }

    name        = models.CharField(max_length=200)
    category    = models.CharField(max_length=20, choices=CATEGORIES)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2, help_text="Max price Avefon pays")
    unit        = models.CharField(max_length=30, default='piece')
    min_qty     = models.PositiveIntegerField(default=1)
    badge       = models.CharField(max_length=10, choices=BADGES, blank=True, default='')
    image       = models.ImageField(upload_to='buying_items/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    pct_filled  = models.PositiveIntegerField(default=0, help_text="% of stock filled (0-100)")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-badge', 'category', 'name']

    def __str__(self):
        return self.name

    @property
    def emoji(self):
        return self.EMOJIS.get(self.category, '📦')

    @property
    def bg(self):
        return self.BG_COLORS.get(self.category, '#EEF1FB')

    @property
    def pct(self):
        return self.pct_filled

    @property
    def cat(self):
        return self.category

    def to_dict(self):
        return {
            'id': self.pk, 'cat': self.category, 'emoji': self.emoji,
            'bg': self.bg, 'name': self.name, 'price': float(self.price),
            'unit': self.unit, 'min_qty': self.min_qty,
            'badge': self.badge, 'pct': self.pct_filled,
            'image_url': self.image.url if self.image else '',
        }


# ── SELLER OFFER ──────────────────────────────────────────────
class SellerOffer(models.Model):
    STATUS = [
        ('pending',  '⏳ Pending Review'),
        ('approved', '✅ Approved'),
        ('received', '📦 Goods Received'),
        ('paid',     '💰 Paid'),
        ('rejected', '❌ Rejected'),
    ]

    ref           = models.CharField(max_length=20, unique=True, editable=False)
    user          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='offers')
    seller_name   = models.CharField(max_length=200)
    seller_phone  = models.CharField(max_length=20)
    seller_email  = models.EmailField(blank=True)
    item          = models.ForeignKey(BuyingItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='offers')
    item_name     = models.CharField(max_length=200)
    quantity      = models.PositiveIntegerField()
    asking_price  = models.DecimalField(max_digits=10, decimal_places=2)
    condition     = models.CharField(max_length=50, default='Brand New')
    description   = models.TextField(blank=True)
    bank_name     = models.CharField(max_length=100)
    account_name  = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    branch        = models.CharField(max_length=100, blank=True)
    location      = models.CharField(max_length=200, blank=True, help_text='Seller location/address for delivery')
    status        = models.CharField(max_length=20, choices=STATUS, default='pending')
    admin_note    = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ref} — {self.item_name} by {self.seller_name}"

    def save(self, *args, **kwargs):
        if not self.ref:
            self.ref = 'AVF-' + uuid.uuid4().hex[:6].upper()
        super().save(*args, **kwargs)

    @property
    def total(self):
        return float(self.quantity) * float(self.asking_price)

    @property
    def bank(self):
        return self.bank_name

    @property
    def qty(self):
        return self.quantity

    @property
    def price(self):
        return float(self.asking_price)
