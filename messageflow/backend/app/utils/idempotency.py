import hashlib

def make_idempotency_key(company_id: str, campaign_id: str, customer_id: str, template_id: str, template_version: str | None = None) -> str:
    """Create a deterministic idempotency key for message sends.

    Include template_version when available so that template edits change the key.
    """
    parts = [company_id or '', campaign_id or '', customer_id or '', template_id or '']
    if template_version:
        parts.append(str(template_version))
    s = ':'.join(parts)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
