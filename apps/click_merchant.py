import hashlib
from decimal import Decimal

import requests
from django.conf import settings


class ClickMerchant:
    """
    Click Merchant API integratsiyasi
    Docs: https://docs.click.uz/
    """

    def __init__(self):
        self.merchant_id = settings.CLICK_MERCHANT_ID
        self.service_id = settings.CLICK_SERVICE_ID
        self.secret_key = settings.CLICK_SECRET_KEY
        self.prepare_url = "https://api.click.uz/v2/merchant/invoice/create"

    def generate_sign_string(self, params):
        """
        Sign string yaratish (MD5 hash)
        """
        # Click dokumentatsiyasiga ko'ra tartib
        sign_string = (
            f"{params.get('click_trans_id', '')}"
            f"{params.get('service_id', '')}"
            f"{self.secret_key}"
            f"{params.get('merchant_trans_id', '')}"
            f"{params.get('amount', '')}"
            f"{params.get('action', '')}"
            f"{params.get('sign_time', '')}"
        )
        return hashlib.md5(sign_string.encode('utf-8')).hexdigest()

    def create_invoice(self, payment):
        """
        To'lov invoce yaratish

        Args:
            payment: Payment model instance

        Returns:
            dict: Response from Click
        """
        payload = {
            "service_id": self.service_id,
            "merchant_id": self.merchant_id,
            "amount": float(payment.amount),
            "transaction_param": str(payment.id),
            "merchant_trans_id": str(payment.id),
            "return_url": settings.CLICK_RETURN_URL,
            "card_type": "UZCARD"  # yoki HUMO
        }

        try:
            response = requests.post(self.prepare_url, json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def verify_sign(self, params):
        """
        Sign string tekshirish
        """
        received_sign = params.get('sign_string', '')
        calculated_sign = self.generate_sign_string(params)
        return received_sign == calculated_sign

    def prepare(self, params):
        """
        PREPARE metodi - to'lovni tekshirish
        Click serveridan birinchi kelgan so'rov
        """
        # Sign tekshirish
        if not self.verify_sign(params):
            return {
                "error": -1,
                "error_note": "Sign check failed"
            }

        # Payment topish
        from .models import Payment

        merchant_trans_id = params.get('merchant_trans_id')
        try:
            payment = Payment.objects.get(id=merchant_trans_id)
        except Payment.DoesNotExist:
            return {
                "error": -5,
                "error_note": "Payment not found"
            }

        # Status tekshirish
        if payment.status == 'completed':
            return {
                "error": -4,
                "error_note": "Already paid"
            }

        # Summani tekshirish
        if Decimal(str(params.get('amount'))) != payment.amount:
            return {
                "error": -2,
                "error_note": "Incorrect amount"
            }

        # Muvaffaqiyatli javob
        return {
            "error": 0,
            "error_note": "Success",
            "click_trans_id": params.get('click_trans_id'),
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": payment.id
        }

    def complete(self, params):
        """
        COMPLETE metodi - to'lovni yakunlash
        Click serveridan ikkinchi kelgan so'rov
        """
        # Sign tekshirish
        if not self.verify_sign(params):
            return {
                "error": -1,
                "error_note": "Sign check failed"
            }

        from datetime import datetime, timedelta

        from users.models import Subscription

        from .models import Payment

        merchant_trans_id = params.get('merchant_trans_id')

        try:
            payment = Payment.objects.get(id=merchant_trans_id)
        except Payment.DoesNotExist:
            return {
                "error": -5,
                "error_note": "Payment not found"
            }

        # To'lovni yakunlash
        if params.get('error') == '0':
            payment.status = 'completed'
            payment.transaction_id = params.get('click_trans_id')
            payment.completed_at = datetime.now()
            payment.metadata = params
            payment.save()

            # Obuna yaratish yoki yangilash
            user = payment.user

            try:
                subscription = Subscription.objects.get(user=user)
                # Mavjud obunani uzaytirish
                if subscription.end_date < datetime.now():
                    subscription.end_date = datetime.now() + timedelta(days=30)
                else:
                    subscription.end_date += timedelta(days=30)
                subscription.is_active = True
                subscription.save()
            except Subscription.DoesNotExist:
                # Yangi obuna yaratish
                subscription = Subscription.objects.create(
                    user=user,
                    subscription_type='monthly',
                    end_date=datetime.now() + timedelta(days=30),
                    price=payment.amount,
                    is_active=True,
                    auto_renew=True
                )

            payment.subscription = subscription
            payment.save()

            return {
                "error": 0,
                "error_note": "Success",
                "click_trans_id": params.get('click_trans_id'),
                "merchant_trans_id": merchant_trans_id,
                "merchant_confirm_id": payment.id
            }
        else:
            # Xato
            payment.status = 'failed'
            payment.save()

            return {
                "error": -9,
                "error_note": "Transaction cancelled"
            }


class ClickAutoPayment:
    """
    Click orqali avtomatik to'lov
    Saqlangan karta orqali har oyda to'lov
    """

    def __init__(self):
        self.merchant_id = settings.CLICK_MERCHANT_ID
        self.service_id = settings.CLICK_SERVICE_ID
        self.secret_key = settings.CLICK_SECRET_KEY
        self.auto_pay_url = "https://api.click.uz/v2/card_token/payment"

    def charge_card(self, payment_method, amount, payment_id):
        """
        Saqlangan kartadan pul yechish

        Args:
            payment_method: PaymentMethod model instance
            amount: To'lov summasi
            payment_id: Payment ID

        Returns:
            dict: Response from Click
        """
        payload = {
            "service_id": self.service_id,
            "merchant_id": self.merchant_id,
            "amount": float(amount),
            "merchant_trans_id": str(payment_id),
            "card_token": payment_method.card_token,  # Saqlangan token
        }

        try:
            response = requests.post(self.auto_pay_url, json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
