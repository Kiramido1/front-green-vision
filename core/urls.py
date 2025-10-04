from django.urls import path
from .views import (
    HomeView, TechnologyView, NDVIAnalysisView, contact_submit, newsletter_subscribe, 
    predict_weather, list_ai_models, get_model_info, generate_report, report_status
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('technology/', TechnologyView.as_view(), name='technology'),
    path('ndvi-analysis/', NDVIAnalysisView.as_view(), name='ndvi_analysis'),
    path('contact/submit/', contact_submit, name='contact_submit'),
    path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe'),
    path('predict-weather/', predict_weather, name='predict_weather'),
    path('api/models/', list_ai_models, name='list_models'),
    path('api/models/<str:model_name>/', get_model_info, name='model_info'),
    path('api/reports/generate/', generate_report, name='generate_report'),
    path('api/reports/status/<str:report_id>/', report_status, name='report_status'),
]
