import django_filters
from .models import Employee

class EmployeeFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains', label='First Name')
    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains', label='Last Name')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains', label='Email')
    department = django_filters.CharFilter(field_name='department', lookup_expr='icontains', label='Department')
    position = django_filters.CharFilter(field_name='position', lookup_expr='icontains', label='Position')
    hire_date = django_filters.DateFilter(field_name='hire_date', lookup_expr='gte', label='Hire Date (Greater Than or Equal)')

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'department', 'position', 'hire_date']
