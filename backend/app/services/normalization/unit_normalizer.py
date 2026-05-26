from typing import Tuple, Optional
from app.utils.unit_converter import convert_unit

class UnitNormalizerService:
    @staticmethod
    def normalize_record_unit(amount_str: str, unit_str: str) -> Tuple[Optional[float], Optional[str], float]:
        """
        Normalizes a string amount and unit name to base floats and standard strings.
        Returns: (normalized_value, normalized_unit, confidence_score)
        """
        if not amount_str or not unit_str:
            return None, None, 0.5  # Low confidence due to missing unit or amount

        # Clean amount string (handles German comma decimals, e.g. 3,5 to 3.5)
        amount_clean = amount_str.replace(",", ".").replace(" ", "")
        try:
            val = float(amount_clean)
        except ValueError:
            return None, None, 0.2  # Very low confidence, unparseable float

        norm_val, norm_unit = convert_unit(val, unit_str)
        if norm_val is not None:
            return norm_val, norm_unit, 1.0
            
        return val, unit_str, 0.5  # Unknown unit but kept original value, lower confidence
unit_normalizer_service = UnitNormalizerService()
