import json
from django.http import JsonResponse
from .models import AmenityModel
from .serializers import AmenitySerializer
from django.views.decorators.csrf import csrf_exempt  # For handling CSRF exemption

@csrf_exempt
def amenities(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                amenity = AmenityModel.objects.get(pk=id)
                serializer = AmenitySerializer(amenity)
                return JsonResponse(serializer.data)
            except AmenityModel.DoesNotExist:
                return JsonResponse({'error': 'Amenity not found'}, status=404)
        else:
            amenities = AmenityModel.objects.all()
            serializer = AmenitySerializer(amenities, many=True)
            return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        # Deserialize JSON data from request body
        data = json.loads(request.body)
        # checking if the name exists 
        name = data.get('name', '').strip().lower()
        
        # Checking if a similar name already exists in the database
        similar_names = AmenityModel.objects.filter(name__iexact=name)  # Case-insensitive match
        if similar_names.exists():
            return JsonResponse({'error': 'A similar Amenity already exists'}, status=400)

        serializer = AmenitySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method == 'PUT':
        # Deserialize JSON data from request body
        data = json.loads(request.body)
        
        # Get the existing amenity object if it exists
        try:
            amenity = AmenityModel.objects.get(pk=id)
        except AmenityModel.DoesNotExist:
            return JsonResponse({'error': 'Amenity not found'}, status=404)

        # Update the existing amenity with the new data
        serializer = AmenitySerializer(amenity, data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        # Get the existing amenity object if it exists
        try:
            amenity = AmenityModel.objects.get(pk=id)
        except AmenityModel.DoesNotExist:
            return JsonResponse({'error': 'Amenity not found'}, status=404)

        # Delete the existing amenity
        amenity.delete()
        return JsonResponse({'message': 'Amenity deleted successfully'}, status=200)
