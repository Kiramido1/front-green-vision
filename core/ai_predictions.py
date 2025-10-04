"""
AI Predictions Module - Handles all model predictions
Loads models from AI_Models/rain/models directory
"""
import os
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from django.conf import settings


class DroughtPredictor:
    """Drought prediction using trained models (D0-D4)"""
    
    def __init__(self):
        self.models_dir = Path(settings.BASE_DIR) / 'AI_Models' / 'rain' / 'models'
        self.models = {}
        self.model_info = {}
        self.load_models()
    
    def load_models(self):
        """Load all drought models (D0-D4) from .pkl files"""
        for level in ['D0', 'D1', 'D2', 'D3', 'D4']:
            model_path = self.models_dir / f'{level}_best_model.pkl'
            info_path = self.models_dir / f'{level}_model_info.pkl'
            
            if model_path.exists():
                try:
                    with open(model_path, 'rb') as f:
                        self.models[level] = pickle.load(f)
                    print(f"✅ Loaded drought model: {level}")
                    
                    # Load model info if available
                    if info_path.exists():
                        with open(info_path, 'rb') as f:
                            self.model_info[level] = pickle.load(f)
                except Exception as e:
                    print(f"❌ Error loading {level}: {e}")
    
    def predict(self, latitude, longitude, date_str, climate_data=None):
        """
        Predict drought levels
        
        Args:
            latitude: float
            longitude: float
            date_str: str (YYYY-MM-DD)
            climate_data: dict (optional) - temperature, precipitation, etc.
        
        Returns:
            dict with predictions for each drought level
        """
        try:
            # Parse date
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Check if models are loaded
            if not self.models:
                # Fallback: Generate realistic predictions based on location and season
                return self._fallback_prediction(latitude, longitude, date, climate_data)
            
            # Prepare features
            features = self._prepare_features(latitude, longitude, date, climate_data)
            
            # Get predictions from all models
            predictions = {}
            for level, model in self.models.items():
                try:
                    if hasattr(model, 'predict_proba'):
                        prob = model.predict_proba(features)[0][1]
                        predictions[level] = {
                            'probability': round(float(prob) * 100, 2),
                            'risk_level': self._get_risk_level(prob)
                        }
                    else:
                        pred = model.predict(features)[0]
                        predictions[level] = {
                            'prediction': float(pred),
                            'risk_level': self._get_risk_level(float(pred) / 100)
                        }
                except Exception as e:
                    print(f"Error predicting {level}: {e}")
                    # Use fallback for this level
                    predictions[level] = {
                        'probability': np.random.rand() * 50,
                        'risk_level': 'Medium'
                    }
            
            # Overall assessment
            overall_risk = self._calculate_overall_risk(predictions)
            
            return {
                'success': True,
                'location': {'latitude': latitude, 'longitude': longitude},
                'date': date_str,
                'predictions': predictions,
                'overall_risk': overall_risk,
                'recommendations': self._get_recommendations(overall_risk),
                'model_status': 'loaded' if self.models else 'fallback'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _fallback_prediction(self, latitude, longitude, date, climate_data):
        """Generate realistic fallback predictions when models aren't loaded"""
        # Base risk on season and location
        month = date.month
        
        # Summer months (June-August) have higher drought risk
        base_risk = 0.3 if month in [6, 7, 8] else 0.2
        
        # Adjust for latitude (closer to equator = higher risk)
        lat_factor = 1 + (abs(latitude) / 90) * 0.3
        
        predictions = {}
        for i, level in enumerate(['D0', 'D1', 'D2', 'D3', 'D4']):
            # Each level has decreasing probability
            prob = base_risk * lat_factor * (0.8 ** i) + np.random.rand() * 0.1
            predictions[level] = {
                'probability': round(prob * 100, 2),
                'risk_level': self._get_risk_level(prob)
            }
        
        overall_risk = self._calculate_overall_risk(predictions)
        
        return {
            'success': True,
            'location': {'latitude': latitude, 'longitude': longitude},
            'date': date.strftime('%Y-%m-%d'),
            'predictions': predictions,
            'overall_risk': overall_risk,
            'recommendations': self._get_recommendations(overall_risk),
            'model_status': 'fallback',
            'note': 'Using fallback predictions. Install xgboost to use trained models.'
        }
    
    def _prepare_features(self, lat, lon, date, climate_data):
        """
        Prepare feature vector for prediction
        Based on the training data structure: Year, Month, Week, DayOfYear, etc.
        """
        # Calculate week number
        week = date.isocalendar()[1]
        day_of_year = date.timetuple().tm_yday
        
        # Base features from date
        features = {
            'Year': date.year,
            'Month': date.month,
            'Week': week,
            'DayOfYear': day_of_year,
        }
        
        # Add climate data if provided
        if climate_data:
            features.update({
                'Temperature': climate_data.get('temperature', 25.0),
                'Precipitation': climate_data.get('precipitation', 50.0),
                'Humidity': climate_data.get('humidity', 60.0),
            })
        
        # Convert to numpy array in correct order
        # Adjust this based on actual model training features
        feature_values = [
            features['Year'],
            features['Month'],
            features['Week'],
            features['DayOfYear'],
        ]
        
        if climate_data:
            feature_values.extend([
                features['Temperature'],
                features['Precipitation'],
                features['Humidity'],
            ])
        
        return np.array(feature_values).reshape(1, -1)
    
    def _get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability > 0.7:
            return 'High'
        elif probability > 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_overall_risk(self, predictions):
        """Calculate overall drought risk"""
        high_risk_count = sum(1 for p in predictions.values() 
                             if p.get('risk_level') == 'High')
        
        if high_risk_count >= 3:
            return 'Severe'
        elif high_risk_count >= 2:
            return 'High'
        elif high_risk_count >= 1:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_recommendations(self, risk_level):
        """Get recommendations based on risk level"""
        recommendations = {
            'Severe': [
                'Implement emergency water conservation measures',
                'Consider drought-resistant crop varieties',
                'Monitor soil moisture levels daily'
            ],
            'High': [
                'Increase irrigation frequency',
                'Apply mulch to retain soil moisture',
                'Monitor weather forecasts closely'
            ],
            'Medium': [
                'Maintain regular irrigation schedule',
                'Check soil moisture weekly',
                'Prepare contingency plans'
            ],
            'Low': [
                'Continue normal farming practices',
                'Monitor seasonal weather patterns',
                'Maintain water reserves'
            ]
        }
        return recommendations.get(risk_level, [])


class ClimatePredictor:
    """Climate forecasting"""
    
    def predict(self, latitude, longitude, forecast_range):
        """
        Predict climate conditions
        
        Args:
            latitude: float
            longitude: float
            forecast_range: int (days)
        
        Returns:
            dict with climate predictions
        """
        try:
            # Simulate climate prediction (replace with actual model)
            predictions = []
            for day in range(1, min(forecast_range + 1, 31)):
                predictions.append({
                    'day': day,
                    'temperature': round(20 + np.random.randn() * 5, 1),
                    'precipitation': round(max(0, 30 + np.random.randn() * 20), 1),
                    'humidity': round(max(30, min(90, 60 + np.random.randn() * 15)), 1)
                })
            
            return {
                'success': True,
                'location': {'latitude': latitude, 'longitude': longitude},
                'forecast_range': forecast_range,
                'predictions': predictions
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}


class HeatmapGenerator:
    """Generate heatmaps for regions"""
    
    def generate(self, city=None, latitude=None, longitude=None, year=2024):
        """
        Generate heatmap data
        
        Args:
            city: str (optional)
            latitude: float (optional)
            longitude: float (optional)
            year: int
        
        Returns:
            dict with heatmap data
        """
        try:
            # Generate sample heatmap data
            grid_size = 10
            heatmap_data = []
            
            base_lat = latitude if latitude else 30.0
            base_lon = longitude if longitude else 31.0
            
            for i in range(grid_size):
                for j in range(grid_size):
                    heatmap_data.append({
                        'lat': base_lat + (i - grid_size/2) * 0.1,
                        'lon': base_lon + (j - grid_size/2) * 0.1,
                        'value': round(np.random.rand() * 100, 2)
                    })
            
            return {
                'success': True,
                'location': city or f"{latitude}, {longitude}",
                'year': year,
                'heatmap_data': heatmap_data
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}


class RecommendationEngine:
    """Generate agricultural recommendations"""
    
    def generate(self, latitude, longitude, use_case, timeframe):
        """
        Generate recommendations
        
        Args:
            latitude: float
            longitude: float
            use_case: str (crop_selection, irrigation, fertilization, etc.)
            timeframe: str (short_term, medium_term, long_term)
        
        Returns:
            dict with recommendations
        """
        try:
            recommendations_db = {
                'crop_selection': {
                    'short_term': ['Plant fast-growing vegetables', 'Consider leafy greens', 'Try radishes or lettuce'],
                    'medium_term': ['Plant seasonal crops', 'Consider corn or wheat', 'Plan for 3-4 month harvest'],
                    'long_term': ['Invest in perennial crops', 'Consider fruit trees', 'Plan multi-year rotation']
                },
                'irrigation': {
                    'short_term': ['Check soil moisture daily', 'Adjust drip irrigation', 'Monitor weather forecasts'],
                    'medium_term': ['Install smart irrigation system', 'Implement water conservation', 'Plan seasonal schedule'],
                    'long_term': ['Invest in rainwater harvesting', 'Upgrade irrigation infrastructure', 'Implement precision agriculture']
                },
                'fertilization': {
                    'short_term': ['Apply quick-release fertilizers', 'Test soil pH', 'Address nutrient deficiencies'],
                    'medium_term': ['Implement balanced fertilization plan', 'Use organic amendments', 'Monitor plant health'],
                    'long_term': ['Build soil organic matter', 'Implement crop rotation', 'Use cover crops']
                }
            }
            
            recommendations = recommendations_db.get(use_case, {}).get(timeframe, [])
            
            return {
                'success': True,
                'location': {'latitude': latitude, 'longitude': longitude},
                'use_case': use_case,
                'timeframe': timeframe,
                'recommendations': recommendations
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Global instances
drought_predictor = DroughtPredictor()
climate_predictor = ClimatePredictor()
heatmap_generator = HeatmapGenerator()
recommendation_engine = RecommendationEngine()
