import httpx

from app.core.config import get_settings

settings = get_settings()

def mark_attendance_onchain(student_id: str, date: str, subject_code: str, present: bool) -> None:
    data = {
        "data": {
            "student_id": student_id,
            "date": date,
            "subject_code": subject_code,
            "present": present,
        }
    }

    with httpx.Client() as client:
        bc_url = getattr(settings, 'blockchain_url', None)
        url = (settings.rpc_url or bc_url or "") + "/blockchain"
        print(url)
        response = client.post(url, json=data)
        print(response.text)


def get_attendance_student_course(student_id: str | int, subject_code: str | None = None):
    params = {"student_id": student_id}
    if subject_code is not None:
        params["subject_code"] = subject_code
    with httpx.Client() as client:
        bc_url = getattr(settings, 'blockchain_url', None)
        url = (settings.rpc_url or bc_url or "") + "/blockchain"
        print(url)
        response = client.get(url, params=params)
        print(response.json())
        return response.json()["data"]


def get_student_subject_percentages(student_id: str):
    with httpx.Client() as client:
        bc_url = getattr(settings, 'blockchain_url', None)
        url = (settings.rpc_url or bc_url or "") + f"/blockchain/student/{student_id}/subjects"
        response = client.get(url)
        try:
            return response.json().get("data")
        except Exception:
            return None

