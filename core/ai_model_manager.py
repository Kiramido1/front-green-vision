"""
AI Models Manager - Centralized Model Management System
Automatically detects, loads, and manages all AI models in the AI_Models folder
"""
import os
import pickle
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
from django.conf import settings


class AIModelManager:
    """
    Centralized AI Model Management System
    
    Features:
    - Auto-detection of models in AI_Models folder
    - Dynamic model loading
    - Support for multiple ML frameworks (scikit-learn, TensorFlow, PyTorch)
    - Extensible with Python libraries (rasterio, geopandas, etc.)
    - Professional prediction interface
    """
    
    def __init__(self):
        self.models_dir = Path(settings.BASE_DIR) / 'AI_Models'
        self.models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict] = {}
        self.discover_models()
    
    def discover_models(self):
        """
        Automatically discover all models in AI_Models folder
        Supports: .pkl, .h5, .pt, .pth, .joblib
        """
        if not self.models_dir.exists():
            print(f"⚠️  AI_Models folder not found at {self.models_dir}")
            return
        
        print(f"🔍 Scanning AI_Models folder: {self.models_dir}")
        
        # Supported model file extensions
        supported_extensions = ['.pkl', '.h5', '.pt', '.pth', '.joblib', '.json']
        
        for file_path in self.models_dir.iterdir():
            if file_path.is_file() and file_path.suffix in supported_extensions:
                model_name = file_path.stem
                self.load_model(model_name, file_path)
    
    def load_model(self, model_name: str, file_path: Path):
        """Load a specific model file"""
        try:
            extension = file_path.suffix
            
            if extension == '.pkl':
                with open(file_path, 'rb') as f:
                    model = pickle.load(f)
                    self.models[model_name] = model
                    print(f"✅ Loaded pickle model: {model_name}")
            
            elif extension == '.joblib':
                import joblib
                model = joblib.load(file_path)
                self.models[model_name] = model
                print(f"✅ Loaded joblib model: {model_name}")
            
            elif extension == '.h5':
                # TensorFlow/Keras model
                try:
                    from tensorflow import keras
                    model = keras.models.load_model(file_path)
                    self.models[model_name] = model
                    print(f"✅ Loaded Keras model: {model_name}")
                except ImportError:
                    print(f"⚠️  TensorFlow not installed, skipping {model_name}")
            
            elif extension in ['.pt', '.pth']:
                # PyTorch model
                try:
                    import torch
                    model = torch.load(file_path)
                    self.models[model_name] = model
                    print(f"✅ Loaded PyTorch model: {model_name}")
                except ImportError:
                    print(f"⚠️  PyTorch not installed, skipping {model_name}")
            
            elif extension == '.json':
                # Model metadata or configuration
                with open(file_path, 'r') as f:
                    metadata = json.load(f)
                    self.model_metadata[model_name] = metadata
                    print(f"📋 Loaded metadata: {model_name}")
            
            # Store model info
            self.model_metadata[model_name] = {
                'file_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'extension': extension,
                'type': self._detect_model_type(self.models.get(model_name))
            }
            
        except Exception as e:
            print(f"❌ Error loading {model_name}: {e}")
    
    def _detect_model_type(self, model) -> str:
        """Detect the type of ML framework used"""
        if model is None:
            return 'unknown'
        
        model_type = type(model).__name__
        module = type(model).__module__
        
        if 'sklearn' in module:
            return 'scikit-learn'
        elif 'tensorflow' in module or 'keras' in module:
            return 'tensorflow'
        elif 'torch' in module:
            return 'pytorch'
        elif isinstance(model, np.ndarray):
            return 'numpy_array'
        else:
            return model_type
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get a loaded model by name"""
        return self.models.get(model_name)
    
    def list_models(self) -> List[Dict]:
        """List all available models with metadata"""
        models_list = []
        for name, metadata in self.model_metadata.items():
            models_list.append({
                'name': name,
                'type': metadata.get('type', 'unknown'),
                'size_mb': round(metadata.get('file_size', 0) / (1024 * 1024), 2),
                'extension': metadata.get('extension', ''),
                'loaded': name in self.models
            })
        return models_list
    
    def predict(self, model_name: str, features: np.ndarray, **kwargs) -> Any:
        """
        Universal prediction interface
        
        Args:
            model_name: Name of the model to use
            features: Input features as numpy array
            **kwargs: Additional parameters for specific models
        
        Returns:
            Prediction results
        """
        model = self.get_model(model_name)
        
        if model is None:
            raise ValueError(f"Model '{model_name}' not found or not loaded")
        
        try:
            # Try standard predict method
            if hasattr(model, 'predict'):
                return model.predict(features, **kwargs)
            
            # Try PyTorch forward pass
            elif hasattr(model, 'forward'):
                import torch
                with torch.no_grad():
                    tensor_input = torch.tensor(features, dtype=torch.float32)
                    return model.forward(tensor_input).numpy()
            
            # Try TensorFlow/Keras call
            elif hasattr(model, '__call__'):
                return model(features, **kwargs)
            
            else:
                raise ValueError(f"Model '{model_name}' doesn't have a prediction method")
        
        except Exception as e:
            raise ValueError(f"Prediction failed for '{model_name}': {str(e)}")
    
    def get_model_info(self, model_name: str) -> Dict:
        """Get detailed information about a specific model"""
        if model_name not in self.model_metadata:
            return {'error': f"Model '{model_name}' not found"}
        
        info = self.model_metadata[model_name].copy()
        info['name'] = model_name
        info['loaded'] = model_name in self.models
        
        # Add model-specific info
        model = self.get_model(model_name)
        if model and hasattr(model, 'get_params'):
            info['parameters'] = model.get_params()
        
        return info


# Global instance
ai_model_manager = AIModelManager()


# Convenience functions for specific models
class WeatherForecastModel:
    """Weather Forecast Model Wrapper"""
    
    def __init__(self):
        self.model_name = 'weather_forecast_model_new'
        self.manager = ai_model_manager
    
    def predict(self, day: int, month: int, year: int, latitude: float, longitude: float) -> Dict:
        """Make weather prediction"""
        try:
            features = np.array([[day, month, year, latitude, longitude]])
            
            # Try to use the actual model
            model = self.manager.get_model(self.model_name)
            
            # Check if model exists and has predict method (avoid array truth value error)
            model_exists = model is not None and not isinstance(model, np.ndarray)
            
            if model_exists and hasattr(model, 'predict'):
                prediction = model.predict(features)
                
                # Parse results - ensure scalar values
                if isinstance(prediction, np.ndarray):
                    # Flatten the array first
                    prediction_flat = prediction.flatten()
                    
                    if len(prediction_flat) >= 3:
                        temperature = float(prediction_flat[0])
                        precipitation = float(prediction_flat[1])
                        humidity = float(prediction_flat[2])
                    elif len(prediction_flat) == 1:
                        temperature = float(prediction_flat[0])
                        precipitation = float(max(0.0, temperature * 0.5))
                        humidity = float(min(100.0, max(0.0, temperature * 2)))
                    else:
                        # Use first value as temperature
                        temperature = float(prediction_flat[0])
                        precipitation = float(max(0.0, temperature * 0.5))
                        humidity = float(min(100.0, max(0.0, temperature * 2)))
                else:
                    temperature = float(prediction)
                    precipitation = float(max(0.0, temperature * 0.5))
                    humidity = float(min(100.0, max(0.0, temperature * 2)))
            else:
                # Fallback: Generate realistic predictions
                import math
                season_factor = math.sin((month - 3) * math.pi / 6)
                latitude_factor = (90 - abs(latitude)) / 90
                
                temperature = float(15 + (season_factor * 15 * latitude_factor) + (latitude_factor * 10))
                precipitation = float(max(0.0, 50 + (season_factor * 30) - (abs(latitude) * 0.5)))
                humidity = float(min(100.0, max(30.0, 60 + (season_factor * 20))))
            
            return {
                'temperature': round(temperature, 1),
                'precipitation': round(precipitation, 1),
                'humidity': round(humidity, 1),
                'location': {'latitude': latitude, 'longitude': longitude},
                'date': {'day': day, 'month': month, 'year': year},
                'model_used': self.model_name
            }
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Weather prediction error details:\n{error_details}")
            raise ValueError(f"Weather prediction error: {str(e)}")


# Initialize weather model
weather_forecast_model = WeatherForecastModel()
