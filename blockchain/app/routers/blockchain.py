from fastapi import APIRouter
from app.schemas.blockchain import DataCreate, DataOut
from app.deps.blackchain_instance import blockchain

router = APIRouter(prefix="/blockchain", tags=["blockchain"])


@router.post("", response_model=DataOut)
async def create_attendance(
    payload: DataCreate
) -> DataOut:
    try:
        data = payload.data
        blockchain.add_data(data)
    except Exception as e:
        return {"error": str(e)}
    return {"data": "success"}


# @router.get("", response_model=list[DataOut])
# async def list_attendance(
#     course_id: str | None = None,
#     user: UserPublic = Depends(require_role("student")),
# ) -> list[AttendanceOut]:
#     query = {"student_id": user.id}
#     if course_id:
#         query["course_id"] = course_id

#     records: list[AttendanceOut] = []
#     async for doc in db.attendance.find(query):
#         records.append(AttendanceOut(**serialize_doc(doc)))
#     return records


# @router.get("/course/{course_id}/summary")
# async def course_attendance_summary(
#     course_id: str,
#     user: UserPublic = Depends(require_role("teacher")),
# ) -> dict:
#     course = await db.courses.find_one({"_id": to_object_id(course_id)})
#     if not course:
#         raise HTTPException(status_code=404, detail="Course not found")
#     if course["teacher_id"] != user.id:
#         raise HTTPException(status_code=403, detail="Forbidden")

#     students: list[dict] = []
#     async for enrollment in db.enrollments.find({"course_id": course_id}):
#         student_id = enrollment["student_id"]
#         total = await db.attendance.count_documents(
#             {"course_id": course_id, "student_id": student_id}
#         )
#         present = await db.attendance.count_documents(
#             {
#                 "course_id": course_id,
#                 "student_id": student_id,
#                 "present": True,
#             }
#         )
#         percentage = (present / total * 100.0) if total else 0.0
#         students.append(
#             {
#                 "student_id": student_id,
#                 "present": present,
#                 "total": total,
#                 "percentage": percentage,
#             }
#         )

#     return {
#         "course_id": course_id,
#         "course_code": course["code"],
#         "students": students,
#     }


# @router.get("/student/{student_id}/summary")
# async def student_attendance_summary(
#     student_id: str,
#     user: UserPublic = Depends(get_current_user),
# ) -> dict:
#     if user.role == "student" and user.id != student_id:
#         raise HTTPException(status_code=403, detail="Forbidden")

#     enrollments = []
#     async for enrollment in db.enrollments.find({"student_id": student_id}):
#         enrollments.append(enrollment)

#     course_object_ids = []
#     for enrollment in enrollments:
#         try:
#             course_object_ids.append(to_object_id(enrollment["course_id"]))
#         except HTTPException:
#             continue

#     course_codes: dict[str, str] = {}
#     if course_object_ids:
#         async for course in db.courses.find({"_id": {"$in": course_object_ids}}):
#             course_codes[str(course["_id"])] = course.get("code", "")

#     courses: list[dict] = []
#     for enrollment in enrollments:
#         course_id = enrollment["course_id"]
#         total = await db.attendance.count_documents(
#             {"course_id": course_id, "student_id": student_id}
#         )
#         present = await db.attendance.count_documents(
#             {
#                 "course_id": course_id,
#                 "student_id": student_id,
#                 "present": True,
#             }
#         )
#         percentage = (present / total * 100.0) if total else 0.0
#         courses.append(
#             {
#                 "course_id": course_id,
#                 "course_code": course_codes.get(course_id, ""),
#                 "present": present,
#                 "total": total,
#                 "percentage": percentage,
#             }
#         )

#     return {"student_id": student_id, "courses": courses}
