from fastapi import FastAPI

from app.routers import blockchain as blockchainRounter

app = FastAPI(title="Student Attendance API")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(blockchainRounter.router)
