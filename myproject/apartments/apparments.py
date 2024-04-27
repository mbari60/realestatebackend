import json
from django.http import JsonResponse
from .models import ApartmentModel
from .serializers import ApartmentSerializer
from django.views.decorators.csrf import csrf_exempt 

@csrf_exempt
def apartments(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                apartment = ApartmentModel.objects.get(pk=id)
                serializer = ApartmentSerializer(apartment)
                return JsonResponse(serializer.data)
            except ApartmentModel.DoesNotExist:
                return JsonResponse({'error': 'Apartment not found'}, status=404)
        else:
            apartments = ApartmentModel.objects.all()
            serializer = ApartmentSerializer(apartments, many=True)
            return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = ApartmentSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method in ['PUT', 'PATCH']:
        data = json.loads(request.body)
        
        try:
            apartment = ApartmentModel.objects.get(pk=id)
        except ApartmentModel.DoesNotExist:
            return JsonResponse({'error': 'Apartment not found'}, status=404)

        serializer = ApartmentSerializer(apartment, data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        try:
            apartment = ApartmentModel.objects.get(pk=id)
            apartment.delete()
            return JsonResponse({'message': 'Apartment deleted successfully'}, status=200)
        except ApartmentModel.DoesNotExist:
            return JsonResponse({'error': 'Apartment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete apartment: {str(e)}'}, status=500)
