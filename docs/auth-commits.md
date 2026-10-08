# Authentication module — commit revision guide

Branch: `authentication-module` (9 commits ahead of `main`)

Chronological walkthrough of each commit: what was added, key files, and how it fits the overall auth design.

---

## 1. `493c20a` — Authentication system: Register user API

**Foundation commit.**

- **`POST /api/v1/auth/register`**: checks email uniqueness, hashes password, saves `User`, returns `UserResponse`.
- **New pieces**: `User` model (PostgreSQL UUID), `UserCreate` / `UserResponse` schemas, `app/core/security.py` (Argon2/Bcrypt via pwdlib), `app/db/base.py` + shared `Base`.
- **`main.py`**: lifespan hook runs `create_all` on startup; mounts auth router at `/api/v1`; removed old DB health route.
- **Config**: `SECRET_KEY`, JWT `ALGORITHM`, token expiry settings.
- **Deps**: `PyJWT`, `pwdlib`, `bcrypt` in `requirements.txt`; `docker-compose.yml` tweaks.

**Takeaway:** Users live in DB; passwords are hashed; app bootstraps tables and exposes register.

---

## 2. `f4655ed` — Login API

**First JWT flow (access only).**

- **`POST /api/v1/auth/login`**: OAuth2 form (`username` = email, `password`); verify user; return **`Token`** (`access_token`, `token_type=bearer`).
- **`create_access_token()`** in `security.py`: signed JWT with `sub` = user id.
- Schemas: `Token`, `TokenPayload`.

**Takeaway:** Login returns a short-lived bearer access token; no refresh yet.

---

## 3. `a7c9e5a` — `get_current_user` + protected GET

**“Who is calling?” dependency.**

- **New `app/api/deps.py`**: `OAuth2PasswordBearer`, **`get_current_user`** — decode JWT, load user from DB, reject inactive users.
- **`GET /api/v1/auth/me`**: returns current user (`UserResponse`) when a valid access token is sent.

**Takeaway:** Any route can use `Depends(get_current_user)`; Swagger “Authorize” points at login.

---

## 4. `f474697` — Securing chat ask and streaming API

**Apply auth to existing chat.**

- **`app/api/v1/chat.py`**: chat endpoints now require **`current_user: User = Depends(get_current_user)`**.

**Takeaway:** Chat is no longer anonymous; same JWT as `/me`.

---

## 5. `c0226ba` — Refresh access token

**Access + refresh pair and rotation entry point.**

- **Login** returns **`TokenResponse`**: `access_token` + **`refresh_token`** (not just access).
- **`POST /api/v1/auth/refresh`**: body `RefreshTokenRequest` → new access token.
- **JWT claims**: access tokens get `type: "access"`; refresh tokens get `type: "refresh"` + longer expiry (`REFRESH_TOKEN_EXPIRE_DAYS`).
- **`get_current_user`**: rejects tokens that are not `type == "access"` (so refresh JWTs cannot be used as API keys).
- Schemas: `TokenResponse`, `RefreshTokenRequest`, `AccessTokenResponse`.

**Takeaway:** Short access token + long refresh token; refresh endpoint renews access without re-login.

---

## 6. `6133a87` — Logout API

**Server-side refresh token tracking.**

- **New `RefreshToken` model**: stores `token_jti`, user, expiry, **`revoked`** flag in PostgreSQL.
- **Login** persists each issued refresh token in DB.
- **Refresh** checks DB: token exists and not revoked.
- **`POST /api/v1/auth/logout`**: authenticated user; marks refresh token **revoked** in DB.
- **`create_refresh_token` / `decode_refresh_token`** updated to use **JTI** and return structured data for DB lookup.
- Schemas: `LogoutRequest`, `MessageResponse`.

**Takeaway:** Logout = invalidate refresh token in DB; stolen refresh tokens can be revoked.

---

## 7. `a41fd3a` — Change password (API 6)

**Logged-in password change.**

- **`POST /api/v1/auth/change-password`**: requires `get_current_user`; verify `current_password`; hash `new_password`; block reusing same password.
- Revokes active refresh tokens after change (force re-login on other devices).
- Schema: `ChangePasswordRequest`.

**Takeaway:** Password change is authenticated and invalidates existing refresh sessions.

---

## 8. `fb17bb6` — Forgot / reset password (API 7 & 8)

**Password recovery without being logged in.**

- **`POST /api/v1/auth/forgot-password`**: if email exists, build reset JWT; **dev: print token to console**; always same generic message (anti-enumeration).
- **`POST /api/v1/auth/reset-password`**: validate reset token, set new password.
- **`security.py`**: `create_password_reset_token`, `verify_password_reset_token`.
- Schemas: `ForgotPasswordRequest`, `ResetPasswordRequest`.

**Takeaway:** Reset flow is token-in-email (simulated locally via terminal); production would send email instead of `print`.

---

## 9. `f277b1f` — Login: form data → JSON

**API ergonomics fix.**

- **Login** switched from **`OAuth2PasswordRequestForm`** to **`LoginRequest`** JSON (`email` + `password`).
- Removed `WWW-Authenticate` header on wrong-password 401 (typical for JSON APIs).

**Takeaway:** Clients send `{"email","password"}` instead of form `username`/`password`; OAuth2 bearer scheme for *protected* routes is unchanged.

---

## Big picture

```text
Register → hash password → User in PostgreSQL
Login    → access JWT (short) + refresh JWT (long) → refresh row in DB
/me, chat, change-password, logout → Authorization: Bearer <access JWT>
/refresh → refresh JWT → new access JWT (DB + not revoked)
/forgot + /reset → separate reset JWT (dev: printed)
/logout → revoke refresh row
```

### Files to re-read

| Area | Path |
|------|------|
| All auth routes | `app/api/v1/auth.py` |
| JWT guard | `app/api/deps.py` |
| Hash + tokens | `app/core/security.py` |
| Models | `app/models/user.py`, `app/models/token.py` |
| Request/response shapes | `app/schemas/user.py` |

### Endpoints (current)

| Method | Path | Auth |
|--------|------|------|
| POST | `/api/v1/auth/register` | No |
| POST | `/api/v1/auth/login` | No (JSON body) |
| GET | `/api/v1/auth/me` | Bearer access |
| POST | `/api/v1/auth/refresh` | No (refresh token in body) |
| POST | `/api/v1/auth/logout` | Bearer access |
| POST | `/api/v1/auth/change-password` | Bearer access |
| POST | `/api/v1/auth/forgot-password` | No |
| POST | `/api/v1/auth/reset-password` | No |
