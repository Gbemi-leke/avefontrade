from django.urls import path
from frontend import views

app_name = 'frontend'

urlpatterns = [
    # Homepage
    path('',                        views.index,            name='index'),

    # Auth
    path('login/',                  views.login_view,       name='login'),
    path('logout/',                 views.logout_view,      name='logout'),
    path('register/',               views.register_view,    name='register'),
    path('register/seller/',        views.vendor_register,  name='vendor-register'),

    # Shop pages
    path('shop/',                   views.product_listing,  name='product-listing'),
    path('shop/<str:category>/',    views.product_listing,  name='product-listing-cat'),
    path('item/<int:pk>/',          views.product_detail,   name='product-detail'),
    path('wishlist/',               views.wishlist,          name='wishlist'),
    path('cart/',                   views.cart,              name='cart'),
    path('checkout/',               views.checkout,          name='checkout'),
    path('track-order/',            views.order_tracking,    name='order-tracking'),

    # Seller actions
    path('sell/',                   views.sell_offer,        name='sell-offer'),
    path('sell/<int:item_pk>/',     views.sell_offer,        name='sell-offer-item'),
    path('offer/<str:ref>/',        views.offer_success,     name='offer-success'),

    # Legal pages
    path('privacy-policy/',         views.privacy_policy,    name='privacy-policy'),
    path('terms-and-conditions/',   views.terms_conditions,  name='terms-conditions'),
    path('seller-agreement/',       views.seller_agreement,  name='seller-agreement'),
    path('help-center/',            views.help_center,       name='help-center'),
]
