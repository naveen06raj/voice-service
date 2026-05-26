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

# 🟢 Enforce structured JSON mode output at the model level if supported by your configuration
llm = get_chat_model()
if hasattr(llm, "bind"):
    llm = llm.bind(response_format={"type": "json_object"})


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
        # 2) Combined single-pass extraction prompt
        # -------------------------------------------------
        combined_prompt = f"""
You are an expert defect classification assistant. Your task is to process the user's input voice text and determine the best matching location, the best matching defect type, and generate professional remarks in a single operation.

User text:
"{user_text}"

Available locations:
{chr(10).join(location_names)}

Instructions for Location:
- Select ONLY ONE location from the available locations list. Do not invent a location.

Instructions for Remarks:
- Rewrite the user text to make it professional, short, and clear.
- It must sound like an engineering team reporting a defect.

Return ONLY a valid JSON object matching this schema:
{{
  "location": "exact selected location name from list",
  "remarks": "professional remark text"
}}
"""
        # Execute first pass for Location and Remarks simultaneously
        first_pass_result = await _llm_json(combined_prompt)
        selected_location_text = first_pass_result.get("location")
        remarks = first_pass_result.get("remarks") or user_text

        if not selected_location_text:
            return {
                "success": False,
                "message": "Location could not be parsed by the assistant."
            }

        matched_location = match_location(locations, selected_location_text)
        if not matched_location:
            return {
                "success": False,
                "message": f"Location not matched on system: {selected_location_text}"
            }

        location_id = matched_location.get("id")

        # -------------------------------------------------
        # 3) Fetch types matching the successfully identified location
        # -------------------------------------------------
        defect_types = await get_defect_types(
            token=token,
            location_id=location_id,
            property_id=property_id
        )

        if not defect_types:
            return {
                "success": False,
                "message": f"No defect types found for matched location ID: {location_id}"
            }

        type_names = [
            item["defect_type"]
            for item in defect_types
            if item.get("defect_type")
        ]

        # -------------------------------------------------
        # 4) Ask LLM to pick the correct type
        # -------------------------------------------------
        type_prompt = f"""
You are a defect type selector.

User text:
"{user_text}"

Selected location:
"{matched_location.get('defect_location')}"

Available defect types for this specific location:
{chr(10).join(type_names)}

Rules:
- Select ONLY ONE defect type from the available types list.
- Do not invent a new type.
- Return ONLY valid JSON.

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
        # 5) Consolidated JSON output structure
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
            "message": "AI response failed validation layout constraints"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }