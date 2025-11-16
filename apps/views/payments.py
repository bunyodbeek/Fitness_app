# import logging
#
# from apps.click_merchant import ClickMerchant
# from apps.models import Payment
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.shortcuts import redirect, render
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
#
# logger = logging.getLogger(__name__)
#
#
# @csrf_exempt
# @require_POST
# def click_prepare(request):
#     """
#     Click PREPARE callback
#     Click serveridan birinchi so'rov
#     """
#     click = ClickMerchant()
#
#     params = {
#         'click_trans_id': request.POST.get('click_trans_id'),
#         'service_id': request.POST.get('service_id'),
#         'merchant_trans_id': request.POST.get('merchant_trans_id'),
#         'amount': request.POST.get('amount'),
#         'action': request.POST.get('action'),
#         'sign_time': request.POST.get('sign_time'),
#         'sign_string': request.POST.get('sign_string'),
#     }
#
#     logger.info(f"Click PREPARE: {params}")
#
#     response = click.prepare(params)
#     return JsonResponse(response)
#
#
# @csrf_exempt
# @require_POST
# def click_complete(request):
#     """
#     Click COMPLETE callback
#     Click serveridan ikkinchi so'rov - to'lovni yakunlash
#     """
#     click = ClickMerchant()
#
#     params = {
#         'click_trans_id': request.POST.get('click_trans_id'),
#         'service_id': request.POST.get('service_id'),
#         'merchant_trans_id': request.POST.get('merchant_trans_id'),
#         'merchant_prepare_id': request.POST.get('merchant_prepare_id'),
#         'amount': request.POST.get('amount'),
#         'action': request.POST.get('action'),
#         'sign_time': request.POST.get('sign_time'),
#         'sign_string': request.POST.get('sign_string'),
#         'error': request.POST.get('error'),
#         'error_note': request.POST.get('error_note'),
#     }
#
#     logger.info(f"Click COMPLETE: {params}")
#
#     response = click.complete(params)
#     return JsonResponse(response)
#
#
# @login_required
# def subscribe_view(request):
#     """
#     Obuna sotib olish sahifasi
#     """
#     user = request.user
#
#     # Agar allaqachon premium bo'lsa
#     if user.is_premium_active():
#         messages.info(request, "Sizda allaqachon faol obuna bor!")
#         return redirect('users:settings')
#
#     # Premium narxi
#     monthly_price = 67000.00
#
#     context = {
#         'monthly_price': monthly_price,
#     }
#
#     return render(request, 'payments/subscribe.html', context)
#
#
# @login_required
# def create_payment(request):
#     """
#     To'lov yaratish va Click ga yo'naltirish
#     """
#     if request.method == 'POST':
#         user = request.user
#
#         # Payment yaratish
#         payment = Payment.objects.create(
#             user=user,
#             payment_type='subscription_new',
#             amount=67000.00,
#             status='pending'
#         )
#
#         # Click invoice yaratish
#         click = ClickMerchant()
#         response = click.create_invoice(payment)
#
#         if 'invoice_id' in response:
#             # Muvaffaqiyatli - Click ga yo'naltirish
#             payment.transaction_id = response.get('invoice_id')
#             payment.save()
#
#             return redirect(response.get('payment_url'))
#         else:
#             # Xato
#             payment.status = 'failed'
#             payment.save()
#             messages.error(request, "To'lov yaratishda xato yuz berdi!")
#             return redirect('payments:subscribe')
#
#     return redirect('payments:subscribe')
#
#
# @login_required
# def add_card_view(request):
#     """
#     Karta qo'shish sahifasi
#     Click orqali karta tokenizatsiyasi
#     """
#     user = request.user
#
#     # Agar karta allaqachon qo'shilgan bo'lsa
#     if hasattr(user, 'payment_method') and user.payment_method.is_active:
#         messages.info(request, "Sizda allaqachon karta mavjud!")
#         return redirect('users:account_settings')
#
#     return render(request, 'payments/add_card.html')
#
#
# @csrf_exempt
# @require_POST
# def click_card_token_callback(request):
#     """
#     Click card token callback
#     Karta saqlangandan keyin callback
#     """
#     from django.contrib.auth import get_user_model
#     User = get_user_model()
#
#     user_id = request.POST.get('merchant_trans_id')
#     card_token = request.POST.get('card_token')
#     card_number = request.POST.get('card_number')  # Masked
#
#     try:
#         user = User.objects.get(id=user_id)
#
#         # Card last 4 digits
#         card_last_four = card_number[-4:] if len(card_number) >= 4 else card_number
#
#         # PaymentMethod yaratish yoki yangilash
#         payment_method, created = PaymentMethod.objects.update_or_create(
#             user=user,
#             defaults={
#                 'card_token': card_token,
#                 'card_last_four': card_last_four,
#                 'card_type': 'uzcard',  # Yoki HUMO
#                 'expiry_month': request.POST.get('expiry_month', '12'),
#                 'expiry_year': request.POST.get('expiry_year', '2025'),
#                 'is_active': True
#             }
#         )
#
#         logger.info(f"Card token saved for user {user.username}")
#
#         # Agar obuna mavjud bo'lsa, auto_renew ni yoqish
#         if hasattr(user, 'subscription'):
#             user.subscription.auto_renew = True
#             user.subscription.save()
#
#         return JsonResponse({
#             'error': 0,
#             'error_note': 'Success'
#         })
#
#     except Exception as e:
#         logger.error(f"Card token callback error: {str(e)}")
#         return JsonResponse({
#             'error': -1,
#             'error_note': str(e)
#         })
#
#
# @login_required
# def remove_card(request):
#     """
#     Kartani o'chirish
#     """
#     if request.method == 'POST':
#         user = request.user
#
#         try:
#             payment_method = user.payment_method
#             payment_method.is_active = False
#             payment_method.save()
#
#             # Auto-renew ni o'chirish
#             if hasattr(user, 'subscription'):
#                 user.subscription.auto_renew = False
#                 user.subscription.save()
#
#             messages.success(request, "Karta o'chirildi!")
#         except PaymentMethod.DoesNotExist:
#             messages.error(request, "Karta topilmadi!")
#
#     return redirect('users:account_settings')
#
#
# @login_required
# def payment_success(request):
#     """
#     To'lov muvaffaqiyatli bo'lgandan keyin
#     """
#     return render(request, 'payments/success.html')
#
#
# @login_required
# def payment_failed(request):
#     """
#     To'lov muvaffaqiyatsiz bo'lgandan keyin
#     """
#     return render(request, 'payments/failed.html')
