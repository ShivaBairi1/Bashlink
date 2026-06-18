import re

def normalize_phone(raw: str | None) -> str | None:
    if not raw:
        return None
    s = re.sub(r'[^0-9]', '', raw)
    if not s:
        return None
    # naive normalization: keep digits only; do not add +
    return s
