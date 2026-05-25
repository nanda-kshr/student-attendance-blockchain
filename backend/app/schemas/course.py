from pydantic import BaseModel


class CourseCreate(BaseModel):
    name: str
    code: str


class CourseUpdate(BaseModel):
    name: str | None = None
    code: str | None = None


class CourseOut(BaseModel):
    id: str
    name: str
    code: str
    teacher_id: str
