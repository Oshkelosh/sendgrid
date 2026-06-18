"""SendGrid email notification integration."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field, SecretStr

from app.addons.notifications.base import NotificationAddon
from app.addons.notifications.helpers import post_json_webhook
from app.addons.log import info, warning
from app.addons.config_serialization import dump_addon_config


class SendgridConfig(BaseModel):
    api_key: SecretStr = Field(default=..., description="SendGrid API key")
    from_address: str = Field(default=..., description="Default From email address")

    @classmethod
    def config_model(cls):
        return cls


class SendgridAddon(NotificationAddon):
    addon_id: str = "sendgrid"
    addon_name: str = "SendGrid"
    addon_description: str = "Send transactional emails via SendGrid v3."
    addon_category: str = "notification"
    version: str = "1.0.0"
    is_enabled: bool = False
    supported_channels: ClassVar[list[str]] = ["email"]

    _config: Dict[str, Any] | None = None
    _api_key: str | None = None
    _from_address: str | None = None

    @classmethod
    def config_schema(cls):
        return SendgridConfig

    async def initialize(self, config: dict) -> None:
        validated = self.config_schema()(**config)
        self._config = dump_addon_config(validated)
        self._api_key = validated.api_key.get_secret_value()
        self._from_address = validated.from_address
        self.is_enabled = True
        info("SendGrid", "Initialized (from={})", self._from_address)

    async def validate_config(self, config: dict) -> None:
        from app.core.exceptions import ValidationError

        validated = self.config_schema()(**config)
        api_key = validated.api_key.get_secret_value()
        if not api_key:
            return
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://api.sendgrid.com/v3/user/profile",
                headers={"Authorization": f"Bearer {api_key}"},
            )
        if resp.status_code == 401:
            raise ValidationError(message="Invalid API key — check your credentials")
        if resp.status_code == 403:
            raise ValidationError(
                message="API key is valid but missing required permissions: user:read"
            )
        if resp.status_code >= 400:
            raise ValidationError(message="SendGrid rejected the API key")

    async def shutdown(self) -> None:
        self._api_key = None
        self._from_address = None
        self.is_enabled = False

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> Dict[str, Any]:
        if not self._api_key or not self._from_address:
            return {"success": False, "message_id": "", "error": "Not configured", "to": to}

        content_type = "text/html" if html else "text/plain"
        payload = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": self._from_address},
            "subject": subject,
            "content": [{"type": content_type, "value": body}],
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                message_id = resp.headers.get("X-Message-Id", "")
                return {"success": True, "message_id": message_id, "to": to}
        except Exception as exc:
            warning("SendGrid", "send_email to={} error: {}", to, exc)
            return {"success": False, "message_id": "", "error": str(exc), "to": to}

    async def send_sms(self, to: str, body: str) -> Dict[str, Any]:
        return self.channel_not_supported("sms", to)

    async def send_push(
        self,
        to: str,
        title: str,
        body: str,
        data: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return self.channel_not_supported("push", to)

    async def send_webhook(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = await post_json_webhook(url, payload)
        if not result.get("success"):
            warning("SendGrid", "send_webhook to={} error: {}", url, result.get("error"))
        return result

    def get_routers(self) -> List[APIRouter]:
        return []

    def get_admin_routes(self) -> List[APIRouter]:
        from app.addons.notifications.sendgrid.routes import admin_router

        return [admin_router]

    def get_admin_templates(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "templates")

    def get_admin_static(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "static")
