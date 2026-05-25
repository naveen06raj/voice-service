from typing import Dict, Any
import json
import re

import httpx
from app.services.llm.model import get_chat_model
from app.services.api_client.defect_client import (
    get_defect_locations,
    get_defect_types,
    match_location,
    match_defect_type,
)


llm = get_chat_model()


def _clean_json(raw: str) -> str:
    raw = re.sub(r"```json|```", "", raw, flags=re.IGNORECASE).strip()
    return raw


async def _llm_json(prompt: str) -> Dict[str, Any]:
    response = await llm.ainvoke(prompt)
    raw_content = response.content if hasattr(response, "content") else str(response)
    cleaned = _clean_json(raw_content)
    return json.loads(cleaned)


async def generate_defect_autofill(
    user_text: str,
    token: str,
    property_id: int = 1
) -> Dict[str, Any]:
    try:
        # -------------------------------------------------
        # 1) Get valid defect locations from API
        # -------------------------------------------------
        locations = await get_defect_locations(
            token=token,
            property_id=property_id
        )

        if not locations:
            return {
                "success": False,
                "message": "No defect locations found"
            }

        location_names = [
            item["defect_location"]
            for item in locations
            if item.get("defect_location")
        ]

        # -------------------------------------------------
        # 2) Ask LLM to select ONE valid location
        # -------------------------------------------------
        location_prompt = f"""
You are a defect location selector.

User text:
{user_text}

Available locations:
{chr(10).join(location_names)}

Rules:
- Select ONLY ONE location from the available locations
- Do not invent a new location
- If the user mentions a room/area, choose the closest matching location
- Return ONLY valid JSON

Format:
{{
  "location": "selected location"
}}
"""

        location_result = await _llm_json(location_prompt)
        selected_location_text = location_result.get("location")

        if not selected_location_text:
            return {
                "success": False,
                "message": "Location not selected"
            }

        matched_location = match_location(locations, selected_location_text)

        if not matched_location:
            return {
                "success": False,
                "message": f"Location not matched: {selected_location_text}"
            }

        location_id = matched_location.get("id")

        # -------------------------------------------------
        # 3) Get defect types based on selected location
        # -------------------------------------------------
        defect_types = await get_defect_types(
            token=token,
            location_id=location_id,
            property_id=property_id
        )

        if not defect_types:
            return {
                "success": False,
                "message": "No defect types found for selected location"
            }

        type_names = [
            item["defect_type"]
            for item in defect_types
            if item.get("defect_type")
        ]

        # -------------------------------------------------
        # 4) Ask LLM to select ONE valid type
        # -------------------------------------------------
        type_prompt = f"""
You are a defect type selector.

User text:
{user_text}

Selected location:
{selected_location_text}

Available defect types:
{chr(10).join(type_names)}

Rules:
- Select ONLY ONE defect type from the available types
- Do not invent a new type
- Choose the best matching defect type
- Return ONLY valid JSON

Format:
{{
  "type": "selected type"
}}
"""

        type_result = await _llm_json(type_prompt)
        selected_type_text = type_result.get("type")

        if not selected_type_text:
            return {
                "success": False,
                "message": "Defect type not selected"
            }

        matched_type = match_defect_type(defect_types, selected_type_text)

        if not matched_type:
            return {
                "success": False,
                "message": f"Defect type not matched: {selected_type_text}"
            }

        # -------------------------------------------------
        # 5) Ask LLM to write professional remarks
        # -------------------------------------------------
        remarks_prompt = f"""
Write a professional defect remark.

User text:
{user_text}

Selected location:
{selected_location_text}

Selected type:
{selected_type_text}

Rules:
- Keep the meaning the same
- Make it short, clear, and professional
- Sound like a user reporting to defect management
- Return ONLY valid JSON

Format:
{{
  "remarks": "professional remark"
}}
"""

        remarks_result = await _llm_json(remarks_prompt)
        remarks = remarks_result.get("remarks") or user_text

        # -------------------------------------------------
        # 6) Final JSON for frontend autofill
        # -------------------------------------------------
        return {
            "success": True,
            "location": {
                "id": matched_location.get("id"),
                "name": matched_location.get("defect_location")
            },
            "type": {
                "id": matched_type.get("id"),
                "name": matched_type.get("defect_type")
            },
            "remarks": remarks,
            "submit_payload": {
                "defect_location_1": matched_location.get("id"),
                "defect_type_1": matched_type.get("id"),
                "notes_1": remarks
            }
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "message": "AI response was not valid JSON"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }