from fastapi import APIRouter, Query
from app.schemas.blockchain import DataCreate, DataOut, SearchOut
from app.deps.blackchain_instance import blockchain

router = APIRouter(prefix="/blockchain", tags=["blockchain"])


@router.post("", response_model=DataOut)
async def add_data(
    payload: DataCreate
) -> DataOut:
    try:
        data = payload.data
        blockchain.add_data(data)
    except Exception as e:
        return {"error": str(e)}
    return {"data": "success"}

@router.get("", response_model=SearchOut)
async def get_data(
    student_id: str = Query(None),
    subject_code: str = Query(None)
) -> SearchOut:
    try:
        mydata = blockchain.get_data(student_id=student_id, subject_code=subject_code)
        return {"data": mydata}
    except Exception as e:
        return {"error": str(e)}


@router.get("/student/{student_id}/subjects")
async def student_subjects_summary(student_id: str):
    """Return a list of subjects with attendance percentages for the given student."""
    try:
        records = blockchain.get_data(student_id=student_id)
        if not isinstance(records, list):
            return {"error": "No records found"}

        # group by subject_code (or course_id if subject_code missing)
        groups: dict[str, dict[str, int]] = {}
        for r in records:
            subj = r.get("subject_code") or r.get("course_id") or ""
            if subj == "":
                continue
            grp = groups.setdefault(subj, {"total": 0, "attended": 0})
            grp["total"] += 1
            if r.get("present") is True:
                grp["attended"] += 1

        result = []
        for subj, vals in groups.items():
            total = vals.get("total", 0)
            attended = vals.get("attended", 0)
            percentage = (attended / total * 100.0) if total else 0.0
            result.append({
                "subject_code": subj,
                "attendance_percentage": percentage,
                "total_classes": total,
                "attended_classes": attended,
            })

        return {"data": result}
    except Exception as e:
        return {"error": str(e)}