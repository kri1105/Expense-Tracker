# expenses/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    EXPENSE_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_type = models.CharField(max_length=10, choices=EXPENSE_TYPES, default='expense')

    def __str__(self):
        return f"{self.amount} - {self.category.name} - {self.date}"