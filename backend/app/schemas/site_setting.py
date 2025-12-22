from typing import Any, Dict, Optional

from pydantic import BaseModel


class SiteSettingResponse(BaseModel):
    key: str
    value: Any
    value_type: str
    category: str
    description: Optional[str] = None
    is_public: bool

    class Config:
        from_attributes = True


class SiteSettingUpdate(BaseModel):
    value: Any


class SiteSettingBulkUpdate(BaseModel):
    settings: Dict[str, Any]


class SiteSettingsResponse(BaseModel):
    settings: Dict[str, Any]


class PublicSiteSettingsResponse(BaseModel):
    """Public settings visible to unauthenticated users"""
    site_name: str = "Clouisle"
    site_description: str = ""
    site_url: str = ""
    site_icon: str = ""
    allow_registration: bool = True
    require_approval: bool = False
    email_verification: bool = True
    enable_captcha: bool = False
    allow_account_deletion: bool = True
