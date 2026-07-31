"""HeyLou Function-Definitions fuer Gemini Function-Calling [CRUX-MK].

Schema-Format: Grok-Function-Declarations (JSON-Schema-Subset).
Pflicht: 5 HeyLou-Capabilities (search_hotels / get_rates / compare_otas / book_direct / optimize_revenue).

Grok-Reference: see vendor docs

[CRUX-MK]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# === HEYLOU FUNCTION DEFINITIONS (Grok-Format) ===

HEYLOU_FUNCTION_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "search_hotels",
        "description": (
            "Search HeyLou Travel-Knowledge-Graph for hotels matching location, dates, and preferences. "
            "Read-only, idempotent. Returns list of hotels with availability + base-rates."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or region (e.g. 'Hildesheim', 'Munich', 'Cape Coral FL').",
                },
                "dates": {
                    "type": "object",
                    "properties": {
                        "check_in": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                        "check_out": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                    },
                    "required": ["check_in", "check_out"],
                },
                "preferences": {
                    "type": "object",
                    "description": "Optional filters (room_type, max_price_eur, amenities).",
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
        "description": (
            "Fetch current rates from PMS/RMS backend (MEWS/Opera/Protel) for a hotel + date-range. "
            "Read-only. Returns per-room-type rates with availability."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string", "description": "HeyLou hotel-ID (e.g. 'hildesheim')."},
                "date_range": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string", "description": "ISO date"},
                        "end": {"type": "string", "description": "ISO date"},
                    },
                    "required": ["start", "end"],
                },
            },
            "required": ["hotel_id", "date_range"],
        },
    },
    {
        "name": "compare_otas",
        "description": (
            "Compare OTA-prices (Booking.com / Expedia / HRS) for a hotel + dates against Direct-Booking. "
            "Read-only. Returns spread + commission-delta."
        ),
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
        "name": "book_direct",
        "description": (
            "Direct-Booking via HeyLou (commission-free). K_0-RELEVANT - requires PHRONESIS_TICKET in Real-Mode. "
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
        "name": "optimize_revenue",
        "description": (
            "Run Revenue-Optimizer for a hotel (Hamilton/Lagrange/KKT pricing optimization). "
            "Returns recommended rate-changes per room-type. W40 Stub - currently mock-only."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {"type": "string"},
            },
            "required": ["hotel_id"],
        },
    },
]


def build_tool_payload() -> dict[str, Any]:
    """Build Grok tools payload from function-definitions.

    Grok accepts tools as: {"function_declarations": [...]}
    """
    return {"function_declarations": HEYLOU_FUNCTION_DEFINITIONS}


def get_function_names() -> list[str]:
    """Return list of all 5 HeyLou function-names."""
    return [fd["name"] for fd in HEYLOU_FUNCTION_DEFINITIONS]


def get_function_schema(name: str) -> dict[str, Any] | None:
    """Lookup function-schema by name."""
    for fd in HEYLOU_FUNCTION_DEFINITIONS:
        if fd["name"] == name:
            return fd
    return None


def is_k0_relevant(name: str) -> bool:
    """K_0-Filter: book_direct triggers K_0-Gate."""
    return name in {"book_direct"}


@dataclass(frozen=True)
class FunctionRoute:
    """Decision made by the local Grok function-call adapter."""

    accepted: bool
    function_name: str | None
    status: str
    required_arguments: list[str]
    missing_arguments: list[str]
    k0_relevant: bool
    tool_payload: dict[str, Any] | None


DESTRUCTIVE_TERMS = {
    "delete",
    "drop",
    "erase",
    "exfiltrate",
    "leak",
    "purge",
    "remove",
    "steal",
    "wipe",
}


def _schema_required_arguments(name: str) -> list[str]:
    schema = get_function_schema(name)
    if schema is None:
        return []
    return list(schema["parameters"].get("required", []))


def _string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        values: list[str] = []
        for nested in value.values():
            values.extend(_string_values(nested))
        return values
    if isinstance(value, list):
        values = []
        for nested in value:
            values.extend(_string_values(nested))
        return values
    return []


def _has_destructive_intent(args: dict[str, Any]) -> bool:
    words = {
        token.strip(".,;:!?()[]{}\"'").lower()
        for text in _string_values(args)
        for token in text.split()
    }
    return bool(words & DESTRUCTIVE_TERMS)


def route_function_call(function_call: dict[str, Any]) -> FunctionRoute:
    """Validate and route a canonical Grok function call.

    The decision is derived from the declared function schemas plus the supplied
    call arguments. Unsupported, incomplete, or destructive calls are rejected
    instead of being coerced into a HeyLou capability.
    """

    name = function_call.get("name")
    args = function_call.get("args") or {}

    if not isinstance(name, str) or get_function_schema(name) is None:
        return FunctionRoute(
            accepted=False,
            function_name=None,
            status="unknown_function",
            required_arguments=[],
            missing_arguments=[],
            k0_relevant=False,
            tool_payload=None,
        )

    if not isinstance(args, dict):
        args = {}

    required = _schema_required_arguments(name)
    missing = [field for field in required if field not in args or args[field] in (None, "")]
    if missing:
        return FunctionRoute(
            accepted=False,
            function_name=name,
            status="missing_required_arguments",
            required_arguments=required,
            missing_arguments=missing,
            k0_relevant=is_k0_relevant(name),
            tool_payload=None,
        )

    if _has_destructive_intent(args):
        return FunctionRoute(
            accepted=False,
            function_name=name,
            status="rejected_destructive_intent",
            required_arguments=required,
            missing_arguments=[],
            k0_relevant=is_k0_relevant(name),
            tool_payload=None,
        )

    return FunctionRoute(
        accepted=True,
        function_name=name,
        status="routed",
        required_arguments=required,
        missing_arguments=[],
        k0_relevant=is_k0_relevant(name),
        tool_payload={"function_declarations": [get_function_schema(name)]},
    )
