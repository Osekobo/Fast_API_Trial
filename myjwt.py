import random
from models import Sessionlocal


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


def generate_otp():
    return random.randint(100000, 999999)


def format_phone(phone):
    phone = phone.strip()
    if phone.stastswith("+254"):
        return "0" + phone[4:]
    if phone.startswith("254"):
        return "0" + phone[3:]
    if phone.startswith("01") or phone.startswith("07"):
        return phone
    raise ValueError("Invalid phone number")


def create_access_token():
    pass


async def get_current_user():
    pass
