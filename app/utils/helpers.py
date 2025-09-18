import hashlib
import random
import string

def generate_order_number(user_id: int) -> str:
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{user_id}-{random_part}"


def hash_string(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
