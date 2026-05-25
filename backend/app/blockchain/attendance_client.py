import json
from pathlib import Path

from web3 import Web3

from app.core.config import get_settings


def _load_abi() -> list[dict]:
    repo_root = Path(__file__).resolve().parents[3]
    abi_path = repo_root / "backend/Attendance.json"
    with abi_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data["abi"]


def get_attendance_contract() -> tuple[Web3, object]:
    settings = get_settings()
    if not settings.contract_address:
        raise RuntimeError("CONTRACT_ADDRESS is required")
    if not settings.rpc_url:
        raise RuntimeError("RPC_URL is required")

    w3 = Web3(Web3.HTTPProvider(settings.rpc_url))
    if not w3.is_connected():
        raise RuntimeError("RPC_URL is not reachable")
    abi = _load_abi()
    contract = w3.eth.contract(address=Web3.to_checksum_address(settings.contract_address), abi=abi)
    return w3, contract


def mark_attendance_onchain(student_id: str, date: str, subject_code: str, present: bool) -> str:
    settings = get_settings()
    if not settings.private_key:
        raise RuntimeError("PRIVATE_KEY is required")
    w3, contract = get_attendance_contract()
    account = w3.eth.account.from_key(settings.private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    tx = contract.functions.markAttendance(
        student_id,
        date,
        subject_code,
        present,
    ).build_transaction(
        {
            "from": account.address,
            "nonce": nonce,
            "gasPrice": w3.eth.gas_price,
        }
    )
    signed = w3.eth.account.sign_transaction(tx, settings.private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()
