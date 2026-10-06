"""Fertilizer and Seed Estimator for AgriPlan."""

import math
from typing import Any, Dict


def calculate_fertilizer_and_seeds(
    crop_info: Dict[str, Any],
    land_area: float,
    area_unit: str = "Acres",
    bag_weight_kg: float = 50.0,
) -> Dict[str, Any]:
    """
    Calculate elemental NPK requirements, commercial fertilizer bags (Urea, DAP, MOP),
    and total estimated seed requirement based on land area and unit.

    Args:
        crop_info: Dictionary containing crop metadata (seed_rate_kg_per_acre, npk_kg_per_acre)
        land_area: Numerical area (e.g., 2.5)
        area_unit: "Acres" or "Hectares"
        bag_weight_kg: Standard fertilizer bag weight (default 50 kg)

    Returns:
        dict with detailed calculations
    """
    if land_area <= 0:
        land_area = 1.0

    # Convert to acres if input is in hectares (1 hectare = 2.47105 acres)
    if area_unit.lower().startswith("hectare"):
        area_in_acres = land_area * 2.47105
        area_display = f"{land_area:.2f} Hectares ({area_in_acres:.2f} Acres)"
    else:
        area_in_acres = land_area
        area_display = f"{land_area:.2f} Acres"

    # Seed rate
    seed_rate_per_acre = float(crop_info.get("seed_rate_kg_per_acre", 1.0))
    total_seed_kg = area_in_acres * seed_rate_per_acre
    seed_unit = crop_info.get("seed_unit", "kg")

    # NPK requirement per acre
    npk_dict = crop_info.get("npk_kg_per_acre", {"N": 50, "P": 25, "K": 25})
    n_per_acre = float(npk_dict.get("N", 50))
    p_per_acre = float(npk_dict.get("P", 25))
    k_per_acre = float(npk_dict.get("K", 25))

    total_n_kg = n_per_acre * area_in_acres
    total_p_kg = p_per_acre * area_in_acres
    total_k_kg = k_per_acre * area_in_acres

    # Commercial fertilizer calculation:
    # 1. DAP (18% N, 46% P2O5) supplies P
    dap_kg = total_p_kg / 0.46 if total_p_kg > 0 else 0.0
    dap_bags = math.ceil(dap_kg / bag_weight_kg)

    # N supplied by DAP
    n_from_dap = dap_kg * 0.18

    # 2. Urea (46% N) supplies remaining N
    remaining_n_kg = max(0.0, total_n_kg - n_from_dap)
    urea_kg = remaining_n_kg / 0.46 if remaining_n_kg > 0 else 0.0
    urea_bags = math.ceil(urea_kg / bag_weight_kg)

    # 3. MOP (60% K2O) supplies K
    mop_kg = total_k_kg / 0.60 if total_k_kg > 0 else 0.0
    mop_bags = math.ceil(mop_kg / bag_weight_kg)

    return {
        "land_area": land_area,
        "area_unit": area_unit,
        "area_in_acres": round(area_in_acres, 2),
        "area_display": area_display,
        "seed": {
            "rate_per_acre": seed_rate_per_acre,
            "unit": seed_unit,
            "total_kg": round(total_seed_kg, 2),
            "display": f"{round(total_seed_kg, 2)} {seed_unit}",
        },
        "nutrients_pure_kg": {
            "Nitrogen (N)": round(total_n_kg, 1),
            "Phosphorus (P2O5)": round(total_p_kg, 1),
            "Potassium (K2O)": round(total_k_kg, 1),
        },
        "commercial_fertilizers": {
            "Urea (46% N)": {
                "kg_needed": round(urea_kg, 1),
                "bags_needed": urea_bags,
                "bag_weight_kg": bag_weight_kg,
                "application_tip": "Split into 2-3 top dressings across vegetative and tillering stages.",
            },
            "DAP (18:46:0)": {
                "kg_needed": round(dap_kg, 1),
                "bags_needed": dap_bags,
                "bag_weight_kg": bag_weight_kg,
                "application_tip": "Apply full quantity as basal dose at the time of sowing/transplanting.",
            },
            "MOP (60% K2O)": {
                "kg_needed": round(mop_kg, 1),
                "bags_needed": mop_bags,
                "bag_weight_kg": bag_weight_kg,
                "application_tip": "Apply half at basal and half during panicle/flowering initiation.",
            },
        },
    }
