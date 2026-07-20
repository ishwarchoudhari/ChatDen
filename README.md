# ChatDen

A secure, production-grade real-time messaging platform — built with the engineering discipline of a company-grade product, in the spirit of WhatsApp/Instagram Direct.

> **Status:** Phases 0–5 complete (environment, auth, profiles, discovery/blocking, direct messaging). Phase 6 (real-time delivery) in progress. See [`docs/PROJECT_ARCHITECTURE.md`](docs/PROJECT_ARCHITECTURE.md) for the full engineering log and open items.

---

## What ChatDen does

- **Accounts** — email/password or Google OAuth, JWT-based sessions with rotating, blacklisted refresh tokens
- **Profiles** — bio and public profile data, auto-provisioned on signup
- **Discovery** — search-based user discovery (never a browsable directory), with blocking as the safety layer
- **Messaging** — direct (1:1) conversations, REST today, real-time delivery landing in Phase 6
- **Coming next** — live presence & typing indicators, an AI chatbot contact, media messages, push notifications

## Tech stack

**Backend:** Python 3.12 · Django 6.0 · Django REST Framework · djangorestframework-simplejwt · PostgreSQL · django-environ

**Realtime (in progress):** Django Channels · Valkey (Redis-protocol-compatible, BSD-licensed)

**Frontend (planned):** Next.js 16 (App Router) · TypeScript · Tailwind CSS · shadcn/ui

**Infra (planned):** Docker · Nginx · GitHub Actions

Full version pins and rationale for each choice: [`docs/PROJECT_ARCHITECTURE.md`](docs/PROJECT_ARCHITECTURE.md#2-finalized-tech-stack).

## Architecture at a glance

```
Client (Next.js)
   │
   ├── REST ──────► Django (DRF) ──► PostgreSQL
   │                    │
   └── WebSocket ──► Django Channels ──► Valkey
                        (Phase 6)
```

Backend apps, each single-responsibility:
```
accounts        identity, custom User model, registration
authentication  JWT lifecycle — login, refresh, logout, /me
profiles        user profile data
relationships   discovery, search, blocking — the safety layer
chat            conversations & messages
```

No app queries another app's models directly for policy decisions — `relationships/services.py` is the single source of truth for "can these two users interact," and every consumer (search, messaging, and eventually calls/presence) calls into it rather than re-implementing the check.

## Security highlights

- Fail-closed permissions by default (`IsAuthenticated` globally, `AllowAny` only where explicit)
- UUID primary keys — no enumerable sequential IDs on any user-facing model
- Every list/detail endpoint is ownership-scoped at the queryset level, not just permission-gated
- Passwords hashed exclusively through a single manager method — no code path can bypass it
- Rate-limited public endpoints; rotating + blacklisted JWT refresh tokens
- No endpoint ever returns a full user listing — discovery is search-only
- Blocked-profile requests return 404, never 403 — existence is never confirmed to a blocked party

Full list, plus what's still open: [`docs/PROJECT_ARCHITECTURE.md`](docs/PROJECT_ARCHITECTURE.md#7-security-posture--implemented).

## Getting started (backend)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

cp .env.example .env          # then fill in real local values

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Requires a local PostgreSQL instance matching the credentials in `.env`.

## API overview

All endpoints are versioned under `/api/v1/`. Full request/response reference: [`docs/PROJECT_ARCHITECTURE.md`](docs/PROJECT_ARCHITECTURE.md#endpoints-current).

| Method | Path | App | Auth |
|---|---|---|---|
| POST | `/api/v1/accounts/register/` | accounts | Public (throttled) |
| GET | `/api/v1/accounts/health/` | accounts | Public |
| POST | `/api/v1/authentication/login/` | authentication | Public (throttled) |
| POST | `/api/v1/authentication/refresh/` | authentication | Public |
| POST | `/api/v1/authentication/logout/` | authentication | Authenticated |
| GET | `/api/v1/authentication/me/` | authentication | Authenticated |
| GET / PATCH | `/api/v1/profiles/` | profiles | Authenticated (own profile only) |
| GET / POST | `/api/v1/relationships/blocks/` | relationships | Authenticated (ownership-scoped) |
| DELETE | `/api/v1/relationships/blocks/<id>/` | relationships | Authenticated (ownership-scoped) |
| GET | `/api/v1/relationships/search/` | relationships | Authenticated, throttled — reported complete, pending review |
| GET | `/api/v1/relationships/users/<id>/` | relationships | Authenticated — reported complete, pending review |
| GET / POST | `/api/v1/chat/conversations/` | chat | Authenticated — reported complete, pending review |
| GET | `/api/v1/chat/conversations/<id>/` | chat | Authenticated + `IsConversationMember` — reported complete, pending review |
| GET / POST | `/api/v1/chat/conversations/<id>/messages/` | chat | Authenticated + `IsConversationMember` — reported complete, pending review |

## Roadmap

```
✅ Phase 0-3   Environment · Foundation · Auth · Profiles
✅ Phase 4-5   Discovery & Blocking · Direct Messaging (REST)
🔄 Phase 6     Real-time delivery, presence (Channels + Valkey)
⬜ Phase 7     AI chatbot
⬜ Phase 8     Media messages, push notifications
⬜ Phase 9     Deployment (Docker, Nginx, CI/CD)
```

## License

**Proprietary — All Rights Reserved.** See [`LICENSE`](LICENSE). This code is not licensed for reuse, redistribution, or modification without explicit permission.

*(If ChatDen is intended as open source instead, see the license discussion in the architecture doc — swap this section and the `LICENSE` file accordingly.)*
