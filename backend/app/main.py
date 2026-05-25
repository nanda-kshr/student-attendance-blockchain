from fastapi import FastAPI

from app.routers import attendance, auth, courses

app = FastAPI(title="Student Attendance API")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(attendance.router)
