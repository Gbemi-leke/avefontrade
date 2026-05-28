from django.urls import path
from backend import views

app_name = 'backend'

urlpatterns = [
    # Dashboards
    path('dashboard/',                              views.user_dashboard,       name='user-dashboard'),
    path('dashboard/seller/',                       views.seller_dashboard,     name='seller-dashboard'),
    path('dashboard/admin/',                        views.admin_dashboard,      name='admin-dashboard'),

    # Admin: Sellers & Offers
    path('dashboard/admin/sellers/',                views.admin_sellers,        name='admin-sellers'),
    path('dashboard/admin/offers/',                 views.admin_offers,         name='admin-offers'),
    path('dashboard/admin/offers/<str:ref>/',       views.offer_detail,         name='offer-detail'),
    path('dashboard/admin/offers/<str:ref>/update/',views.update_offer_status,  name='update-offer-status'),

    # Admin: Buying Items CRUD
    path('dashboard/admin/products/',               views.admin_products,       name='admin-products'),
    path('dashboard/admin/products/add/',           views.add_product,          name='add-product'),
    path('dashboard/admin/products/<int:pk>/edit/', views.edit_product,         name='edit-product'),
    path('dashboard/admin/products/<int:pk>/delete/', views.delete_product,     name='delete-product'),

    # Account
    path('profile/edit/',                           views.edit_profile,         name='edit-profile'),
    path('profile/password/',                       views.change_password,      name='change-password'),

    # OTP
    path('send-otp/',                               views.send_otp,             name='send-otp'),
    path('dashboard/admin/create-admin/',           views.create_admin,         name='create-admin'),
]
