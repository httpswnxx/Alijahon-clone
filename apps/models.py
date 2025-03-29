from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import Model, CharField, ForeignKey, DecimalField, ImageField, DateTimeField, CASCADE, TextField, \
    IntegerField, SET_NULL, BigIntegerField, TextChoices, SlugField, FloatField, DateField
from django.utils.text import slugify

from alijahon import settings


class CustomUserManager(UserManager):
    def _create_user(self, phone_number, password, **extra_fields):

        if not phone_number:
            raise ValueError("The given phone number must be set")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)


class BaseSlugify(Model):
    name = CharField(max_length=100)
    slug = CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        original_slug = self.slug
        i = 1
        while self.__class__.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{i}"
            i += 1

        super().save(*args, **kwargs)


class User(AbstractUser):
    class RoleType(TextChoices):
        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'
        OPERATOR = 'operator', 'Operator'

    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    username = None
    phone_number = CharField(max_length=20, unique=True)
    district = ForeignKey('District', on_delete=SET_NULL, null=True, blank=True)
    address = TextField()
    telegram_id = BigIntegerField(unique=True, blank=True, null=True)
    about = TextField(blank=True, null=True)
    role = CharField(max_length=10, choices=RoleType, default=RoleType.USER)
    full_name = CharField(max_length=255, blank=True, null=True)
    profile_image = ImageField(upload_to='profile_images/', blank=True, null=True)
    balance = DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Balans")


class Region(Model):
    name = CharField(max_length=255)


class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey('Region', on_delete=CASCADE)


class Category(BaseSlugify):
    icon = CharField(max_length=255)
    image = ImageField(upload_to='category_images/')

    def __str__(self):
        return self.name


class Product(Model):
    name = CharField(max_length=255)
    slug = SlugField(unique=True, blank=True, null=True)
    category = ForeignKey('Category', on_delete=CASCADE)
    price = DecimalField(max_digits=10, decimal_places=2)
    image = ImageField(upload_to='products/')
    description = TextField()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Wishlist(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    product = ForeignKey('Product', on_delete=CASCADE)


class Thread(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    product = ForeignKey('Product', on_delete=CASCADE)
    discount_sum = DecimalField(max_digits=10, decimal_places=2)
    name = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    visit_count = IntegerField(default=0)


class Order(Model):
    class StatusType(TextChoices):
        NEW = 'new', 'New'
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        CANCELED = 'canceled', 'Canceled'
        READY_TO_ORDER = 'ready_to_order', 'Ready To Order'
        DELIVERING = 'delivering', 'Delivering'
        DELIVERED = 'delivered', 'Delivered'
        NOT_PICK_UP = 'not_pick_up', 'Not Pick Up'
        ARCHIVED = 'archived', 'Archived'

    owner = ForeignKey('User', on_delete=SET_NULL, null=True, blank=True)
    phone_number = CharField(max_length=20)
    ordered_at = DateTimeField(auto_now_add=True)
    thread = ForeignKey('Thread', on_delete=SET_NULL, null=True, blank=True)
    product = ForeignKey('Product', on_delete=CASCADE)
    quantity = IntegerField(default=1)
    status = CharField(max_length=20, choices=StatusType, default=StatusType.NEW)
    full_name = CharField(max_length=255)
    total_sum = DecimalField(max_digits=10, decimal_places=2, default=0)

    send_date = DateTimeField(null=True, blank=True)
    district = ForeignKey('District', on_delete=SET_NULL, null=True, blank=True)
    comment_operator = TextField(blank=True, null=True)

    @property
    def amount(self):
        try:
            if self.product and self.product.price is not None:
                return float(self.quantity) * float(self.product.price)
            return 0.0
        except (AttributeError, TypeError, ValueError) as e:
            print(f"Error calculating amount for order {self.id}: {e}")
            return 0.0


class Payment(Model):
    class StatusType(TextChoices):
        REVIEW = 'review', 'Review'
        COMPLETED = 'completed', 'Completed'
        CANCEL = 'cancel', 'Cancel'

    user = ForeignKey('User', on_delete=CASCADE)
    amount = DecimalField(max_digits=10, decimal_places=2)
    photo = ImageField(upload_to='payment/')
    payment_at = DateTimeField(auto_now_add=True)
    status = CharField(max_length=10, choices=StatusType, default=StatusType.REVIEW)
    description = TextField(blank=True, null=True)


class Stream(Model):
    name = CharField(max_length=255)
    discount = FloatField()
    count = IntegerField(default=0)
    product = ForeignKey('apps.Product', SET_NULL, null=True, related_name='streams')
    owner = ForeignKey('apps.User', CASCADE, related_name='streams')

    class Meta:
        ordering = '-id',

    def __str__(self):
        return self.name


class AdminSetting(Model):
    deliver_price = DecimalField(max_digits=5, decimal_places=0)
    competition_photo = ImageField(upload_to='admin/')
    start = DateField()
    finish = DateField()
    description = RichTextUploadingField()


class Withdraw(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='withdraws')
    amount = DecimalField(max_digits=15, decimal_places=2, verbose_name="Miqdor (so‘m)")
    payment_method = CharField(
        max_length=20,
        choices=[('card', 'Karta'), ('cash', 'Naqd')],
        verbose_name="To‘lov usuli"
    )
    status = CharField(
        max_length=20,
        choices=[('pending', 'Kutilmoqda'), ('approved', 'Tasdiqlangan'), ('rejected', 'Rad etilgan')],
        default='pending',
        verbose_name="Holati"
    )
    created_at = DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")

    def __str__(self):
        return f"{self.user} - {self.amount} so‘m - {self.status}"

    class Meta:
        verbose_name = "To‘lov so‘rovi"
        verbose_name_plural = "To‘lov so‘rovlari"
