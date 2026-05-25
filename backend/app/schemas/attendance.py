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
