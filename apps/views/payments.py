from django.views.generic import ListView

from apps.models import Payment


class PaymentHistoryListView(ListView):
    model = Payment
    template_name = 'users/payment_history.html'
    context_object_name = 'payment_history'