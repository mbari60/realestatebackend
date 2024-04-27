import json
from django.http import JsonResponse
from .models import LandModel
from .serializers import LandSerializer
from django.views.decorators.csrf import csrf_exempt 

@csrf_exempt
def lands(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                land = LandModel.objects.get(pk=id)
                serializer = LandSerializer(land)
                return JsonResponse(serializer.data)
            except LandModel.DoesNotExist:
                return JsonResponse({'error': 'Land not found'}, status=404)
        else:
            lands = LandModel.objects.all()
            serializer = LandSerializer(lands, many=True)
            return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = LandSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method in ['PUT', 'PATCH']:
        data = json.loads(request.body)
        
        try:
            land = LandModel.objects.get(pk=id)
        except LandModel.DoesNotExist:
            return JsonResponse({'error': 'Land not found'}, status=404)

        serializer = LandSerializer(land, data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        try:
            land = LandModel.objects.get(pk=id)
            land.delete()
            return JsonResponse({'message': 'Land deleted successfully'}, status=200)
        except LandModel.DoesNotExist:
            return JsonResponse({'error': 'Land not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete land: {str(e)}'}, status=500)
