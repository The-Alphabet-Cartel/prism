<p align="center">
  <img src="images/Prism-PFP.png" alt="Prism" width="200" />
</p>

# Prism

Member onboarding bot for [The Alphabet Cartel](https://fluxer.gg/yGJfJH5C)'s Fluxer community.

Part of the [Bragi](https://github.com/the-alphabet-cartel/bragi) bot infrastructure.

---

## What Prism Does

Named for the way light passes through a prism and reveals every color of the spectrum, Prism welcomes new members into the community. When someone posts their introduction in the designated `#introductions` channel, Prism assigns them the base member role and sends a warm welcome message — officially opening the server to them.

**Command-aware.** Prism distinguishes between introductions and staff commands. Messages starting with `!` are routed exclusively to the utility handler. Only genuine introduction posts trigger role assignment, so staff activity in the introductions channel never causes false welcome responses.

**Idempotent.** Prism checks whether a member already has roles before acting. If a member already has the base role (or any role beyond `@everyone`), Prism silently skips them. No double-welcomes, no errors.

**Admin-only commands.** Staff utility commands are silently ignored for non-administrator users — no error messages, no acknowledgement. Commands simply don't exist for regular members.

---

## How It Works

1. A member posts a message in the configured **introductions** channel
2. Prism fetches the member's current roles and checks for existing membership
3. If the member has no roles beyond `@everyone`, Prism assigns the configured base role
4. Prism replies with a welcome message confirming their role and orienting them to the community
5. If the member already has roles, Prism silently skips them

### Staff Commands

| Command | Permission | Description |
|---------|------------|-------------|
| `!roles` | Administrator | Lists all guild roles and their IDs |

---

## Configuration

Prism uses the Bragi three-layer config stack:

```
prism_config.json     ← structural defaults (committed)
      ↓
.env                  ← runtime overrides (not committed)
      ↓
Docker Secrets        ← sensitive values (never in source)
```

### Environment Variables

Copy `.env.template` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `LOG_FORMAT` | `human` | `human` (colorized) or `json` (structured) |
| `LOG_CONSOLE` | `true` | Enable console logging |
| `PRISM_LOG_FILE` | — | Optional log file path |
| `COMMAND_PREFIX` | `!` | Prefix for staff commands |
| `GUILD_ID` | — | Fluxer guild ID (**required**) |
| `PRISM_INTRODUCTIONS_CHANNEL_ID` | — | Channel ID to monitor (**required**) |
| `PRISM_BASE_ROLE_ID` | — | Role ID to assign on introduction (**required**) |
| `PUID` | `1000` | Container user ID |
| `PGID` | `1000` | Container group ID |

### Docker Secrets

| Secret | File | Description |
|--------|------|-------------|
| `prism_token` | `secrets/prism_fluxer_token` | Fluxer bot token |

---

## Deployment

### Prerequisites

- Docker Engine 29.x + Compose v5
- A Fluxer bot application with a token
- The `bragi` Docker network: `docker network create bragi`
- Host directories created:
  ```
  mkdir -p /opt/bragi/bots/prism-bot/logs
  mkdir -p /opt/bragi/bots/prism-bot/data
  ```

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/the-alphabet-cartel/prism.git
cd prism

# 2. Copy and configure environment
cp .env.template .env
# Edit .env — set GUILD_ID, PRISM_INTRODUCTIONS_CHANNEL_ID, and PRISM_BASE_ROLE_ID at minimum

# 3. Create the bot token secret
mkdir -p secrets
printf 'your-token-here' > secrets/prism_fluxer_token
chmod 600 secrets/prism_fluxer_token

# 4. Deploy
docker compose up -d
```

### Fluxer Bot Permissions

| Permission | Why |
|------------|-----|
| View Channels | Read messages in `#introductions` |
| Read Message History | Access existing channel messages |
| Send Messages | Send welcome replies |
| Manage Roles | Assign the base member role |

The bot's role must be positioned **above** the base member role in the Fluxer role hierarchy, or role assignment will fail with `Forbidden`.

---

## Project Structure

```
prism/
├── docker-compose.yml            ← Container orchestration
├── Dockerfile                    ← Multi-stage build (Rule #10)
├── docker-entrypoint.py          ← PUID/PGID + tini (Rule #12)
├── .env.template                 ← Config reference (committed)
├── requirements.txt              ← fluxer-py
├── images/
│   └── Prism-PFP.png            ← Bot profile picture
├── secrets/
│   ├── README.md                 ← Setup instructions (committed)
│   └── prism_fluxer_token       ← Bot token (gitignored)
└── src/
    ├── main.py                   ← Entry point + event dispatcher
    ├── config/
    │   └── prism_config.json     ← JSON defaults (Rule #4)
    ├── cogs/
    │   ├── introductions.py      ← Role assignment + welcome message
    │   └── utility_temp.py       ← Admin-only staff commands
    └── managers/
        ├── config_manager.py           ← Three-layer config (Rule #7)
        └── logging_config_manager.py   ← Colorized logging (Rule #9)
```

---

## Technical Notes

Prism uses a **command-first dispatcher** pattern due to fluxer-py's single-handler-per-event limitation:

- Messages starting with `!` are routed **exclusively** to the utility handler. The introductions handler never sees them.
- All other messages are routed **exclusively** to the introductions handler. The utility handler never sees them.
- This ensures commands typed in `#introductions` never trigger role assignment.

`member.roles` in fluxer-py 0.3.1 returns a **flat list of integer role IDs**, not role objects. All role comparisons are done by ID. Permission checks use Discord's bitfield standard (`0x8` = Administrator). See the [fluxer-py Quirks & API Reference](https://github.com/the-alphabet-cartel/bragi/blob/main/docs/standards/fluxer-py_quirks.md) for full details.

---

## Charter Compliance

| Rule | Status |
|------|--------|
| #1 Factory Functions | ✅ All managers use `create_*()` |
| #2 Dependency Injection | ✅ All managers accept deps via constructor |
| #3 Additive Development | ✅ |
| #4 JSON Config + Secrets | ✅ Three-layer stack |
| #5 Resilient Validation | ✅ Fallbacks with logging |
| #6 File Versioning | ✅ All files versioned |
| #7 Config Hygiene | ✅ Secrets/env/JSON separated |
| #8 Real-World Testing | ✅ Tested on live Fluxer instance |
| #9 LoggingConfigManager | ✅ Standard colorization |
| #10 Python 3.12 + Venv | ✅ Multi-stage Docker build |
| #11 File System Tools | ✅ |
| #12 Python Entrypoint + tini | ✅ PUID/PGID support |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| [fluxer-py](https://github.com/akarealemil/fluxer.py) | Fluxer bot library |

---

## Naming

Prism refracts light into its full spectrum — every color visible, every member seen. As the welcome bot, Prism is the first thing new members encounter: the moment the community opens up to them. Pairs with [Portia](https://github.com/the-alphabet-cartel/portia) (voice channel manager, from *The Merchant of Venice*) and [Puck](https://github.com/the-alphabet-cartel/puck) (stream monitor, from *A Midsummer Night's Dream*) in the Bragi bot family.

---

**Built with care for chosen family** 🏳️‍🌈
