
from sqlalchemy import text
from services.database import SessionLocal


def get_modules():
    with SessionLocal() as db:
        rows = db.execute(text("""
            SELECT
                module_id,
                module_name,
                description,
                enabled,
                is_core,
                sort_order,
                instructions,
                output_type,
                created_at,
                updated_at
            FROM modules
            ORDER BY sort_order ASC, module_id ASC
        """)).mappings().all()

        return [dict(row) for row in rows]


def get_module(module_id):
    with SessionLocal() as db:
        row = db.execute(text("""
            SELECT
                module_id,
                module_name,
                description,
                enabled,
                is_core,
                sort_order,
                instructions,
                output_type,
                created_at,
                updated_at
            FROM modules
            WHERE module_id = :module_id
        """), {
            "module_id": module_id
        }).mappings().first()

        return dict(row) if row else None


def create_module(
    module_id,
    module_name,
    instructions,
    description=None,
    enabled=True,
    is_core=False,
    sort_order=100,
    output_type="json",
):
    module_id = module_id.strip()
    module_name = module_name.strip()
    instructions = instructions.strip()

    if not module_id:
        raise ValueError("Module ID is required.")

    if not module_name:
        raise ValueError("Module name is required.")

    if not instructions:
        raise ValueError("Instructions are required.")

    with SessionLocal() as db:
        db.execute(text("""
            INSERT INTO modules (
                module_id,
                module_name,
                description,
                enabled,
                is_core,
                sort_order,
                instructions,
                output_type
            )
            VALUES (
                :module_id,
                :module_name,
                :description,
                :enabled,
                :is_core,
                :sort_order,
                :instructions,
                :output_type
            )
        """), {
            "module_id": module_id,
            "module_name": module_name,
            "description": description or None,
            "enabled": enabled,
            "is_core": is_core,
            "sort_order": sort_order,
            "instructions": instructions,
            "output_type": output_type,
        })

        db.commit()


def update_module(
    module_id,
    module_name,
    instructions,
    description=None,
    enabled=True,
    is_core=False,
    sort_order=100,
    output_type="json",
):
    module_name = module_name.strip()
    instructions = instructions.strip()

    if not module_name:
        raise ValueError("Module name is required.")

    if not instructions:
        raise ValueError("Instructions are required.")

    with SessionLocal() as db:
        result = db.execute(text("""
            UPDATE modules
            SET
                module_name = :module_name,
                description = :description,
                enabled = :enabled,
                is_core = :is_core,
                sort_order = :sort_order,
                instructions = :instructions,
                output_type = :output_type
            WHERE module_id = :module_id
        """), {
            "module_id": module_id,
            "module_name": module_name,
            "description": description or None,
            "enabled": enabled,
            "is_core": is_core,
            "sort_order": sort_order,
            "instructions": instructions,
            "output_type": output_type,
        })

        db.commit()
        return result.rowcount > 0


def delete_module(module_id):
    with SessionLocal() as db:
        result = db.execute(text("""
            DELETE FROM modules
            WHERE module_id = :module_id
        """), {
            "module_id": module_id
        })

        db.commit()
        return result.rowcount > 0
