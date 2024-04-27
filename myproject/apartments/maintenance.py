import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import MaintenanceRequestModel, ApartmentModel
from .serializers import MaintenanceRequestSerializer
from django.views.decorators.csrf import csrf_exempt 
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

@csrf_exempt
def maintenance_requests(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                maintenance_request = MaintenanceRequestModel.objects.get(pk=id)
                serializer = MaintenanceRequestSerializer(maintenance_request)
                return JsonResponse(serializer.data)
            except MaintenanceRequestModel.DoesNotExist:
                return JsonResponse({'error': 'Maintenance Request not found'}, status=404)
        else:
            maintenance_requests = MaintenanceRequestModel.objects.all()
            serializer = MaintenanceRequestSerializer(maintenance_requests, many=True)
            return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        user_id = data['user']
        #get the user email so as to send the email that we have received his/her request
        try:
            user = User.objects.get(pk=user_id)
            user_email = user.email


            serializer = MaintenanceRequestSerializer(data=data)
            if serializer.is_valid():
              serializer.save()
              #sending email
              send_maintenance_request_confirmation_email(user,user_email)

              return JsonResponse(serializer.data, status=201)
            else:
              return JsonResponse(serializer.errors, status=400)
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'User does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method in ['PUT', 'PATCH']:
        data = json.loads(request.body)
        
        try:
            maintenance_request = MaintenanceRequestModel.objects.get(pk=id)
        except MaintenanceRequestModel.DoesNotExist:
            return JsonResponse({'error': 'Maintenance Request not found'}, status=404)

        serializer = MaintenanceRequestSerializer(maintenance_request, data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        try:
            maintenance_request = MaintenanceRequestModel.objects.get(pk=id)
            maintenance_request.delete()
            return JsonResponse({'message': 'Maintenance Request deleted successfully'}, status=200)
        except MaintenanceRequestModel.DoesNotExist:
            return JsonResponse({'error': 'Maintenance Request not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete Maintenance Request: {str(e)}'}, status=500)

@csrf_exempt
def solved_maintenance(request, id=None):
    if request.method == 'POST':
        try:
            maintenance_request = MaintenanceRequestModel.objects.get(pk=id)
            maintenance_request.solved = True
            maintenance_request.save()
            serializer = MaintenanceRequestSerializer(maintenance_request)
            return JsonResponse(serializer.data, status=200)
        except MaintenanceRequestModel.DoesNotExist:
            return JsonResponse({'error': 'Maintenance Request not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to mark Maintenance Request as solved: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


#sending the email
def send_maintenance_request_confirmation_email(user, user_email):
    # Prepare email content
    subject = 'Maintenance Request Confirmation'
    context = {
        'user': user,
    }
    html_message = render_to_string('maintenance_request_confirmation_email.html', context)
    
    # Create the email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_message),  # Plain text version of the email
        from_email='info@propertyhub.co.ke',
        to=[user_email],
    )
    email.attach_alternative(html_message, 'text/html')  # Attach HTML content
    
    # Send the email
    email.send()