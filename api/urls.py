from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContactMessageViewSet, 
    NewsletterSubscriberViewSet, 
    MapLocationViewSet,
    predict_ndvi,
    predict_ndvi_sequence,
    predict_drought,
    predict_climate,
    predict_heatmap,
    predict_recommendations
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'contact', ContactMessageViewSet, basename='contact')
router.register(r'newsletter', NewsletterSubscriberViewSet, basename='newsletter')
router.register(r'locations', MapLocationViewSet, basename='locations')

urlpatterns = [
    path('', include(router.urls)),
    path('predict-ndvi/', predict_ndvi, name='predict-ndvi'),
    path('predict-ndvi-sequence/', predict_ndvi_sequence, name='predict-ndvi-sequence'),
    path('predict/drought/', predict_drought, name='predict-drought'),
    path('predict/climate/', predict_climate, name='predict-climate'),
    path('predict/heatmap/', predict_heatmap, name='predict-heatmap'),
    path('predict/recommendations/', predict_recommendations, name='predict-recommendations'),
]
