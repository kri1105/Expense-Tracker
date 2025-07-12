# expenses/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Expense, Category
from .forms import ExpenseForm, UserRegisterForm, UserLoginForm
from django.db.models import Sum
from datetime import datetime, timedelta
from django.http import JsonResponse  
import json

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    today = datetime.today()
    month_start = today.replace(day=1)
    
    # Monthly expenses
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        expense_type='expense',
        date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Monthly income
    monthly_income = Expense.objects.filter(
        user=request.user,
        expense_type='income',
        date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    monthly_balance = monthly_income - monthly_expenses
    
    # Recent transactions
    recent_transactions = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Category-wise expenses for chart
    categories = Category.objects.filter(user=request.user)
    category_data = []
    for category in categories:
        total = Expense.objects.filter(
            user=request.user,
            category=category,
            expense_type='expense',
            date__gte=month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        if total > 0:
            category_data.append({
                'category': category.name,
                'amount': float(total)
            })
    
    context = {
        'monthly_expenses': monthly_expenses,
        'monthly_income': monthly_income,
        'monthly_balance': monthly_balance,  
        'recent_transactions': recent_transactions,
        'category_data': json.dumps(category_data),
    }
    return render(request, 'expenses/dashboard.html', context)


@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'expenses/expenses.html', {'expenses': expenses})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expenses')
    else:
        form = ExpenseForm(request.user)
    return render(request, 'expenses/expense_form.html', {'form': form})

@login_required
def reports(request):
    # Last 6 months data
    months = []
    expense_data = []
    income_data = []
    
    for i in range(6):
        month = datetime.now() - timedelta(days=30*i)
        month_start = month.replace(day=1)
        next_month = month_start + timedelta(days=32)
        next_month = next_month.replace(day=1)
        
        expenses = Expense.objects.filter(
            user=request.user,
            expense_type='expense',
            date__gte=month_start,
            date__lt=next_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        income = Expense.objects.filter(
            user=request.user,
            expense_type='income',
            date__gte=month_start,
            date__lt=next_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        months.append(month.strftime('%b %Y'))
        expense_data.append(float(expenses))
        income_data.append(float(income))
    
    months.reverse()
    expense_data.reverse()
    income_data.reverse()
    
    context = {
        'months': json.dumps(months),
        'expense_data': json.dumps(expense_data),
        'income_data': json.dumps(income_data),
    }
    return render(request, 'expenses/report.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = ExpenseForm(request.user, request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('dashboard')  # Redirect to dashboard after success
    else:
        form = ExpenseForm(request.user)
    
    return render(request, 'expenses/add_transaction.html', {
        'form': form,
        'categories': Category.objects.filter(user=request.user)
    })
# views.py
@login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        try:
            category = Category.objects.get(id=category_id, user=request.user)
            category.delete()
            return JsonResponse({'success': True})
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Category not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Category name cannot be empty'}, status=400)
        if Category.objects.filter(name__iexact=name, user=request.user).exists():
            return JsonResponse({'success': False, 'error': 'Category already exists'}, status=400)
        category = Category.objects.create(name=name, user=request.user)
        return JsonResponse({
            'success': True,
            'category': {'id': category.id, 'name': category.name}
        })
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)