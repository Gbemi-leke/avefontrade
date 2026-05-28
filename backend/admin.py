from django.contrib import admin
from django.utils.html import format_html
from .models import BuyingItem, SellerOffer


@admin.register(BuyingItem)
class BuyingItemAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'price_display', 'badge', 'pct_filled', 'is_active')
    list_filter   = ('category', 'badge', 'is_active')
    list_editable = ('badge', 'is_active', 'pct_filled')
    search_fields = ('name',)

    def price_display(self, obj):
        return format_html('<strong style="color:#1B2D6B">GH₵ {}</strong>', obj.price)
    price_display.short_description = 'Price'


@admin.register(SellerOffer)
class SellerOfferAdmin(admin.ModelAdmin):
    list_display   = ('ref', 'seller_name', 'item_name', 'quantity', 'total_display', 'bank_name', 'status', 'status_badge', 'created_at')
    list_filter    = ('status', 'created_at')
    list_editable  = ('status',)
    search_fields  = ('ref', 'seller_name', 'seller_phone', 'item_name')
    readonly_fields = ('ref', 'created_at', 'updated_at')

    def total_display(self, obj):
        return format_html('<strong>GH₵ {:,.2f}</strong>', obj.total)
    total_display.short_description = 'Total'

    def status_badge(self, obj):
        colors = {
            'pending':  '#F59E0B',
            'approved': '#3B82F6',
            'received': '#8B5CF6',
            'paid':     '#10B981',
            'rejected': '#EF4444',
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:10px;font-size:11px;font-weight:700">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Label'