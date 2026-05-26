from typing import Tuple
from app.core.constants import SCOPE_1, SCOPE_2, SCOPE_3, FUEL_MAPPINGS

class ScopeClassifierService:
    @staticmethod
    def classify_scope(source_type: str, activity_indicator: str) -> Tuple[str, str]:
        """
        Determines the Greenhouse Gas (GHG) Protocol Scope and Category based on data source type and details.
        Returns: (scope_string, category_string)
        """
        source = source_type.strip().lower()
        indicator = activity_indicator.strip().lower()

        if source == "sap":
            standardized_fuel = FUEL_MAPPINGS.get(indicator, indicator)
            if standardized_fuel in ["diesel", "petrol", "propane", "heating_oil"]:
                return SCOPE_1, "Mobile/Stationary Combustion"
            elif standardized_fuel == "natural_gas":
                return SCOPE_1, "Stationary Combustion"
            else:
                return SCOPE_1, "Other Scope 1 Combustion"

        elif source == "utility":
            if "electricity" in indicator or "kwh" in indicator or "power" in indicator:
                return SCOPE_2, "Purchased Electricity"
            else:
                return SCOPE_2, "Purchased Heating/Cooling"

        elif source == "travel":
            if indicator == "flight":
                return SCOPE_3, "Business Travel - Air Travel"
            elif indicator == "hotel":
                return SCOPE_3, "Business Travel - Hotel Stays"
            elif indicator in ["taxi", "train", "cab", "transport"]:
                return SCOPE_3, "Business Travel - Land Transport"
            else:
                return SCOPE_3, "Business Travel - Other"

        return SCOPE_3, "General Activity"
scope_classifier_service = ScopeClassifierService()
