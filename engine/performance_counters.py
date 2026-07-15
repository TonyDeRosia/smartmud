"""Typed performance counter reset/validation helpers."""

from __future__ import annotations

from collections import deque
from typing import Any


REASON_MAP_COUNTERS = {"combat_validation_rejection_by_reason"}
PROFILE_MAP_COUNTERS = {"violence_profile_sections", "violence_profile_last_sections"}
PRESERVED_PREFIXES = ("scheduler_",)
PRESERVED_KEYS = {"pulse_config", "runtime_scheduler_task", "runtime_scheduler_thread"}


def _typed_default_for(key: str, current: Any) -> Any:
    if key in PRESERVED_KEYS or key.startswith(PRESERVED_PREFIXES):
        return current
    if key in REASON_MAP_COUNTERS or key.endswith("_by_reason"):
        return {}
    if key in PROFILE_MAP_COUNTERS or "profile" in key and isinstance(current, dict):
        return {}
    if "history" in key or "recent" in key:
        if isinstance(current, deque):
            return deque(maxlen=current.maxlen)
        if isinstance(current, list):
            return []
        if isinstance(current, set):
            return set()
    if key.endswith("_seconds") or key.endswith("_duration") or key.endswith("_duration_s"):
        return 0.0
    if key.endswith("_ms") or key.endswith("_max_ms") or key.startswith("max_") or "_max_" in key:
        return 0
    if isinstance(current, float):
        return 0.0
    if isinstance(current, int) and not isinstance(current, bool):
        return 0
    if isinstance(current, dict):
        return {}
    if isinstance(current, list):
        return []
    if isinstance(current, set):
        return set()
    if isinstance(current, deque):
        return deque(maxlen=current.maxlen)
    return current


def validate_performance_counter_schema(counters: dict[str, Any]) -> tuple[bool, str]:
    """Return (ok, invalid_key) without mutating counters."""
    for key, value in counters.items():
        if key in PRESERVED_KEYS or key.startswith(PRESERVED_PREFIXES):
            continue
        if key in REASON_MAP_COUNTERS or key.endswith("_by_reason"):
            if not isinstance(value, dict):
                return False, key
        elif key in PROFILE_MAP_COUNTERS:
            if not isinstance(value, dict):
                return False, key
        elif "history" in key or "recent" in key:
            if not isinstance(value, (list, set, deque)):
                return False, key
        elif isinstance(value, (int, float, dict, list, set, deque)) and not isinstance(value, bool):
            continue
        else:
            # Unknown object counters are allowed only when preserved by identity.
            continue
    return True, ""


def reset_performance_counters(runtime: Any) -> tuple[bool, str]:
    """Reset counters with typed defaults and recompute live gauges atomically."""
    counters = getattr(runtime, "performance_counters", None)
    if not isinstance(counters, dict):
        return False, "performance_counters"
    ok, invalid = validate_performance_counter_schema(counters)
    if not ok:
        return False, invalid
    new_values = {key: _typed_default_for(key, value) for key, value in counters.items()}
    for key in sorted(REASON_MAP_COUNTERS | PROFILE_MAP_COUNTERS):
        new_values.setdefault(key, {})
    cr = getattr(runtime, "combat_runtime", None)
    if cr is not None:
        active = [e for e in getattr(cr, "resident_encounters", {}).values() if getattr(e, "status", "") == "active"]
        new_values["combat_encounters_active"] = len(active)
    ok, invalid = validate_performance_counter_schema(new_values)
    if not ok:
        return False, invalid
    counters.clear()
    counters.update(new_values)
    return True, ""
