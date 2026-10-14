
from sqlalchemy import text
from services.database import SessionLocal


def get_students():
    with SessionLocal() as db:
        rows = db.execute(
            text("""
                SELECT
                    student_id,
                    full_name,
                    email,
                    phone,
                    wechat_id,
                    notes,
                    created_at
                FROM students
                ORDER BY student_id DESC
            """)
        ).mappings().all()

        return [dict(row) for row in rows]


def create_student(full_name, email=None, phone=None,
                   wechat_id=None, notes=None):

    full_name = full_name.strip()

    if not full_name:
        raise ValueError("Student name is required.")

    with SessionLocal() as db:
        result = db.execute(
            text("""
                INSERT INTO students (
                    full_name,
                    email,
                    phone,
                    wechat_id,
                    notes
                )
                VALUES (
                    :full_name,
                    :email,
                    :phone,
                    :wechat_id,
                    :notes
                )
            """),
            {
                "full_name": full_name,
                "email": email or None,
                "phone": phone or None,
                "wechat_id": wechat_id or None,
                "notes": notes or None,
            },
        )

        student_id = result.lastrowid
        db.commit()

        return student_id


def get_student(student_id):
    with SessionLocal() as db:
        row = db.execute(
            text("""
                SELECT
                    student_id,
                    full_name,
                    email,
                    phone,
                    wechat_id,
                    notes
                FROM students
                WHERE student_id = :student_id
            """),
            {"student_id": student_id},
        ).mappings().first()

        return dict(row) if row else None



def update_student(student_id, full_name, email=None,
                   phone=None, wechat_id=None, notes=None):

    full_name = full_name.strip()

    if not full_name:
        raise ValueError("Student name is required.")

    with SessionLocal() as db:
        result = db.execute(
            text("""
                UPDATE students
                SET full_name = :full_name,
                    email = :email,
                    phone = :phone,
                    wechat_id = :wechat_id,
                    notes = :notes
                WHERE student_id = :student_id
            """),
            {
                "student_id": student_id,
                "full_name": full_name,
                "email": email or None,
                "phone": phone or None,
                "wechat_id": wechat_id or None,
                "notes": notes or None,
            },
        )

        db.commit()

        return result.rowcount > 0
