import json

import stripe
from django.conf import settings
from django.http.response import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, TemplateView

from .models import OrderDetail, Product


# Create your views here.
class PaymentConfirmation(DetailView):
    model = Product
    template_name = 'payment.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super(PaymentConfirmation, self).get_context_data(**kwargs)
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


@csrf_exempt
def create_checkout_session(request, id):
    request_data = json.loads(request.body)
    product = get_object_or_404(Product, pk=id)

    stripe.api_key = settings.STRIPE_API_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email=request_data['email'],
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': request.user
                    },

                    'unit_amount': int(product.price * 100)
                },
                'quantity': 1
            }
        ],
        mode='payment',
        success_url=request.build_absolute_url(
            reverse('success')
        ) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_url(reverse('failed'))
    )

    order = OrderDetail()
    order.customer_email = request_data['email']
    order.product = product
    order.stripe_payment_intent = create_checkout_session['id']
    order.amount = int(product.price)
    order.save()

    print("checkout_session ==============", checkout_session)

    return JsonResponse({'session_id': create_checkout_session})


def payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    print("session ===========", session)
    order = get_object_or_404(OrderDetail, stripe_payment_intent=session_id)
    order.has_paid = True
    order.save()
    print("order ====", order)

    context = {
        'order': order
    }

    return render(request, 'payment_success.html', context)

def product_create(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        product = Product.objects.create(price=amount)

        print("Product ID ========", product)
        return redirect("detail", product.id)

    return render('detail', 'payment_create.html')


def product_edit(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        product.price = amount
        product.save()

        print("Product ID ========", product)
        return redirect("detail", id)
    
    context = {
        "product":product
    }
    
    return render(request, "payment_edit.html", context)


class PaymentFailedView(TemplateView):
    template_name = "payment_failed.html"


class OrderHistoryListView(ListView):
    model = OrderDetail
    template_name = "order_history.html"


# class PaymentSuccessView(TemplateView):
#     template_name = "payments/payment_success.html"

#     def get(self, request, *args, **kwargs):
#         session_id = request.GET.get('session_id')
#         if session_id is None:
#             return HttpResponseNotFound()
        
#         stripe.api_key = settings.STRIPE_SECRET_KEY
#         session = stripe.checkout.Session.retrieve(session_id)
#         print("session ===========", session)
#         order = get_object_or_404(OrderDetail, stripe_payment_intent=session.id)
#         order.has_paid = True
#         order.save()
#         print("order ====", order)
#         return render(request, self.template_name)