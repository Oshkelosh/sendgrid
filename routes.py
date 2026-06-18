"""SendGrid addon routes."""

from __future__ import annotations

from typing import Any

from app.addons.notifications.shared_routes import build_notification_routers


def _parse_sendgrid_config_form(form: Any) -> tuple[dict[str, Any], bool]:
    return (
        {
            "api_key": form.get("api_key", ""),
            "from_address": form.get("from_address", ""),
        },
        form.get("is_enabled") == "on",
    )


admin_router, jinja_env = build_notification_routers(
    "sendgrid",
    template_name="sendgrid_config.html",
    page_title="SendGrid Settings",
    secret_keys=("api_key",),
    parse_config_form=_parse_sendgrid_config_form,
)
