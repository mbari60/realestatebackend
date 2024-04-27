import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import AppartmentBookingModel, AirbnbBookingModel , AirbnbModel ,ApartmentModel
from .serializers import AppartmentBookingSerializer, AirbnbBookingSerializer,ApartmentSerializer
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Q
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

#getting all bookings for the admin
def get_all_aparment_bookings(request):
    if request.method == 'GET':
        bookings = ApartmentModel.objects.filter(booked=True)
        serializer = ApartmentSerializer(bookings, many=True)
        return JsonResponse(serializer.data, safe=False)

# declaring a apartment vacant
@csrf_exempt
def declare_not_booked(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        apartment_id = data['apartment']
        try:
            apartment = ApartmentModel.objects.get(pk=apartment_id)
            apartment.booked = False
            apartment.save()
        except ApartmentModel.DoesNotExist:
            return JsonResponse({'error': 'Apartment not found'}, status=404)
        return JsonResponse({'message': 'Apartment declared vacant'}, status=201)


@csrf_exempt
def appartment_bookings(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                booking = AppartmentBookingModel.objects.get(pk=id)
                serializer = AppartmentBookingSerializer(booking)
                return JsonResponse(serializer.data)
            except AppartmentBookingModel.DoesNotExist:
                return JsonResponse({'error': 'Booking not found'}, status=404)
        else:
            bookings = AppartmentBookingModel.objects.filter(booked=False)
            serializer = AppartmentBookingSerializer(bookings, many=True)
            return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)

        apartment_id = data['apartment']
        user_id = data['user']
        user = User.objects.get(pk = user_id)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        try:
            apartment = ApartmentModel.objects.get(pk=apartment_id)
            apartment.booked = True
            apartment.save()
        except ApartmentModel.DoesNotExist:
            return JsonResponse({'error': 'Apartment not found'}, status=404)


        serializer = AppartmentBookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            #email sending 
            send_apartmentBooking_confirmation_email(user,apartment)
            return JsonResponse({'message': 'Apartment booked successfully'}, status=201)
        
        return JsonResponse({'errors': serializer.errors}, status=400)

    elif request.method == 'PUT' or request.method == 'PATCH':
        data = json.loads(request.body)
        try:
            booking = AppartmentBookingModel.objects.get(pk=id)
        except AppartmentBookingModel.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        serializer = AppartmentBookingSerializer(booking, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        try:
            booking = AppartmentBookingModel.objects.get(pk=id)
            booking.delete()
            return JsonResponse({'message': 'Booking deleted successfully'}, status=200)
        except AppartmentBookingModel.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete booking: {str(e)}'}, status=500)

@csrf_exempt
#@login_required
def airbnb_bookings(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                booking = AirbnbBookingModel.objects.get(pk=id)
                serializer = AirbnbBookingSerializer(booking)
                return JsonResponse(serializer.data)
            except AirbnbBookingModel.DoesNotExist:
                return JsonResponse({'error': 'Booking not found'}, status=404)
        else:
            bookings = AirbnbBookingModel.objects.all()
            serializer = AirbnbBookingSerializer(bookings, many=True)
            return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        existing_bookings = AirbnbBookingModel.objects.filter(
            Q(airbnb=data['airbnb']) &
            (Q(start_date__range=[start_date, end_date]) |
            Q(end_date__range=[start_date, end_date]) |
            Q(start_date__lte=start_date, end_date__gte=end_date))
        )

        if existing_bookings.exists():
            return JsonResponse({'error': 'This property is already booked for the selected dates'}, status=400)

        airbnb_id = data['airbnb']
        airbnb = AirbnbModel.objects.get(pk=airbnb_id)
        price_per_night = airbnb.price_per_night
        num_nights = (end_date - start_date).days

        total_cost = num_nights * price_per_night

        try:
            user_id = data['user']
            user_details = User.objects.get(pk=user_id)
            user_email = user_details.email
        except User.DoesNotExist:
            # Handle the case where the user does not exist
            # This could involve returning an error response or taking other appropriate action
            user_email = None  # Set user_email to None or any default value as needed
            # Log an error message or perform any other necessary logging
            return JsonResponse({'error':'user does not exist'})
        except Exception as e:
            # Handle any other exceptions that might occur during user retrieval
            # This could involve logging the exception or taking other appropriate action
            user_email = None  # Set user_email to None or any default value as needed
            return JsonResponse({'error':"Error occurred while retrieving user details:"})
        
        #data['user'] = request.user.id
        serializer = AirbnbBookingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            #sending confirmation email
            send_booking_confirmation_email(data,airbnb,user_details,user_email, total_cost)


            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'PUT' or request.method == 'PATCH':
        data = json.loads(request.body)
        try:
            booking = AirbnbBookingModel.objects.get(pk=id)
        except AirbnbBookingModel.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        serializer = AirbnbBookingSerializer(booking, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        try:
            booking = AirbnbBookingModel.objects.get(pk=id)
            booking.delete()
            return JsonResponse({'message': 'Booking deleted successfully'}, status=200)
        except AirbnbBookingModel.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete booking: {str(e)}'}, status=500)

def send_booking_confirmation_email(data, airbnb, user_details, user_email, total_cost):
    subject = 'Booking Confirmation'

    # Prepare email content
    context = {
        'booking': data,
        'airbnb': airbnb,
        'user': user_details,
        'total_cost': total_cost
    }
    html_message = render_to_string('booking_confirmation_email.html', context)

    # Create the email object
    email = EmailMultiAlternatives(subject, strip_tags(html_message), 'kevin.wanjiru600@gmail.com', [user_email])

    # Attach the HTML content
    email.attach_alternative(html_message, "text/html")

    # Send the email
    email.send()


def send_apartmentBooking_confirmation_email(user, apartment):
    subject_user = 'Apartment Booking Confirmation'
    subject_owner = 'New Apartment Booking'

    user_email = user.email
    owner_email = 'kevin.wanjiru600@gmail.com'

    # Prepare email content for user
    context_user = {
        'user': user,
        'apartment': apartment
    }
    html_message_user = render_to_string('apartment_booking_confirmation_email.html', context_user)

    # Prepare email content for owner
    context_owner = {
        'user': user,
        'apartment': apartment
    }
    text_message_owner = f"New apartment booking by {user.username}. User's email: {user.email} for apartment {apartment.name}"
    #html_message_owner = f"<p>New apartment booking by {user.username}. User's email: {user.email}</p>"

    # Create the email objects
    email_user = EmailMultiAlternatives(subject_user, strip_tags(html_message_user), 'kevin.wanjiru600@gmail.com', [user_email])
    email_owner = EmailMultiAlternatives(subject_owner, text_message_owner, 'kevin.wanjiru600@gmail.com', [owner_email])

    # Attach the HTML content for user
    email_user.attach_alternative(html_message_user, "text/html")

    # Send the emails
    email_user.send()
    email_owner.send()