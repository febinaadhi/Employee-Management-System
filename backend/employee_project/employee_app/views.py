from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Employee
from .serializers import EmployeeSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterUserSerializer, LoginUserSerializer, ChangePasswordSerializer
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .filters import EmployeeFilter  # Import EmployeeFilter
from .serializers import FormSerializer, FormResponseSerializer
from .models import Form, FormResponse


# User Registration View
class RegisterUserView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access to the registration view

    def post(self, request):
        # Check if the user is already authenticated
        if request.user.is_authenticated:
            response_data = {
                'statuscode': status.HTTP_403_FORBIDDEN,
                'title': 'Forbidden',
                'data': {},
                'errors': {'error': 'Authenticated users cannot register a new account.'},
                'message': 'You are already logged in. Please log out to register a new account.'
            }
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)

        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Create a new user
                user = CustomUser.objects.create_user(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=serializer.validated_data['password']
                )
                user.save()

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)

                response_data = {
                    'statuscode': status.HTTP_201_CREATED,
                    'title': 'Created',
                    'data': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    },
                    'errors': None,
                    'message': 'User registered successfully.'
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            except Exception as e:
                response_data = {
                    'statuscode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'title': 'Internal Server Error',
                    'data': {},
                    'errors': {'error': str(e)},
                    'message': 'An error occurred during registration.'
                }
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = {
            'statuscode': status.HTTP_400_BAD_REQUEST,
            'title': 'Bad Request',
            'data': {},
            'errors': serializer.errors,
            'message': 'Registration failed due to validation errors.'
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

# User Login View
class LoginUserView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access to login

    def post(self, request):
        if request.user.is_authenticated:
            return Response({
                'statuscode': status.HTTP_403_FORBIDDEN,
                'title': 'Forbidden',
                'message': 'Already logged in. Logout to login with another account.',
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], 
                                password=serializer.validated_data['password'])

            if user:
                # Create JWT token for the user
                refresh = RefreshToken.for_user(user)

                response_data = {
                    'statuscode': status.HTTP_200_OK,
                    'title': 'Success',
                    'data': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    },
                    'errors': None,
                    'message': 'Login successful.'
                }

                return Response(response_data, status=status.HTTP_200_OK)

            # Invalid credentials
            response_data = {
                'statuscode': status.HTTP_401_UNAUTHORIZED,
                'title': 'Unauthorized',
                'data': {},
                'errors': {'error': 'Invalid credentials'},
                'message': 'Login failed due to invalid username or password.'
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)

        else:
            response_data = {
                'statuscode': status.HTTP_400_BAD_REQUEST,
                'title': 'Bad Request',
                'data': {},
                'errors': serializer.errors,
                'message': 'Login failed due to validation errors.'
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

# Password Change View
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            # Check if old password is correct
            if not user.check_password(old_password):
                response_data = {
                    'statuscode': status.HTTP_400_BAD_REQUEST,
                    'title': 'Bad Request',
                    'data': {},
                    'errors': {'error': 'Incorrect old password'},
                    'message': 'Password change failed.'
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Validate and update the password
                validate_password(new_password, user)
                user.set_password(new_password)
                user.save()

                response_data = {
                    'statuscode': status.HTTP_200_OK,
                    'title': 'Success',
                    'data': {},
                    'errors': None,
                    'message': 'Password updated successfully.'
                }
                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as e:
                response_data = {
                    'statuscode': status.HTTP_400_BAD_REQUEST,
                    'title': 'Bad Request',
                    'data': {},
                    'errors': {'error': str(e)},
                    'message': 'Password change failed due to validation errors.'
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            'statuscode': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'title': 'Internal Server Error',
            'data': {},
            'errors': {'error': 'Unknown error occurred.'},
            'message': 'An error occurred while changing the password.'
        }
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# User Profile View 
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Requires authentication to view profile

    def get(self, request):
        try:
            # Get the authenticated user
            user = request.user

            if not user:
                # If no user is found (this shouldn't happen with IsAuthenticated)
                response_data = {
                    'statuscode': status.HTTP_404_NOT_FOUND,
                    'title': 'Not Found',
                    'data': {},
                    'errors': {"error": "User not found."},
                    'message': 'No profile found for the authenticated user.'
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

            # Returning profile data
            response_data = {
                'statuscode': status.HTTP_200_OK,
                'title': 'Success',
                'data': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,  # Example additional data
                    'last_name': user.last_name,    # Example additional data
                    'is_admin': user.is_admin       # Example additional data
                },
                'errors': None,
                'message': 'Profile fetched successfully.'
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors
            response_data = {
                'statuscode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'title': 'Internal Server Error',
                'data': {},
                'errors': {"error": str(e)},
                'message': 'An error occurred while fetching the profile.'
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EmployeeListView(APIView):
    permission_classes = [IsAuthenticated]  # Enforce authentication for employee details
    
    def get(self, request):
        try:
            employees = Employee.objects.all()

            # Apply the dynamic filters if any query parameters are passed
            employee_filter = EmployeeFilter(request.GET, queryset=employees)  # Pass query parameters to the filter
            employees = employee_filter.qs  # Apply the filter and get the filtered queryset

            if not employees:
                response_data = {
                    'statuscode': status.HTTP_404_NOT_FOUND,
                    'title': 'Not Found',
                    'data': [],
                    'errors': {"error": "No employees found."},
                    'message': 'No employees available.',
                }
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

            serializer = EmployeeSerializer(employees, many=True)
            response_data = {
                'statuscode': status.HTTP_200_OK,
                'title': 'Success',
                'data': serializer.data,
                'errors': None,
                'message': 'Employee list retrieved successfully.',
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = {
                'statuscode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'title': 'Internal Server Error',
                'data': [],
                'errors': {"error": str(e)},
                'message': 'An error occurred while fetching the employee list.',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = EmployeeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'statuscode': status.HTTP_201_CREATED,
                    'title': 'Created',
                    'data': serializer.data,
                    'errors': None,
                    'message': 'Employee created successfully.',
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

            response_data = {
                'statuscode': status.HTTP_400_BAD_REQUEST,
                'title': 'Bad Request',
                'data': {},
                'errors': serializer.errors,
                'message': 'Employee creation failed. Validation errors.',
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {
                'statuscode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'title': 'Internal Server Error',
                'data': {},
                'errors': {"error": str(e)},
                'message': 'An error occurred while creating the employee.',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Enforce authentication for employee details

    def get(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
            serializer = EmployeeSerializer(employee)
            response_data = {
                'statuscode': status.HTTP_200_OK,
                'title': 'Success',
                'data': serializer.data,
                'errors': None,
                'message': 'Employee details retrieved successfully.',
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            response_data = {
                'statuscode': status.HTTP_404_NOT_FOUND,
                'title': 'Not Found',
                'data': [],
                'errors': {"error": "Employee not found."},
                'message': 'No employee found with the given ID.',
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                'statuscode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'title': 'Internal Server Error',
                'data': [],
                'errors': {"error": str(e)},
                'message': 'An error occurred while fetching the employee details.',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
            serializer = EmployeeSerializer(employee, data=request.data)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'statuscode': status.HTTP_200_OK,
                    'title': 'Success',
                    'data': serializer.data,
                    'errors': None,
                    'message': 'Employee details updated successfully.',
                }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                'statuscode': status.HTTP_400_BAD_REQUEST,
                'title': 'Validation Error',
                'data': [],
                'errors': serializer.errors,
                'message': 'Validation failed while updating employee details.',
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            response_data = {
                'statuscode': status.HTTP_404_NOT_FOUND,
                'title': 'Not Found',
                'data': [],
                'errors': {"error": "Employee not found."},
                'message': 'No employee found with the given ID.',
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                'statuscode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'title': 'Internal Server Error',
                'data': [],
                'errors': {"error": str(e)},
                'message': 'An error occurred while updating the employee details.',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
            serializer = EmployeeSerializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = {
                    'statuscode': status.HTTP_200_OK,
                    'title': 'Success',
                    'data': serializer.data,
                    'errors': None,
                    'message': 'Employee details partially updated successfully.',
                }
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                'statuscode': status.HTTP_400_BAD_REQUEST,
                'title': 'Validation Error',
                'data': [],
                'errors': serializer.errors,
                'message': 'Validation failed while partially updating employee details.',
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            response_data = {
                'statuscode': status.HTTP_404_NOT_FOUND,
                'title': 'Not Found',
                'data': [],
                'errors': {"error": "Employee not found."},
                'message': 'No employee found with the given ID.',
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                'statuscode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'title': 'Internal Server Error',
                'data': [],
                'errors': {"error": str(e)},
                'message': 'An error occurred while partially updating the employee details.',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
            employee.delete()
            response_data = {
                'statuscode': status.HTTP_204_NO_CONTENT,
                'title': 'Success',
                'data': [],
                'errors': None,
                'message': 'Employee deleted successfully.',
            }
            return Response(response_data, status=status.HTTP_204_NO_CONTENT)
        except Employee.DoesNotExist:
            response_data = {
                'statuscode': status.HTTP_404_NOT_FOUND,
                'title': 'Not Found',
                'data': [],
                'errors': {"error": "Employee not found."},
                'message': 'No employee found with the given ID.',
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = {
                'statuscode': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'title': 'Internal Server Error',
                'data': [],
                'errors': {"error": str(e)},
                'message': 'An error occurred while deleting the employee.',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


# View to create a dynamic form with fields and sections
class CreateFormView(APIView):
    def post(self, request):
        serializer = FormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save form and fields
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View to submit form responses
class SubmitFormResponseView(APIView):
    def post(self, request, form_id):
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'error': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FormResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(form=form)  # Save the form response
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
