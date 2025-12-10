from django.views.generic import ListView, TemplateView

from apps.models import Payment


class PaymentHistoryListView(ListView):
    model = Payment
    template_name = 'users/payment_history.html'
    context_object_name = 'payment_history'


class ManageSubscriptionListView(TemplateView):
    template_name = 'users/manage_subscription.html'