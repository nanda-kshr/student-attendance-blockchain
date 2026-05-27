import os
import random
import time
from datetime import date

import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from web3 import Web3


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


def load_contract() -> tuple[Web3, object] | None:
    rpc_url = os.environ.get("RPC_URL")
    contract_address = os.environ.get("CONTRACT_ADDRESS")
    if not rpc_url or not contract_address:
        print("Skipping chain verify: RPC_URL or CONTRACT_ADDRESS missing")
        return None

    abi_path = Path(__file__).resolve().parents[1] / "Attendance.json"
    with abi_path.open("r", encoding="utf-8") as file:
        abi = json.load(file)["abi"]

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("Skipping chain verify: RPC_URL not reachable")
        return None

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=abi,
    )
    return w3, contract


def main() -> None:
    load_dotenv()
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
    chain = load_contract()
    start_count = None
    if chain:
        w3, contract = chain
        start_count = contract.functions.getCount().call()
        print("On-chain count before:", start_count)

    today = date.today().isoformat()
    expected = []
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
        expected.append((entry["id"], today, first_course["code"], present))

    if chain and start_count is not None:
        expected_count = start_count + len(expected)
        end_count = contract.functions.getCount().call()
        attempts = 0
        while end_count < expected_count and attempts < 10:
            time.sleep(2)
            end_count = contract.functions.getCount().call()
            attempts += 1

        print("On-chain count after:", end_count)
        if end_count != expected_count:
            raise RuntimeError("On-chain count mismatch")

        for idx, record in enumerate(expected, start=0):
            chain_index = end_count - len(expected) + idx
            try:
                student_id, rec_date, subject_code, present = contract.functions.getRecord(
                    chain_index
                ).call()
            except Exception:
                student_id, rec_date, subject_code, present = contract.functions.records(
                    chain_index
                ).call()
            print(
                "On-chain record",
                chain_index,
                student_id,
                rec_date,
                subject_code,
                present,
            )
            if (student_id, rec_date, subject_code, present) != record:
                raise RuntimeError("On-chain record mismatch")
        print("On-chain verification passed")

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
