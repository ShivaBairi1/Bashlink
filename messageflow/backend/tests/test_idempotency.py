import pytest
from app.utils.idempotency import make_idempotency_key

def test_idempotency_key_deterministic():
    k1 = make_idempotency_key('c1','camp1','cust1','tmpl1')
    k2 = make_idempotency_key('c1','camp1','cust1','tmpl1')
    k3 = make_idempotency_key('c1','camp1','cust2','tmpl1')
    assert k1 == k2
    assert k1 != k3
