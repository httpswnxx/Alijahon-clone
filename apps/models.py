from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import Model, CharField, ForeignKey, DecimalField, ImageField, DateTimeField, CASCADE, TextField, \
    IntegerField, SET_NULL, BigIntegerField, TextChoices, SlugField


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




class Region(Model):
    name = CharField(max_length=255)


class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey('Region', on_delete=CASCADE)


class Category(Model):
    name = CharField(max_length=255)
    icon = CharField(max_length=255)
    image = ImageField(upload_to='category_images/', null=True, blank=True)
    slug = SlugField(unique=True)

class Product(Model):
    name = CharField(max_length=255)
    description = TextField()
    price = DecimalField(max_digits=10, decimal_places=2)
    image = ImageField(upload_to='products/')
    category = ForeignKey('Category', on_delete=CASCADE)

    class Meta:
        ordering = ['name']


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

    owner = ForeignKey('User', on_delete=SET_NULL, null=True, blank=True)
    phone_number = CharField(max_length=20)
    ordered_at = DateTimeField(auto_now_add=True)
    thread = ForeignKey('Thread', on_delete=SET_NULL, null=True, blank=True)
    product = ForeignKey('Product', on_delete=CASCADE)
    quantity = IntegerField(default=1)
    status = CharField(max_length=20, choices=StatusType, default=StatusType.NEW)


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
