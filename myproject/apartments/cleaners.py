import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CleanerModel
from .serializers import CleanerSerializer

@csrf_exempt
def cleaners(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                cleaner = CleanerModel.objects.get(pk=id)
                serializer = CleanerSerializer(cleaner)
                return JsonResponse(serializer.data)
            except CleanerModel.DoesNotExist:
                return JsonResponse({'error': 'Cleaner not found'}, status=404)
        else:
            cleaners = CleanerModel.objects.all()
            serializer = CleanerSerializer(cleaners, many=True)
            return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = CleanerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'PUT' or request.method == 'PATCH':
        data = json.loads(request.body)
        try:
            cleaner = CleanerModel.objects.get(pk=id)
        except CleanerModel.DoesNotExist:
            return JsonResponse({'error': 'Cleaner not found'}, status=404)
        serializer = CleanerSerializer(cleaner, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        try:
            cleaner = CleanerModel.objects.get(pk=id)
            cleaner.delete()
            return JsonResponse({'message': 'Cleaner deleted successfully'}, status=200)
        except CleanerModel.DoesNotExist:
            return JsonResponse({'error': 'Cleaner not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete cleaner: {str(e)}'}, status=500)
