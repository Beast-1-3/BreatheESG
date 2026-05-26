from typing import Tuple, Optional
from app.core.constants import EMISSION_FACTORS, FUEL_MAPPINGS

class EmissionMapperService:
    @staticmethod
    def calculate_emissions(
        source_type: str,
        activity_type: str,
        normalized_value: Optional[float],
        travel_class: Optional[str] = None
    ) -> Tuple[Optional[float], Optional[float], float]:
        """
        Calculates estimated CO2 emissions in kg and retrieves appropriate emission factor.
        Returns: (estimated_emissions_kg, emission_factor, confidence_adjustment_factor)
        """
        if normalized_value is None or normalized_value < 0:
            return None, None, 0.0

        source = source_type.strip().lower()
        act = activity_type.strip().lower()

        factor = None
        confidence = 1.0

        if source == "sap":
            standard_fuel = FUEL_MAPPINGS.get(act, act)
            factor = EMISSION_FACTORS["sap"].get(standard_fuel)
            if not factor:
                # Default factor if unrecognized fuel
                factor = 2.0  
                confidence = 0.5  # Lower confidence due to fallback factor

        elif source == "utility":
            factor = EMISSION_FACTORS["utility"].get("electricity")

        elif source == "travel":
            if act == "flight":
                t_class = (travel_class or "economy").strip().lower()
                factor_key = f"flight_{t_class}"
                if factor_key not in EMISSION_FACTORS["travel"]:
                    factor_key = "flight_economy"
                factor = EMISSION_FACTORS["travel"].get(factor_key)
            elif act == "hotel":
                factor = EMISSION_FACTORS["travel"].get("hotel")
            elif act == "train":
                factor = EMISSION_FACTORS["travel"].get("train")
            elif act in ["taxi", "cab"]:
                factor = EMISSION_FACTORS["travel"].get("taxi")
            else:
                factor = 0.1  # Low default travel factor
                confidence = 0.4

        if factor is not None:
            emissions = normalized_value * factor
            return emissions, factor, confidence

        return None, None, 0.0
emission_mapper_service = EmissionMapperService()
