from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json, uuid

from backend.models import BuyingItem, SellerOffer

CATEGORIES = [
    ('mens',        "Men's Wear",          '👔', '#EEF1FB'),
    ('womens',      "Women's Clothing",    '👗', '#FDE8F5'),
    ('kente',       'Kente & Traditional', '🧣', '#FDF6DC'),
    ('fabric',      'Fabrics & Textiles',  '🧵', '#EEF1FB'),
    ('accessories', 'Accessories',         '👜', '#FDF6DC'),
    ('wholesale',   'Wholesale Lots',      '📦', '#E8F5E9'),
    ('traditional', 'Traditional Wear',    '🏵', '#FDF6DC'),
    ('smock',       'Smock & Fugu',        '🪡', '#EEF1FB'),
]


def get_items(cat=None, badge=None, q=None):
    qs = BuyingItem.objects.filter(is_active=True)
    if cat:   qs = qs.filter(category=cat)
    if badge: qs = qs.filter(badge=badge)
    if q:     qs = qs.filter(name__icontains=q)
    return qs


def get_item(pk):
    try:
        return BuyingItem.objects.get(pk=pk, is_active=True)
    except BuyingItem.DoesNotExist:
        return None


# ── INDEX ─────────────────────────────────────────────────────
def index(request):
    return render(request, 'frontend/index.html', {
        'categories':     CATEGORIES,
        'urgent_items':   get_items(badge='URGENT')[:6],
        'featured_items': get_items()[:8],
        'fabric_items':   BuyingItem.objects.filter(is_active=True, category__in=['fabric','kente'])[:6],
    })


# ── PRODUCT LISTING ───────────────────────────────────────────
def product_listing(request, category=None):
    cat   = category or request.GET.get('cat', '')
    badge = request.GET.get('badge', '')
    q     = request.GET.get('q', '')
    items = get_items(cat=cat or None, badge=badge or None, q=q or None)
    return render(request, 'frontend/product-listing.html', {
        'items': items, 'categories': CATEGORIES,
        'active_cat': cat, 'query': q, 'badge_filter': badge,
    })


# ── PRODUCT DETAIL ────────────────────────────────────────────
def product_detail(request, pk):
    item = get_item(pk)
    if not item:
        messages.error(request, 'Item not found.')
        return redirect('frontend:product-listing')
    related = BuyingItem.objects.filter(is_active=True, category=item.category).exclude(pk=pk)[:4]
    return render(request, 'frontend/product-detail.html', {
        'item': item, 'related': related, 'categories': CATEGORIES,
    })


# ── SELL OFFER ────────────────────────────────────────────────
def sell_offer(request, item_pk=None):
    item = get_item(item_pk) if item_pk else None
    if request.method == 'POST':
        qty   = request.POST.get('quantity', '1')
        price = request.POST.get('asking_price', '0')
        try:    total = float(qty) * float(price)
        except: total = 0
 
        # Handle custom bank name
        bank_name = request.POST.get('bank_name', '')
        if bank_name == '__other__':
            bank_name = request.POST.get('bank_name_custom', '').strip()
 
        offer = SellerOffer.objects.create(
            user           = request.user if request.user.is_authenticated else None,
            seller_name    = request.POST.get('seller_name', ''),
            seller_phone   = request.POST.get('seller_phone', ''),
            seller_email   = request.POST.get('seller_email', ''),
            item           = item,
            item_name      = request.POST.get('item_name', item.name if item else ''),
            quantity       = int(qty),
            asking_price   = float(price),
            condition      = request.POST.get('condition', 'Brand New'),
            description    = request.POST.get('description', ''),
            bank_name      = bank_name,
            account_name   = request.POST.get('account_name', ''),
            account_number = request.POST.get('account_number', ''),
            branch         = request.POST.get('branch', ''),
            location       = request.POST.get('location', ''),
        )
        request.session['last_offer'] = {
            'ref':         offer.ref,
            'item_name':   offer.item_name,
            'seller_name': offer.seller_name,
            'bank':        offer.bank_name,
            'qty':         qty,
            'price':       price,
            'total':       f"{total:.2f}",
        }
        messages.success(request, f'✅ Offer submitted! Reference: {offer.ref}')
        return redirect('frontend:offer-success', ref=offer.ref)
 
    return render(request, 'frontend/sell-offer.html', {
        'item': item, 'categories': CATEGORIES,
    })
 
 
def offer_success(request, ref):
    offer = request.session.get('last_offer', {'ref': ref})
    return render(request, 'frontend/offer-success.html', {
        'offer': offer, 'categories': CATEGORIES,
    })

# ── AUTH ──────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('backend:user-dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'👋 Welcome back, {user.first_name or user.username}!')
            nxt = request.GET.get('next', '')
            return redirect(nxt if nxt else 'backend:user-dashboard')
        messages.error(request, '❌ Invalid username or password.')
    return render(request, 'frontend/login.html', {'categories': CATEGORIES})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('frontend:index')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('backend:user-dashboard')
    if request.method == 'POST':
        first = request.POST.get('first_name', '').strip()
        last  = request.POST.get('last_name', '').strip()
        uname = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        pwd1  = request.POST.get('password1', '')
        pwd2  = request.POST.get('password2', '')
        if pwd1 != pwd2:
            messages.error(request, '❌ Passwords do not match.')
        elif User.objects.filter(username=uname).exists():
            messages.error(request, '❌ Username already taken.')
        elif len(pwd1) < 6:
            messages.error(request, '❌ Password must be at least 6 characters.')
        else:
            user = User.objects.create_user(username=uname, email=email,
                password=pwd1, first_name=first, last_name=last)
            login(request, user)
            messages.success(request, f'🎉 Welcome {first}! Your account is ready.')
            return redirect('backend:user-dashboard')
    return render(request, 'frontend/register.html', {'categories': CATEGORIES})


def vendor_register(request):
    if request.method == 'POST':
        first = request.POST.get('first_name', '').strip()
        last  = request.POST.get('last_name', '').strip()
        uname = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        pwd1  = request.POST.get('password1', '')
        pwd2  = request.POST.get('password2', '')
        otp   = request.POST.get('otp_code', '').strip()

        # Normalise phone for session key lookup
        phone_key = phone.replace(' ', '').replace('-', '')
        if phone_key.startswith('0'):
            phone_key = '+233' + phone_key[1:]
        elif not phone_key.startswith('+'):
            phone_key = '+' + phone_key

        saved_otp = request.session.get(f'otp_{phone_key}', '')

        if not otp or not saved_otp:
            messages.error(request, '❌ Please request and enter your verification code.')
        elif otp != saved_otp:
            messages.error(request, '❌ Incorrect verification code. Please try again.')
        elif pwd1 != pwd2:
            messages.error(request, '❌ Passwords do not match.')
        elif User.objects.filter(username=uname).exists():
            messages.error(request, '❌ Username already taken.')
        elif len(pwd1) < 6:
            messages.error(request, '❌ Password must be at least 6 characters.')
        else:
            user = User.objects.create_user(username=uname, email=email,
                password=pwd1, first_name=first, last_name=last)
            login(request, user)
            # Clear OTP from session
            request.session.pop(f'otp_{phone_key}', None)
            messages.success(request, f'🎉 Seller account created! Welcome {first}.')
            return redirect('backend:seller-dashboard')
    return render(request, 'frontend/vendor-register.html', {'categories': CATEGORIES})


# ── OTHER PAGES ───────────────────────────────────────────────
def wishlist(request):
    return render(request, 'frontend/wishlist.html', {'categories': CATEGORIES})

def cart(request):
    return render(request, 'frontend/cart.html', {'categories': CATEGORIES})

def checkout(request):
    return render(request, 'frontend/checkout.html', {'categories': CATEGORIES})

def order_tracking(request):
    return render(request, 'frontend/order-tracking.html', {'categories': CATEGORIES})


# ── PRIVACY POLICY ────────────────────────────────────────────
def privacy_policy(request):
    sections = [
        {'title': 'Information We Collect', 'content': '<p>When you register or use our platform, we may collect:</p><ul style="padding-left:20px;margin:10px 0"><li style="margin-bottom:6px"><strong>Personal Identity:</strong> Full name, username, phone number, email address</li><li style="margin-bottom:6px"><strong>Financial Information:</strong> Bank account name, account number, branch, and mobile money details (used solely to process payments to you)</li><li style="margin-bottom:6px"><strong>Business Information:</strong> Seller type, location/address, clothing items you wish to sell</li><li style="margin-bottom:6px"><strong>Usage Data:</strong> Pages visited, offers submitted, device type, browser information</li><li style="margin-bottom:6px"><strong>Communications:</strong> Messages sent via WhatsApp or our contact form</li></ul>'},
        {'title': 'How We Use Your Information', 'content': '<p>We use the information we collect to:</p><ul style="padding-left:20px;margin:10px 0"><li style="margin-bottom:6px">Process and manage your clothing sale offers</li><li style="margin-bottom:6px">Transfer payments to your bank account or mobile money wallet</li><li style="margin-bottom:6px">Verify your identity as a seller on our platform</li><li style="margin-bottom:6px">Send you notifications about your offer status</li><li style="margin-bottom:6px">Improve our platform and services</li><li style="margin-bottom:6px">Prevent fraud, abuse, and unauthorized access</li></ul><p style="margin-top:10px">We do <strong>not</strong> sell, rent, or trade your personal information to third parties for marketing purposes.</p>'},
        {'title': 'Payment Information & Security', 'content': '<p>Your bank account and mobile money details are collected solely for the purpose of paying you for goods purchased by Avefon Trade Ltd.</p><ul style="padding-left:20px;margin:10px 0"><li style="margin-bottom:6px">All data is transmitted over encrypted HTTPS connections</li><li style="margin-bottom:6px">Payment details are accessible only to authorized Avefon staff</li><li style="margin-bottom:6px">Payments are processed directly through Ghanaian banks and Mobile Money networks</li></ul><p style="margin-top:10px;background:#FEF3C7;padding:10px;border-radius:6px;font-weight:600;color:#92400E">⚠ Avefon Trade Ltd will never ask for your ATM PIN, internet banking password, or OTP. Please report any suspicious requests immediately.</p>'},
        {'title': 'Phone Verification & OTP', 'content': '<p>To register as a seller, we require phone number verification via a One-Time Password (OTP). OTP codes are valid for 10 minutes and are never stored after use.</p>'},
        {'title': 'Data Sharing', 'content': '<p>We only share your data with Ghanaian banks and Mobile Money providers (GCB, Ecobank, MTN MoMo, Vodafone Cash, AirtelTigo) solely to complete your payment, or when required by Ghanaian law.</p>'},
        {'title': 'Data Retention', 'content': '<p>We retain your personal information for as long as your account is active, or as required by Ghanaian tax and financial regulations (typically 7 years). You may request deletion by contacting lixuwu61@gmail.com</p>'},
        {'title': 'Your Rights', 'content': '<p>You have the right to access, correct, delete, or export your personal data. Contact us at lixuwu61@gmail.com to exercise these rights.</p>'},
        {'title': 'Cookies & Tracking', 'content': '<p>Our website uses cookies to keep you logged in and understand how visitors use our website. You can control cookies through your browser settings.</p>'},
        {'title': 'Changes to This Policy', 'content': '<p>We may update this Privacy Policy from time to time. We will notify you of significant changes by posting the new policy on this page with an updated date.</p>'},
    ]
    return render(request, 'frontend/privacy-policy.html', {
        'categories': CATEGORIES, 'sections': sections,
        'last_updated': 'May 2025',
    })
 
 
def terms_conditions(request):
    terms = [
        ('1', 'Acceptance of Terms', '''
            <p>By creating an account, submitting an offer, or otherwise using the Avefon Trade Ltd platform, you confirm that you:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Are at least 18 years of age</li>
              <li style="margin-bottom:6px">Have the legal capacity to enter into a binding agreement</li>
              <li style="margin-bottom:6px">Are the legal owner of, or are authorised to sell, the clothing items you submit</li>
              <li style="margin-bottom:6px">Agree to comply with all applicable laws of the Republic of Ghana</li>
            </ul>
        '''),
        ('2', 'Platform Description', '''
            <p>Avefon Trade Ltd is a clothing procurement platform that:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Posts a buying list of clothing items Avefon wishes to purchase</li>
              <li style="margin-bottom:6px">Allows registered sellers to submit offers to sell those items</li>
              <li style="margin-bottom:6px">Reviews submitted offers and pays approved sellers within 24 hours of goods receipt</li>
            </ul>
            <p style="margin-top:10px"><strong>Avefon is a buyer, not a marketplace.</strong> We do not resell goods on behalf of sellers.</p>
        '''),
        ('3', 'Seller Obligations', '''
            <p>As a seller on our platform, you agree to:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Provide accurate, complete, and truthful information about items you wish to sell</li>
              <li style="margin-bottom:6px">Only submit offers for items you legally own and have the right to sell</li>
              <li style="margin-bottom:6px">Deliver goods in the exact condition described in your offer</li>
              <li style="margin-bottom:6px">Provide valid bank account or mobile money details for payment</li>
              <li style="margin-bottom:6px">Not submit counterfeit, stolen, or illegally obtained goods</li>
              <li style="margin-bottom:6px">Comply with all delivery arrangements agreed with Avefon</li>
            </ul>
        '''),
        ('4', 'Offer & Acceptance Process', '''
            <ol style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:8px"><strong>Submission:</strong> You submit an offer via our platform with item details, quantity, price, and payment information</li>
              <li style="margin-bottom:8px"><strong>Review:</strong> Our team reviews your offer within 24-48 hours</li>
              <li style="margin-bottom:8px"><strong>Approval:</strong> If approved, we contact you to arrange delivery of goods</li>
              <li style="margin-bottom:8px"><strong>Inspection:</strong> Goods are inspected upon receipt at our warehouse</li>
              <li style="margin-bottom:8px"><strong>Payment:</strong> Payment is transferred to your account within 24 hours of successful inspection</li>
            </ol>
            <p style="margin-top:10px;background:#FEF3C7;padding:10px;border-radius:6px;color:#92400E;font-weight:600">⚠ Avefon reserves the right to reject any offer at its sole discretion without obligation to provide reasons.</p>
        '''),
        ('5', 'Pricing & Payment', '''
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Prices listed on our buying list represent the maximum we are willing to pay per unit</li>
              <li style="margin-bottom:6px">Final payment may differ based on actual quantity, condition, and quality of goods received</li>
              <li style="margin-bottom:6px">Payment is made in <strong>Ghana Cedis (GH₵)</strong> only</li>
              <li style="margin-bottom:6px">Avefon is not responsible for delays caused by incorrect bank details provided by the seller</li>
              <li style="margin-bottom:6px">Payments are processed via GCB Bank, Ecobank, MTN MoMo, Vodafone Cash, or AirtelTigo</li>
            </ul>
        '''),
        ('6', 'Prohibited Activities', '''
            <p>You may not use our platform to:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Submit fraudulent, misleading, or false offers</li>
              <li style="margin-bottom:6px">Sell stolen, counterfeit, or illegally obtained goods</li>
              <li style="margin-bottom:6px">Create multiple accounts to circumvent restrictions</li>
              <li style="margin-bottom:6px">Attempt to hack, disrupt, or damage our platform</li>
              <li style="margin-bottom:6px">Impersonate Avefon staff or other sellers</li>
              <li style="margin-bottom:6px">Use our platform for any illegal purpose under Ghanaian law</li>
            </ul>
            <p style="margin-top:10px">Violations may result in immediate account termination and legal action.</p>
        '''),
        ('7', 'Intellectual Property', '''
            <p>All content on the Avefon Trade Ltd platform — including the logo, brand name, text, images, and design — is the property of Avefon Trade Ltd and is protected by Ghanaian copyright law. You may not copy, reproduce, or distribute our content without written permission.</p>
        '''),
        ('8', 'Limitation of Liability', '''
            <p>To the maximum extent permitted by Ghanaian law, Avefon Trade Ltd shall not be liable for:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Loss of profit, revenue, or business arising from use of our platform</li>
              <li style="margin-bottom:6px">Delays in payment caused by banking system failures or force majeure events</li>
              <li style="margin-bottom:6px">Goods lost or damaged during delivery by the seller</li>
              <li style="margin-bottom:6px">Indirect or consequential losses of any kind</li>
            </ul>
            <p style="margin-top:10px">Our total liability in any dispute shall not exceed the value of the specific transaction in question.</p>
        '''),
        ('9', 'Account Termination', '''
            <p>Avefon Trade Ltd reserves the right to suspend or terminate your account if:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">You violate these Terms and Conditions</li>
              <li style="margin-bottom:6px">We suspect fraudulent activity on your account</li>
              <li style="margin-bottom:6px">You provide false information during registration or offer submission</li>
              <li style="margin-bottom:6px">You engage in abusive, threatening, or offensive behaviour toward our staff</li>
            </ul>
        '''),
        ('10', 'Governing Law & Disputes', '''
            <p>These Terms and Conditions are governed by the laws of the <strong>Republic of Ghana</strong>. Any disputes arising from your use of our platform shall be resolved through:</p>
            <ol style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">First, good-faith negotiation between the parties</li>
              <li style="margin-bottom:6px">If unresolved, mediation through an agreed mediator in Accra, Ghana</li>
              <li style="margin-bottom:6px">If still unresolved, the courts of Ghana shall have exclusive jurisdiction</li>
            </ol>
        '''),
    ]
    return render(request, 'frontend/terms-conditions.html', {
        'categories': CATEGORIES, 'terms': terms
    })

def seller_agreement(request):
    clauses = [
        ('1.0', 'Parties to This Agreement', '''
            <p>This Seller Agreement is entered into between:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px"><strong>Avefon Trade Ltd</strong> — a clothing procurement company registered and operating in Accra, Ghana ("the Buyer")</li>
              <li style="margin-bottom:6px"><strong>The Registered Seller</strong> — the individual or business entity who creates an account and submits offers on our platform ("the Seller")</li>
            </ul>
        '''),
        ('2.0', 'Seller Eligibility', '''
            <p>To sell on Avefon Trade Ltd, you must:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Be at least 18 years of age</li>
              <li style="margin-bottom:6px">Hold a valid Ghanaian identity document (Ghana Card, Passport, or Voter ID)</li>
              <li style="margin-bottom:6px">Have a valid bank account or registered mobile money wallet in Ghana</li>
              <li style="margin-bottom:6px">Verify your phone number via OTP during registration</li>
              <li style="margin-bottom:6px">Be the legal owner of the goods you submit for sale</li>
            </ul>
        '''),
        ('3.0', 'What Avefon Buys', '''
            <p>Avefon Trade Ltd purchases new, quality clothing items including but not limited to:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Men's and Women's clothing (Ankara, batik, casual, formal)</li>
              <li style="margin-bottom:6px">Kente cloth and traditional Ghanaian fabrics</li>
              <li style="margin-bottom:6px">Ankara and Holland wax print fabrics</li>
              <li style="margin-bottom:6px">Traditional wear — Smock, Fugu, Dashiki, Kaba & Slit</li>
              <li style="margin-bottom:6px">Accessories — headwraps, fabric bags, hats</li>
              <li style="margin-bottom:6px">Wholesale and bulk clothing lots</li>
            </ul>
            <p style="margin-top:10px;background:#FEF3C7;padding:10px;border-radius:6px;color:#92400E;font-size:12px">
              ⚠ Avefon does not purchase used clothing, electronics, or non-clothing items. Any such submissions will be automatically rejected.
            </p>
        '''),
        ('4.0', 'Offer Submission', '''
            <p>When submitting an offer, the Seller agrees to:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Accurately describe the item, including fabric type, quantity, condition, and size range</li>
              <li style="margin-bottom:6px">Upload clear photographs of the actual items being offered</li>
              <li style="margin-bottom:6px">State a fair asking price per unit in Ghana Cedis (GH₵)</li>
              <li style="margin-bottom:6px">Provide complete and correct bank/mobile money payment details</li>
              <li style="margin-bottom:6px">Be available for contact within 48 hours of submission</li>
            </ul>
            <p style="margin-top:10px">Avefon reserves the right to counter-offer a lower price, which the Seller may accept or decline.</p>
        '''),
        ('5.0', 'Delivery of Goods', '''
            <p>Upon offer approval, the Seller agrees to deliver goods as follows:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px"><strong>Method 1 — Drop-off:</strong> Deliver goods to Avefon's warehouse at the agreed address in Accra</li>
              <li style="margin-bottom:6px"><strong>Method 2 — Pickup:</strong> Avefon arranges pickup from the Seller's location (available for bulk orders)</li>
              <li style="margin-bottom:6px">Goods must be properly packed and labelled with the offer reference number</li>
              <li style="margin-bottom:6px">Delivery must be completed within <strong>7 days</strong> of offer approval unless otherwise agreed</li>
            </ul>
            <p style="margin-top:10px">Risk of loss or damage during delivery remains with the Seller until goods are received and inspected by Avefon.</p>
        '''),
        ('6.0', 'Inspection & Quality Check', '''
            <p>Upon receipt of goods, Avefon Trade Ltd will:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Inspect all items within <strong>24 hours</strong> of receipt</li>
              <li style="margin-bottom:6px">Verify quantity, condition, and quality against the submitted offer</li>
              <li style="margin-bottom:6px">Accept items that match the offer description</li>
              <li style="margin-bottom:6px">Return items that do not meet the agreed specifications at the Seller's cost</li>
            </ul>
            <p style="margin-top:10px">If only part of a delivery meets quality standards, Avefon will pay for the accepted portion only.</p>
        '''),
        ('7.0', 'Payment Terms', '''
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Payment will be made within <strong>24 hours</strong> of successful inspection and acceptance of goods</li>
              <li style="margin-bottom:6px">Payment will be transferred to the bank account or mobile money number provided in the offer</li>
              <li style="margin-bottom:6px">All payments are in <strong>Ghana Cedis (GH₵)</strong></li>
              <li style="margin-bottom:6px">Avefon is not responsible for delays caused by incorrect payment details</li>
              <li style="margin-bottom:6px">Payment confirmation will be sent via WhatsApp or SMS to the Seller's registered number</li>
            </ul>
            <div style="background:#D1FAE5;border-radius:6px;padding:10px;margin-top:10px">
              <p style="font-size:12px;color:#065F46;margin:0;font-weight:600">✅ We pay fast — our commitment is payment within 24 hours of receiving your goods.</p>
            </div>
        '''),
        ('8.0', 'Fraud & Misrepresentation', '''
            <p>The Seller warrants that all goods offered are:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Legitimately owned by the Seller</li>
              <li style="margin-bottom:6px">Not stolen, counterfeit, or illegally obtained</li>
              <li style="margin-bottom:6px">Accurately described in the offer</li>
            </ul>
            <p style="margin-top:10px">Avefon reserves the right to report suspected fraud to Ghana Police Service. Any Seller found to have submitted fraudulent offers will be permanently banned and may face legal prosecution under the laws of Ghana.</p>
        '''),
        ('9.0', 'Confidentiality', '''
            <p>Both parties agree to keep confidential any pricing information, business processes, or proprietary information shared during the course of this agreement. The Seller may not share Avefon's buying prices or processes with competitors.</p>
        '''),
        ('10.0', 'Termination', '''
            <p>Either party may terminate this agreement at any time. Avefon may immediately suspend or terminate a Seller account for:</p>
            <ul style="padding-left:20px;margin:10px 0">
              <li style="margin-bottom:6px">Breach of this agreement</li>
              <li style="margin-bottom:6px">Fraudulent activity</li>
              <li style="margin-bottom:6px">Repeated non-delivery after offer approval</li>
              <li style="margin-bottom:6px">Abusive behaviour toward Avefon staff</li>
            </ul>
            <p style="margin-top:10px">Any pending payments owed to the Seller at time of termination will still be honoured if goods were received and accepted.</p>
        '''),
    ]
    return render(request, 'frontend/seller-agreement.html', {
        'categories': CATEGORIES, 'clauses': clauses
    })


# ── HELP CENTER ───────────────────────────────────────────────
def help_center(request):
    faqs = [
        {'q': 'How do I submit an offer to sell my clothes?',
         'a': 'Go to any item on our buying list and click "Sell This to Us". Fill in your item details, quantity, asking price, and bank/MoMo payment details. Once submitted, you will receive a reference number. Our team will contact you within 24 hours.'},
        {'q': 'How long does it take to get paid?',
         'a': 'Payment is made within <strong>24 hours</strong> of goods being received and inspected at our warehouse. You will receive an SMS/WhatsApp confirmation once the transfer is made.'},
        {'q': 'What items does Avefon Trade Ltd buy?',
         'a': 'We buy Men and Womens clothing (Ankara, Batik, Dashiki), Kente cloth, traditional fabrics, Smock & Fugu, wholesale lots, and accessories. We only buy new or brand-new items. We do not buy used clothing or non-clothing items.'},
        {'q': 'How do I deliver my goods to Avefon?',
         'a': 'After your offer is approved, you can either: (1) Drop off your goods at our warehouse in Accra, or (2) We arrange pickup from your location for bulk orders. Our team will contact you via WhatsApp to coordinate delivery.'},
        {'q': 'My offer status is still Pending — what should I do?',
         'a': 'Offers are typically reviewed within 24–48 hours. If your offer has been pending for more than 48 hours, please contact us on WhatsApp with your reference number and we will look into it immediately.'},
        {'q': 'Can I submit an offer without registering?',
         'a': 'Yes, you can submit an offer as a guest. However, registering gives you access to your dashboard where you can track all your offers and their payment status.'},
        {'q': 'What if I entered the wrong bank details?',
         'a': 'Contact us immediately on WhatsApp with your reference number. If payment has not yet been processed, we can update your details. Avefon is not responsible for payments sent to incorrect details provided by the seller.'},
        {'q': 'How do I track my offer?',
         'a': 'Log in to your dashboard at <strong>Dashboard → My Offers</strong> to see the status of all your submitted offers. You can also contact us on WhatsApp with your reference number (e.g. AVF-XXXXXX).'},
        {'q': 'Is my personal and bank information safe?',
         'a': 'Yes. All data is transmitted over encrypted HTTPS. Your bank details are only accessible to authorised Avefon staff for payment processing. We will never ask for your ATM PIN or internet banking password. Read our <a href="/privacy-policy/" style="color:#1B2D6B;font-weight:600">Privacy Policy</a> for more details.'},
        {'q': 'How do I register as a seller?',
         'a': 'Click "Register as Seller" in the top navigation. Fill in your name, phone number (required for OTP verification), email, and create a password. Once verified, you can immediately start submitting offers.'},
    ]
    return render(request, 'frontend/help-center.html', {
        'categories': CATEGORIES,
        'faqs': faqs,
    })