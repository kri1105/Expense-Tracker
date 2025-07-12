# expense_tracker/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from expenses import views
from expenses.views import add_transaction

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('expenses/', views.expense_list, name='expenses'),
    path('add-expense/', views.add_expense, name='add-expense'),
    path('reports/', views.reports, name='reports'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('add-transaction/', add_transaction, name='add_transaction'),
    path('add-category/', views.add_category, name='add_category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
]