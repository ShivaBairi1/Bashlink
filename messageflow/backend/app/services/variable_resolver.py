import re
from typing import Dict, Any

TOKEN_RE = re.compile(r"{{\s*([^}]+?)\s*}}")

class VariableResolver:
    @staticmethod
    def extract_tokens(template: str):
        return sorted({m.group(1).strip() for m in TOKEN_RE.finditer(template)})

    @staticmethod
    def render(template: str, dynamic_fields: Dict[str, Any], fallback: str = "") -> str:
        def lookup(key: str):
            # support dotted lookup
            if "." in key:
                parts = key.split(".")
                cur = dynamic_fields
                for p in parts:
                    if isinstance(cur, dict) and p in cur:
                        cur = cur[p]
                    else:
                        return fallback
                return cur
            return dynamic_fields.get(key, fallback)

        def repl(m):
            key = m.group(1).strip()
            val = lookup(key)
            if val is None:
                return fallback
            return str(val)

        return TOKEN_RE.sub(lambda m: repl(m), template)
