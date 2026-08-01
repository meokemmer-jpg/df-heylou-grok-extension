"""HeyLou Function-Definitions for Grok Function-Calling [CRUX-MK].

Schema format: Grok function declarations (JSON-Schema subset).
Mission: df-heylou-grok-extension.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


HEYLOU_FUNCTION_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "book_direct",
        "description": (
            "Direct booking via HeyLou. Requires strict argument validation and K_0 routing. "
            "Returns confirmed booking with booking_id."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
                "room_type": {"type": "string"},
                "guest": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                    },
                    "required": ["email"],
                },
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                    },
                    "required": ["check_in", "check_out"],
                },
            },
            "required": ["hotel_id", "room_type", "guest", "dates"],
        },
    },
    {
        "name": "search_hotels",
        "description": "Search HeyLou Travel-Knowledge-Graph for matching hotels.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                    },
                    "required": ["check_in", "check_out"],
                },
                "preferences": {
                    "type": "object",
                    "properties": {
                        "room_type": {"type": "string"},
                        "max_price_eur": {"type": "number"},
                        "amenities": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "required": ["location", "dates"],
        },
    },
    {
        "name": "get_rates",
        "description": "Fetch current rates from PMS/RMS backend for a hotel and date range.",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
                "date_range": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                    },
                    "required": ["start", "end"],
                },
            },
            "required": ["hotel_id", "date_range"],
        },
    },
    {
        "name": "compare_otas",
        "description": "Compare OTA prices against direct booking.",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string"},
                        "check_out": {"type": "string"},
                    },
                    "required": ["check_in", "check_out"],
                },
            },
            "required": ["hotel_id", "dates"],
        },
    },
    {
        "name": "optimize_revenue",
        "description": "Run revenue optimizer for a hotel.",
        "parameters": {
            "type": "object",
            "properties": {"hotel_id": {"type": "string"}},
            "required": ["hotel_id"],
        },
    },
]

_DESTRUCTIVE_TERMS = (
    "delete",
    "drop",
    "truncate",
    "erase",
    "destroy",
    "wipe",
    "remove all",
    "after confirming",
)


@dataclass(frozen=True)
class RoutedFunctionCall:
    accepted: bool
    function_name: str | None
    status: str
    k0_relevant: bool
    tool_payload: dict[str, Any] | None
    errors: tuple[str, ...] = ()


def build_tool_payload(function_name: str | None = None) -> dict[str, Any]:
    """Build Grok tools payload from function definitions."""
    declarations = HEYLOU_FUNCTION_DEFINITIONS
    if function_name is not None:
        schema = get_function_schema(function_name)
        declarations = [schema] if schema is not None else []
    return {"function_declarations": declarations}


def get_function_names() -> list[str]:
    """Return all HeyLou function names."""
    return [fd["name"] for fd in HEYLOU_FUNCTION_DEFINITIONS]


def get_function_schema(name: str) -> dict[str, Any] | None:
    """Look up a function schema by name."""
    for fd in HEYLOU_FUNCTION_DEFINITIONS:
        if fd["name"] == name:
            return fd
    return None


def is_k0_relevant(name: str) -> bool:
    """K_0 gate marker for calls that can create bookings."""
    return name == "book_direct"


def route_function_call(call: dict[str, Any]) -> RoutedFunctionCall:
    """Validate and route one Grok function call against the declared HeyLou schema."""
    function_name = call.get("name") if isinstance(call, dict) else None
    if not isinstance(function_name, str):
        return RoutedFunctionCall(False, None, "rejected_invalid_call", False, None, ("missing function name",))

    schema = get_function_schema(function_name)
    if schema is None:
        return RoutedFunctionCall(False, function_name, "rejected_unknown_function", False, None, ("unknown function",))

    args = call.get("args")
    if not isinstance(args, dict):
        return RoutedFunctionCall(False, function_name, "rejected_invalid_args", is_k0_relevant(function_name), None, ("args must be object",))

    if _contains_destructive_intent(args):
        return RoutedFunctionCall(False, function_name, "rejected_destructive_intent", is_k0_relevant(function_name), None)

    errors = tuple(_validate_object(args, schema["parameters"], path="args"))
    if errors:
        return RoutedFunctionCall(False, function_name, "rejected_schema_mismatch", is_k0_relevant(function_name), None, errors)

    return RoutedFunctionCall(
        accepted=True,
        function_name=function_name,
        status="routed",
        k0_relevant=is_k0_relevant(function_name),
        tool_payload=build_tool_payload(function_name),
    )


def _contains_destructive_intent(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return any(term in lowered for term in _DESTRUCTIVE_TERMS)
    if isinstance(value, dict):
        return any(_contains_destructive_intent(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_destructive_intent(item) for item in value)
    return False


def _validate_object(value: dict[str, Any], schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for field in required:
        if field not in value:
            errors.append(f"{path}.{field} is required")

    for field, item in value.items():
        if field not in properties:
            errors.append(f"{path}.{field} is not declared")
            continue
        errors.extend(_validate_value(item, properties[field], f"{path}.{field}"))

    return errors


def _validate_value(value: Any, schema: dict[str, Any], path: str) -> list[str]:
    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(value, dict):
            return [f"{path} must be object"]
        return _validate_object(value, schema, path)
    if expected_type == "array":
        if not isinstance(value, list):
            return [f"{path} must be array"]
        item_schema = schema.get("items", {})
        errors: list[str] = []
        for index, item in enumerate(value):
            errors.extend(_validate_value(item, item_schema, f"{path}[{index}]"))
        return errors
    if expected_type == "string" and not isinstance(value, str):
        return [f"{path} must be string"]
    if expected_type == "number" and not isinstance(value, int | float):
        return [f"{path} must be number"]
    return []
