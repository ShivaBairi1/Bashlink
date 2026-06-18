import hashlib

def make_idempotency_key(company_id: str, campaign_id: str, customer_id: str, template_id: str) -> str:
    s = f"{company_id}:{campaign_id}:{customer_id}:{template_id}"
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
