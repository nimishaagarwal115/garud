from django.contrib import admin
from account.models import *
from django.contrib.auth import get_user_model

from catalogue.models import *
from orders.models import *
User = get_user_model()

# # Register your models here.
# Admin configuration for user roles
# This class customizes how RoleModel appears in the Django admin interface
@admin.register(RoleModel)
class RoleModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Shows ID and name columns in the list view
    search_fields = ('name',)  # Enables searching by role name

# Admin configuration for language preferences
# Controls how language options appear in the admin interface
@admin.register(LanguagePreferenceModel)
class LanguagePreferenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')  # Shows ID, language name, and language code
    search_fields = ('name', 'code')  # Enables searching by name or language code

# Admin configuration for custom user accounts
# Manages the main user model with authentication details
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile', 'roles', 'language_preference', 'is_active', 'is_staff')  # Shows key user account fields
    search_fields = ('mobile',)  # Enables searching by phone number
    list_filter = ('roles', 'language_preference', 'is_active', 'is_staff')  # Adds filter options in the sidebar
    ordering = ('id',)  # Sorts users by ID by default

# Admin configuration for user profile information
# Manages personal details associated with user accounts
@admin.register(UserProfileModel)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'gender', 'date_of_birth')  # Shows basic profile information
    search_fields = ('full_name', 'user__phone_number')  # Enables searching by name or linked user's phone

# Admin configuration for bank account details
# Manages financial account information for users
@admin.register(BankAccountModel)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'bank_name', 'account_number')  # Shows bank account basics
    search_fields = ('bank_name', 'account_number')  # Enables searching by bank name or account number

# Admin configuration for user addresses
# Manages location/contact information for users
@admin.register(AddressModel)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'village', 'city', 'state')  # Shows address components
    search_fields = ('village', 'city', 'state')  # Enables searching by location fields

# Admin configuration for government identity documents
# Manages official identity information for users
@admin.register(GovernmentDetailsModel)
class GovernmentDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'aadhar_card_number', 'pan_card_number', 'gst_number')  # Shows ID document information
    search_fields = ('aadhar_card_number', 'pan_card_number', 'gst_number')  # Enables searching by document numbers



@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'name': ('name',)}


@admin.register(ProductMediaModel)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'product', 'media_type', 'is_primary', 'display_order', 'image', 'video', 'title', 'duration'
    )
    list_filter = ('media_type', 'is_primary', 'product')
    search_fields = ('product__name', 'title', 'alt_text')
    ordering = ('product', 'display_order')
    readonly_fields = ('thumbnail',)


@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'category', 'price', 'offer_price', 'status', 'created_at')
    list_filter = ('status', 'category', 'ai_generated_name', 'ai_generated_description', 'ai_generated_price', 'ai_generated_category', 'created_at')
    search_fields = ('name', 'description', 'user__phone_number')
    readonly_fields = ('slug', 'ai_generated_name', 'ai_generated_description', 'ai_generated_price', 'ai_generated_category')
    inlines = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'category', 'name', 'slug', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'offer_price', 'stock_quantity')
        }),
        ('AI Generated Flags', {
            'fields': ('ai_generated_name', 'ai_generated_description', 'ai_generated_price', 'ai_generated_category'),
            'classes': ('collapse',)
        }),
        ('Status & SEO', {
            'fields': ('status', 'is_featured', 'meta_description')
        })
    )



@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user__mobile',)
    inlines = []

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    search_fields = ('cart__user__mobile', 'product__name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'transaction_user', 'purpose', 'amount', 'payment_status')
    search_fields = ('user__mobile', 'transaction_user', 'purpose')
    list_filter = ('payment_status',)

@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pg_order_id', 'pg_order_status', 'created_at')
    search_fields = ('user__mobile', 'pg_order_id', 'pg_order_status')
    list_filter = ('pg_order_status', 'created_at')

@admin.register(OrderItemModel)
class OrderItemModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('order__pg_order_id', 'product__name')