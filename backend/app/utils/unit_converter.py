from typing import Tuple, Optional
from app.core.constants import UNIT_CONVERSIONS

def convert_unit(value: float, unit_str: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Converts a given value and unit string to a standardized base value and unit.
    Returns: (converted_value, standardized_unit_name) or (None, None) if unsupported.
    """
    if value is None:
        return None, None
        
    unit_clean = unit_str.strip().lower()
    
    # Determine normalized category base unit
    # 1. Volume/Fuel
    if unit_clean in ["l", "liter", "liters", "litre", "litres", "gal", "gallon", "gallons", "kl", "kiloliter", "kiloliters"]:
        normalized_unit = "L"
        factor = UNIT_CONVERSIONS.get(unit_clean, 1.0)
        return value * factor, normalized_unit
        
    # 2. Gas
    elif unit_clean in ["m3", "cubic meter", "cubic meters", "cf", "cubic feet"]:
        normalized_unit = "m3"
        factor = UNIT_CONVERSIONS.get(unit_clean, 1.0)
        return value * factor, normalized_unit
        
    # 3. Weight
    elif unit_clean in ["kg", "kilogram", "kilograms", "lbs", "pounds", "ton", "metric ton", "t"]:
        normalized_unit = "kg"
        factor = UNIT_CONVERSIONS.get(unit_clean, 1.0)
        return value * factor, normalized_unit
        
    # 4. Electricity
    elif unit_clean in ["kwh", "mwh"]:
        normalized_unit = "kWh"
        factor = UNIT_CONVERSIONS.get(unit_clean, 1.0)
        return value * factor, normalized_unit
        
    # 5. Travel Distance
    elif unit_clean in ["km", "kilometer", "kilometers", "miles", "mi"]:
        normalized_unit = "km"
        factor = UNIT_CONVERSIONS.get(unit_clean, 1.0)
        return value * factor, normalized_unit
        
    # 6. Hotel
    elif unit_clean in ["nights", "night"]:
        normalized_unit = "nights"
        return value, normalized_unit

    return None, None
