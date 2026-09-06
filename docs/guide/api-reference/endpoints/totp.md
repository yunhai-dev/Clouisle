# Two-Factor Authentication (TOTP) API

The TOTP API provides endpoints for setting up, enabling, verifying, and disabling Time-based One-Time Password (TOTP) two-factor authentication (2FA) for user accounts.

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/totp/setup` | Generate a TOTP secret and QR code URI for 2FA binding |
| `POST` | `/api/v1/totp/enable` | Verify code and permanently activate TOTP 2FA |
| `POST` | `/api/v1/totp/disable` | Disable TOTP 2FA for the account |
| `POST` | `/api/v1/totp/verify` | Verify a 6-digit TOTP code during two-factor login challenge |

---

## Setup TOTP

Generate an authenticator setup URI and secret key.

```http
POST /api/v1/totp/setup HTTP/1.1
Authorization: Bearer <token>
```

### Response (`200 OK`)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "secret": "JBSWY3DPEHPK3PXP",
    "otpauth_url": "otpauth://totp/Clouisle:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Clouisle"
  }
}
```

---

## Enable TOTP

Verify the initial 6-digit verification code from your authenticator app to enable 2FA.

```http
POST /api/v1/totp/enable HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "123456"
}
```

### Response (`200 OK`)

```json
{
  "code": 0,
  "message": "TOTP two-factor authentication enabled successfully",
  "data": {
    "recovery_codes": [
      "a1b2-c3d4",
      "e5f6-g7h8",
      "i9j0-k1l2"
    ]
  }
}

---

## Disable TOTP

Disable TOTP 2FA for the authenticated user. Requires the current account password and either a valid TOTP code or a recovery backup code.

```http
POST /api/v1/totp/disable HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "CurrentPassword123!",
  "code": "123456",
  "is_backup_code": false
}
```

### Response (`200 OK`)

```json
{
  "code": 0,
  "message": "TOTP two-factor authentication disabled successfully",
  "data": null
}
```
```

---

## Verify TOTP Challenge (Login)

Used during authentication when a user with TOTP enabled enters valid username/password credentials and receives a 2FA challenge response.

```http
POST /api/v1/totp/verify HTTP/1.1
Content-Type: application/json

{
  "challenge_token": "ch_9876543210...",
  "code": "654321"
}
```

### Response (`200 OK`)

```json
{
  "code": 0,
  "message": "Authentication successful",
  "data": {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```
