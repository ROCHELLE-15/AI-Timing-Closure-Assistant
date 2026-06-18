"""
parser.py
Parses a simple STA timing report (.rpt) and extracts for each Path:
- arrival time
- required time
- slack

API:
- parse_timing_report(source) -> list of dicts [{ "arrival": float, "required": float, "slack": float, ... }, ...]

The parser accepts:
- a file path (str)
- a bytes-like object (e.g., uploaded_file.getvalue())
- a file-like object (has .read())

The parser is intentionally permissive to handle common report variants such as:
  Arrival Time: 12.345ns
  Required Time: 10.000
  Slack: -2.345
"""
import re
from typing import List, Dict, Union, IO

FLOAT_RE = r'[-+]?\d*\.\d+|[-+]?\d+'


def _to_text(source: Union[str, bytes, IO]) -> str:
    # Accept path, bytes, or file-like
    if hasattr(source, "read"):
        raw = source.read()
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="ignore")
        return str(raw)
    if isinstance(source, bytes):
        return source.decode("utf-8", errors="ignore")
    # assume path
    with open(source, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _try_float(s: str):
    try:
        if s is None:
            return None
        s = s.strip()
        m = re.match(r'^(' + FLOAT_RE + r')', s)
        if m:
            return float(m.group(1))
        return None
    except Exception:
        return None


def parse_timing_report(source: Union[str, bytes, IO]) -> List[Dict]:
    """
    Parse timing report text and return list of path dicts.
    Each dict contains keys at minimum: 'arrival', 'required', 'slack'
    May also include 'raw_block' for debugging.
    """
    text = _to_text(source)
    if not text:
        return []

    # Split into blocks. Many STA reports include multiple "Path" sections.
    # We split on lines starting with "Path" (case-insensitive) or "path".
    blocks = re.split(r'(?mi)^\s*Path\b', text)

    results = []
    # patterns
    pat_arrival = re.compile(r'Arrival(?:\s*Time)?\s*[:=]\s*([-.\d]+)', re.IGNORECASE)
    pat_required = re.compile(r'Required(?:\s*Time)?\s*[:=]\s*([-.\d]+)', re.IGNORECASE)
    pat_slack = re.compile(r'Slack\s*[:=]\s*([-.\d]+)', re.IGNORECASE)

    # Also support inline table rows: <start> <end> <arrival> <required> <slack>
    table_row = re.compile(r'([^\s]+)\s+([^\s]+)\s+(' + FLOAT_RE + r')\s+(' + FLOAT_RE + r')\s+(' + FLOAT_RE + r')')

    for b in blocks:
        block = b.strip()
        if not block:
            continue

        # Try table row match first (may capture many formats)
        m_row = table_row.search(block)
        if m_row:
            try:
                arrival = _try_float(m_row.group(3))
                required = _try_float(m_row.group(4))
                slack = _try_float(m_row.group(5))
                results.append({
                    "arrival": arrival,
                    "required": required,
                    "slack": slack,
                    "raw_block": block
                })
                continue
            except Exception:
                pass

        # Fallback: look for labeled fields anywhere in block
        m_a = pat_arrival.search(block)
        m_r = pat_required.search(block)
        m_s = pat_slack.search(block)

        if m_a or m_r or m_s:
            arrival = _try_float(m_a.group(1)) if m_a else None
            required = _try_float(m_r.group(1)) if m_r else None
            slack = _try_float(m_s.group(1)) if m_s else None
            # Only add if at least one numeric found
            if arrival is not None or required is not None or slack is not None:
                results.append({
                    "arrival": arrival,
                    "required": required,
                    "slack": slack,
                    "raw_block": block
                })

    # Final sanitize: ensure numeric types for known keys; drop entries with no slack info
    sanitized = []
    for r in results:
        slack = r.get("slack")
        if slack is None:
            nums = re.findall(FLOAT_RE, r.get("raw_block", ""))
            nums_floats = [_try_float(n) for n in nums]
            nums_floats = [x for x in nums_floats if x is not None]
            if len(nums_floats) >= 3:
                r["arrival"], r["required"], r["slack"] = nums_floats[-3], nums_floats[-2], nums_floats[-1]
            else:
                continue
        sanitized.append({
            "arrival": float(r.get("arrival")) if r.get("arrival") is not None else None,
            "required": float(r.get("required")) if r.get("required") is not None else None,
            "slack": float(r.get("slack")) if r.get("slack") is not None else None,
            "raw_block": r.get("raw_block")
        })

    return sanitized


if __name__ == "__main__":
    sample = """
    Path 1:
      Startpoint: A
      Endpoint: Z
      Arrival Time: 12.345ns
      Required Time: 10.000
      Slack: -2.345

    Path 2:
      A B 8.5 10.0 1.5
    """
    print(parse_timing_report(sample))
