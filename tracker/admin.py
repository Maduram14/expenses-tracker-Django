from django.contrib import admin
from .models import Expense, Category, Budget


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'date', 'user', 'payment_method')
    list_filter = ('category', 'payment_method', 'date')
    search_fields = ('title', 'notes')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'amount')
