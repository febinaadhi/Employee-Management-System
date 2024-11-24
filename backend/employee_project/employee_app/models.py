from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _  # For verbose names


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)

    # Specify custom related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group', related_name='customuser_set', blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='customuser_permissions_set', blank=True
    )

    def __str__(self):
        return self.username


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="employee_profile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'models_employee'  # Custom database table name
        verbose_name = _('employee')  # Singular verbose name
        verbose_name_plural = _('employees')  # Plural verbose name
        ordering = ('-hire_date',)  # Default ordering: newest hire_date first

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position}"



# Model to store dynamic form structure (forms)
class Form(models.Model):
    title = models.CharField(max_length=200)  # Form title

    def __str__(self):
        return self.title


# Model to store dynamic form sections
class FormSection(models.Model):
    form = models.ForeignKey(Form, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)  # Section title (e.g., "Personal Information")
    order = models.PositiveIntegerField(default=0)  # The order of sections

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']


# Model to store dynamic form fields
class FormField(models.Model):
    FIELD_TYPES = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('password', 'Password'),
    )

    form = models.ForeignKey(Form, related_name='fields', on_delete=models.CASCADE)
    section = models.ForeignKey(FormSection, related_name='fields', on_delete=models.CASCADE, null=True, blank=True)  # Optional section link
    label = models.CharField(max_length=200)  # Label for the field (e.g., "Name", "Email")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)  # Field type (text, number, date)
    required = models.BooleanField(default=True)  # Whether the field is required
    order = models.PositiveIntegerField(default=0)  # Order of the field in the form

    def __str__(self):
        return self.label

    class Meta:
        ordering = ['order']


# Model to store form responses
class FormResponse(models.Model):
    form = models.ForeignKey(Form, related_name='responses', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.form.title} - {self.created_at}"

# Model to store the actual answers to form fields
class FormResponseField(models.Model):
    form_response = models.ForeignKey(FormResponse, related_name='response_fields', on_delete=models.CASCADE)
    form_field = models.ForeignKey(FormField, on_delete=models.CASCADE)  # The specific field
    answer = models.TextField()  # The user's answer to the field (could be text, number, etc.)

    def __str__(self):
        return f"Response for {self.form_field.label}"
