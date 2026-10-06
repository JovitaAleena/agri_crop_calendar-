"""Date math & schedule generator for AgriPlan."""

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd


DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "crops.json"


def load_crops_data(filepath: Optional[Path] = None) -> Dict[str, Any]:
    """Load crop definitions and stages from crops.json."""
    path = filepath or DEFAULT_DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Crop database file not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_crop_list(crops_data: Dict[str, Any]) -> List[str]:
    """Return available crop names."""
    return list(crops_data.keys())


def generate_crop_schedule(
    crop_name: str,
    sowing_date: date,
    crops_data: Optional[Dict[str, Any]] = None,
    reference_date: Optional[date] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Generate dynamic calendar schedule for the selected crop and sowing date.

    Returns:
        tuple: (DataFrame of stage details, Dict of summary metrics)
    """
    if crops_data is None:
        crops_data = load_crops_data()

    if crop_name not in crops_data:
        raise ValueError(f"Crop '{crop_name}' is not in database.")

    crop_info = crops_data[crop_name]
    stages_raw = crop_info.get("stages", [])
    total_duration = int(crop_info.get("growth_duration_days", 100))

    today = reference_date or date.today()
    days_elapsed = (today - sowing_date).days

    if days_elapsed < 0:
        progress_pct = 0.0
    elif total_duration > 0:
        progress_pct = min(100.0, max(0.0, (days_elapsed / total_duration) * 100.0))
    else:
        progress_pct = 0.0

    harvest_date = sowing_date + timedelta(days=total_duration)

    records = []
    next_task = None
    min_upcoming_diff = float("inf")

    for idx, stage in enumerate(stages_raw):
        day_offset = int(stage.get("day_offset", 0))
        duration = int(stage.get("duration_days", 7))
        target_date = sowing_date + timedelta(days=day_offset)
        end_date = target_date + timedelta(days=max(1, duration))

        # Determine status
        if target_date < today:
            status = "Completed"
            status_badge = "🟢 Completed"
        elif target_date == today:
            status = "Due Today"
            status_badge = "🟠 Due Today"
        else:
            status = "Upcoming"
            status_badge = "🔵 Upcoming"

        days_diff = (target_date - today).days

        # Identify next immediate task (earliest task today or in future)
        if days_diff >= 0 and days_diff < min_upcoming_diff:
            min_upcoming_diff = days_diff
            next_task = {
                "stage": stage.get("stage", f"Stage {idx+1}"),
                "target_date": target_date,
                "days_diff": days_diff,
                "action": stage.get("action", ""),
                "category": stage.get("category", "General"),
            }

        records.append({
            "stage_id": idx + 1,
            "stage": stage.get("stage", f"Stage {idx+1}"),
            "category": stage.get("category", "General"),
            "day_offset": day_offset,
            "target_date": target_date,
            "end_date": end_date,
            "duration_days": duration,
            "status": status,
            "status_badge": status_badge,
            "action": stage.get("action", ""),
            "details": stage.get("details", ""),
            "days_diff": days_diff,
        })

    df = pd.DataFrame(records)

    # If all tasks are completed
    if next_task is None and len(records) > 0:
        next_task = {
            "stage": "All Scheduled Stages Completed",
            "target_date": harvest_date,
            "days_diff": (harvest_date - today).days,
            "action": "Harvest completed or awaiting post-harvest storage/sales.",
            "category": "Harvesting",
        }

    summary = {
        "crop_name": crop_name,
        "sowing_date": sowing_date,
        "total_duration_days": total_duration,
        "harvest_date": harvest_date,
        "days_elapsed": days_elapsed,
        "progress_pct": round(progress_pct, 1),
        "next_task": next_task,
        "total_tasks": len(records),
        "completed_tasks": sum(1 for r in records if r["status"] == "Completed"),
        "due_today_tasks": sum(1 for r in records if r["status"] == "Due Today"),
        "upcoming_tasks": sum(1 for r in records if r["status"] == "Upcoming"),
        "description": crop_info.get("description", ""),
        "seed_rate_kg_per_acre": crop_info.get("seed_rate_kg_per_acre", 1.0),
        "seed_unit": crop_info.get("seed_unit", "kg"),
        "npk_kg_per_acre": crop_info.get("npk_kg_per_acre", {"N": 50, "P": 25, "K": 25}),
    }

    return df, summary
