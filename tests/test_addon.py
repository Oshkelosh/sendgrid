"""Minimal unit tests for the sendgrid addon."""

from app.addons.notifications.sendgrid.addon import SendgridAddon


def test_addon_identity():
    assert SendgridAddon.addon_id == "sendgrid"
    assert SendgridAddon.addon_category == "notification"
