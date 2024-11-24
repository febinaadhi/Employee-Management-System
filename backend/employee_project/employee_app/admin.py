from django.contrib import admin
from .models import CustomUser, Employee, Form, FormSection, FormField, FormResponse, FormResponseField

# CustomUser Admin
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_staff', 'is_active')
    list_filter = ('is_admin', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        ('Login Info', {
            'fields': ('username', 'email', 'password'),
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name'),
        }),
        ('Permissions', {
            'fields': ('is_admin', 'is_staff', 'is_active', 'groups', 'user_permissions'),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

# Register CustomUser with the custom admin
admin.site.register(CustomUser, CustomUserAdmin)

# Employee Admin
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email', 'phone', 'department', 'position',
        'hire_date', 'salary', 'is_active'
    )
    list_filter = ('department', 'position', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'department')
    ordering = ('-hire_date',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone'),
        }),
        ('Job Details', {
            'fields': ('department', 'position', 'hire_date', 'salary'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
    )

# Register Employee with the custom admin
admin.site.register(Employee, EmployeeAdmin)


# Form Admin
class FormAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)
    ordering = ('title',)

# Register Form with the custom admin
admin.site.register(Form, FormAdmin)


# FormSection Admin
class FormSectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'form', 'order')
    list_filter = ('form',)
    search_fields = ('title', 'form__title')
    ordering = ('order',)

# Register FormSection with the custom admin
admin.site.register(FormSection, FormSectionAdmin)


# FormField Admin
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'field_type', 'form', 'section', 'order', 'required')
    list_filter = ('field_type', 'required', 'form', 'section')
    search_fields = ('label', 'form__title', 'section__title')
    ordering = ('order',)

# Register FormField with the custom admin
admin.site.register(FormField, FormFieldAdmin)


# FormResponse Admin
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'form', 'created_at')
    list_filter = ('form', 'created_at')
    search_fields = ('form__title',)
    ordering = ('-created_at',)

# Register FormResponse with the custom admin
admin.site.register(FormResponse, FormResponseAdmin)


# FormResponseField Admin
class FormResponseFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'form_response', 'form_field', 'answer')
    list_filter = ('form_response__form', 'form_field')
    search_fields = ('form_field__label', 'form_response__form__title', 'answer')
    ordering = ('form_response',)

# Register FormResponseField with the custom admin
admin.site.register(FormResponseField, FormResponseFieldAdmin)