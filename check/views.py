from rest_framework import generics
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, LoginSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import stripe
from datetime import timedelta
from .models import Subscription, Video
from .serializers import SubscriptionSerializer, VideoSerializer

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)

from rest_framework_simplejwt.tokens import RefreshToken

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                # Return access and refresh tokens along with user ID
                return Response({
                    'message': 'Login successful',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user_id': user.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_type = request.data.get('plan_type')  # 'Master' or 'Bachelor'
        duration = request.data.get('duration')  # '1 Hour', '7 Days', or '1 Month'
        user = request.user

        # Determine amount and billing logic
        if duration == '1 Hour':
            amount = 500  # $5.00
        elif duration == '7 Days':
            amount = 2000  # $20.00
        elif duration == '1 Month':
            amount = 7000  # $70.00
        else:
            return Response({'error': 'Invalid duration'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{plan_type} Subscription',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:8000/check/success/?session_id={CHECKOUT_SESSION_ID}',  # Pass session_id
            cancel_url='http://localhost:8000/cancel/',
            metadata={
                'user_email': user.email,
                'plan_type': plan_type,
                'duration': duration
            }
        )

        return Response({'session_id': checkout_session.id}, status=status.HTTP_200_OK)
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import stripe
from django.conf import settings
from .models import Subscription
from django.contrib.auth.models import User

# Configure your Stripe secret key
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class PaymentSuccessView(APIView):
    permission_classes = [AllowAny]  # You can make this accessible to all users

    def get(self, request):
        session_id = request.query_params.get('session_id')  # Get session_id from URL query params
        if not session_id:
            return Response({'error': 'Session ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the Stripe checkout session using the session ID
            session = stripe.checkout.Session.retrieve(session_id)

            # Check if payment was successful
            if session.payment_status == 'paid':
                # Retrieve the metadata from the session to use for subscription creation
                user_email = session.metadata['user_email']
                plan_type = session.metadata['plan_type']
                duration = session.metadata['duration']

                # Get the user from the email stored in metadata
                user = User.objects.get(email=user_email)

                # Create the subscription in your database
                Subscription.objects.create(
                    user=user,
                    plan_type=plan_type,
                    duration=duration,
                    end_date = '2029-12-08',
                )

                return Response({'message': 'Subscription created successfully'}, status=status.HTTP_200_OK)

            return Response({'error': 'Payment not completed'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)









class VideoListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, plan_type):
        videos = Video.objects.filter(plan_type=plan_type)
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)


