from django.db import models
from django.core import validators


# Create your models here.
class Product(models.Model):
    price = models.DecimalField(verbose_name='price', max_digits=12, decimal_places=2, default=0.00)


class OrderDetail(models.Model):
    customer_email = models.EmailField(verbose_name='Customer Email') # Foreign Key can be User 
    product = models.ForeignKey(to=Product, verbose_name='Product', on_delete=models.PROTECT)
    amount = models.IntegerField(verbose_name='Amount')
    stripe_payment_intent = models.CharField(max_length=200, null=True, blank=True)
    has_paid = models.BooleanField(default=False, verbose_name='Payment Status')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)