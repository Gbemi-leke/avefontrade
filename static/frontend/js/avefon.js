/* ============================================================
   AVEFON TRADE LTD — Platform JavaScript
   Requires: jQuery (already bundled)
   ============================================================ */
$(function () {

  /* ── BUYING ITEMS DATA ───────────────────────────────── */
  var ITEMS = [
    {id:1,  cat:'mens',    emoji:'👔', bg:'#EEF1FB', name:"Men's Ankara Long Sleeve Shirts",        price:35,  unit:'/ piece', qty:'Min 20 pcs',  stars:5, pct:78,  badge:'HOT',    color:'gold'},
    {id:2,  cat:'womens',  emoji:'👗', bg:'#FDE8F5', name:"Women's Kaba & Slit Sets (Traditional)", price:80,  unit:'/ set',   qty:'Any qty',     stars:5, pct:62,  badge:'HOT',    color:'gold'},
    {id:3,  cat:'kente',   emoji:'🧣', bg:'#FDF6DC', name:'Authentic Kente Strip Cloth',            price:120, unit:'/ yard',  qty:'Min 10 yards',stars:5, pct:45,  badge:'URGENT', color:'red'},
    {id:4,  cat:'fabric',  emoji:'🧵', bg:'#EEF1FB', name:'Ankara / Holland Wax Print 6-Yard',      price:55,  unit:'/ 6yds',  qty:'Any qty',     stars:4, pct:55,  badge:'',       color:''},
    {id:5,  cat:'mens',    emoji:'🩳', bg:'#EEF1FB', name:"Men's Casual Linen Shorts (Bulk)",       price:22,  unit:'/ piece', qty:'Min 50 pcs',  stars:4, pct:80,  badge:'',       color:''},
    {id:6,  cat:'womens',  emoji:'👘', bg:'#FDE8F5', name:"Women's Wrap Dashiki Dress",             price:45,  unit:'/ piece', qty:'Any qty',     stars:5, pct:70,  badge:'HOT',    color:'gold'},
    {id:7,  cat:'fabric',  emoji:'🪡', bg:'#EEF1FB', name:'Northern Smock / Fugu Fabric',          price:40,  unit:'/ yard',  qty:'Any qty',     stars:4, pct:40,  badge:'NEW',    color:'green'},
    {id:8,  cat:'kente',   emoji:'👒', bg:'#FDF6DC', name:'Kente Accessories — Bags, Hats',        price:25,  unit:'/ piece', qty:'Any qty',     stars:4, pct:50,  badge:'',       color:''},
    {id:9,  cat:'mens',    emoji:'🧥', bg:'#EEF1FB', name:"Men's Batik Short Sleeve Shirts",        price:28,  unit:'/ piece', qty:'Min 30 pcs',  stars:4, pct:65,  badge:'',       color:''},
    {id:10, cat:'womens',  emoji:'🥻', bg:'#FDE8F5', name:"Women's Batik Skirt & Blouse Set",       price:55,  unit:'/ set',   qty:'Any qty',     stars:4, pct:48,  badge:'NEW',    color:'green'},
    {id:11, cat:'fabric',  emoji:'🎀', bg:'#EEF1FB', name:'Polyester Chiffon Fabric (Wholesale)',   price:18,  unit:'/ yard',  qty:'Min 20 yards',stars:3, pct:55,  badge:'',       color:''},
    {id:12, cat:'kente',   emoji:'🏵', bg:'#FDF6DC', name:'Royal Kente Cloth — Full Piece',        price:350, unit:'/ piece', qty:'Any qty',     stars:5, pct:20,  badge:'URGENT', color:'red'},
    {id:13, cat:'mens',    emoji:'👕', bg:'#EEF1FB', name:"Men's Plain Cotton T-Shirts (Bulk)",     price:12,  unit:'/ piece', qty:'Min 100 pcs', stars:3, pct:90,  badge:'',       color:''},
    {id:14, cat:'womens',  emoji:'🧤', bg:'#FDE8F5', name:"Women's Ankara Headwraps (Gele)",        price:15,  unit:'/ piece', qty:'Any qty',     stars:5, pct:85,  badge:'HOT',    color:'gold'},
    {id:15, cat:'fabric',  emoji:'🧶', bg:'#EEF1FB', name:'Pure Cotton Fabric Roll (Wholesale)',    price:30,  unit:'/ yard',  qty:'Min 50 yards',stars:4, pct:35,  badge:'NEW',    color:'green'},
    {id:16, cat:'kente',   emoji:'🧣', bg:'#FDF6DC', name:'Kente Strip — Ashanti Royal Pattern',   price:180, unit:'/ yard',  qty:'Any qty',     stars:5, pct:30,  badge:'URGENT', color:'red'},
  ];

  var currentItem = null;

  /* ── BUILD PRODUCT CARD HTML ─────────────────────────── */
  function buildCard(p) {
    var stars = '★'.repeat(p.stars) + '☆'.repeat(5 - p.stars);
    var badgeHtml = '';
    if (p.badge) {
      var bgMap = { HOT:'#D4AF37', URGENT:'#E53935', NEW:'#2E7D32' };
      var fgMap = { HOT:'#111E4A', URGENT:'#fff',    NEW:'#fff' };
      badgeHtml = '<span class="product-card-badge" style="background:' + bgMap[p.badge] + ';color:' + fgMap[p.badge] + ';position:absolute;top:8px;left:8px;padding:2px 8px;font-size:10px;font-weight:700;border-radius:3px">' + p.badge + '</span>';
    }
    return '<li class="product-card" role="listitem" style="position:relative">' +
      badgeHtml +
      '<button class="product-wishlist" aria-label="Save item" style="position:absolute;top:8px;right:8px;background:#fff;border:1px solid #E0E4EF;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-size:14px;cursor:pointer">🤍</button>' +
      '<div class="product-img-wrap" style="height:150px;display:flex;align-items:center;justify-content:center;background:' + p.bg + ';font-size:54px">' + p.emoji + '</div>' +
      '<div class="product-info" style="padding:12px 12px 0">' +
        '<h3 class="product-name" style="min-height:36px"><a href="#">' + p.name + '</a></h3>' +
        '<div class="product-rating"><div class="stars">' + stars + '</div><span class="review-count" style="font-size:11px;color:#6B7280">(' + p.pct + ' sellers)</span></div>' +
        '<div style="margin-top:6px"><span class="price-label" style="font-size:10px;color:#6B7280;display:block;margin-bottom:2px">We pay up to</span>' +
          '<div class="product-price-row"><span class="price-current">GH₵ ' + p.price + '</span><span style="font-size:11px;color:#6B7280;margin-left:4px">' + p.unit + '</span></div>' +
        '</div>' +
        '<div style="font-size:10px;color:#6B7280;margin-top:3px">📦 ' + p.qty + '</div>' +
        '<div class="av-progress-wrap"><div class="av-progress-label"><span>Stock needed</span><span>' + p.pct + '% filled</span></div><div class="av-progress-bar"><div class="av-progress-fill" style="width:' + p.pct + '%"></div></div></div>' +
      '</div>' +
      '<div class="product-actions">' +
        '<button class="action-btn action-btn-cart av-sell-trigger" data-id="' + p.id + '">🏷 Sell This to Avefon →</button>' +
        '<button class="action-btn action-btn-quick" data-id="' + p.id + '" onclick="avOpenDetail(' + p.id + ')">View Details</button>' +
      '</div>' +
    '</li>';
  }

  /* ── RENDER INTO GRIDS ───────────────────────────────── */
  function renderGrid(selector, list) {
    $(selector).html(list.map(buildCard).join(''));
  }

  /* Fill the page grids */
  renderGrid('#avFlashGrid',   ITEMS.filter(function(p){ return p.badge === 'URGENT' || p.badge === 'HOT'; }).slice(0,6));
  renderGrid('#avFeaturedGrid', ITEMS.filter(function(p){ return p.cat === 'mens' || p.cat === 'womens'; }).slice(0,6));
  renderGrid('#avFabricGrid',  ITEMS.filter(function(p){ return p.cat === 'fabric' || p.cat === 'kente'; }).slice(0,4));

  /* ── OPEN SELL MODAL ─────────────────────────────────── */
  $(document).on('click', '.av-sell-trigger', function(e) {
    e.preventDefault(); e.stopPropagation();
    var id = parseInt($(this).data('id'));
    currentItem = ITEMS.find(function(p){ return p.id === id; });
    if (currentItem) {
      $('#avSellItemName').text(currentItem.name);
      $('#avSellItemPrice').text('We pay up to GH₵ ' + currentItem.price + ' ' + currentItem.unit + ' | ' + currentItem.qty);
      $('#avSellItemField').val(currentItem.name);
    }
    $('#avSellSuccess').hide(); $('#avSellForm').show();
    openModal('sell');
  });

  window.avOpenDetail = function(id) {
    var p = ITEMS.find(function(x){ return x.id === id; });
    if (!p) return;
    currentItem = p;
    $('#avDetailEmoji').text(p.emoji);
    $('#avDetailBg').css('background', p.bg);
    $('#avDetailName').text(p.name);
    $('#avDetailPrice').text('GH₵ ' + p.price + ' ' + p.unit);
    $('#avDetailQty').text(p.qty);
    $('#avDetailPct').text(p.pct + '% of needed stock already submitted');
    $('#avDetailBar').css('width', p.pct + '%');
    var stars = '★'.repeat(p.stars) + '☆'.repeat(5 - p.stars);
    $('#avDetailStars').text(stars);
    $('#avDetailSellBtn').data('id', p.id);
    openModal('detail');
  };

  $(document).on('click', '#avDetailSellBtn', function() {
    closeModal('detail');
    setTimeout(function(){ $('.av-sell-trigger[data-id="' + currentItem.id + '"]').first().trigger('click'); }, 200);
  });

  /* ── MODALS ──────────────────────────────────────────── */
  function openModal(k) {
    $('#av' + k.charAt(0).toUpperCase() + k.slice(1) + 'Modal').addClass('open');
    $('body').css('overflow', 'hidden');
  }
  function closeModal(k) {
    $('#av' + k.charAt(0).toUpperCase() + k.slice(1) + 'Modal').removeClass('open');
    $('body').css('overflow', '');
  }
  window.openModal  = openModal;
  window.closeModal = closeModal;

  $(document).on('click', '.av-overlay', function(e) {
    if ($(e.target).hasClass('av-overlay')) { $(this).removeClass('open'); $('body').css('overflow',''); }
  });
  $(document).on('click', '.av-modal-close', function() {
    $(this).closest('.av-overlay').removeClass('open'); $('body').css('overflow','');
  });
  $(document).on('click', '.av-modal', function(e){ e.stopPropagation(); });

  /* ── AUTH TABS ───────────────────────────────────────── */
  $(document).on('click', '.av-tab', function() {
    var t = $(this).data('tab');
    $(this).closest('.av-tabs').find('.av-tab').removeClass('active');
    $(this).addClass('active');
    if (t === 'login') { $('#avLoginForm').show(); $('#avRegForm').hide(); }
    else               { $('#avLoginForm').hide(); $('#avRegForm').show(); }
  });

  /* Header buttons */
  $(document).on('click', '#avHeaderSignIn', function(e){ e.preventDefault(); openModal('auth'); });
  $(document).on('click', '#avHeaderSell',   function(e){ e.preventDefault(); openModal('auth'); });

  /* ── SEND VERIFICATION CODE ──────────────────────────── */
  $(document).on('click', '.av-vc-btn', function() {
    var $b = $(this), phone = $('#avRegPhone').val().trim();
    if (!phone) { toast('⚠ Please enter your phone number first.', 'error'); return; }
    $b.text('Sending…').prop('disabled', true);
    setTimeout(function() {
      $b.text('Sent ✓').addClass('sent');
      toast('📱 Verification code sent to ' + phone, 'success');
      setTimeout(function(){ $b.text('Resend Code').removeClass('sent').prop('disabled', false); }, 30000);
    }, 1200);
  });

  /* ── LOGIN ───────────────────────────────────────────── */
  $(document).on('click', '#avLoginBtn', function() {
    var u = $('#avLoginUser').val().trim(), p = $('#avLoginPass').val().trim();
    if (!u || !p) { toast('⚠ Enter your phone/email and password.', 'error'); return; }
    setLoading($(this), true);
    setTimeout(function() {
      setLoading($('#avLoginBtn'), false, '🔐 Sign In');
      closeModal('auth');
      toast('👋 Welcome back! You are now signed in.', 'success');
    }, 1500);
  });

  /* ── REGISTER ────────────────────────────────────────── */
  $(document).on('click', '#avRegBtn', function() {
    var ok = $('#avRegName').val() && $('#avRegPhone').val() && $('#avRegEmail').val() && $('#avRegPass').val() && $('#avRegCode').val();
    if (!ok) { toast('⚠ Please fill all fields and verify your phone number.', 'error'); return; }
    if (!$('#avRegTerms').is(':checked')) { toast('⚠ Please accept the Terms of Service.', 'error'); return; }
    setLoading($(this), true);
    setTimeout(function() {
      setLoading($('#avRegBtn'), false, '✅ Create Seller Account');
      closeModal('auth');
      toast('🎉 Account created! You can now sell to Avefon Trade Ltd.', 'success');
    }, 1800);
  });

  /* ── SELL FORM SUBMIT ────────────────────────────────── */
  $(document).on('click', '#avSellSubmit', function() {
    var name  = $('#avBankName').val().trim();
    var bank  = $('#avBank').val();
    var accNo = $('#avAccNum').val().trim();
    var qty   = $('#avSellQty').val().trim();
    var price = $('#avSellPrice').val().trim();
    if (!name || !bank || !accNo || !qty || !price) {
      toast('⚠ Please fill all required fields, including bank details.', 'error'); return;
    }
    setLoading($(this), true);
    setTimeout(function() {
      setLoading($('#avSellSubmit'), false, '📤 Submit Offer to Avefon Trade Ltd');
      $('#avSellForm').fadeOut(300, function(){ $('#avSellSuccess').fadeIn(400); });
      var ref = 'AVF-' + Date.now().toString().slice(-6);
      $('#avRefCode').text(ref);
      toast('✅ Offer submitted! We\'ll be in touch within 24 hours.', 'success');
    }, 2000);
  });

  /* ── WISHLIST TOGGLE ─────────────────────────────────── */
  $(document).on('click', '.product-wishlist', function(e) {
    e.stopPropagation();
    var $b = $(this);
    $b.text($b.text() === '🤍' ? '❤️' : '🤍');
    if ($b.text() === '❤️') toast('❤️ Item saved to your list.', 'info');
  });

  /* ── COUNTDOWN ───────────────────────────────────────── */
  function tick() {
    var now = new Date(), end = new Date(now);
    end.setHours(23,59,59,0);
    var d = Math.max(0, Math.floor((end - now) / 1000));
    var h = Math.floor(d/3600), m = Math.floor((d%3600)/60), s = d%60;
    $('#cdH').text(String(h).padStart(2,'0'));
    $('#cdM').text(String(m).padStart(2,'0'));
    $('#cdS').text(String(s).padStart(2,'0'));
  }
  tick(); setInterval(tick, 1000);

  /* ── BACK TO TOP ─────────────────────────────────────── */
  $(window).on('scroll', function(){ $(this).scrollTop() > 300 ? $('#avTop').addClass('show') : $('#avTop').removeClass('show'); });
  $('#avTop').on('click', function(){ $('html,body').animate({scrollTop:0},500); });

  /* ── TOAST ───────────────────────────────────────────── */
  function toast(msg, type) {
    $('#av-toast').remove();
    var $t = $('<div id="av-toast" class="av-toast t-' + (type||'info') + '">' + msg + '</div>');
    $('body').append($t);
    setTimeout(function(){ $t.addClass('show'); }, 50);
    setTimeout(function(){ $t.removeClass('show'); setTimeout(function(){ $t.remove(); }, 400); }, 3500);
  }
  window.avToast = toast;

  /* ── LOADING STATE ───────────────────────────────────── */
  function setLoading($btn, loading, label) {
    if (loading) {
      $btn.prop('disabled', true).html('<span class="av-spinner"></span> Please wait…');
    } else {
      $btn.prop('disabled', false).html(label || 'Submit');
    }
  }

  /* ── SEARCH ──────────────────────────────────────────── */
  $('#avSearchForm').on('submit', function(e){
    e.preventDefault();
    var q = $(this).find('input[type=search]').val().trim().toLowerCase();
    if (!q) return;
    var results = ITEMS.filter(function(p){ return p.name.toLowerCase().indexOf(q) > -1 || p.cat.toLowerCase().indexOf(q) > -1; });
    if (results.length === 0) { toast('No items found for "' + q + '"', 'info'); return; }
    renderGrid('#avFlashGrid', results.slice(0, 6));
    $('html,body').animate({scrollTop: $('#avFlashSection').offset().top - 80}, 500);
    toast('Showing ' + results.length + ' result(s) for "' + q + '"', 'info');
  });

});
