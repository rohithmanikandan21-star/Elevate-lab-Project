# scanner/tests.py (partial)
import random, string

def _random_token(prefix="SCAN"):
    rnd = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}_{rnd}"

def test_reflection_on_params(session, url, param_names=None, payload=None, timeout=10):
    """
    Safe: submit payload (or benign marker) in query params and check for reflection.
    - payload: if None, a random token is generated (non-destructive).
    """
    if payload is None:
        payload = _random_token("REFL")
    if param_names is None:
        param_names = ["q"]
    params = {p: payload for p in param_names}
    try:
        r = session.get(url, params=params, timeout=timeout)
    except Exception:
        return None
    if r and payload in (r.text or ""):
        start = r.text.find(payload)
        snippet = r.text[max(0, start-120):start+len(payload)+120]
        return {"type": "reflected-token", "payload_used": payload, "url": r.url, "status_code": r.status_code, "snippet": snippet}
    return None

def test_reflection_on_form(session, form, payload=None, timeout=10):
    """
    Safe: submit payload to all fields of a discovered form.
    """
    if payload is None:
        payload = _random_token("REFL")
    data = {inp['name']: payload for inp in form.get('inputs', [])}
    try:
        if form.get('method','get').lower() == 'get':
            r = session.get(form.get('action'), params=data, timeout=timeout)
        else:
            r = session.post(form.get('action'), data=data, timeout=timeout)
    except Exception:
        return None
    if r and payload in (r.text or ""):
        start = r.text.find(payload)
        snippet = r.text[max(0, start-120):start+len(payload)+120]
        return {"type": "reflected-token-form", "payload_used": payload, "url": r.url, "status_code": r.status_code, "snippet": snippet}
    return None
