from rest_framework import serializers
from core.models import ContactMessage, NewsletterSubscriber, MapLocation


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at', 'is_read']


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['id', 'email', 'subscribed_at', 'is_active']
        read_only_fields = ['id', 'subscribed_at']


class MapLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapLocation
        fields = [
            'id', 'country', 'city', 'latitude', 'longitude', 
            'description', 'crop_yield', 'soil_health', 'efficiency',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MapLocationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    class Meta:
        model = MapLocation
        fields = ['id', 'country', 'city', 'latitude', 'longitude']
