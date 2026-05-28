from fastapi import APIRouter, Depends, HTTPException

from app.blockchain.attendance_client import (
    mark_attendance_onchain,
    get_attendance_student_course,
    get_student_subject_percentages,
)
from app.db.mongo import db
from app.deps import get_current_user, require_role, serialize_doc, to_object_id
from app.schemas.attendance import AttendanceCreate, AttendanceOut, SearchAttendanceOut
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

    date_str = payload.date.isoformat()
    try:
        mark_attendance_onchain(payload.student_id,date_str,payload.course_id,payload.present)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Blockchain write failed: {exc}",
        ) from exc

    attendance_doc = {
        "course_id": payload.course_id,
        "date": date_str,
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

@router.get("/student", response_model=SearchAttendanceOut)
async def get_student_attendance(
    student_id: str,
    subject_code: str,
    user: UserPublic = Depends(get_current_user),
) -> SearchAttendanceOut:
    if user.role == "student" and user.id != student_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    remote = get_attendance_student_course(student_id, subject_code)
    if not isinstance(remote, list):
        raise HTTPException(status_code=502, detail="Blockchain read failed")

    try:
        attended_classes = sum(1 for i in remote if i.get("present") is True)
        total_classes = len(remote)
        attendance_percentage = (attended_classes / total_classes * 100.0) if total_classes else 0.0

        data = {
            "student_id": student_id,
            "subject_code": subject_code,
            "attendance_percentage": attendance_percentage,
            "total_classes": total_classes,
            "attended_classes": attended_classes,
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Blockchain read failed: {exc}") from exc

    return data



@router.get("/student/{student_id}/subjects", response_model=list[SearchAttendanceOut])
async def student_subjects(
    student_id: str,
    user: UserPublic = Depends(get_current_user),
) -> list[SearchAttendanceOut]:
    # students can only query their own data
    if user.role == "student" and user.id != student_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    remote = get_student_subject_percentages(student_id)
    if remote is None:
        raise HTTPException(status_code=502, detail="Blockchain read failed")

    results: list[SearchAttendanceOut] = []
    try:
        for item in remote:
            results.append(SearchAttendanceOut(**item))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Malformed blockchain response: {exc}") from exc

    return results

@router.get("/course/{course_id}/summary")
async def course_attendance_summary(
    course_id: str,
    user: UserPublic = Depends(require_role("teacher")),
) -> dict:
    course = await db.courses.find_one({"_id": to_object_id(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course["teacher_id"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    students: list[dict] = []
    async for enrollment in db.enrollments.find({"course_id": course_id}):
        student_id = enrollment["student_id"]
        total = await db.attendance.count_documents(
            {"course_id": course_id, "student_id": student_id}
        )
        present = await db.attendance.count_documents(
            {
                "course_id": course_id,
                "student_id": student_id,
                "present": True,
            }
        )
        percentage = (present / total * 100.0) if total else 0.0
        students.append(
            {
                "student_id": student_id,
                "present": present,
                "total": total,
                "percentage": percentage,
            }
        )

    return {
        "course_id": course_id,
        "course_code": course["code"],
        "students": students,
    }


@router.get("/student/{student_id}/summary")
async def student_attendance_summary(
    student_id: str,
    user: UserPublic = Depends(get_current_user),
) -> dict:
    if user.role == "student" and user.id != student_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    enrollments = []
    async for enrollment in db.enrollments.find({"student_id": student_id}):
        enrollments.append(enrollment)

    course_object_ids = []
    for enrollment in enrollments:
        try:
            course_object_ids.append(to_object_id(enrollment["course_id"]))
        except HTTPException:
            continue

    course_codes: dict[str, str] = {}
    if course_object_ids:
        async for course in db.courses.find({"_id": {"$in": course_object_ids}}):
            course_codes[str(course["_id"])] = course.get("code", "")

    courses: list[dict] = []
    for enrollment in enrollments:
        course_id = enrollment["course_id"]
        total = await db.attendance.count_documents(
            {"course_id": course_id, "student_id": student_id}
        )
        present = await db.attendance.count_documents(
            {
                "course_id": course_id,
                "student_id": student_id,
                "present": True,
            }
        )
        percentage = (present / total * 100.0) if total else 0.0
        courses.append(
            {
                "course_id": course_id,
                "course_code": course_codes.get(course_id, ""),
                "present": present,
                "total": total,
                "percentage": percentage,
            }
        )

    return {"student_id": student_id, "courses": courses}
