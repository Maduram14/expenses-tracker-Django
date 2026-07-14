import json
from datetime import date
from calendar import month_name

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .models import Expense, Category, Budget
from .forms import ExpenseForm, CategoryForm, BudgetForm, SignUpForm


class CustomLoginView(LoginView):
    template_name = 'tracker/login.html'


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'tracker/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created! You can now log in.')
        return response


@login_required
def dashboard(request):
    today = date.today()
    expenses_qs = Expense.objects.filter(user=request.user)

    # This month's expenses
    this_month_qs = expenses_qs.filter(date__year=today.year, date__month=today.month)
    total_this_month = this_month_qs.aggregate(total=Sum('amount'))['total'] or 0
    total_all_time = expenses_qs.aggregate(total=Sum('amount'))['total'] or 0
    transaction_count = expenses_qs.count()

    # Category breakdown (this month) for pie/doughnut chart
    category_breakdown = (
        this_month_qs.values('category__name', 'category__color')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    category_labels = [c['category__name'] or 'Uncategorized' for c in category_breakdown]
    category_totals = [float(c['total']) for c in category_breakdown]
    category_colors = [c['category__color'] or '#94a3b8' for c in category_breakdown]

    # Last 6 months trend for bar/line chart
    six_months_ago = today.replace(day=1)
    for _ in range(5):
        prev_month = six_months_ago.month - 1 or 12
        prev_year = six_months_ago.year - 1 if six_months_ago.month == 1 else six_months_ago.year
        six_months_ago = six_months_ago.replace(year=prev_year, month=prev_month)

    monthly_trend = (
        expenses_qs.filter(date__gte=six_months_ago)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    trend_labels = [f"{month_name[m['month'].month][:3]} {m['month'].year}" for m in monthly_trend]
    trend_totals = [float(m['total']) for m in monthly_trend]

    # Budget progress for current month
    budget = Budget.objects.filter(
        user=request.user, month__year=today.year, month__month=today.month
    ).first()
    budget_amount = float(budget.amount) if budget else 0
    budget_percent = round((float(total_this_month) / budget_amount) * 100, 1) if budget_amount else None

    recent_expenses = expenses_qs[:8]
    top_category = category_breakdown[0] if category_breakdown else None

    context = {
        'total_this_month': total_this_month,
        'total_all_time': total_all_time,
        'transaction_count': transaction_count,
        'recent_expenses': recent_expenses,
        'category_labels': json.dumps(category_labels),
        'category_totals': json.dumps(category_totals),
        'category_colors': json.dumps(category_colors),
        'trend_labels': json.dumps(trend_labels),
        'trend_totals': json.dumps(trend_totals),
        'budget': budget,
        'budget_amount': budget_amount,
        'budget_percent': budget_percent,
        'top_category': top_category,
        'current_month_label': today.strftime('%B %Y'),
        'has_categories': Category.objects.exists(),
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)

    category_id = request.GET.get('category')
    search = request.GET.get('q')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if search:
        expenses = expenses.filter(title__icontains=search)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    total = expenses.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': expenses,
        'categories': Category.objects.all(),
        'total': total,
        'selected_category': category_id or '',
        'search': search or '',
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'tracker/expense_list.html', context)


@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('dashboard')
    else:
        form = ExpenseForm(initial={'date': date.today()})
    return render(request, 'tracker/expense_form.html', {'form': form, 'title': 'Add Expense'})


@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'tracker/expense_form.html', {'form': form, 'title': 'Edit Expense'})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('expense_list')
    return render(request, 'tracker/expense_confirm_delete.html', {'expense': expense})


@login_required
def category_list(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('category_list')
    else:
        form = CategoryForm()
    categories = Category.objects.annotate(expense_count=Count('expenses'))
    return render(request, 'tracker/category_list.html', {'categories': categories, 'form': form})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
    return redirect('category_list')


@login_required
def budget_set(request):
    today = date.today().replace(day=1)
    budget = Budget.objects.filter(
        user=request.user, month__year=today.year, month__month=today.month
    ).first()
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            b = form.save(commit=False)
            b.user = request.user
            b.save()
            messages.success(request, 'Budget saved.')
            return redirect('dashboard')
    else:
        form = BudgetForm(instance=budget, initial={'month': today})
    return render(request, 'tracker/budget_form.html', {'form': form})
