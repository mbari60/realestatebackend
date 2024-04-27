import json
from django.http import JsonResponse
from .models import AirbnbModel
from .serializers import AirbnbSerializer
from django.views.decorators.csrf import csrf_exempt 

@csrf_exempt
def airbnbs(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                airbnb = AirbnbModel.objects.get(pk=id)
                serializer = AirbnbSerializer(airbnb)
                return JsonResponse(serializer.data)
            except AirbnbModel.DoesNotExist:
                return JsonResponse({'error': 'Airbnb not found'}, status=404)
        else:
            airbnbs = AirbnbModel.objects.all()
            serializer = AirbnbSerializer(airbnbs, many=True)
            return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = AirbnbSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method in ['PUT', 'PATCH']:
        data = json.loads(request.body)
        
        try:
            airbnb = AirbnbModel.objects.get(pk=id)
        except AirbnbModel.DoesNotExist:
            return JsonResponse({'error': 'Airbnb not found'}, status=404)

        serializer = AirbnbSerializer(airbnb, data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        try:
            airbnb = AirbnbModel.objects.get(pk=id)
            airbnb.delete()
            return JsonResponse({'message': 'Airbnb deleted successfully'}, status=200)
        except AirbnbModel.DoesNotExist:
            return JsonResponse({'error': 'Airbnb not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete airbnb: {str(e)}'}, status=500)
