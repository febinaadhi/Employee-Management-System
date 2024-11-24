from rest_framework import serializers
from .models import CustomUser, Employee
from django.contrib.auth.password_validation import validate_password
from .models import Form, FormField, FormResponse, FormResponseField, FormSection


# Serializer for User Registration
class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'is_admin']
    
    def validate_password(self, value):
        """
        Validate the password using Django's built-in validation system.
        """
        validate_password(value)
        return value

# Serializer for User Login
class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

# Serializer for Password Change
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, style={'input_type': 'password'})


# CustomUser Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_admin']

    def validate_email(self, value):
        """
        Custom validation for email field.
        Ensure email is not already taken by another user.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

# Employee Serializer
class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested User Serializer for handling user creation

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'phone',
            'department', 'position', 'hire_date', 'salary', 'is_active'
        ]

    def create(self, validated_data):
        """
        Create an Employee instance along with the associated CustomUser.
        """
        user_data = validated_data.pop('user')  # Extract user data
        user = CustomUser.objects.create(**user_data)  # Create the CustomUser instance
        employee = Employee.objects.create(user=user, **validated_data)  # Create the Employee instance
        return employee

    def update(self, instance, validated_data):
        """
        Update an existing Employee instance and its related CustomUser.
        """
        user_data = validated_data.pop('user', None)
        
        # Update the related CustomUser instance if user data is provided
        if user_data:
            instance.user.username = user_data.get('username', instance.user.username)
            instance.user.email = user_data.get('email', instance.user.email)
            instance.user.is_admin = user_data.get('is_admin', instance.user.is_admin)
            instance.user.save()

        # Update the Employee instance fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.department = validated_data.get('department', instance.department)
        instance.position = validated_data.get('position', instance.position)
        instance.hire_date = validated_data.get('hire_date', instance.hire_date)
        instance.salary = validated_data.get('salary', instance.salary)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()
        return instance



class FormSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormSection
        fields = ['id', 'title', 'order']

class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'label', 'field_type', 'required', 'order']

class FormSerializer(serializers.ModelSerializer):
    sections = FormSectionSerializer(many=True)
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = Form
        fields = ['id', 'title', 'sections', 'fields']

    def create(self, validated_data):
        sections_data = validated_data.pop('sections')
        fields_data = validated_data.pop('fields')
        form = Form.objects.create(**validated_data)

        # Create sections
        for section_data in sections_data:
            section = FormSection.objects.create(form=form, **section_data)

        # Create fields
        for field_data in fields_data:
            section = FormSection.objects.get(id=field_data.get('section', None))
            field_data['section'] = section if section else None
            FormField.objects.create(form=form, **field_data)

        return form

class FormResponseFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormResponseField
        fields = ['form_field', 'answer']

class FormResponseSerializer(serializers.ModelSerializer):
    response_fields = FormResponseFieldSerializer(many=True)

    class Meta:
        model = FormResponse
        fields = ['id', 'form', 'created_at', 'response_fields']

    def create(self, validated_data):
        response_fields_data = validated_data.pop('response_fields')
        form_response = FormResponse.objects.create(**validated_data)
        for response_field_data in response_fields_data:
            FormResponseField.objects.create(form_response=form_response, **response_field_data)
        return form_response


















# from rest_framework import serializers
# from .models import CustomUser, Employee

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'is_admin']

# class EmployeeSerializer(serializers.ModelSerializer):
#     user = UserSerializer()  # Nested user data

#     class Meta:
#         model = Employee
#         fields = ['id', 'user', 'first_name', 'last_name', 'email', 'phone', 'department', 'position', 'hire_date', 'salary', 'is_active']

#     def create(self, validated_data):
#         user_data = validated_data.pop('user')
#         user = CustomUser.objects.create(**user_data)
#         employee = Employee.objects.create(user=user, **validated_data)
#         return employee

#     def update(self, instance, validated_data):
#         user_data = validated_data.pop('user', None)
#         if user_data:
#             for attr, value in user_data.items():
#                 setattr(instance.user, attr, value)
#             instance.user.save()
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance
