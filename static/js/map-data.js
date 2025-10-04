/**
 * Map Data - Countries and Cities with Coordinates
 * Green Vision Technology Map
 */

const mapData = {
    "United States": {
        coords: [37.0902, -95.7129],
        zoom: 4,
        cities: {
            "New York": [40.7128, -74.0060],
            "Los Angeles": [34.0522, -118.2437],
            "Chicago": [41.8781, -87.6298],
            "Houston": [29.7604, -95.3698],
            "Phoenix": [33.4484, -112.0740],
            "San Francisco": [37.7749, -122.4194],
            "Miami": [25.7617, -80.1918],
            "Seattle": [47.6062, -122.3321]
        }
    },
    "United Kingdom": {
        coords: [55.3781, -3.4360],
        zoom: 6,
        cities: {
            "London": [51.5074, -0.1278],
            "Manchester": [53.4808, -2.2426],
            "Birmingham": [52.4862, -1.8904],
            "Liverpool": [53.4084, -2.9916],
            "Edinburgh": [55.9533, -3.1883],
            "Bristol": [51.4545, -2.5879],
            "Leeds": [53.8008, -1.5491]
        }
    },
    "France": {
        coords: [46.2276, 2.2137],
        zoom: 6,
        cities: {
            "Paris": [48.8566, 2.3522],
            "Marseille": [43.2965, 5.3698],
            "Lyon": [45.7640, 4.8357],
            "Toulouse": [43.6047, 1.4442],
            "Nice": [43.7102, 7.2620],
            "Nantes": [47.2184, -1.5536],
            "Bordeaux": [44.8378, -0.5792]
        }
    },
    "Germany": {
        coords: [51.1657, 10.4515],
        zoom: 6,
        cities: {
            "Berlin": [52.5200, 13.4050],
            "Munich": [48.1351, 11.5820],
            "Hamburg": [53.5511, 9.9937],
            "Frankfurt": [50.1109, 8.6821],
            "Cologne": [50.9375, 6.9603],
            "Stuttgart": [48.7758, 9.1829],
            "Düsseldorf": [51.2277, 6.7735]
        }
    },
    "Japan": {
        coords: [36.2048, 138.2529],
        zoom: 5,
        cities: {
            "Tokyo": [35.6762, 139.6503],
            "Osaka": [34.6937, 135.5023],
            "Kyoto": [35.0116, 135.7681],
            "Yokohama": [35.4437, 139.6380],
            "Nagoya": [35.1815, 136.9066],
            "Sapporo": [43.0642, 141.3469],
            "Fukuoka": [33.5904, 130.4017]
        }
    },
    "China": {
        coords: [35.8617, 104.1954],
        zoom: 4,
        cities: {
            "Beijing": [39.9042, 116.4074],
            "Shanghai": [31.2304, 121.4737],
            "Guangzhou": [23.1291, 113.2644],
            "Shenzhen": [22.5431, 114.0579],
            "Chengdu": [30.5728, 104.0668],
            "Hangzhou": [30.2741, 120.1551],
            "Xi'an": [34.3416, 108.9398]
        }
    },
    "India": {
        coords: [20.5937, 78.9629],
        zoom: 5,
        cities: {
            "New Delhi": [28.6139, 77.2090],
            "Mumbai": [19.0760, 72.8777],
            "Bangalore": [12.9716, 77.5946],
            "Hyderabad": [17.3850, 78.4867],
            "Chennai": [13.0827, 80.2707],
            "Kolkata": [22.5726, 88.3639],
            "Pune": [18.5204, 73.8567]
        }
    },
    "Brazil": {
        coords: [-14.2350, -51.9253],
        zoom: 4,
        cities: {
            "São Paulo": [-23.5505, -46.6333],
            "Rio de Janeiro": [-22.9068, -43.1729],
            "Brasília": [-15.8267, -47.9218],
            "Salvador": [-12.9714, -38.5014],
            "Fortaleza": [-3.7172, -38.5433],
            "Belo Horizonte": [-19.9167, -43.9345],
            "Manaus": [-3.1190, -60.0217]
        }
    },
    "Australia": {
        coords: [-25.2744, 133.7751],
        zoom: 4,
        cities: {
            "Sydney": [-33.8688, 151.2093],
            "Melbourne": [-37.8136, 144.9631],
            "Brisbane": [-27.4698, 153.0251],
            "Perth": [-31.9505, 115.8605],
            "Adelaide": [-34.9285, 138.6007],
            "Canberra": [-35.2809, 149.1300],
            "Gold Coast": [-28.0167, 153.4000]
        }
    },
    "Canada": {
        coords: [56.1304, -106.3468],
        zoom: 4,
        cities: {
            "Toronto": [43.6532, -79.3832],
            "Vancouver": [49.2827, -123.1207],
            "Montreal": [45.5017, -73.5673],
            "Calgary": [51.0447, -114.0719],
            "Ottawa": [45.4215, -75.6972],
            "Edmonton": [53.5461, -113.4938],
            "Quebec City": [46.8139, -71.2080]
        }
    },
    "Egypt": {
        coords: [26.8206, 30.8025],
        zoom: 6,
        cities: {
            "Cairo": [30.0444, 31.2357],
            "Alexandria": [31.2001, 29.9187],
            "Giza": [30.0131, 31.2089],
            "Luxor": [25.6872, 32.6396],
            "Aswan": [24.0889, 32.8998],
            "Port Said": [31.2653, 32.3019],
            "Suez": [29.9668, 32.5498]
        }
    },
    "South Africa": {
        coords: [-30.5595, 22.9375],
        zoom: 5,
        cities: {
            "Johannesburg": [-26.2041, 28.0473],
            "Cape Town": [-33.9249, 18.4241],
            "Durban": [-29.8587, 31.0218],
            "Pretoria": [-25.7479, 28.2293],
            "Port Elizabeth": [-33.9608, 25.6022],
            "Bloemfontein": [-29.0852, 26.1596]
        }
    },
    "Mexico": {
        coords: [23.6345, -102.5528],
        zoom: 5,
        cities: {
            "Mexico City": [19.4326, -99.1332],
            "Guadalajara": [20.6597, -103.3496],
            "Monterrey": [25.6866, -100.3161],
            "Cancún": [21.1619, -86.8515],
            "Tijuana": [32.5149, -117.0382],
            "Puebla": [19.0414, -98.2063]
        }
    },
    "Italy": {
        coords: [41.8719, 12.5674],
        zoom: 6,
        cities: {
            "Rome": [41.9028, 12.4964],
            "Milan": [45.4642, 9.1900],
            "Naples": [40.8518, 14.2681],
            "Turin": [45.0703, 7.6869],
            "Florence": [43.7696, 11.2558],
            "Venice": [45.4408, 12.3155]
        }
    },
    "Spain": {
        coords: [40.4637, -3.7492],
        zoom: 6,
        cities: {
            "Madrid": [40.4168, -3.7038],
            "Barcelona": [41.3851, 2.1734],
            "Valencia": [39.4699, -0.3763],
            "Seville": [37.3891, -5.9845],
            "Bilbao": [43.2630, -2.9350],
            "Málaga": [36.7213, -4.4214]
        }
    }
};
