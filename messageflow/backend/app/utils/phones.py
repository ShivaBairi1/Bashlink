import re
import phonenumbers


def normalize_phone(raw: str | None) -> str | None:
    if not raw:
        return None
    s = str(raw).strip()
    if not s:
        return None
    # attempt to parse using libphonenumber
    try:
        # If number has a leading +, parse without default region
        if s.startswith('+'):
            pn = phonenumbers.parse(s, None)
        else:
            # try parse with no region; fallback to US
            try:
                pn = phonenumbers.parse(s, None)
            except Exception:
                pn = phonenumbers.parse(s, "US")
        if phonenumbers.is_valid_number(pn):
            # return E164 without leading + for storage consistency
            return phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164).lstrip('+')
    except Exception:
        pass
    # fallback: digits only
    digits = re.sub(r'\D', '', s)
    return digits or None
