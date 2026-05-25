from typing import Dict, Any, List, Optional
import httpx
import os


BASE_URL = os.getenv("DEFECT_API_BASE_URL", "https://aerea.panzerplayground.com")
LOCATION_API_URL = f"{BASE_URL}/api/v8/getDefectslocation"
TYPE_API_URL = f"{BASE_URL}/api/v8/getDefectstype"


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip().lower()


async def get_defect_locations(
    token: str,
    property_id: int = 1
) -> List[Dict[str, Any]]:
    payload = {"property": property_id}

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            LOCATION_API_URL,
            data=payload,
            headers=_headers(token),
        )

    response.raise_for_status()
    result = response.json()
    return result.get("data", [])


async def get_defect_types(
    token: str,
    location_id: int,
    property_id: int = 1
) -> List[Dict[str, Any]]:
    payload = {
        "property": property_id,
        "location": location_id
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            TYPE_API_URL,
            data=payload,
            headers=_headers(token),
        )

    response.raise_for_status()
    result = response.json()
    return result.get("data", [])


def match_location(
    locations: List[Dict[str, Any]],
    location_text: str
) -> Optional[Dict[str, Any]]:
    target = _normalize_text(location_text)

    for item in locations:
        location_name = _normalize_text(item.get("defect_location"))
        if not location_name:
            continue

        if (
            target == location_name
            or target in location_name
            or location_name in target
        ):
            return item

    return None


def match_defect_type(
    defect_types: List[Dict[str, Any]],
    type_text: str
) -> Optional[Dict[str, Any]]:
    target = _normalize_text(type_text)

    for item in defect_types:
        defect_type_name = _normalize_text(item.get("defect_type"))
        if not defect_type_name:
            continue

        if (
            target == defect_type_name
            or target in defect_type_name
            or defect_type_name in target
        ):
            return item

    return None