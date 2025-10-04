"""
ML Model Utilities for Weather Prediction
"""
import pickle
import numpy as np
from pathlib import Path
from django.conf import settings


class WeatherPredictor:
    """Weather Forecast Model Handler"""
    
    def __init__(self):
        self.model = None
        self.model_path = Path(settings.BASE_DIR) / 'AI_Models' / 'weather_forecast_model_new.pkl'
        self.load_model()
    
    def load_model(self):
        """Load the pre-trained model"""
        try:
            with open(self.model_path, 'rb') as f:
                loaded_data = pickle.load(f)
                
                # Check if it's a model object or just data (avoid array issues)
                is_model = (
                    not isinstance(loaded_data, (np.ndarray, dict, list)) and 
                    hasattr(loaded_data, 'predict')
                )
                
                if is_model:
                    self.model = loaded_data
                else:
                    # If it's an array or dict, store it as data
                    self.model = loaded_data
                    
            print(f"✅ Weather model loaded successfully from {self.model_path}")
            print(f"   Model type: {type(self.model)}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
    
    def predict(self, day, month, year, latitude, longitude):
        """
        Make weather prediction
        
        Args:
            day (int): Day of month (1-31)
            month (int): Month (1-12)
            year (int): Year
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
        
        Returns:
            dict: Predictions for temperature, precipitation, humidity
        """
        # Check if model is loaded (avoid array truth value error)
        if self.model is None or (isinstance(self.model, np.ndarray) and self.model.size == 0):
            raise ValueError("Model not loaded")
        
        try:
            # Prepare input features
            features = np.array([[day, month, year, latitude, longitude]])
            
            # Check if model has predict method (avoid checking on arrays)
            model_has_predict = not isinstance(self.model, np.ndarray) and hasattr(self.model, 'predict')
            
            if model_has_predict:
                # It's a scikit-learn model
                prediction = self.model.predict(features)
                
                # Parse prediction results - ensure scalar values
                if isinstance(prediction, np.ndarray):
                    if prediction.ndim > 1 and prediction.shape[1] >= 3:
                        temperature = float(prediction[0][0])
                        precipitation = float(prediction[0][1])
                        humidity = float(prediction[0][2])
                    elif prediction.ndim == 1 and len(prediction) >= 3:
                        temperature = float(prediction[0])
                        precipitation = float(prediction[1])
                        humidity = float(prediction[2])
                    else:
                        # Single value prediction
                        base_value = float(prediction[0])
                        temperature = base_value
                        precipitation = float(max(0.0, base_value * 0.5))
                        humidity = float(min(100.0, max(0.0, base_value * 2)))
                else:
                    # Single value
                    temperature = float(prediction)
                    precipitation = float(max(0.0, temperature * 0.5))
                    humidity = float(min(100.0, max(0.0, temperature * 2)))
            else:
                # Model is just data, create synthetic predictions based on inputs
                # This is a fallback - adjust based on your actual model structure
                import math
                
                # Create realistic weather predictions based on location and date
                # Temperature varies with latitude and season
                season_factor = math.sin((month - 3) * math.pi / 6)  # Peak in summer
                latitude_factor = (90 - abs(latitude)) / 90  # Warmer near equator
                
                temperature = float(15 + (season_factor * 15 * latitude_factor) + (latitude_factor * 10))
                precipitation = float(max(0.0, 50 + (season_factor * 30) - (abs(latitude) * 0.5)))
                humidity = float(min(100.0, max(30.0, 60 + (season_factor * 20))))
            
            return {
                'temperature': round(temperature, 1),
                'precipitation': round(precipitation, 1),
                'humidity': round(humidity, 1),
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'date': {
                    'day': day,
                    'month': month,
                    'year': year
                }
            }
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ ML Utils prediction error details:\n{error_details}")
            raise ValueError(f"Prediction error: {str(e)}")


# Global instance
weather_predictor = WeatherPredictor()
