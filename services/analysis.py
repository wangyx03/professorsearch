
import json

from sqlalchemy import text
from services.database import SessionLocal


def get_student_profile(student_id):
    """Get the current profile for a student."""
    db = SessionLocal()

    try:
        row = db.execute(
            text("""
                SELECT
                    profile_id,
                    student_id,
                    profile_data,
                    module_results,
                    status,
                    model_name,
                    error_message,
                    created_at,
                    updated_at
                FROM student_profiles
                WHERE student_id = :student_id
                LIMIT 1
            """),
            {"student_id": student_id}
        ).mappings().first()

        if row is None:
            return None

        profile = dict(row)

        for field in ("profile_data", "module_results"):
            value = profile.get(field)

            if isinstance(value, str):
                try:
                    profile[field] = json.loads(value)
                except json.JSONDecodeError:
                    profile[field] = {}

            elif value is None:
                profile[field] = {}

        return profile

    finally:
        db.close()


def get_module_analysis_rows(modules, profile):
    """Combine configured modules with saved analysis results."""
    results = {}

    if profile:
        results = profile.get("module_results") or {}

    if not isinstance(results, dict):
        results = {}

    rows = []

    for module in modules:
        module = dict(module)

        module_id = str(module["module_id"])
        saved = results.get(module_id)

        status = "not_analyzed"
        model_name = ""
        analyzed_at = ""

        if isinstance(saved, dict):
            status = saved.get("status", "completed")
            model_name = saved.get("model", "")
            analyzed_at = saved.get("analyzed_at", "")

        elif saved is not None:
            status = "completed"

        rows.append({
            "module_id": module_id,
            "module_name": module.get("module_name", module_id),
            "description": module.get("description") or "",
            "sort_order": module.get("sort_order") or 0,
            "status": status,
            "model_name": model_name,
            "analyzed_at": analyzed_at,
            "has_result": saved is not None,
        })

    return rows
