# ESG Constants, Conversion Factors, and Master Data

# Scope Definitions
SCOPE_1 = "Scope 1"
SCOPE_2 = "Scope 2"
SCOPE_3 = "Scope 3"

# Source Types
SOURCE_SAP = "sap"
SOURCE_UTILITY = "utility"
SOURCE_TRAVEL = "travel"

# Validation Statuses
STATUS_PENDING = "pending"
STATUS_VALIDATED = "validated"
STATUS_FLAGGED = "flagged"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_LOCKED = "locked"

# Validation Issue Categories
ISSUE_DUPLICATE = "duplicate"
ISSUE_NEGATIVE_VALUE = "negative_value"
ISSUE_MISSING_VALUE = "missing_value"
ISSUE_INVALID_MAPPING = "invalid_mapping"
ISSUE_OVERLAPPING_CYCLE = "overlapping_cycle"
ISSUE_ANOMALY = "anomaly"
ISSUE_INVALID_UNIT = "invalid_unit"
ISSUE_INVALID_AIRPORT = "invalid_airport"

# Unit Conversion (to Normalized Base Units)
# Base Units: Liters (liquid fuel), Cubic Meters (gas), kWh (electricity), Passenger-km (travel distance), Room-nights (hotel)
UNIT_CONVERSIONS = {
    # Liquid Volume (Base: Liters - L)
    "l": 1.0,
    "liter": 1.0,
    "liters": 1.0,
    "litre": 1.0,
    "litres": 1.0,
    "gal": 3.78541,
    "gallon": 3.78541,
    "gallons": 3.78541,
    "kl": 1000.0,
    "kiloliter": 1000.0,
    "kiloliters": 1000.0,
    
    # Gas Volume (Base: Cubic Meters - m3)
    "m3": 1.0,
    "cubic meter": 1.0,
    "cubic meters": 1.0,
    "cf": 0.0283168,
    "cubic feet": 0.0283168,
    
    # Weight (Base: Kilograms - kg)
    "kg": 1.0,
    "kilogram": 1.0,
    "kilograms": 1.0,
    "lbs": 0.453592,
    "pounds": 0.453592,
    "ton": 907.185,
    "metric ton": 1000.0,
    "t": 1000.0,
    
    # Electricity (Base: kWh)
    "kwh": 1.0,
    "mwh": 1000.0,
    
    # Travel Distance (Base: km)
    "km": 1.0,
    "kilometer": 1.0,
    "kilometers": 1.0,
    "miles": 1.60934,
    "mi": 1.60934,
    
    # Hotel (Base: nights)
    "nights": 1.0,
    "night": 1.0
}

# Emission Factors (kg CO2e per Normalized Unit)
EMISSION_FACTORS = {
    # Scope 1 (SAP Fuel) - per normalized unit
    "sap": {
        "diesel": 2.68,        # kg CO2e per Liter
        "heating_oil": 2.68,   # kg CO2e per Liter (Heizöl)
        "natural_gas": 1.91,   # kg CO2e per m3 (Erdgas)
        "petrol": 2.31,        # kg CO2e per Liter (Benzin)
        "propane": 1.51,       # kg CO2e per Liter (Propangas) - if volume. per kg: 3.0
    },
    # Scope 2 (Electricity) - per kWh
    "utility": {
        "electricity": 0.385,  # kg CO2e per kWh (standard grid average)
    },
    # Scope 3 (Travel API) - per passenger-km or hotel night
    "travel": {
        "flight_economy": 0.15,  # kg CO2e per passenger-km
        "flight_business": 0.29, # kg CO2e per passenger-km (higher multiplier)
        "flight_first": 0.44,    # kg CO2e per passenger-km
        "hotel": 15.0,           # kg CO2e per night (room average)
        "train": 0.04,           # kg CO2e per passenger-km
        "taxi": 0.18,            # kg CO2e per km
    }
}

# Mapping of raw fuel names to standardized fuel IDs
FUEL_MAPPINGS = {
    "diesel": "diesel",
    "diesel oil": "diesel",
    "heizöl": "heating_oil",
    "heating oil": "heating_oil",
    "erdgas": "natural_gas",
    "natural gas": "natural_gas",
    "gas": "natural_gas",
    "benzin": "petrol",
    "gasoline": "petrol",
    "petrol": "petrol",
    "propangas": "propane",
    "propane": "propane"
}

# Registered Plant Codes (Multi-tenancy asset validations)
REGISTERED_PLANTS = {
    "PL-001": {"name": "Frankfurt Plant 1", "region": "DE-HE"},
    "PL-002": {"name": "Munich Logistics Hub", "region": "DE-BY"},
    "PL-003": {"name": "London Office HQ", "region": "GB-ENG"}
}

# Registered Meters
REGISTERED_METERS = {
    "MTR-1001": {"plant_code": "PL-001", "provider": "Vattenfall"},
    "MTR-1002": {"plant_code": "PL-002", "provider": "E.ON"},
    "MTR-1003": {"plant_code": "PL-003", "provider": "British Gas"}
}

# Airport Database (for distance verification / calculations)
# Coordinates (Lat, Lon)
AIRPORT_COORDINATES = {
    "LHR": (51.4700, -0.4543),
    "JFK": (40.6413, -73.7781),
    "CDG": (49.0097, 2.5479),
    "DXB": (25.2532, 55.3657),
    "SIN": (1.3644, 103.9915),
    "HND": (35.5494, 139.7798),
    "SFO": (37.6213, -122.3790),
    "FRA": (50.0379, 8.5622)
}
