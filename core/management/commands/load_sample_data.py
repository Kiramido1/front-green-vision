from django.core.management.base import BaseCommand
from core.models import MapLocation


class Command(BaseCommand):
    help = 'Load sample map location data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading sample map data...')
        
        sample_locations = [
            # United States
            {'country': 'United States', 'city': 'Des Moines', 'latitude': 41.5868, 'longitude': -93.6250, 
             'crop_yield': 24.7, 'soil_health': 92.3, 'efficiency': 18.9},
            {'country': 'United States', 'city': 'Omaha', 'latitude': 41.2565, 'longitude': -95.9345,
             'crop_yield': 22.5, 'soil_health': 88.5, 'efficiency': 16.2},
            
            # India
            {'country': 'India', 'city': 'Ludhiana', 'latitude': 30.9010, 'longitude': 75.8573,
             'crop_yield': 28.3, 'soil_health': 85.7, 'efficiency': 21.4},
            {'country': 'India', 'city': 'Amritsar', 'latitude': 31.6340, 'longitude': 74.8723,
             'crop_yield': 26.8, 'soil_health': 87.2, 'efficiency': 19.8},
            
            # Brazil
            {'country': 'Brazil', 'city': 'São Paulo', 'latitude': -23.5505, 'longitude': -46.6333,
             'crop_yield': 25.6, 'soil_health': 90.1, 'efficiency': 20.3},
            {'country': 'Brazil', 'city': 'Brasília', 'latitude': -15.8267, 'longitude': -47.9218,
             'crop_yield': 23.4, 'soil_health': 86.9, 'efficiency': 17.5},
            
            # Argentina
            {'country': 'Argentina', 'city': 'Buenos Aires', 'latitude': -34.6037, 'longitude': -58.3816,
             'crop_yield': 27.2, 'soil_health': 91.5, 'efficiency': 22.1},
            {'country': 'Argentina', 'city': 'Rosario', 'latitude': -32.9442, 'longitude': -60.6505,
             'crop_yield': 25.9, 'soil_health': 89.3, 'efficiency': 20.7},
            
            # China
            {'country': 'China', 'city': 'Beijing', 'latitude': 39.9042, 'longitude': 116.4074,
             'crop_yield': 24.1, 'soil_health': 84.6, 'efficiency': 18.3},
            {'country': 'China', 'city': 'Shanghai', 'latitude': 31.2304, 'longitude': 121.4737,
             'crop_yield': 26.5, 'soil_health': 88.9, 'efficiency': 21.0},
            
            # Egypt
            {'country': 'Egypt', 'city': 'Cairo', 'latitude': 30.0444, 'longitude': 31.2357,
             'crop_yield': 22.8, 'soil_health': 82.4, 'efficiency': 16.9},
            {'country': 'Egypt', 'city': 'Alexandria', 'latitude': 31.2001, 'longitude': 29.9187,
             'crop_yield': 21.5, 'soil_health': 80.7, 'efficiency': 15.8},
            
            # Kenya
            {'country': 'Kenya', 'city': 'Nairobi', 'latitude': -1.2864, 'longitude': 36.8172,
             'crop_yield': 19.3, 'soil_health': 78.5, 'efficiency': 14.2},
            {'country': 'Kenya', 'city': 'Mombasa', 'latitude': -4.0435, 'longitude': 39.6682,
             'crop_yield': 18.7, 'soil_health': 76.9, 'efficiency': 13.5},
            
            # Australia
            {'country': 'Australia', 'city': 'Sydney', 'latitude': -33.8688, 'longitude': 151.2093,
             'crop_yield': 23.9, 'soil_health': 87.6, 'efficiency': 19.1},
            {'country': 'Australia', 'city': 'Melbourne', 'latitude': -37.8136, 'longitude': 144.9631,
             'crop_yield': 22.6, 'soil_health': 85.3, 'efficiency': 17.8},
        ]
        
        created_count = 0
        updated_count = 0
        
        for location_data in sample_locations:
            location, created = MapLocation.objects.update_or_create(
                country=location_data['country'],
                city=location_data['city'],
                defaults={
                    'latitude': location_data['latitude'],
                    'longitude': location_data['longitude'],
                    'crop_yield': location_data.get('crop_yield'),
                    'soil_health': location_data.get('soil_health'),
                    'efficiency': location_data.get('efficiency'),
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {location}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {location}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully loaded {created_count} new locations'))
        self.stdout.write(self.style.SUCCESS(f'↻ Updated {updated_count} existing locations'))
        self.stdout.write(self.style.SUCCESS(f'📊 Total locations in database: {MapLocation.objects.count()}'))
