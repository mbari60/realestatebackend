import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TransportServiceModel
from .serializers import TransportServiceSerializer

@csrf_exempt
def transport_services(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                transport_service = TransportServiceModel.objects.get(pk=id)
                serializer = TransportServiceSerializer(transport_service)
                return JsonResponse(serializer.data)
            except TransportServiceModel.DoesNotExist:
                return JsonResponse({'error': 'Transport Service not found'}, status=404)
        else:
            transport_services = TransportServiceModel.objects.all()
            serializer = TransportServiceSerializer(transport_services, many=True)
            return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = TransportServiceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'PUT' or request.method == 'PATCH':
        data = json.loads(request.body)
        try:
            transport_service = TransportServiceModel.objects.get(pk=id)
        except TransportServiceModel.DoesNotExist:
            return JsonResponse({'error': 'Transport Service not found'}, status=404)
        serializer = TransportServiceSerializer(transport_service, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        try:
            transport_service = TransportServiceModel.objects.get(pk=id)
            transport_service.delete()
            return JsonResponse({'message': 'Transport Service deleted successfully'}, status=200)
        except TransportServiceModel.DoesNotExist:
            return JsonResponse({'error': 'Transport Service not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete transport service: {str(e)}'}, status=500)
