from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import numpy as np
from .models import ContactMessage, NewsletterSubscriber
from .ai_model_manager import weather_forecast_model, ai_model_manager


class HomeView(TemplateView):
    """Main homepage view"""
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Green Vision - Future of Agriculture Technology'
        return context


class TechnologyView(TemplateView):
    """Technology/Solution page with interactive map"""
    template_name = 'technology.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Try Our Technology - Green Vision'
        return context


def contact_submit(request):
    """Handle contact form submission"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message')
        
        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for contacting us! We will get back to you soon.'
                })
            else:
                messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
                return redirect('home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please fill in all required fields.'
                }, status=400)
            else:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('home')
    
    return redirect('home')


def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            
            if created:
                message = 'Successfully subscribed to our newsletter!'
                success = True
            else:
                if subscriber.is_active:
                    message = 'You are already subscribed to our newsletter.'
                    success = True
                else:
                    subscriber.is_active = True
                    subscriber.save()
                    message = 'Welcome back! Your subscription has been reactivated.'
                    success = True
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': success,
                    'message': message
                })
            else:
                messages.success(request, message)
                return redirect('home')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Please provide a valid email address.'
                }, status=400)
            else:
                messages.error(request, 'Please provide a valid email address.')
                return redirect('home')
    
    return redirect('home')



@csrf_exempt
@require_http_methods(["POST"])
def predict_weather(request):
    """
    Weather Prediction API Endpoint
    
    Accepts POST requests with:
    - day, month, year
    - latitude, longitude
    
    Returns JSON with weather predictions
    """
    try:
        # Parse JSON body
        data = json.loads(request.body)
        
        # Extract parameters
        day = int(data.get('day'))
        month = int(data.get('month'))
        year = int(data.get('year'))
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # Validate inputs - ensure they are scalar values
        day = int(day) if not isinstance(day, (list, np.ndarray)) else int(day[0]) if len(day) > 0 else 1
        month = int(month) if not isinstance(month, (list, np.ndarray)) else int(month[0]) if len(month) > 0 else 1
        year = int(year) if not isinstance(year, (list, np.ndarray)) else int(year[0]) if len(year) > 0 else 2024
        latitude = float(latitude) if not isinstance(latitude, (list, np.ndarray)) else float(latitude[0]) if len(latitude) > 0 else 0.0
        longitude = float(longitude) if not isinstance(longitude, (list, np.ndarray)) else float(longitude[0]) if len(longitude) > 0 else 0.0
        
        if not (1 <= day <= 31):
            return JsonResponse({
                'success': False,
                'error': 'Day must be between 1 and 31'
            }, status=400)
        
        if not (1 <= month <= 12):
            return JsonResponse({
                'success': False,
                'error': 'Month must be between 1 and 12'
            }, status=400)
        
        if not (1900 <= year <= 2100):
            return JsonResponse({
                'success': False,
                'error': 'Year must be between 1900 and 2100'
            }, status=400)
        
        if not (-90 <= latitude <= 90):
            return JsonResponse({
                'success': False,
                'error': 'Latitude must be between -90 and 90'
            }, status=400)
        
        if not (-180 <= longitude <= 180):
            return JsonResponse({
                'success': False,
                'error': 'Longitude must be between -180 and 180'
            }, status=400)
        
        # Make prediction using AI Model Manager
        prediction = weather_forecast_model.predict(day, month, year, latitude, longitude)
        
        return JsonResponse({
            'success': True,
            'prediction': prediction
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)



def list_ai_models(request):
    """
    List all available AI models
    GET /api/models/
    """
    try:
        models = ai_model_manager.list_models()
        return JsonResponse({
            'success': True,
            'models': models,
            'total_count': len(models)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_model_info(request, model_name):
    """
    Get detailed information about a specific model
    GET /api/models/<model_name>/
    """
    try:
        info = ai_model_manager.get_model_info(model_name)
        
        if 'error' in info:
            return JsonResponse({
                'success': False,
                'error': info['error']
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'model': info
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)



class NDVIAnalysisView(TemplateView):
    """NDVI Vegetation Health Analysis page"""
    template_name = 'ndvi_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'NDVI Vegetation Health Analysis - Green Vision'
        return context



@csrf_exempt
@require_http_methods(["POST"])
def generate_report(request):
    """
    Generate PDF Report from AI Model Outputs
    POST /api/reports/generate/
    
    Accepts:
    - models: dict of model outputs (weather, ndvi, drought, climate)
    - title: report title (optional)
    - date_range: date range info (optional)
    - map_snapshot: base64 encoded map image (optional)
    - include_csv: boolean to include CSV attachments
    """
    try:
        from .report_generator import report_generator
        
        # Parse request data
        data = json.loads(request.body)
        
        # Extract parameters
        report_data = {
            'weather': data.get('weather'),
            'ndvi': data.get('ndvi'),
            'drought': data.get('drought'),
            'climate': data.get('climate'),
            'map_snapshot': data.get('map_snapshot'),
            'date_range': data.get('date_range', {})
        }
        
        title = data.get('title', 'Green Vision AI Models Report')
        include_csv = data.get('include_csv', False)
        
        # Generate report
        result = report_generator.generate_report(
            report_data=report_data,
            title=title,
            include_csv=include_csv
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'report_url': result['report_url'],
                'filename': result['filename'],
                'csv_files': result.get('csv_files', []),
                'generated_at': result['generated_at'],
                'file_size': result['file_size']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def report_status(request, report_id):
    """
    Check status of report generation (for async processing)
    GET /api/reports/status/<report_id>/
    """
    # Placeholder for async report status checking
    # Can be implemented with Celery task tracking
    return JsonResponse({
        'success': True,
        'status': 'completed',
        'report_id': report_id
    })
