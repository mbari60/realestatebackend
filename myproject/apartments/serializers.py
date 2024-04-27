from rest_framework import serializers
from django.contrib.auth.models import User

from .models import CommunityForumPostModel,AmenityModel,CleanerModel,ApartmentModel,TransportServiceModel,AirbnbBookingModel,LandModel,AirbnbModel,MaintenanceRequestModel,InquiryModel,AppartmentBookingModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AmenityModel
        fields = '__all__'

class ApartmentSerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True, read_only=True)

    class Meta:
        model = ApartmentModel
        fields = '__all__'

class LandSerializer(serializers.ModelSerializer):
    # zoning_display = serializers.CharField(source='get_zoning_display', read_only=True)
    class Meta:
        model = LandModel
        fields = '__all__'

class AirbnbSerializer(serializers.ModelSerializer):
    amenities = AmenitySerializer(many=True, read_only=True)
    class Meta:
        model = AirbnbModel
        fields = '__all__'

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    # Define a custom field to represent the related apartment's ID
    # apartment_id = serializers.PrimaryKeyRelatedField(queryset=ApartmentModel.objects.all(), source='apartment')

    class Meta:
        model = MaintenanceRequestModel
        fields = '__all__'

    # def create(self, validated_data):
    #     # No need to extract apartment_id, it will be included in validated_data
    #     maintenance_request = MaintenanceRequestModel.objects.create(**validated_data)
    #     return maintenance_request

class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryModel
        fields = '__all__'

class AppartmentBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppartmentBookingModel
        fields = ['id', 'user', 'apartment', 'booked']

class AirbnbBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirbnbBookingModel
        fields = ['id', 'user', 'airbnb', 'start_date', 'end_date', 'booked']

class CleanerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleanerModel
        fields = ['id', 'name', 'contact_information', 'photo_url', 'rating']

class TransportServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportServiceModel
        fields = ['id', 'name', 'contact_information', 'service_type', 'photo_url', 'rating']

class CommunityForumPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityForumPostModel
        fields = ['id', 'user', 'title', 'content', 'photo_url', 'created_at']