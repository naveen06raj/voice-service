from pydantic import BaseModel
from typing import Optional, Dict, Any


# =====================================================
# WEBSOCKET RESPONSE
# =====================================================

class VoiceResponse(BaseModel):
    type: str
    transcript: str
    module: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# =====================================================
# DEFECT EXTRACTION
# =====================================================

class DefectExtraction(BaseModel):
    location: Optional[str] = None
    type: Optional[str] = None
    remarks: Optional[str] = None


# =====================================================
# FEEDBACK EXTRACTION
# =====================================================

class FeedbackExtraction(BaseModel):
    category: Optional[str] = None
    subject: Optional[str] = None
    notes: Optional[str] = None


# =====================================================
# FACILITY EXTRACTION
# =====================================================

class FacilityExtraction(BaseModel):
    facility_type: Optional[str] = None
    booking_date: Optional[str] = None
    time_slot: Optional[str] = None
    remarks: Optional[str] = None


# =====================================================
# ANNOUNCEMENT EXTRACTION
# =====================================================

class AnnouncementExtraction(BaseModel):
    title: Optional[str] = None
    month: Optional[str] = None
    year: Optional[int] = None


# =====================================================
# MODULE DETECTION
# =====================================================

class ModuleDetection(BaseModel):
    module: str