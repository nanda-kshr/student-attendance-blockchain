from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.db.mongo import db
from app.deps import get_current_user, require_role, serialize_doc, to_object_id
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate
from app.schemas.user import UserPublic

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseOut)
async def create_course(
    payload: CourseCreate, user: UserPublic = Depends(require_role("teacher"))
) -> CourseOut:
    course_doc = {
        "name": payload.name,
        "code": payload.code,
        "teacher_id": user.id,
    }
    result = await db.courses.insert_one(course_doc)
    course_doc["_id"] = result.inserted_id
    return CourseOut(**serialize_doc(course_doc))


@router.get("", response_model=list[CourseOut])
async def list_courses(
    mine: bool = False, user: UserPublic = Depends(get_current_user)
) -> list[CourseOut]:
    if mine and user.role != "teacher":
        raise HTTPException(status_code=403, detail="Forbidden")

    query = {"teacher_id": user.id} if user.role == "teacher" else {}

    courses = []
    async for doc in db.courses.find(query):
        courses.append(CourseOut(**serialize_doc(doc)))
    return courses


@router.get("/enrolled", response_model=list[CourseOut])
async def list_enrolled_courses(
    user: UserPublic = Depends(require_role("student")),
) -> list[CourseOut]:
    course_ids: list[ObjectId] = []
    async for enrollment in db.enrollments.find({"student_id": user.id}):
        try:
            course_ids.append(to_object_id(enrollment["course_id"]))
        except HTTPException:
            continue

    if not course_ids:
        return []

    courses: list[CourseOut] = []
    async for doc in db.courses.find({"_id": {"$in": course_ids}}):
        courses.append(CourseOut(**serialize_doc(doc)))
    return courses


@router.get("/available", response_model=list[CourseOut])
async def list_available_courses(
    user: UserPublic = Depends(require_role("student")),
) -> list[CourseOut]:
    enrolled_ids: list[ObjectId] = []
    async for enrollment in db.enrollments.find({"student_id": user.id}):
        try:
            enrolled_ids.append(to_object_id(enrollment["course_id"]))
        except HTTPException:
            continue

    query = {"_id": {"$nin": enrolled_ids}} if enrolled_ids else {}
    courses: list[CourseOut] = []
    async for doc in db.courses.find(query):
        courses.append(CourseOut(**serialize_doc(doc)))
    return courses


@router.get("/{course_id}", response_model=CourseOut)
async def get_course(
    course_id: str, user: UserPublic = Depends(get_current_user)
) -> CourseOut:
    doc = await db.courses.find_one({"_id": to_object_id(course_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Course not found")
    return CourseOut(**serialize_doc(doc))


@router.put("/{course_id}", response_model=CourseOut)
async def update_course(
    course_id: str,
    payload: CourseUpdate,
    user: UserPublic = Depends(require_role("teacher")),
) -> CourseOut:
    doc = await db.courses.find_one({"_id": to_object_id(course_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Course not found")
    if doc["teacher_id"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    update_doc = {k: v for k, v in payload.model_dump().items() if v is not None}
    if update_doc:
        await db.courses.update_one({"_id": doc["_id"]}, {"$set": update_doc})
        doc.update(update_doc)
    return CourseOut(**serialize_doc(doc))


@router.delete("/{course_id}")
async def delete_course(
    course_id: str, user: UserPublic = Depends(require_role("teacher"))
) -> dict:
    doc = await db.courses.find_one({"_id": to_object_id(course_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Course not found")
    if doc["teacher_id"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await db.courses.delete_one({"_id": doc["_id"]})
    await db.enrollments.delete_many({"course_id": course_id})
    await db.attendance.delete_many({"course_id": course_id})
    return {"status": "deleted"}


@router.post("/{course_id}/enroll")
async def enroll_course(
    course_id: str, user: UserPublic = Depends(require_role("student"))
) -> dict:
    course = await db.courses.find_one({"_id": to_object_id(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = await db.enrollments.find_one(
        {"course_id": course_id, "student_id": user.id}
    )
    if existing:
        return {"status": "already-enrolled"}

    await db.enrollments.insert_one({"course_id": course_id, "student_id": user.id})
    return {"status": "enrolled"}


@router.get("/{course_id}/students", response_model=list[UserPublic])
async def list_course_students(
    course_id: str, user: UserPublic = Depends(require_role("teacher"))
) -> list[UserPublic]:
    course = await db.courses.find_one({"_id": to_object_id(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course["teacher_id"] != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    students: list[UserPublic] = []
    async for enrollment in db.enrollments.find({"course_id": course_id}):
        student = await db.users.find_one({"_id": to_object_id(enrollment["student_id"])})
        if student:
            students.append(UserPublic(**serialize_doc(student)))
    return students
