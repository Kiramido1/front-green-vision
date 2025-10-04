from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.models import ContactMessage, NewsletterSubscriber, MapLocation
from .serializers import (
    ContactMessageSerializer, 
    NewsletterSubscriberSerializer, 
    MapLocationSerializer,
    MapLocationListSerializer
)
from core.ndvi_model import ndvi_model


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for contact messages
    POST: Create new contact message
    GET: List all messages (admin only in production)
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'success': True,
            'message': 'Thank you for contacting us! We will get back to you soon.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class NewsletterSubscriberViewSet(viewsets.ModelViewSet):
    """
    API endpoint for newsletter subscriptions
    POST: Subscribe to newsletter
    """
    queryset = NewsletterSubscriber.objects.all()
    serializer_class = NewsletterSubscriberSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            message = 'Successfully subscribed to our newsletter!'
        else:
            if subscriber.is_active:
                message = 'You are already subscribed to our newsletter.'
            else:
                subscriber.is_active = True
                subscriber.save()
                message = 'Welcome back! Your subscription has been reactivated.'
        
        serializer = self.get_serializer(subscriber)
        return Response({
            'success': True,
            'message': message,
            'data': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class MapLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for map locations
    GET: List all locations or get specific location
    """
    queryset = MapLocation.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MapLocationListSerializer
        return MapLocationSerializer
    
    @action(detail=False, methods=['get'])
    def by_country(self, request):
        """Get locations grouped by country"""
        countries = {}
        locations = MapLocation.objects.all()
        
        for location in locations:
            if location.country not in countries:
                countries[location.country] = {
                    'coords': [float(location.latitude), float(location.longitude)],
                    'zoom': 6,
                    'cities': {}
                }
            
            countries[location.country]['cities'][location.city] = [
                float(location.latitude),
                float(location.longitude)
            ]
        
        return Response(countries)
    
    @action(detail=False, methods=['get'])
    def countries(self, request):
        """Get list of all countries"""
        countries = MapLocation.objects.values_list('country', flat=True).distinct()
        return Response(list(countries))
    
    @action(detail=False, methods=['get'])
    def cities(self, request):
        """Get cities for a specific country"""
        country = request.query_params.get('country')
        if not country:
            return Response({
                'error': 'Country parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cities = MapLocation.objects.filter(country=country).values(
            'city', 'latitude', 'longitude'
        )
        return Response(list(cities))



@api_view(['POST'])
@permission_classes([AllowAny])
def predict_ndvi(request):
    """
    NDVI Prediction API Endpoint
    
    POST /api/predict-ndvi/
    
    Request Body:
    {
        "latitude": 30.0,
        "longitude": 31.0,
        "historical_ndvi": [0.45, 0.52, 0.48, 0.55, 0.51, 0.53],  // Optional
        "day": 15,      // Optional
        "month": 6,     // Optional
        "year": 2024    // Optional
    }
    
    Response:
    {
        "success": true,
        "data": {
            "location": {...},
            "current_analysis": {...},
            "forecast": {...},
            "recommendations": [...]
        }
    }
    """
    try:
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        historical_ndvi = request.data.get('historical_ndvi')
        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')
        
        # Validate inputs
        if latitude is None or longitude is None:
            return Response({
                'success': False,
                'error': 'Latitude and longitude are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'Invalid latitude or longitude format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate latitude/longitude ranges
        if not (-90 <= latitude <= 90):
            return Response({
                'success': False,
                'error': 'Latitude must be between -90 and 90'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not (-180 <= longitude <= 180):
            return Response({
                'success': False,
                'error': 'Longitude must be between -180 and 180'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate historical NDVI if provided
        if historical_ndvi is not None:
            if not isinstance(historical_ndvi, list):
                return Response({
                    'success': False,
                    'error': 'historical_ndvi must be a list of numbers'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if len(historical_ndvi) < 6:
                return Response({
                    'success': False,
                    'error': 'At least 6 historical NDVI values are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                historical_ndvi = [float(v) for v in historical_ndvi]
            except (ValueError, TypeError):
                return Response({
                    'success': False,
                    'error': 'All historical NDVI values must be numbers'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform NDVI analysis
        result = ndvi_model.analyze_location(
            latitude=latitude,
            longitude=longitude,
            historical_ndvi=historical_ndvi,
            day=day,
            month=month,
            year=year
        )
        
        return Response({
            'success': True,
            'data': result,
            'message': 'NDVI analysis completed successfully'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def predict_ndvi_sequence(request):
    """
    Multi-step NDVI Prediction API Endpoint
    
    POST /api/predict-ndvi-sequence/
    
    Request Body:
    {
        "historical_ndvi": [0.45, 0.52, 0.48, 0.55, 0.51, 0.53],
        "steps": 3  // Number of future predictions (default: 3)
    }
    """
    try:
        historical_ndvi = request.data.get('historical_ndvi')
        steps = request.data.get('steps', 3)
        
        if not historical_ndvi:
            return Response({
                'success': False,
                'error': 'historical_ndvi is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not isinstance(historical_ndvi, list) or len(historical_ndvi) < 6:
            return Response({
                'success': False,
                'error': 'At least 6 historical NDVI values are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            historical_ndvi = [float(v) for v in historical_ndvi]
            steps = int(steps)
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'Invalid data format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if steps < 1 or steps > 12:
            return Response({
                'success': False,
                'error': 'Steps must be between 1 and 12'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Perform prediction
        result = ndvi_model.predict_sequence(historical_ndvi, steps)
        
        return Response({
            'success': True,
            'data': result
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# AI Models Prediction Endpoints
from core.ai_predictions import (
    drought_predictor,
    climate_predictor,
    heatmap_generator,
    recommendation_engine
)


@api_view(['POST'])
@permission_classes([AllowAny])
def predict_drought(request):
    """
    Drought Prediction API
    POST /api/predict/drought/
    
    Body: {
        "latitude": 30.0,
        "longitude": 31.0,
        "date": "2024-06-15",
        "climate_data": {  // optional
            "temperature": 28.5,
            "precipitation": 45.0,
            "humidity": 65.0
        }
    }
    """
    try:
        data = request.data
        result = drought_predictor.predict(
            latitude=float(data.get('latitude')),
            longitude=float(data.get('longitude')),
            date_str=data.get('date'),
            climate_data=data.get('climate_data')
        )
        return Response(result)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def predict_climate(request):
    """
    Climate Forecast API
    POST /api/predict/climate/
    
    Body: {
        "latitude": 30.0,
        "longitude": 31.0,
        "forecast_range": 7
    }
    """
    try:
        data = request.data
        result = climate_predictor.predict(
            latitude=float(data.get('latitude')),
            longitude=float(data.get('longitude')),
            forecast_range=int(data.get('forecast_range', 7))
        )
        return Response(result)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def predict_heatmap(request):
    """
    Heatmap Generation API
    POST /api/predict/heatmap/
    
    Body: {
        "city": "Cairo",  // optional
        "latitude": 30.0,  // optional if city provided
        "longitude": 31.0,  // optional if city provided
        "year": 2024
    }
    """
    try:
        data = request.data
        result = heatmap_generator.generate(
            city=data.get('city'),
            latitude=float(data.get('latitude')) if data.get('latitude') else None,
            longitude=float(data.get('longitude')) if data.get('longitude') else None,
            year=int(data.get('year', 2024))
        )
        return Response(result)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def predict_recommendations(request):
    """
    Recommendations API
    POST /api/predict/recommendations/
    
    Body: {
        "latitude": 30.0,
        "longitude": 31.0,
        "use_case": "crop_selection",  // crop_selection, irrigation, fertilization
        "timeframe": "short_term"  // short_term, medium_term, long_term
    }
    """
    try:
        data = request.data
        result = recommendation_engine.generate(
            latitude=float(data.get('latitude')),
            longitude=float(data.get('longitude')),
            use_case=data.get('use_case', 'crop_selection'),
            timeframe=data.get('timeframe', 'short_term')
        )
        return Response(result)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=400)
