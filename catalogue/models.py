from django.db import models
import uuid
from django.db.models import *
from account.managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator
from datetime import date
from core.base.models import BaseModel
from django.utils.text import slugify
from core.base.models import BaseModel
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.conf import settings



# ======================================= Product Tag Model =======================================

class CategoryModel(BaseModel):
    """Product categories"""
    name = CharField(max_length=100, unique=True)
    description = TextField(blank=True, null=True)
    image = ImageField(upload_to='categories/', blank=True, null=True)
    is_active = BooleanField(default=True)
    parent = ForeignKey('self', on_delete=CASCADE, blank=True, null=True, related_name='subcategories')
    
    class Meta:
        verbose_name = 'Category'  
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProductModel(BaseModel):
    """Main product model"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    ]
    
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='products')
    category = ForeignKey(CategoryModel, on_delete=SET_NULL, null=True, blank=True, related_name='products')
    name = CharField(max_length=200)
    slug = SlugField(max_length=220, unique=True, blank=True)
    description = TextField()
    price = DecimalField(max_digits=10, decimal_places=2)
    offer_price = DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = PositiveIntegerField(default=0)
    sku = CharField(max_length=50, unique=True, blank=True)
    status = CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_featured = BooleanField(default=False)
    meta_description = CharField(max_length=160, blank=True)
    description_detected_script = TextField(null=True, blank=True)
    # inclusive_tax = DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Price including tax")
    # exclusive_tax = DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Price excluding tax")
    
    # AI generation flags
    ai_generated_name = BooleanField(default=False)
    ai_generated_description = BooleanField(default=False)
    ai_generated_price = BooleanField(default=False)
    ai_generated_category = BooleanField(default=False)
    
    # SEO and additional fields
    views_count = PositiveIntegerField(default=0)
    weight = DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, help_text="Weight in kg")
    dimensions = CharField(max_length=100, blank=True, help_text="L x W x H in cm")


    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            Index(fields=['slug']),
            Index(fields=['status']),
            Index(fields=['category']),
            Index(fields=['user']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while ProductModel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        if not self.sku:
            self.sku = f"PRD-{uuid.uuid4().hex[:8].upper()}"
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if offer price exists"""
        if self.offer_price and self.price > self.offer_price:
            return round(((self.price - self.offer_price) / self.price) * 100, 2)
        return 0
    
    @property
    def is_on_sale(self):
        """Check if product has an active offer"""
        return self.offer_price and self.offer_price < self.price
    
    @property
    def effective_price(self):
        """Get the effective selling price"""
        return self.offer_price if self.is_on_sale else self.price
    
    @property
    def primary_image(self):
        """Get the primary image for the product"""
        images = self.media.exclude(image='').exclude(image__isnull=True)
        return images.filter(is_primary=True).first() or images.first()


class ProductMediaModel(BaseModel):
    """Product media: images and videos"""
    MEDIA_TYPE_CHOICES = [
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    ]
    product = ForeignKey(ProductModel, on_delete=CASCADE, related_name='media')
    media_type = CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    # For images
    image = ImageField(upload_to='products/images/', blank=True, null=True)
    alt_text = CharField(max_length=200, blank=True)
    is_primary = BooleanField(default=False)
    # For videos
    video = FileField(upload_to='products/videos/', blank=True, null=True)
    title = CharField(max_length=200, blank=True)
    duration = PositiveIntegerField(blank=True, null=True, help_text="Duration in seconds")
    thumbnail = ImageField(upload_to='products/video_thumbnails/', blank=True, null=True)
    display_order = PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Product Media'
        verbose_name_plural = 'Product Media'
        ordering = ['display_order', 'created_at']
        indexes = [
            Index(fields=['product', 'is_primary']),
            Index(fields=['product']),
        ]

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.media_type == 'IMAGE' and self.is_primary:
            ProductMediaModel.objects.filter(
                product=self.product, media_type='IMAGE', is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.media_type == 'IMAGE':
            return f"{self.product.name} - Image {self.display_order + 1}"
        else:
            return f"{self.product.name} - Video {self.display_order + 1}"


class ProductReviewModel(BaseModel):
    """Product reviews and ratings"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    product = ForeignKey(ProductModel, on_delete=CASCADE, related_name='reviews')
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='product_reviews')
    rating = PositiveSmallIntegerField(choices=RATING_CHOICES)
    review_text = TextField(blank=True)
    is_verified_purchase = BooleanField(default=False)
    is_approved = BooleanField(default=True)
    helpful_count = PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
        # unique_together = ('product', 'user')  # One review per user per product
        # indexes = [
        #     Index(fields=('product', 'is_approved')),
        #     Index(fields=('rating',)),
        # ]
    
    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.user.mobile}"


class ProductTagModel(BaseModel):
    """Product tags for better searchability"""
    name = CharField(max_length=50, unique=True)
    color = CharField(max_length=7, default='#007bff', help_text="Hex color code")
    
    class Meta:
        verbose_name = 'Product Tag'
        verbose_name_plural = 'Product Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProductTagAssignmentModel(BaseModel):
    """Many-to-many relationship between products and tags"""
    product = ForeignKey(ProductModel, on_delete=CASCADE, related_name='tag_assignments')
    tag = ForeignKey(ProductTagModel, on_delete=CASCADE, related_name='product_assignments')
    
    class Meta:
        verbose_name = 'Product Tag Assignment'
        verbose_name_plural = 'Product Tag Assignments'
        unique_together = ['product', 'tag']
    
    def __str__(self):
        return f"{self.product.name} - {self.tag.name}"


class ProductVariantModel(BaseModel):
    """Product variants (size, color, etc.)"""
    product = ForeignKey(ProductModel, on_delete=CASCADE, related_name='variants')
    name = CharField(max_length=100)  # e.g., "Size", "Color"
    value = CharField(max_length=100)  # e.g., "Large", "Red"
    price_adjustment = DecimalField(max_digits=8, decimal_places=2, default=0)
    stock_quantity = PositiveIntegerField(default=0)
    sku_suffix = CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        ordering = ['name', 'value']
        unique_together = ['product', 'name', 'value']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"
    
    @property
    def effective_price(self):
        """Calculate effective price including variant adjustment"""
        base_price = self.product.effective_price
        return base_price + self.price_adjustment



class Wishlist(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)

class WishlistItem(Model):
    wishlist = ForeignKey(Wishlist, on_delete=CASCADE, related_name='items')
    product = ForeignKey('ProductModel', on_delete=CASCADE)
    added_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'product')

class ProductVisualEmbedding(Model):
    product = OneToOneField(ProductModel, on_delete=CASCADE, related_name='visual_embedding')
    embedding = JSONField(help_text='768-dimensional float array from text-embedding-004')
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Embedding for {self.product.name}"