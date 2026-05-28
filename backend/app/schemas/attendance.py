from datetime import date

from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    course_id: str
    date: date
    student_id: str
    present: bool


class AttendanceOut(BaseModel):
    id: str
    course_id: str
    date: date
    student_id: str
    present: bool
    teacher_id: str

class SearchAttendance(BaseModel):
    student_id: str | None = None
    subject_code: str | None = None

class SearchAttendanceOut(BaseModel):
    student_id: str | None = None
    subject_code: str | None = None
    attendance_percentage: float | None = None
    total_classes: int | None = None
    attended_classes: int | None = None
