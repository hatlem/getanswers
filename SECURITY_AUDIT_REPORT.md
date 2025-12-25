# 🛡️ SaaS Sikkerhets- og Lisensieringsaudit Rapport

**Prosjekt:** GetAnswers
**Dato:** 2025-12-24
**Analysert av:** AI Security Auditor
**Versjon:** 1.0

---

## 📋 Sammendrag

GetAnswers har en solid grunnleggende sikkerhetsarkitektur med JWT-autentisering, bcrypt passord-hashing, Fernet-kryptering for OAuth-tokens, og omfattende audit-logging. Men det er **kritiske hull** i lisenshåndtering og kontodeling-forebygging som må adresseres for en per-bruker SaaS-prismodell.

### Kritiske Funn:
- ❌ **Ingen begrensning på samtidige økter** - Samme bruker kan logge inn fra uendelig mange enheter
- ❌ **Ingen enhets- eller IP-sporing** knyttet til brukerprofil
- ❌ **Ingen mekanisme for å oppdage kontodeling**
- ❌ **MFA er ikke implementert**
- ❌ **JWT-tokens har 7 dagers levetid** uten rotasjon
- ❌ **Ingen server-side session invalidering**

---

## 🔑 Modul 1: Lisensieringsetterlevelse og Kontodeling

### Risiko 1.1: Ubegrenset Samtidige Økter
**Beskrivelse:** Systemet tillater ubegrenset antall samtidige økter per bruker. En bruker kan dele påloggingsinformasjon med hele teamet sitt, og alle kan bruke tjenesten samtidig.

**Teknisk Årsak:** JWT-tokens er stateless og valideres kun mot signatur og utløpstid. Ingen server-side øktregistrering eksisterer.

**Anbefalt Tiltak:**
```python
# Ny modell: UserSession
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    token_jti = Column(String(64), unique=True, nullable=False)  # JWT ID
    device_fingerprint = Column(String(256))
    ip_address = Column(String(45))
    user_agent = Column(String(512))
    city = Column(String(100))
    country = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
```

Implementer roterende øktnøkkel:
1. Ved innlogging: Opprett UserSession-rad og inkluder `jti` i JWT
2. Ved API-kall: Valider at `jti` eksisterer og `is_active=True`
3. Ved ny innlogging: Deaktiver eldste økt hvis maks antall overskrides (standard: 2 økter)
4. Gi brukeren varsling: "Du er nå logget ut fra [enhet] fordi du logget inn her"

**Innsats:** Middels
**Effekt:** Høy

---

### Risiko 1.2: Ingen Enhets- og IP-sporing
**Beskrivelse:** Systemet logger IP-adresser i audit-log, men knytter dem ikke til brukerøkter eller analyserer mønstre.

**Anbefalt Tiltak:**
```python
# Utvidelse av UserSession-modellen (se 1.1)
# Pluss ny tabell for historikk:

class DeviceHistory(Base):
    __tablename__ = "device_history"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"), index=True)
    device_fingerprint = Column(String(256), index=True)
    ip_address = Column(String(45))
    geolocation = Column(JSON)  # {"city": "Oslo", "country": "NO", "lat": ..., "lon": ...}
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    trust_level = Column(String(20))  # "trusted", "suspicious", "blocked"
    login_count = Column(Integer, default=1)
```

**Terskel-policy for mistenkelig aktivitet:**
- > 3 unike IP-adresser i 24 timer → Soft warning
- > 5 unike IP-adresser i 24 timer → Krever re-autentisering
- Innlogging fra nytt land innen 1 time → Blokkér + e-postvarsling
- > 10 unike enheter i 7 dager → Automatisk flagging for manuell gjennomgang

**Innsats:** Middels
**Effekt:** Høy

---

### Risiko 1.3: Ingen Adferdsheuristikk for Kontodeling
**Beskrivelse:** Ingen mekanismer for å oppdage bruksmønstre som tyder på at flere personer bruker samme konto.

**Anbefalt Tiltak:**
Implementer "Usage Anomaly Score" basert på:

```python
class UsagePattern(Base):
    __tablename__ = "usage_patterns"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"), unique=True)

    # Normale mønstre (lært over tid)
    typical_active_hours = Column(JSON)  # {"weekday": [9,10,11,...], "weekend": [...]}
    typical_countries = Column(JSON)     # ["NO", "SE"]
    typical_devices = Column(Integer)    # 2

    # Anomali-indikatorer
    sharing_score = Column(Float, default=0.0)  # 0.0-1.0
    last_anomaly_detected = Column(DateTime)
    anomaly_count_30d = Column(Integer, default=0)
```

**Delingsindikatorer å overvåke:**
1. **Geografisk umulighet:** To API-kall fra Oslo og New York innen 10 minutter
2. **Aktivitetsspredning:** Aktivitet fordelt over 18+ timer per dag konsekvent
3. **Enhetseksplosjon:** Plutselig økning i antall enheter
4. **Varierte User-Agents:** Blanding av Windows/Mac/Linux/Mobile som ikke passer én bruker

**Innsats:** Høy
**Effekt:** Høy

---

### Risiko 1.4: Manglende Brukervarslinger
**Beskrivelse:** Ingen mekanismer for å varsle brukere om ny enhetsaktivitet eller mistenkelige innlogginger.

**Anbefalt Tiltak:**
Implementer e-postvarslingssystem:

```python
# Ny notification service
async def notify_new_login(user: User, session: UserSession):
    if session.is_new_device or session.is_new_country:
        await send_email(
            to=user.email,
            template="security_alert",
            context={
                "type": "new_login",
                "device": session.user_agent,
                "location": f"{session.city}, {session.country}",
                "time": session.created_at.isoformat(),
                "action_url": f"{settings.FRONTEND_URL}/security/sessions"
            }
        )
```

**Varslings-maler (fokus på sikkerhet, ikke anklage):**
- "Ny innlogging oppdaget fra [by, land]"
- "Din konto ble nylig brukt fra en ny enhet"
- "Sikkerhetsvarsel: Uvanlig innloggingsmønster oppdaget"

**Innsats:** Lav
**Effekt:** Middels

---

## 🛡️ Modul 2: Sikkerhet og Autentisering

### Risiko 2.1: Ingen Multi-Faktor Autentisering (MFA)
**Beskrivelse:** Systemet støtter kun passord og magic link, ingen MFA.

**Anbefalt Tiltak:**
```python
# Ny MFA-modell
class UserMFA(Base):
    __tablename__ = "user_mfa"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"), unique=True)
    totp_secret = Column(String(64))  # Kryptert med Fernet
    totp_enabled = Column(Boolean, default=False)
    backup_codes = Column(JSON)  # Liste med hashed backup-koder
    last_used = Column(DateTime)

# TOTP-implementasjon med pyotp
import pyotp

def generate_totp_secret() -> str:
    return pyotp.random_base32()

def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # ±30 sekunder
```

**Implementasjonsflyt:**
1. Bruker aktiverer MFA i innstillinger
2. Backend genererer TOTP-hemmelighet og QR-kode
3. Bruker skanner med Google Authenticator/Authy
4. Bruker verifiserer med engangskode
5. System genererer 8 backup-koder (hashed lagret)
6. Ved fremtidige innlogginger: Passord → MFA-kode kreves

**Effekt på kontodeling:** MFA gjør deling betydelig vanskeligere da bruker må dele fysisk enhet eller appen.

**Innsats:** Middels
**Effekt:** Høy

---

### Risiko 2.2: Lang JWT Token-levetid uten Rotasjon
**Beskrivelse:** JWT-tokens har 7 dagers levetid (`ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7`). Et stjålet token gir full tilgang i en uke.

**Anbefalt Tiltak:**
Implementer kortlivede access tokens + refresh tokens:

```python
# Ny token-strategi
ACCESS_TOKEN_EXPIRE_MINUTES = 15    # 15 minutter
REFRESH_TOKEN_EXPIRE_DAYS = 7       # 7 dager

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"), index=True)
    token_hash = Column(String(64), unique=True)  # SHA256 av token
    session_id = Column(UUID, ForeignKey("user_sessions.id"))
    expires_at = Column(DateTime)
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime)
    replaced_by = Column(UUID)  # Token rotation

def create_tokens(user_id: str, session_id: str) -> dict:
    access_token = create_access_token(
        data={"sub": user_id, "session_id": session_id},
        expires_delta=timedelta(minutes=15)
    )
    refresh_token = secrets.token_urlsafe(32)
    # Lagre hashed refresh token i database
    return {"access_token": access_token, "refresh_token": refresh_token}
```

**Frontend-håndtering:**
- Ved 401: Automatisk prøv refresh
- Ved refresh-feil: Logg ut og redirect til login

**Innsats:** Middels
**Effekt:** Middels

---

### Risiko 2.3: Ingen Server-Side Token Invalidering
**Beskrivelse:** JWT-tokens kan ikke ugyldiggjøres før utløp. Logout på frontend sletter kun lokal kopi.

**Anbefalt Tiltak:**
Implementer token blacklist med Redis:

```python
# Token blacklist service
class TokenBlacklist:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "token_blacklist:"

    async def add(self, jti: str, expires_in: int):
        """Legg til token i blacklist til den uansett utløper"""
        key = f"{self.prefix}{jti}"
        await self.redis.setex(key, expires_in, "1")

    async def is_blacklisted(self, jti: str) -> bool:
        key = f"{self.prefix}{jti}"
        return await self.redis.exists(key)

# I get_current_user():
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    jti = payload.get("jti")

    if await token_blacklist.is_blacklisted(jti):
        raise AuthenticationError("Token har blitt ugyldiggjort")

    # ... resten av valideringen
```

**Innsats:** Lav
**Effekt:** Middels

---

### Risiko 2.4: API-nøkler ikke Implementert
**Beskrivelse:** Ingen API-nøkkel-system for programmatisk tilgang. Brukere kan dele JWT-tokens.

**Anbefalt Tiltak:**
```python
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"), index=True)
    organization_id = Column(UUID, ForeignKey("organizations.id"))
    name = Column(String(100))  # "CI/CD Integration"
    key_prefix = Column(String(8))  # "ga_live_" eller "ga_test_"
    key_hash = Column(String(64), unique=True)  # SHA256
    scopes = Column(JSON)  # ["read:emails", "write:policies"]
    rate_limit = Column(Integer, default=1000)  # per time
    last_used = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Bruksbegrensninger
    allowed_ips = Column(JSON)  # ["192.168.1.0/24"]
    allowed_origins = Column(JSON)  # ["https://app.example.com"]

# API-nøkkel-format: ga_live_abc123...xyz789 (40 tegn)
# Kun prefix + key_hash lagres, full nøkkel vises kun ved opprettelse
```

**Innsats:** Middels
**Effekt:** Middels

---

### Risiko 2.5: Brukervilkår (TOS) Mangler Eksplisitt Kontodelingsklausul
**Beskrivelse:** TOS-håndhevelse er uklar. Ingen teknisk referanse til konsekvenser.

**Anbefalt Tiltak:**
Legg til eksplisitt klausul i TOS:

```markdown
## Kontodeling og Lisensiering

1. **Én bruker per lisens:** Hver betalte lisens gir tilgang til én navngitt bruker.
   Deling av påloggingsinformasjon er strengt forbudt.

2. **Overvåking:** Vi overvåker innloggingsmønstre for å beskytte kontoen din og
   sikre rettferdig bruk av tjenesten.

3. **Konsekvenser ved brudd:**
   - Første gang: Advarsel via e-post
   - Andre gang: Midlertidig suspendering (7 dager)
   - Tredje gang: Permanent utestengelse uten refusjon

4. **Team-tilgang:** For team-bruk, vennligst oppgrader til en Team-plan som
   inkluderer separate kontoer for hvert teammedlem.
```

**Innsats:** Lav
**Effekt:** Lav (preventiv)

---

## 📈 Modul 3: Skaleringsklarhet og Datainnsamling

### Risiko 3.1: Audit Logs Lagres Kun Lokalt
**Beskrivelse:** Audit-logger skrives til fil/konsoll, ingen persistent database-lagring for analyse.

**Anbefalt Tiltak:**
```python
# Ny AuditLogEntry-modell for database-lagring
class AuditLogEntry(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID, primary_key=True)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    event_type = Column(String(50), index=True)
    user_id = Column(UUID, index=True)
    organization_id = Column(UUID, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(512))
    request_id = Column(String(64))
    endpoint = Column(String(200))
    method = Column(String(10))
    status_code = Column(Integer)
    response_time_ms = Column(Float)
    details = Column(JSON)

    # Partisjonering etter måned for ytelse
    __table_args__ = (
        Index('ix_audit_logs_user_time', 'user_id', 'timestamp'),
        Index('ix_audit_logs_event_type', 'event_type', 'timestamp'),
    )
```

**Retensjonspolicy:**
- Hot storage (PostgreSQL): 90 dager
- Cold storage (S3/Object Storage): 7 år (compliance)
- Automatisk arkivering via Celery-jobb

**Innsats:** Middels
**Effekt:** Høy

---

### Risiko 3.2: Ingen Kostnadsanalyse per Bruker
**Beskrivelse:** Ingen sporing av variable kostnader per bruker (AI-kall, e-post, lagring).

**Anbefalt Tiltak:**
```python
class UserUsageMetrics(Base):
    __tablename__ = "user_usage_metrics"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"), index=True)
    organization_id = Column(UUID, ForeignKey("organizations.id"))
    period_start = Column(Date, index=True)  # Første dag i måneden

    # Bruksmålinger
    emails_processed = Column(Integer, default=0)
    ai_responses_generated = Column(Integer, default=0)
    ai_tokens_input = Column(Integer, default=0)
    ai_tokens_output = Column(Integer, default=0)
    storage_bytes = Column(BigInteger, default=0)
    api_calls = Column(Integer, default=0)

    # Kostnadssporing (i cent)
    ai_cost_cents = Column(Integer, default=0)
    email_cost_cents = Column(Integer, default=0)
    storage_cost_cents = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint('user_id', 'period_start'),
    )

# Oppdateres atomisk ved hver operasjon
async def track_ai_usage(user_id: UUID, input_tokens: int, output_tokens: int):
    cost = calculate_ai_cost(input_tokens, output_tokens)
    await db.execute(
        update(UserUsageMetrics)
        .where(user_id=user_id, period_start=current_month_start())
        .values(
            ai_tokens_input=UserUsageMetrics.ai_tokens_input + input_tokens,
            ai_tokens_output=UserUsageMetrics.ai_tokens_output + output_tokens,
            ai_cost_cents=UserUsageMetrics.ai_cost_cents + cost,
            ai_responses_generated=UserUsageMetrics.ai_responses_generated + 1
        )
    )
```

**Variable kostnader å spore:**
| Ressurs | Estimert kost |
|---------|---------------|
| Claude Sonnet (input) | $3 / 1M tokens |
| Claude Sonnet (output) | $15 / 1M tokens |
| E-post sending | $0.001 / e-post |
| Lagring | $0.023 / GB / måned |

**Innsats:** Middels
**Effekt:** Høy

---

### Risiko 3.3: Begrenset Prismodellfleksibilitet
**Beskrivelse:** Nåværende planer (Free/Starter/Pro/Enterprise) mangler team-rabatt.

**Anbefalt Tiltak:**
Utvid prismodellen med volum-rabatt:

```python
# Ny prisstruktur
PRICING_TIERS = {
    "individual": {
        "starter": {"price": 29, "seats": 1},
        "pro": {"price": 79, "seats": 1},
    },
    "team": {
        "team_5": {"price": 25 * 5, "seats": 5},       # 125/mnd, 25/sete
        "team_10": {"price": 22 * 10, "seats": 10},    # 220/mnd, 22/sete
        "team_25": {"price": 19 * 25, "seats": 25},    # 475/mnd, 19/sete
    },
    "enterprise": {
        "custom": {"price": "kontakt", "seats": "ubegrenset"}
    }
}

# I Subscription-modellen:
class Subscription(Base):
    # ... eksisterende felt
    seat_count = Column(Integer, default=1)
    price_per_seat = Column(Integer)  # I cent

    @property
    def monthly_price(self):
        return self.seat_count * self.price_per_seat
```

**Foreslått landing page messaging:**
- "Bruker teamet ditt GetAnswers? Spar opptil 35% med Team-planer"
- Pop-up til brukere med mistenkelig delingsaktivitet: "Det ser ut som flere bruker denne kontoen. Oppgrader til Team-plan for separate tilganger og bedre sikkerhet."

**Innsats:** Høy
**Effekt:** Middels

---

## 📊 Prioriteringsmatrise

| Risiko | Beskrivelse | Innsats | Effekt | Prioritet |
|--------|-------------|---------|--------|-----------|
| 1.1 | Samtidige økter | Middels | Høy | 🔴 Kritisk |
| 2.1 | Manglende MFA | Middels | Høy | 🔴 Kritisk |
| 1.2 | Enhets/IP-sporing | Middels | Høy | 🔴 Kritisk |
| 3.1 | Audit logs i DB | Middels | Høy | 🟡 Høy |
| 3.2 | Kostnadsanalyse | Middels | Høy | 🟡 Høy |
| 2.2 | Token-rotasjon | Middels | Middels | 🟡 Høy |
| 2.3 | Token blacklist | Lav | Middels | 🟢 Medium |
| 1.3 | Adferdsheuristikk | Høy | Høy | 🟡 Høy |
| 1.4 | Brukervarslinger | Lav | Middels | 🟢 Medium |
| 2.4 | API-nøkler | Middels | Middels | 🟢 Medium |
| 2.5 | TOS-oppdatering | Lav | Lav | 🟢 Medium |
| 3.3 | Team-prising | Høy | Middels | 🔵 Lav |

---

## 🚀 Implementeringsrekkefølge (Anbefalt)

### Fase 1: Kritiske Sikkerhetshull (2-3 uker)
1. ✅ Implementer UserSession-modell med øktbegrensning
2. ✅ Legg til enhets- og IP-sporing
3. ✅ Implementer token blacklist med Redis
4. ✅ Reduser JWT-levetid + refresh tokens

### Fase 2: Lisensbeskyttelse (2-3 uker)
1. ✅ Implementer MFA (TOTP)
2. ✅ Legg til brukervarslinger for ny enhetsaktivitet
3. ✅ Oppdater TOS med kontodelings-klausul
4. ✅ Migrer audit logs til database

### Fase 3: Innsikt og Skalering (2-3 uker)
1. ✅ Implementer brukskostnadsanalyse
2. ✅ Bygg adferdsheuristikk for delingdeteksjon
3. ✅ Legg til API-nøkler for programmatisk tilgang
4. ✅ Utvid prismodell med team-planer

---

## 📁 Vedlegg: Foreslått Mappestruktur for Nye Moduler

```
backend/app/
├── models/
│   ├── user_session.py      # Ny: Økthåndtering
│   ├── device_history.py    # Ny: Enhetssporing
│   ├── user_mfa.py          # Ny: MFA-konfigurasjon
│   ├── refresh_token.py     # Ny: Refresh tokens
│   ├── api_key.py           # Ny: API-nøkler
│   ├── audit_log_entry.py   # Ny: Persistent audit logs
│   └── usage_metrics.py     # Ny: Brukskostnader
│
├── services/
│   ├── session_manager.py   # Ny: Økthåndtering
│   ├── mfa_service.py       # Ny: TOTP/backup-koder
│   ├── anomaly_detector.py  # Ny: Adferdsheuristikk
│   ├── notification_service.py  # Ny: E-postvarsler
│   └── usage_tracker.py     # Ny: Kostnadssporing
│
├── api/
│   ├── sessions.py          # Ny: /api/sessions endpoints
│   ├── mfa.py               # Ny: /api/mfa endpoints
│   └── api_keys.py          # Ny: /api/keys endpoints
```

---

*Rapport generert av AI Security Auditor - GetAnswers*
