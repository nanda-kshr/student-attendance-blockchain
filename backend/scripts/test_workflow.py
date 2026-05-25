import os
import random
import time
from datetime import date

import requests


def base_url() -> str:
    port = os.environ.get("PORT", "4000")
    return f"http://127.0.0.1:{port}"


def post(path: str, token: str | None = None, payload: dict | None = None) -> dict:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.post(f"{base_url()}{path}", json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def get(path: str, token: str | None = None, params: dict | None = None) -> dict:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(f"{base_url()}{path}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def register_user(email: str, password: str, role: str) -> dict:
    return post(
        "/auth/register",
        payload={"email": email, "password": password, "role": role},
    )


def login_user(email: str, password: str) -> str:
    data = post("/auth/login", payload={"email": email, "password": password})
    return data["access_token"]


def main() -> None:
    suffix = str(int(time.time()))
    teacher_email = f"teacher_{suffix}@example.com"
    student_email = f"student_{suffix}@example.com"
    password = "Password123!"

    print("1) Teacher creates an account")
    register_user(teacher_email, password, "teacher")

    print("2) Teacher creates a course")
    teacher_token = login_user(teacher_email, password)
    course = post(
        "/courses",
        teacher_token,
        {"name": "Intro to Attendance", "code": f"ATT-{suffix}"},
    )
    course_id = course["id"]

    print("3) Register as a student")
    student = register_user(student_email, password, "student")
    student_token = login_user(student_email, password)

    print("4) Get all my courses (should be empty)")
    my_courses = get("/courses/enrolled", student_token)
    print("My courses:", my_courses)

    print("5) Get all other courses")
    other_courses = get("/courses/available", student_token)
    print("Other courses:", other_courses)

    print("6) Enroll the course")
    post(f"/courses/{course_id}/enroll", student_token)

    print("7) Login as a teacher")
    teacher_token = login_user(teacher_email, password)

    print("8) Show all teacher courses")
    teacher_courses = get("/courses", teacher_token)
    print("Teacher courses:", teacher_courses)

    print("9) Select first course")
    first_course = teacher_courses[0]
    first_course_id = first_course["id"]

    print("10) Get all students in the first course")
    students = get(f"/courses/{first_course_id}/students", teacher_token)
    print("Students:", students)

    print("11) Mark students present/absent randomly")
    today = date.today().isoformat()
    for entry in students:
        present = random.choice([True, False])
        post(
            "/attendance",
            teacher_token,
            {
                "course_id": first_course_id,
                "date": today,
                "student_id": entry["id"],
                "present": present,
            },
        )

    print("12) Login as a student")
    student_token = login_user(student_email, password)

    print("13) Get all my courses")
    my_courses = get("/courses/enrolled", student_token)
    print("My courses:", my_courses)

    print("14) Select the first enrolled course")
    enrolled_course_id = my_courses[0]["id"]

    print("15) Check the attendance")
    records = get("/attendance", student_token, {"course_id": enrolled_course_id})
    print("Attendance:", records)


if __name__ == "__main__":
    main()
