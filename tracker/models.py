from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6366f1', help_text='Hex color for charts, e.g. #6366f1')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='expenses')
    date = models.DateField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cash')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.title} - ₹{self.amount}'

    def get_absolute_url(self):
        return reverse('expense_detail', kwargs={'pk': self.pk})


class Budget(models.Model):
    """Optional monthly budget per user, used to show progress on the dashboard."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    month = models.DateField(help_text='Use the 1st day of the month, e.g. 2026-07-01')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'month')
        ordering = ['-month']

    def __str__(self):
        return f'{self.user.username} budget for {self.month.strftime("%B %Y")}'
