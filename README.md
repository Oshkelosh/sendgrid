# SendGrid (`sendgrid`)

Send transactional emails via SendGrid Mail Send v3.

## Overview

| | |
|---|---|
| Addon ID | `sendgrid` |
| Category | notification |
| Channels | email |
| Version | 1.0.0 |
| Category guide | [../README.md](../README.md) |

Only **one** notification provider per channel can be active at a time.

## Enable and configure

1. Install this package under `app/addons/notifications/sendgrid/`
2. Open **Admin → Notifications → SendGrid** at `/admin/notifications/sendgrid`
3. Enter API key and verified sender address
4. Enable the provider checkbox and save

## Configuration schema

| Field | Type | Description |
|-------|------|-------------|
| `api_key` | secret | SendGrid API key with **Mail Send** permission |
| `from_address` | string | Verified sender email address |

Secrets are stored in `addon_configs`, not in `.env`.

## Routes

### Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/notifications/sendgrid` | Config form |
| POST | `/admin/notifications/sendgrid/save` | Save config |

### Public API

None — core calls `send_email()` directly.

## Provider setup

1. Create a [SendGrid](https://sendgrid.com/) account.
2. Complete **Sender Authentication** (domain or single sender verification).
3. Create an API key with **Mail Send** scope under **Settings → API Keys**.
4. Use the verified sender as **From** in admin config.
5. Enable the addon.

Uses `POST https://api.sendgrid.com/v3/mail/send` with Bearer auth.

SMS and push are not supported.

## Package layout

```
sendgrid/
├── README.md
├── addon.py
├── routes.py
└── templates/
    └── sendgrid_config.html
```

## See also

- [Notification addon development](../README.md)
- [Oshkelosh addon guide](../../README.md)
