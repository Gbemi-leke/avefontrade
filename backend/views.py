from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
import json, random

try:
    from backend.models import BuyingItem, SellerOffer
    USE_DB = True
except Exception:
    USE_DB = False

from frontend.views import CATEGORIES


def _get_offers_for_user(request, user):
    if USE_DB:
        try:
            return list(SellerOffer.objects.filter(user=user).order_by('-created_at'))
        except Exception:
            pass
    return request.session.get('user_offers', [])


def _get_all_offers(request):
    if USE_DB:
        try:
            return list(SellerOffer.objects.all().order_by('-created_at'))
        except Exception:
            pass
    return request.session.get('all_offers', [])


# ── USER DASHBOARD ────────────────────────────────────────────
@login_required
def user_dashboard(request):
    offers = _get_offers_for_user(request, request.user)
    return render(request, 'backend/user-dashboard.html', {
        'offers':  offers,
        'total':   len(offers),
        'pending': sum(1 for o in offers if (o.status if hasattr(o,'status') else o.get('status')) == 'pending'),
        'paid':    sum(1 for o in offers if (o.status if hasattr(o,'status') else o.get('status')) == 'paid'),
    })


# ── SELLER DASHBOARD ──────────────────────────────────────────
@login_required
def seller_dashboard(request):
    offers = _get_offers_for_user(request, request.user)
    def st(o): return o.status if hasattr(o, 'status') else o.get('status')
    return render(request, 'backend/seller-dashboard.html', {
        'offers':   offers,
        'total':    len(offers),
        'pending':  sum(1 for o in offers if st(o) == 'pending'),
        'approved': sum(1 for o in offers if st(o) == 'approved'),
        'paid':     sum(1 for o in offers if st(o) == 'paid'),
    })


# ── ADMIN DASHBOARD ───────────────────────────────────────────
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('backend:user-dashboard')
    all_offers = _get_all_offers(request)
    def st(o): return o.status if hasattr(o, 'status') else o.get('status', 'pending')
    def tot(o): return float(o.total) if hasattr(o, 'total') else float(o.get('total', 0))
    recent_sellers = list(User.objects.all().order_by('-date_joined')[:6])
    for u in recent_sellers:
        u.offer_count = SellerOffer.objects.filter(user=u).count() if USE_DB else 0
    paid_total = sum(tot(o) for o in all_offers if st(o) == 'paid')
    return render(request, 'backend/admin-dashboard.html', {
        'total_sellers':  User.objects.count(),
        'total_offers':   len(all_offers),
        'pending_offers': sum(1 for o in all_offers if st(o) == 'pending'),
        'paid_out':       f"GH₵ {paid_total:,.2f}",
        'recent_offers':  all_offers[:8],
        'recent_sellers': recent_sellers,
    })


# ── ADMIN: ALL SELLERS ────────────────────────────────────────
@login_required
def admin_sellers(request):
    if not request.user.is_staff:
        return redirect('backend:user-dashboard')
    sellers = User.objects.all().order_by('-date_joined')
    return render(request, 'backend/admin-sellers.html', {'sellers': sellers})


# ── ADMIN: ALL OFFERS ─────────────────────────────────────────
@login_required
def admin_offers(request):
    if not request.user.is_staff:
        return redirect('backend:user-dashboard')
    offers = _get_all_offers(request)
    return render(request, 'backend/admin-offers.html', {'offers': offers})


# ── ADMIN: BUYING ITEMS ───────────────────────────────────────
@login_required
def admin_products(request):
    if not request.user.is_staff:
        return redirect('backend:user-dashboard')
    if USE_DB:
        try:
            products = BuyingItem.objects.all().order_by('category', 'name')
            return render(request, 'backend/admin-products.html', {'products': products, 'use_db': True})
        except Exception:
            pass
    return render(request, 'backend/admin-products.html', {'products': _FALLBACK_ITEMS, 'use_db': False})


# ── ADMIN: OFFER DETAIL ───────────────────────────────────────
@login_required
def offer_detail(request, ref):
    if not request.user.is_staff:
        return redirect('backend:user-dashboard')
    offer = None
    if USE_DB:
        try:
            offer = SellerOffer.objects.get(ref=ref)
        except Exception:
            pass
    if not offer:
        all_offers = request.session.get('all_offers', [])
        offer = next((o for o in all_offers if o.get('ref') == ref), None)
    if not offer:
        messages.error(request, 'Offer not found.')
        return redirect('backend:admin-offers')
    return render(request, 'backend/offer-detail.html', {'offer': offer})


# ── UPDATE OFFER STATUS ───────────────────────────────────────
@login_required
def update_offer_status(request, ref):
    if not request.user.is_staff:
        return redirect('backend:user-dashboard')
    if request.method == 'POST':
        new_status = request.POST.get('status', 'pending')
        if USE_DB:
            try:
                SellerOffer.objects.filter(ref=ref).update(status=new_status)
                messages.success(request, f'✅ Offer {ref} updated to {new_status}.')
                return redirect('backend:admin-offers')
            except Exception:
                pass
        # session fallback
        for store_key in ('all_offers', 'user_offers'):
            lst = request.session.get(store_key, [])
            for o in lst:
                if o.get('ref') == ref:
                    o['status'] = new_status
            request.session[store_key] = lst
        request.session.modified = True
        messages.success(request, f'✅ Offer {ref} updated.')
    return redirect('backend:admin-offers')


# ── EDIT PROFILE ──────────────────────────────────────────────
@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name  = request.POST.get('last_name', '').strip()
        new_un = request.POST.get('username', '').strip()
        if new_un and new_un != user.username:
            if User.objects.filter(username=new_un).exclude(pk=user.pk).exists():
                messages.error(request, '❌ Username already taken.')
                return redirect('backend:edit-profile')
            user.username = new_un
        user.email = request.POST.get('email', '').strip()
        user.save()
        messages.success(request, '✅ Profile updated!')
    return render(request, 'backend/edit-profile.html')


# ── CHANGE PASSWORD ───────────────────────────────────────────
@login_required
def change_password(request):
    if request.method == 'POST':
        old  = request.POST.get('old_password', '')
        pw1  = request.POST.get('new_password1', '')
        pw2  = request.POST.get('new_password2', '')
        if not request.user.check_password(old):
            messages.error(request, '❌ Current password is incorrect.')
        elif pw1 != pw2:
            messages.error(request, '❌ New passwords do not match.')
        elif len(pw1) < 6:
            messages.error(request, '❌ Password must be at least 6 characters.')
        else:
            request.user.set_password(pw1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, '✅ Password changed!')
    return render(request, 'backend/change-password.html')


# ── SEND OTP ──────────────────────────────────────────────────
def send_otp(request):
    if request.method == 'POST':
        try:
            data  = json.loads(request.body)
            phone = data.get('phone', '').strip()
        except Exception:
            phone = request.POST.get('phone', '').strip()
        if not phone:
            return JsonResponse({'success': False, 'message': 'Phone required'})
        code = str(random.randint(100000, 999999))
        request.session[f'otp_{phone}'] = code
        print(f"\n📱 OTP for {phone}: {code}\n")
        return JsonResponse({'success': True, 'message': f'Code sent to {phone}', 'dev_code': code})
    return JsonResponse({'success': False})


# ── ADD BUYING ITEM ───────────────────────────────────────────
@login_required
def add_product(request):
    if not request.user.is_staff:
        return redirect('backend:user-dashboard')
    from frontend.views import CATEGORIES
    if request.method == 'POST':
        try:
            from backend.models import BuyingItem
            item = BuyingItem(
                name        = request.POST.get('name', '').strip(),
                category    = request.POST.get('category', ''),
                price       = float(request.POST.get('price', 0)),
                unit        = request.POST.get('unit', 'piece'),
                min_qty     = int(request.POST.get('min_qty', 1)),
                badge       = request.POST.get('badge', ''),
                pct_filled  = int(request.POST.get('pct_filled', 0)),
                description = request.POST.get('description', ''),
                is_active   = 'is_active' in request.POST,
            )
            if 'image' in request.FILES:
                item.image = request.FILES['image']
            item.save()
            messages.success(request, '✅ New buying item added!')
            return redirect('backend:admin-products')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'backend/product-form.html', {'categories': CATEGORIES})


# ── EDIT BUYING ITEM ──────────────────────────────────────────
@login_required
def edit_product(request, pk):
    if not request.user.is_staff:
        return redirect('backend:user-dashboard')
    from frontend.views import CATEGORIES
    from backend.models import BuyingItem
    try:
        product = BuyingItem.objects.get(pk=pk)
    except BuyingItem.DoesNotExist:
        messages.error(request, 'Item not found.')
        return redirect('backend:admin-products')

    if request.method == 'POST':
        product.name        = request.POST.get('name', '').strip()
        product.category    = request.POST.get('category', '')
        product.price       = float(request.POST.get('price', 0))
        product.unit        = request.POST.get('unit', 'piece')
        product.min_qty     = int(request.POST.get('min_qty', 1))
        product.badge       = request.POST.get('badge', '')
        product.pct_filled  = int(request.POST.get('pct_filled', 0))
        product.description = request.POST.get('description', '')
        product.is_active   = 'is_active' in request.POST
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        elif 'clear_image' in request.POST and product.image:
            product.image.delete(save=False)
            product.image = None
        product.save()
        messages.success(request, f'✅ "{product.name}" updated!')
        return redirect('backend:admin-products')

    return render(request, 'backend/product-form.html', {
        'product': product, 'categories': CATEGORIES
    })


# ── DELETE BUYING ITEM ────────────────────────────────────────
@login_required
def delete_product(request, pk):
    if not request.user.is_staff:
        return redirect('backend:user-dashboard')
    if request.method == 'POST':
        try:
            from backend.models import BuyingItem
            item = BuyingItem.objects.get(pk=pk)
            name = item.name
            item.delete()
            messages.success(request, f'🗑 "{name}" deleted.')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('backend:admin-products')


# ── CREATE ADMIN ──────────────────────────────────────────────
@login_required
def create_admin(request):
    if not request.user.is_staff:
        return redirect('backend:user-dashboard')

    if request.method == 'POST':
        first  = request.POST.get('first_name', '').strip()
        last   = request.POST.get('last_name', '').strip()
        uname  = request.POST.get('username', '').strip()
        email  = request.POST.get('email', '').strip()
        pwd1   = request.POST.get('password1', '')
        pwd2   = request.POST.get('password2', '')
        level  = request.POST.get('admin_level', 'staff')

        if pwd1 != pwd2:
            messages.error(request, '❌ Passwords do not match.')
        elif len(pwd1) < 6:
            messages.error(request, '❌ Password must be at least 6 characters.')
        elif User.objects.filter(username=uname).exists():
            messages.error(request, f'❌ Username "{uname}" is already taken.')
        else:
            new_admin = User.objects.create_user(
                username=uname, email=email,
                password=pwd1, first_name=first, last_name=last
            )
            new_admin.is_staff = True
            if level == 'superuser':
                new_admin.is_superuser = True
            new_admin.save()
            messages.success(request, f'✅ Admin account created for {first} {last} (@{uname})!')
            return redirect('backend:create-admin')

    admins = User.objects.filter(is_staff=True).order_by('-date_joined')
    return render(request, 'backend/create-admin.html', {'admins': admins})
