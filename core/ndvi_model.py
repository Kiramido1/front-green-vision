"""
NDVI Prediction Model - Vegetation Health Analysis
Integrates PyTorch CNN model for NDVI spatial-temporal prediction
"""
import os
import sys
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from django.conf import settings


# Add NDVI folder to path for model loading
ndvi_path = Path(settings.BASE_DIR) / 'AI_Models' / 'NDVI'
if str(ndvi_path) not in sys.path:
    sys.path.insert(0, str(ndvi_path))


class NDVIModel:
    """
    NDVI (Normalized Difference Vegetation Index) Prediction Model
    
    Features:
    - Time series prediction using LSTM
    - Vegetation health classification
    - Historical data analysis
    - Multi-temporal predictions
    """
    
    def __init__(self):
        self.model_path = Path(settings.BASE_DIR) / 'AI_Models' / 'ndvi_model.pki'
        self.model = None
        self.sequence_length = 6  # Number of historical points needed
        self.load_model()
    
    def load_model(self):
        """Load the PyTorch CNN model from pickle file"""
        try:
            import torch
            import torch.nn as nn
            
            # Define the model architecture (must match the saved model)
            class ImprovedNDVIModel(nn.Module):
                def __init__(self, input_channels=1, time_features=3):
                    super(ImprovedNDVIModel, self).__init__()
                    
                    # NDVI processing with convolutional layers
                    self.conv1 = nn.Conv2d(input_channels, 16, kernel_size=3, padding=1)
                    self.bn1 = nn.BatchNorm2d(16)
                    self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
                    self.bn2 = nn.BatchNorm2d(32)
                    self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
                    self.bn3 = nn.BatchNorm2d(64)
                    self.conv4 = nn.Conv2d(64, 32, kernel_size=3, padding=1)
                    self.bn4 = nn.BatchNorm2d(32)
                    self.conv5 = nn.Conv2d(32, 16, kernel_size=3, padding=1)
                    self.bn5 = nn.BatchNorm2d(16)
                    self.conv6 = nn.Conv2d(16, 1, kernel_size=3, padding=1)
                    
                    # Time data processing
                    self.time_fc1 = nn.Linear(time_features, 64)
                    self.time_bn1 = nn.BatchNorm1d(64)
                    self.time_fc2 = nn.Linear(64, 128)
                    self.time_bn2 = nn.BatchNorm1d(128)
                    
                    # Attention mechanism for time features
                    self.attention = nn.Linear(128, 1)
                    
                    self.relu = nn.ReLU()
                    self.dropout = nn.Dropout(0.3)
                    
                def forward(self, ndvi, time):
                    # Process NDVI data with skip connections
                    x1 = self.relu(self.bn1(self.conv1(ndvi)))
                    x2 = self.relu(self.bn2(self.conv2(x1)))
                    x3 = self.relu(self.bn3(self.conv3(x2)))
                    x4 = self.relu(self.bn4(self.conv4(x3))) + x2  # Skip connection
                    x5 = self.relu(self.bn5(self.conv5(x4))) + x1  # Skip connection
                    x_ndvi = self.conv6(x5)
                    
                    # Process time data
                    x_time = self.relu(self.time_bn1(self.time_fc1(time)))
                    x_time = self.dropout(x_time)
                    x_time = self.relu(self.time_bn2(self.time_fc2(x_time)))
                    
                    return x_ndvi
            
            # Make the class available for unpickling
            sys.modules['__main__'].ImprovedNDVIModel = ImprovedNDVIModel
            
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.model.eval()
                print(f"✅ NDVI Model loaded from {self.model_path}")
            else:
                print(f"⚠️  NDVI model not found at {self.model_path}")
        except ImportError:
            print("⚠️  PyTorch not installed. Install with: pip install torch")
        except Exception as e:
            print(f"❌ Error loading NDVI model: {e}")
    
    def classify_vegetation_health(self, ndvi_value: float) -> Dict[str, str]:
        """
        Classify vegetation health based on NDVI value
        
        NDVI Scale:
        - < 0: Water, snow, clouds
        - 0 - 0.1: Barren rock, sand, snow
        - 0.1 - 0.2: Sparse vegetation
        - 0.2 - 0.5: Moderate vegetation
        - 0.5 - 0.7: Dense vegetation
        - > 0.7: Very dense vegetation (forests)
        """
        if ndvi_value < 0:
            return {
                'category': 'Non-Vegetation',
                'health': 'N/A',
                'description': 'Water, snow, or clouds',
                'color': '#4A90E2'
            }
        elif ndvi_value < 0.1:
            return {
                'category': 'Barren',
                'health': 'Poor',
                'description': 'Barren rock, sand, or urban areas',
                'color': '#D4A574'
            }
        elif ndvi_value < 0.2:
            return {
                'category': 'Sparse Vegetation',
                'health': 'Poor',
                'description': 'Sparse or stressed vegetation',
                'color': '#E8C547'
            }
        elif ndvi_value < 0.5:
            return {
                'category': 'Moderate Vegetation',
                'health': 'Fair',
                'description': 'Moderate vegetation cover',
                'color': '#B8D96D'
            }
        elif ndvi_value < 0.7:
            return {
                'category': 'Dense Vegetation',
                'health': 'Good',
                'description': 'Healthy, dense vegetation',
                'color': '#6BBF59'
            }
        else:
            return {
                'category': 'Very Dense Vegetation',
                'health': 'Excellent',
                'description': 'Very dense vegetation (forests)',
                'color': '#2D7A3E'
            }
    
    def predict_single(self, historical_ndvi: List[float], 
                      day: int = 1, month: int = 1, year: int = 2024) -> Dict:
        """
        Predict next NDVI value from historical sequence
        
        Args:
            historical_ndvi: List of historical NDVI values
            day: Day of prediction
            month: Month of prediction
            year: Year of prediction
        
        Returns:
            Dictionary with prediction and analysis
        """
        if len(historical_ndvi) < self.sequence_length:
            raise ValueError(f"Need at least {self.sequence_length} historical NDVI values")
        
        try:
            # Use the model if available
            if self.model:
                try:
                    import torch
                    
                    # Prepare NDVI spatial data (simulate a small patch)
                    # For time series data, we create a simple spatial representation
                    ndvi_patch = np.array(historical_ndvi[-self.sequence_length:])
                    ndvi_mean = np.mean(ndvi_patch)
                    
                    # Create a small spatial patch (e.g., 10x10) with the mean value
                    spatial_size = 10
                    ndvi_spatial = np.full((1, 1, spatial_size, spatial_size), ndvi_mean, dtype=np.float32)
                    
                    # Prepare time features (day of year, month, year normalized)
                    day_of_year = (datetime(year, month, day) - datetime(year, 1, 1)).days + 1
                    time_features = np.array([[
                        day_of_year / 365.0,  # Normalized day of year
                        month / 12.0,          # Normalized month
                        (year - 2000) / 50.0   # Normalized year
                    ]], dtype=np.float32)
                    
                    # Convert to tensors
                    ndvi_tensor = torch.tensor(ndvi_spatial, dtype=torch.float32)
                    time_tensor = torch.tensor(time_features, dtype=torch.float32)
                    
                    # Predict
                    with torch.no_grad():
                        output = self.model(ndvi_tensor, time_tensor)
                        prediction = float(output.mean().numpy())
                except ImportError:
                    # Fallback if torch not available
                    prediction = self._fallback_prediction(historical_ndvi, month)
            else:
                # Fallback: Weighted moving average with seasonal adjustment
                prediction = self._fallback_prediction(historical_ndvi, month)
            
            # Ensure NDVI is in valid range [-1, 1]
            prediction = np.clip(prediction, -1, 1)
            
            # Classify health
            health_info = self.classify_vegetation_health(prediction)
            
            # Calculate trend
            trend = self._calculate_trend(historical_ndvi)
            
            return {
                'predicted_ndvi': round(float(prediction), 4),
                'health_classification': health_info,
                'trend': trend,
                'confidence': self._calculate_confidence(historical_ndvi),
                'historical_mean': round(float(np.mean(historical_ndvi)), 4),
                'historical_std': round(float(np.std(historical_ndvi)), 4),
                'prediction_date': f"{year}-{month:02d}-{day:02d}",
                'model_used': 'CNN' if self.model else 'Fallback'
            }
        
        except Exception as e:
            raise ValueError(f"NDVI prediction error: {str(e)}")
    
    def _fallback_prediction(self, historical_ndvi: List[float], month: int) -> float:
        """Fallback prediction method when PyTorch model is not available"""
        # Weighted moving average with more weight on recent values
        recent_values = historical_ndvi[-3:]
        weights = np.array([0.2, 0.3, 0.5])
        prediction = np.average(recent_values, weights=weights)
        
        # Add seasonal adjustment based on month
        seasonal_factor = np.sin((month - 3) * np.pi / 6) * 0.1
        prediction += seasonal_factor
        
        return float(prediction)
    
    def predict_sequence(self, historical_ndvi: List[float], steps: int = 3) -> Dict:
        """
        Predict multiple future NDVI values
        
        Args:
            historical_ndvi: List of historical NDVI values
            steps: Number of future steps to predict
        
        Returns:
            Dictionary with multi-step predictions
        """
        predictions = []
        current_sequence = historical_ndvi.copy()
        
        for i in range(steps):
            result = self.predict_single(current_sequence)
            predictions.append({
                'step': i + 1,
                'ndvi': result['predicted_ndvi'],
                'health': result['health_classification']
            })
            # Add prediction to sequence for next iteration
            current_sequence.append(result['predicted_ndvi'])
        
        return {
            'predictions': predictions,
            'overall_trend': self._calculate_trend([p['ndvi'] for p in predictions]),
            'forecast_period': f"Next {steps} time periods"
        }
    
    def analyze_location(self, latitude: float, longitude: float, 
                        historical_ndvi: Optional[List[float]] = None,
                        day: int = None, month: int = None, year: int = None) -> Dict:
        """
        Comprehensive NDVI analysis for a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            historical_ndvi: Optional historical NDVI data
            day: Day for prediction (default: current day)
            month: Month for prediction (default: current month)
            year: Year for prediction (default: current year)
        
        Returns:
            Complete analysis including predictions and recommendations
        """
        # Use current date if not provided
        if day is None or month is None or year is None:
            now = datetime.now()
            day = day or now.day
            month = month or now.month
            year = year or now.year
        
        # If no historical data provided, generate sample data
        if historical_ndvi is None:
            historical_ndvi = self._generate_sample_ndvi(latitude, longitude, month)
        
        # Single prediction
        prediction = self.predict_single(historical_ndvi, day, month, year)
        
        # Multi-step forecast
        forecast = self.predict_sequence(historical_ndvi, steps=3)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            prediction['predicted_ndvi'],
            prediction['trend']
        )
        
        return {
            'location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'current_analysis': prediction,
            'forecast': forecast,
            'recommendations': recommendations,
            'historical_data': {
                'values': historical_ndvi,
                'length': len(historical_ndvi)
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, str]:
        """Calculate trend from values"""
        if len(values) < 2:
            return {'direction': 'stable', 'description': 'Insufficient data'}
        
        # Linear regression slope
        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.01:
            return {
                'direction': 'increasing',
                'description': 'Vegetation health improving',
                'icon': '📈'
            }
        elif slope < -0.01:
            return {
                'direction': 'decreasing',
                'description': 'Vegetation health declining',
                'icon': '📉'
            }
        else:
            return {
                'direction': 'stable',
                'description': 'Vegetation health stable',
                'icon': '➡️'
            }
    
    def _calculate_confidence(self, historical_ndvi: List[float]) -> str:
        """Calculate prediction confidence based on data quality"""
        std = np.std(historical_ndvi)
        
        if std < 0.05:
            return 'High'
        elif std < 0.15:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_sample_ndvi(self, latitude: float, longitude: float, current_month: int = 1) -> List[float]:
        """Generate realistic sample NDVI data based on location"""
        # Base NDVI on latitude (vegetation zones)
        # Tropical regions (near equator) have higher NDVI
        lat_factor = 1 - (abs(latitude) / 90)
        base_ndvi = 0.25 + (lat_factor * 0.35)
        
        # Add seasonal variation (12 months of historical data)
        ndvi_values = []
        for i in range(12):
            # Seasonal pattern (peaks in growing season)
            month_offset = (current_month - 12 + i) % 12
            seasonal_factor = np.sin((month_offset - 3) * np.pi / 6) * 0.2
            
            # Add some randomness
            noise = np.random.normal(0, 0.03)
            
            ndvi = base_ndvi + seasonal_factor + noise
            ndvi_values.append(float(np.clip(ndvi, 0, 0.9)))
        
        return ndvi_values
    
    def _generate_recommendations(self, predicted_ndvi: float, trend: Dict) -> List[Dict]:
        """Generate actionable recommendations based on NDVI analysis"""
        recommendations = []
        
        if predicted_ndvi < 0.2:
            recommendations.append({
                'priority': 'High',
                'action': 'Immediate Intervention Required',
                'description': 'Vegetation is sparse or stressed. Consider irrigation, fertilization, or pest control.',
                'icon': '⚠️'
            })
        elif predicted_ndvi < 0.5:
            recommendations.append({
                'priority': 'Medium',
                'action': 'Monitor Closely',
                'description': 'Vegetation health is moderate. Regular monitoring recommended.',
                'icon': '👁️'
            })
        else:
            recommendations.append({
                'priority': 'Low',
                'action': 'Maintain Current Practices',
                'description': 'Vegetation is healthy. Continue current management practices.',
                'icon': '✅'
            })
        
        if trend['direction'] == 'decreasing':
            recommendations.append({
                'priority': 'High',
                'action': 'Address Declining Trend',
                'description': 'Vegetation health is declining. Investigate potential causes (drought, disease, pests).',
                'icon': '🔍'
            })
        
        return recommendations


# Global instance
ndvi_model = NDVIModel()
