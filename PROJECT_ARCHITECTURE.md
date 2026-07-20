# ChatDen — Tech Stack & Product Architecture Reference

> Living document. Reflects the actual, decided, built-and-verified state of the project — not the original plan. Where something was proposed but not yet confirmed in code, it's marked **Pending**, not ✅. Update this file whenever a real decision changes; don't let it drift from reality.

Last reviewed: July 2026 · Covers Phases 0–5 · Phase 6 in progress

> **Verification note on Phase 5:** the developer reports Phase 5 (Conversations & Messages) and all endpoint testing through Phase 5 as complete. Unlike Phases 0–4, the actual `chat` app files (models, permissions, views) have not yet been reviewed file-by-file in this document's audit trail. Status below reflects that distinction — treat Phase 5 as "reported done," not "independently verified," until the files are checked the same way every earlier phase was.

---

## 1. Product overview

**ChatDen** — a production-grade, real-time messaging web application in the spirit of WhatsApp/Instagram DMs, deliberately scoped smaller but engineered to the same standard: secure, fast, defensible under scrutiny.

**Core product decisions, locked in:**
- **Open messaging model.** No friend-request approval flow. Any registered user can start a conversation with any other, subject only to blocking. (Explicitly rejected a Facebook-style `FriendRequest` pending/accept/reject model — see §3.)
- **Discovery is search-based, never a directory.** No endpoint ever lists "all users." You find someone by searching a username/name, via an invite link, or because a conversation already exists — never by browsing.
- **Auth is Google OAuth or email+password.** Phone-number OTP was evaluated and explicitly rejected for cost reasons (no SMS provider offers real production-scale free tier). Phone number may exist later as an unverified profile field for contact-matching, not as a login credential.
- **AI chatbot (future)** is modeled as an ordinary user account (`is_bot=True`), not a separate subsystem — it participates in conversations like any contact.

---

## 2. Finalized tech stack

| Layer | Technology | Version | Status |
|---|---|---|---|
| Language (backend) | Python | 3.12 | ✅ installed |
| Backend framework | Django | **6.0.7** | ✅ installed, confirmed current stable |
| API layer | Django REST Framework | **3.17.1** | ✅ installed |
| Auth tokens | djangorestframework-simplejwt | **5.5.1** | ✅ installed & configured |
| OAuth | django-allauth | **65.18.0** | ✅ installed (confirmed Django 6.0–compatible as of 65.13.1+) — **not yet wired into `INSTALLED_APPS`/settings** |
| Env config | django-environ | **0.14.0** | ✅ installed & in use |
| DB driver | psycopg (v3) | **3.3.4** | ✅ installed. Note: production Docker image should prefer a system-libpq build over `psycopg-binary` |
| Database | PostgreSQL | 17.x or 18.x | ✅ in use — SQLite fully removed, no `.sqlite3` files remain |
| Cache / channel layer | Valkey (BSD-3, Redis-protocol-compatible) *or* Redis 8 | — | **Pending** — needed starting Phase 6 (real-time). Valkey recommended over Redis 8 for licensing reasons (Redis 8 ships AGPLv3/SSPL; Valkey is unencumbered BSD-3) |
| Realtime | Django Channels | 4.x | **Pending** — Phase 6 |
| ASGI server | Daphne or Uvicorn+Gunicorn | — | **Pending** — Phase 6/9 |
| Media storage | AWS S3 or Cloudinary | — | **Pending** — later phase |
| AI provider | OpenAI API (or compatible) | — | **Pending** — later phase |
| Frontend framework | Next.js | 16.2.x (App Router, Turbopack default) | **Pending** — not started |
| Language (frontend) | TypeScript | 5.x | **Pending** |
| UI | React 19 + Tailwind CSS + shadcn/ui | — | **Pending** |
| Runtime | Node.js | 22.x LTS | **Pending** |
| Containerization | Docker + Compose | — | **Pending** — Phase 9 |
| CI/CD | GitHub Actions | — | **Pending** — no remote configured yet |

Other pinned packages currently installed: `asgiref 3.12.1`, `PyJWT 2.13.0` (transitive via simplejwt), `sqlparse 0.5.5`, `typing_extensions 4.16.0`, `tzdata 2026.3`.

---

## 3. Key architectural decisions (with rationale)

Recorded here so the *why* survives, not just the *what*.

| Decision | Chosen | Rejected | Why |
|---|---|---|---|
| User model base | `AbstractUser` (kept `username` as a required, unique field alongside `email` login) | `AbstractBaseUser` rewrite (dropping `username`) | Once the serializer was built enforcing username uniqueness, this became the de facto decision. Consequence: Google OAuth signup will need a collision-safe username generator later, since Google doesn't supply one. |
| User/Block primary keys | UUID, explicit, set before first migration | Sequential integer (Django default) | Prevents enumeration of user count / record IDs via public APIs |
| Relationship/discovery app name | `relationships` | `friends`, `contacts`, `social` | Domain is relationship *policy* (block, visibility), not friendship. Renamed before the app was registered — zero migration cost |
| Social graph model | **Block only.** No `FriendRequest`/`Friend`/`Follow` table | Facebook-style mutual friend request | Contradicts "message anyone" product decision; adds a pending/accept state machine the product doesn't use |
| Relationship enforcement | Centralized in `relationships/services.py` (`is_blocked`, `can_view_profile`, `can_message`) — every future app calls these, never queries `Block` directly | Ad-hoc `if blocked:` checks scattered across `chat`, `notifications`, etc. | Single source of truth for interaction policy; `chat` (Phase 5) consumes this without knowing `Block` exists as a table |
| Block creation duplicate-check | **Directional** (`blocker=A, blocked=B` only) | Bidirectional (`is_blocked()`) | A blocking B must never prevent B from independently blocking A. Using the bidirectional check here would be a real bug — see engineering log below |
| Refresh token delivery | JSON response body | httpOnly cookie | Simpler MVP path; consciously trades some XSS resistance for implementation speed. Frontend must store in memory, never `localStorage` |
| Phone-number OTP | Rejected for v1 | — | No SMS provider is free at real production scale (checked Firebase, Twilio, MSG91 — all billed per-SMS beyond a small trial credit). Google OAuth + email/password cover auth for $0 |
| API versioning | `/api/v1/...` from the first endpoint | Unversioned | Cheap to add before frontend hardcodes paths, expensive after |
| Repo root | `backend/` (`.git` lives inside it) | Project root (`ChatDen/`) | Deliberately deferred — cheapest to move *before* `frontend/` has its own commit history. Revisit before `create-next-app` |
| Conversation scope, Phase 5 | Direct (1:1) messaging only | Group conversations | Group chat deferred to its own later milestone, same reasoning as deferring `FriendRequest` — ship the simpler case first |
| Conversation membership authorization | Declarative `IsConversationMember` permission class | Manual `raise PermissionDenied(...)` inside view logic | Keeps authorization consistent with the ownership-scoping pattern already used in `relationships`; declarative permission classes are easier to audit than logic buried in a view method |
| Duplicate direct-conversation prevention | Documented known limitation — narrow race-condition window on simultaneous first-contact requests between the same two users | DB-level uniqueness constraint on the participant pair | Same category as the `Block` model's `IntegrityError` backstop, but **not yet mitigated** at the DB level for `Conversation`. Flagged in §8 as an open item, not silently accepted |

---

## 4. Repository structure (current, confirmed)

```
ChatDen/                     ← .git is NOT here (see §3)
├── backend/                 ← .git lives here
│   ├── .venv/                ← the one and only virtualenv
│   ├── .env / .env.example
│   ├── manage.py
│   ├── requirements.txt
│   ├── accounts/             ← Phase 2 — identity
│   ├── authentication/       ← Phase 2 — JWT lifecycle
│   ├── profiles/             ← Phase 3 — profile data
│   ├── relationships/        ← Phase 4 — discovery & blocking policy
│   └── core/
│       ├── asgi.py / wsgi.py / urls.py
│       └── settings/
│           ├── base.py
│           ├── development.py
│           └── production.py
├── docs/
├── frontend/                  ← not yet created
├── LICENSE
└── README.md
```

`.env` — real secrets, gitignored, never committed (confirmed via `git ls-files`/`git log` audit — clean, nothing was ever tracked; no remote configured, so no exposure risk even during the near-miss when a key was pasted mid-conversation and subsequently rotated).
`.env.example` — same variable names, placeholder values, committed — the checklist for what needs to be set on a fresh clone.

---

## 5. Backend apps — responsibilities & status

| App | Owns | Status |
|---|---|---|
| `accounts` | Custom `User` (UUID pk, `AbstractUser`-based, `email` as `USERNAME_FIELD`), `UserManager` (hashing, email normalization, staff-default guards), registration | ✅ Complete, reviewed |
| `authentication` | JWT login/refresh/logout (blacklist), `/me` | ✅ Complete, reviewed |
| `profiles` | `Profile` (bio, auto-created via `post_save` signal on `User`), read/update API | ✅ Complete, reviewed |
| `relationships` | `Block` model + `services.py` policy layer + Blocking API | ✅ Complete, reviewed |
| `relationships` (discovery half) | User search, public profile detail, public serializer | 🟡 Reported complete — pending final file review |
| `chat` | `Conversation`, `Message`, `IsConversationMember` permission, direct-message REST API | 🟡 Reported complete (Phase 5) — pending file review |

### Endpoints, current

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

*Rows marked "reported complete, pending review" reflect developer-reported status. Endpoint paths for `chat` are the last agreed design — confirm against the actual `urls.py` once shared.*

---

## 6. Data model (current)

```
accounts.User (UUID pk)
  email (unique, USERNAME_FIELD), username (unique, AbstractUser default)
  password (hashed via UserManager, never bypassed)
  is_active, is_staff, is_superuser, date_joined
        │
        │ OneToOne
        ▼
profiles.Profile
  bio, created_at, updated_at

relationships.Block (UUID pk)
  blocker (FK → User), blocked (FK → User), created_at
  UniqueConstraint(blocker, blocked) — directional pair
  CheckConstraint(blocker != blocked)
  Individual indexes on both blocker and blocked (bidirectional query support)
```

```
chat.Conversation (UUID pk) — reported implemented, schema per last agreed design
  type ("direct"; group deferred), created_at
        │
        ▼
chat.Message
  conversation (FK), sender (FK → User), content, message_type,
  created_at, edited_at (nullable)
  — composite index on (conversation, created_at) recommended
    for the "last N messages" query pattern
```

🟡 Schema above reflects the last agreed Phase 5 design, not a confirmed read of the actual migration file. Confirm exact field names/constraints once `chat/models.py` is shared — same file-level confirmation every earlier app received.

---

## 7. Security posture — implemented

- Passwords hashed via `UserManager.create_user()` (`set_password()`) on every code path; DRF's default `.create()` never used
- `validate_password()` wired at the serializer level with a full `User` instance context, so `UserAttributeSimilarityValidator` actually functions (a raw field-level validator call would silently skip this check)
- Email treated case-insensitively end-to-end (`.lower()` in both the manager and serializer — closes a real duplicate-account bug found in review)
- Fail-closed DRF permissions: `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]` globally, `AllowAny` only where explicit
- `AnonRateThrottle` on public write endpoints (registration, login); `UserRateThrottle` on authenticated relationship endpoints
- JWT: short-lived access token, rotating + blacklisted refresh tokens (`token_blacklist` app installed & migrated)
- UUID primary keys on `User` and `Block` — no enumerable sequential IDs
- Every list/detail queryset in `relationships` is ownership-scoped via `get_queryset()` (not permission classes alone) — closes real IDOR risk on block list/delete
- Blocked-profile visibility returns 404, not 403 — never confirms an account exists to someone who's blocked
- No endpoint ever returns the full user table — search only, minimum query length
- Public user serializer excludes `email` and all sensitive fields by design
- Database-level `CheckConstraint`/`UniqueConstraint` back up app-level validation on `Block` (self-block, duplicate-block) as defense-in-depth
- `.env` audited clean — no secrets ever committed to git history; `.gitignore` correctly located at the actual repo root with working exception patterns
- 🟡 *Reported* (not yet file-verified): conversation/message access gated by a declarative `IsConversationMember` permission class, following the same ownership-scoping pattern as `relationships`

## 8. Security / engineering — deferred, open items

Tracked, not forgotten. Roughly in priority order:

- [ ] CORS (`django-cors-headers`) — blocking once frontend integration starts, not before
- [ ] `STATIC_ROOT` — needed before first `collectstatic`/deploy
- [ ] Centralized DRF exception handler (consistent `{"error": {...}}` shape across all apps)
- [ ] Argon2 password hasher (currently Django's PBKDF2 default)
- [ ] Separate JWT signing key, distinct from Django's `SECRET_KEY`
- [ ] `DEFAULT_PAGINATION_CLASS` + `DEFAULT_THROTTLE_RATES["user"]` — confirm both are actually in `base.py`
- [ ] Google OAuth wiring (`django-allauth` is installed but not in `INSTALLED_APPS`/middleware/settings yet)
- [ ] Automated test suite (`pytest-django`) — everything to date verified by manual testing only
- [ ] Git repo-root relocation to project root — before `frontend/` gets real commits
- [ ] Remote/CI-CD — no remote configured at all yet (local-only repo)
- [ ] **File-level audit of `chat/` (Phase 5)** — models, `IsConversationMember`, views, serializers reported complete but not yet reviewed the way every earlier app was
- [ ] **Duplicate direct-conversation race condition** — documented, not yet mitigated with a DB-level constraint (see §3)
- [ ] Cursor-based pagination on the message-list endpoint specifically — offset pagination degrades on a fast-growing table; confirm this was used rather than the default `PageNumberPagination`

---

## 9. Roadmap — phase status

```
Phase 0 — Environment                    ✅ 100%
Phase 1 — Foundation                     ✅ 100%
Phase 2 — Authentication                  ✅ 100%  (register, login, refresh, logout, me)
Phase 3 — User Profiles                   ✅ 100%
Phase 4 — Discovery & Relationship Policy ✅ Reported 100%  (Block subsystem independently
                                                     verified; discovery half reported
                                                     complete, pending file review)
Phase 5 — Conversations & Messages (REST) ✅ Reported 100%  (developer-reported complete
                                                     incl. manual endpoint testing;
                                                     NOT YET independently file-reviewed —
                                                     see verification note at top of doc)
Phase 6 — Real-time (Channels + Valkey)   🔄 Starting now — including presence
Phase 7 — AI Chatbot                       ⬜
Phase 8 — Media, Notifications             ⬜
Phase 9 — Deployment (Docker/Nginx/CI)     ⬜
```

**Explicitly corrected during planning:** presence/online-status was proposed as "Phase 5" at one point and rejected — it depends on both a `Conversation`/`Message` model and real-time infrastructure. It belongs with Channels/Valkey in Phase 6, matching the original architecture plan — now underway.

**On "all API/endpoint testing done":** confirmed as manual testing (Postman/equivalent) through Phase 5. No automated regression suite exists yet (`pytest-django`, tracked in §8) — manual testing proves today's behavior works, it doesn't protect Phase 6+ changes from silently breaking Phase 0–5 behavior. Worth prioritizing before the real-time layer adds real concurrency complexity.

---

## 10. House rules (established through review, still in force)

- Never bypass `UserManager.create_user()` for account creation, from any code path (registration, OAuth, admin, future bot accounts)
- Every list/detail view scopes its queryset to the requesting user's own data — permission classes alone are not ownership enforcement
- Relationship policy (`is_blocked`, `can_message`, `can_view_profile`) lives only in `relationships/services.py`; no other app queries `Block` directly
- Database constraints back up serializer/view-level validation, never replace it — always translate `IntegrityError` into a clean 4xx, never let it surface as a 500
- New apps are additive only: one `INSTALLED_APPS` line, one `urls.py` include line, no edits to already-shipped files unless fixing a confirmed bug
- Naming decisions (app names especially) get settled *before* `python manage.py startapp`, not after — free before registration, real cost after

---

## 11. Frontend architecture — planned, not yet started

No frontend code exists yet. This is the agreed design to build against once `chat` (Phase 5) is confirmed stable.

**Stack:** Next.js 16 (App Router) + TypeScript + Tailwind CSS + shadcn/ui, React 19, Node 22 LTS.

**Request paths:**
- **REST** (via `fetch`/an API client wrapper) for: auth, profile, conversation list, paginated message history, search — anything that isn't "must update live."
- **WebSocket** (once Phase 6 lands) for: live message delivery, typing indicators, presence — anything that must update live.
- **Direct-to-storage uploads**: client requests a pre-signed URL from the backend, uploads media straight to S3/Cloudinary, backend never proxies file bytes. Biggest single lever for keeping the backend fast under media load.

**Structure:**
```
frontend/
├── app/
│   ├── (auth)/login/, register/
│   └── (chat)/ layout.tsx, page.tsx (conversation list), [conversationId]/
├── components/chat/, ui/ (shadcn primitives, copied not installed — full restyle control), layout/
├── lib/api.ts (REST client), websocket.ts (connection hook, reconnect/backoff), auth.ts
└── hooks/
```

**Auth token handling (frontend responsibility, not yet built):** access token in memory (React state/context), refresh token from the JSON login response stored in-memory as well — **not `localStorage`**, per the XSS-exposure tradeoff already accepted in §3.

---

## 12. Feature scope

**In scope for v1 (per Phases 0–7 as currently planned):**
- Email/password + Google OAuth registration and login
- 1:1 direct messaging, text only initially
- Block/unblock, search-based user discovery
- Real-time delivery, typing indicators, online/last-seen presence (Phase 6)
- AI chatbot as a regular contact, streamed responses (Phase 7)
- Media messages — image, video, voice note, document (Phase 8)
- Web push notifications (Phase 8)

**Explicitly out of scope for v1** (each was proposed and deliberately deferred during planning, not overlooked):
- Group conversations
- Friend requests / followers / mutual-friends / suggestions
- Voice/video calls
- Message reactions, replies/threads, edit/delete, disappearing messages
- End-to-end encryption
- Phone-number OTP as an auth factor (cost-prohibitive at $0 budget — see §3)

---

## 13. License

No legal advice implied here — worth a quick decision, not a default left to chance, since `LICENSE` already exists as a placeholder in the repo.

**The real fork is business intent, not license text:**

| If your goal is... | Recommended | Why |
|---|---|---|
| A commercial product / SaaS you may monetize | **Proprietary — "All Rights Reserved."** No OSS license text; a short `LICENSE` stating the code is copyrighted, all rights reserved, no permission granted to copy/modify/redistribute | A permissive license (MIT/Apache) legally lets anyone — including a competitor — clone, rebrand, and ship this. Default to closed unless you have a specific reason to open it |
| A public portfolio piece / learning-in-public project | **MIT** | Simplest permissive license, minimal text, universally recognized, no real downside for a non-commercial goal |
| Open source but with patent protection (e.g. planning to accept outside contributions at some point) | **Apache 2.0** | Adds an explicit patent grant MIT doesn't have — matters more once other contributors are involved |

Given everything discussed in this thread — "production grade," "company grade," "for more users," "long run" — **proprietary/all-rights-reserved is the fit unless you tell me otherwise.** Say the word and I'll write the actual `LICENSE` file text for whichever direction you confirm.

---

## 14. GitHub readiness checklist

- [x] `.gitignore` at the correct repo root, with working `.env`/`.env.example` and `*.sqlite3` patterns
- [x] No secrets ever committed (audited via `git log --all -- .env`, confirmed clean)
- [ ] `LICENSE` file — pending your decision in §13
- [ ] `README.md` — see the companion file generated alongside this doc
- [ ] Confirm `SECRET_KEY`/`DB_PASSWORD` were rotated after the earlier in-chat exposure, before any push to a remote
- [ ] Decide repo-root relocation (§3) *before* adding a remote, if you're moving it — much cheaper before history includes a push
- [ ] Add a remote and push only after the above are settled
- [ ] Consider branch protection on `main` once collaborators exist (not urgent solo)
- [ ] `docs/` folder — this file and the README are good candidates to live there long-term
