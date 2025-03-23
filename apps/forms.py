import re

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.forms import Form, ModelForm, IntegerField
from django.forms.widgets import PasswordInput

from apps.models import User, Order, Product, Stream, Withdraw
from django import forms


class AuthForm(Form):
    phone_number = CharField(max_length=20)
    password = CharField(max_length=20)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        digits_only = re.sub(r"\D", "", phone_number)
        return "+" + digits_only

    def save(self):
        phone_number = self.cleaned_data.get("phone_number")
        password = self.cleaned_data.get("password")

        user = User.objects.create(phone_number=phone_number, password=password)
        return user


class ProfileUpdateForm(Form):
    first_name = CharField(required=False)
    last_name = CharField(required=False)
    district_id = CharField(required=False)
    address = CharField(required=False)
    telegram_id = IntegerField(required=False)
    about = CharField(required=False)

    def update(self, user):
        data = self.cleaned_data
        User.objects.filter(pk=user.id).update(**data)


class CustomPasswordChangeForm(Form):
    old = CharField(required=True, widget=PasswordInput, label="Eski parol")
    new = CharField(required=True, widget=PasswordInput, label="Yangi parol")
    confirm = CharField(required=True, widget=PasswordInput, label="Yangi parolni tasdiqlash")

    def clean(self):
        cleaned_data = super().clean()
        old = cleaned_data.get("old")
        new = cleaned_data.get("new")
        confirm = cleaned_data.get("confirm")

        if new and confirm and new != confirm:
            raise ValidationError("Yangi parol va tasdiqlash paroli mos kelmadi.")

        return cleaned_data

    def clean_new(self):
        new_password = self.cleaned_data.get("new")
        if new_password:
            return new_password
        raise ValidationError("Yangi parol kiritilishi shart.")

    def save(self, user):
        new_password = self.cleaned_data.get("new")
        user.set_password(new_password)
        user.save()


class OrderForm(Form):
    full_name = CharField(max_length=255, required=True)
    phone_number = CharField(max_length=20)
    product_id = IntegerField()

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        digits_only = re.sub(r'\D', '', phone_number)
        return "+" + digits_only

    def save(self, owner):
        product_id = self.cleaned_data.get("product_id")

        # Ensure the product exists
        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise ValidationError("Selected product does not exist.")

        return Order.objects.create(
            owner=owner,
            phone_number=self.cleaned_data["phone_number"],
            product=product,
            full_name=self.cleaned_data["full_name"]
        )


class StreamForm(ModelForm):
    class Meta:
        model = Stream
        fields = ['name', 'discount', 'product', 'owner']
        widgets = {
            'owner': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].required = False
        self.fields['discount'].required = False

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        return discount if discount is not None else 0.0


class WithdrawForm(ModelForm):
    class Meta:
        model = Withdraw
        fields = ['amount', 'payment_method']
        labels = {
            'amount': 'Miqdor (so‘m)',
            'payment_method': 'To‘lov usuli',
        }
