from fastapi import APIRouter, Depends, HTTPException

from app.db.mongo import db
from app.deps import require_role, serialize_doc, to_object_id
from app.schemas.attendance import AttendanceCreate, AttendanceOut
from app.schemas.user import UserPublic

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("", response_model=AttendanceOut)
async def create_attendance(
    payload: AttendanceCreate, user: UserPublic = Depends(require_role("teacher"))
) -> AttendanceOut:
    course = await db.courses.find_one({"_id": to_object_id(payload.course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course["teacher_id"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    enrolled = await db.enrollments.find_one(
        {"course_id": payload.course_id, "student_id": payload.student_id}
    )
    if not enrolled:
        raise HTTPException(status_code=400, detail="Student not enrolled")

    attendance_doc = {
        "course_id": payload.course_id,
        "date": payload.date.isoformat(),
        "student_id": payload.student_id,
        "present": payload.present,
        "teacher_id": user.id,
    }
    result = await db.attendance.insert_one(attendance_doc)
    attendance_doc["_id"] = result.inserted_id
    return AttendanceOut(**serialize_doc(attendance_doc))


@router.get("", response_model=list[AttendanceOut])
async def list_attendance(
    course_id: str | None = None,
    user: UserPublic = Depends(require_role("student")),
) -> list[AttendanceOut]:
    query = {"student_id": user.id}
    if course_id:
        query["course_id"] = course_id

    records: list[AttendanceOut] = []
    async for doc in db.attendance.find(query):
        records.append(AttendanceOut(**serialize_doc(doc)))
    return records
