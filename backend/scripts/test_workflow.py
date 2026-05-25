import os
import random
import time
from datetime import date

import requests


def base_url() -> str:
    port = os.environ.get("PORT", "5000")
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
    student_emails = [f"student_{suffix}_{i}@example.com" for i in range(5)]
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

    print("3) 5 Students create accounts")
    students: list[dict] = []
    for email in student_emails:
        students.append(register_user(email, password, "student"))

    print("4) 5 Students enroll in the course")
    student_tokens: list[str] = []
    for email in student_emails:
        token = login_user(email, password)
        student_tokens.append(token)
        post(f"/courses/{course_id}/enroll", token)

    print("5) Teacher logs in")
    teacher_token = login_user(teacher_email, password)

    print("6) Marks attendance (random 2/5 students are absent)")
    absent_indexes = set(random.sample(range(len(students)), 2))
    today = date.today().isoformat()
    for idx, student in enumerate(students):
        present = idx not in absent_indexes
        post(
            "/attendance",
            teacher_token,
            {
                "course_id": course_id,
                "date": today,
                "student_id": student["id"],
                "present": present,
            },
        )

    print("7) Students log in")
    student_tokens = [login_user(email, password) for email in student_emails]

    print("8) Students check attendance")
    for email, token in zip(student_emails, student_tokens):
        records = get("/attendance", token, {"course_id": course_id})
        print(email, records)


if __name__ == "__main__":
    main()
