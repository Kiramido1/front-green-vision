# Green Vision - AI-Powered Agriculture Monitoring System

## 🌱 Overview
Green Vision is an advanced agriculture monitoring platform that leverages AI, NASA satellite data, and real-time analytics to revolutionize farming practices and promote sustainable agriculture.

## ✨ Features

### 🛰️ Satellite Data Integration
- Real-time NASA satellite imagery analysis
- NDVI (Normalized Difference Vegetation Index) calculations
- Vegetation health monitoring
- Multi-spectral image processing

### 🤖 AI-Powered Analytics
- Machine learning models for crop health prediction
- Drought risk assessment
- Weather forecasting integration
- Automated anomaly detection

### 📊 Interactive Dashboard
- Real-time data visualization
- Interactive global map with location selection
- Comprehensive reporting system
- PDF report generation

### 🌍 Technology Map
- Interactive world map powered by Leaflet.js
- Country and city selection
- Location-based agriculture insights
- Real-time data overlay

## 🚀 Tech Stack

### Frontend
- HTML5, CSS3, JavaScript
- Bootstrap 5.3.2
- Font Awesome 6.4.0
- AOS (Animate On Scroll)
- Leaflet.js for maps
- Three.js & Globe.gl for 3D visualizations

### Backend
- Python 3.11
- Django 4.2
- PostgreSQL / SQLite
- RESTful API

### AI/ML
- TensorFlow / PyTorch
- OpenCV for image processing
- NumPy, Pandas for data analysis
- Scikit-learn for ML models

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 16+ (optional, for frontend build tools)
- Git

### Local Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd green-vision
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

7. **Run the development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## 🌐 Deployment on Vercel

### Prerequisites
- Vercel account
- Vercel CLI installed: `npm i -g vercel`

### Deployment Steps

1. **Login to Vercel**
```bash
vercel login
```

2. **Deploy**
```bash
vercel --prod
```

3. **Environment Variables**
Set these in Vercel dashboard:
- `SECRET_KEY`: Django secret key
- `DEBUG`: False
- `ALLOWED_HOSTS`: your-domain.vercel.app
- `DATABASE_URL`: Your database connection string

### Configuration Files
- `vercel.json`: Vercel deployment configuration
- `build.sh`: Build script for static files
- `requirements.txt`: Python dependencies

## 📁 Project Structure

```
green-vision/
├── api/                    # API endpoints
├── core/                   # Core Django app
│   ├── ml_utils.py        # ML utilities
│   ├── ndvi_model.py      # NDVI processing
│   └── views.py           # View functions
├── greenvision/           # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/             # HTML templates
│   └── reports/          # Report templates
├── static/               # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── media/                # User uploaded files
├── index.html           # Main landing page
├── technology.html      # Technology showcase page
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── vercel.json        # Vercel configuration
├── build.sh          # Build script
└── README.md        # This file
```

## 🎨 Features Documentation

### Weather Forecast
- 7-day weather predictions
- Temperature, precipitation, humidity data
- Location-based forecasting
- Historical weather data analysis

### NDVI Analysis
- Upload satellite images
- Automatic NDVI calculation
- Color-coded vegetation health maps
- Detailed statistics and insights

### Drought Prediction
- Multi-factor risk assessment
- Historical data analysis
- Early warning system
- Actionable recommendations

### Report Generation
- Comprehensive PDF reports
- Data visualization charts
- Export functionality
- Customizable templates

## 🔧 Configuration

### Django Settings
Key settings in `greenvision/settings.py`:
- `ALLOWED_HOSTS`: Add your domain
- `DATABASES`: Configure your database
- `STATIC_ROOT`: Static files directory
- `MEDIA_ROOT`: Media files directory

### API Keys
Required API keys (add to `.env`):
- NASA API Key (for satellite data)
- Weather API Key (for forecasts)
- Google Maps API Key (optional)

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

## 📝 API Documentation

### Endpoints

#### Weather Forecast
```
POST /api/weather/predict/
Body: {
  "latitude": float,
  "longitude": float,
  "date": "YYYY-MM-DD"
}
```

#### NDVI Analysis
```
POST /api/ndvi/analyze/
Body: {
  "image": file
}
```

#### Drought Prediction
```
POST /api/drought/predict/
Body: {
  "temperature": float,
  "precipitation": float,
  "soil_moisture": float
}
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Team

**McCarthies Team**
- AI/ML Development
- Full-Stack Development
- UI/UX Design
- Data Science

## 📧 Contact

- Email: green8vision@gmail.com
- Website: [Green Vision](https://your-domain.vercel.app)

## 🙏 Acknowledgments

- NASA for satellite data access
- OpenWeather for weather data
- Bootstrap team for the framework
- All open-source contributors

## 🔄 Updates

### Version 1.0.0 (2025)
- Initial release
- Core features implementation
- NDVI analysis
- Weather forecasting
- Drought prediction
- Interactive maps
- Report generation

---

**Built with ❤️ by McCarthies Team**
