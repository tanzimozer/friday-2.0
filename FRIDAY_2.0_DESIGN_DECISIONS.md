# FRIDAY 2.0: DESIGN DECISIONS & SECURITY REQUIREMENTS
**Extract from PDF Documents**  
**Date:** June 09, 2026  

---

## DESIGN DECISIONS SUMMARY

### Core Architectural Decisions

| Decision | Rationale | Implementation |
|----------|-----------|-----------------|
| **Single-factor vault** → **Three-factor vault** | Eliminate single points of failure; hardware binding prevents credential portability | Hardware UUID + Passphrase + Time-window gating |
| **Implicit decision rules** → **Explicit codified rules** | Eliminate hidden inference; make autonomous decisions transparent & auditable | 5 rules with quantified thresholds in code |
| **Scattered credentials** → **Centralized EDITH vault** | Single source of truth; consistent encryption; unified access control | All OAuth + PAT in `~/.hermes/.edith/` with AES-256-GCM |
| **No verification protocol** → **3-question challenge** | Gate sensitive operations; prevent unauthorized credential access | SHA-256 hashed Q&A with 30-min lockout on failure |
| **Implicit autonomy** → **Explicit silence protocol** | Clarify when system acts without user input; require explicit work queue | Autonomy only after 60+ min idle AND queued work present |

### Security Decisions

| Requirement | Standard | Implementation |
|-------------|----------|-----------------|
| **Credential encryption** | AES-256-GCM | All OAuth + PAT stored encrypted; no plaintext ever on disk |
| **Passphrase hashing** | bcrypt | bcrypt-10 with constant-time comparison (timing-attack resistant) |
| **Question hashing** | SHA-256 | Verification answers hashed + salted; no plaintext recovery |
| **File permissions** | Unix modes | All vault files 0600 (user read/write only) |
| **Hardware binding** | System UUID | Vault only accessible on original hardware (UUID mismatch = inaccessible) |
| **Time-window gating** | Behavioral control | ±5 min from last auth; 5 min auto-purge; re-auth required outside window |
| **Obfuscated naming** | Reconnaissance prevention | File names don't reveal contents (e.g., `google_oauth_vault` not `google_token.txt`) |

### Framework Decisions

| Rule | Trigger | Threshold | Rationale |
|------|---------|-----------|-----------|
| **30-Day Rule** | Recurring task + effort ≤ 30 days | Auto-design if eligible | Invest in automation for repeating work; eliminate drudgery |
| **Minimal Context** | Rough notes + intent ambiguous | Confidence ≥ 0.75 to execute | Infer intent from patterns; ask if uncertain; bias toward action |
| **Intent Inference** | Pattern observed in history | Pattern strength ≥ 0.75 | Deliver on best historical match; reduce clarification overhead |
| **Silence Protocol** | Idle > 60 min + work queue | Queued work only | Continue autonomously on explicit work; don't speculate |
| **Execution-First** | New task requested | MVP score ≥ 0.75 + ≤ 24h | Ship early & often; iterate on live work; reduce planning overhead |

---

## SECURITY REQUIREMENTS (FROM DESIGN DOCS)

### EDITH Vault Requirements

**Requirement 1.1: Three-Factor Authentication**
- All vault access requires all 3 factors in sequence
- Failure on any factor → immediate denial + logging
- Hardware UUID must match system on startup
- Passphrase verification must be constant-time (no timing leaks)
- Time-window must enforce ±5 min window from last successful auth

**Requirement 1.2: Credential Encryption**
- All OAuth tokens → AES-256-GCM encrypted
- All GitHub PAT → AES-256-GCM encrypted
- No plaintext credentials ever written to disk
- Encryption key derived from passphrase (hardware UUID + bcrypt)
- Authenticated encryption (AES-GCM) detects tampering

**Requirement 1.3: Verification Protocol**
- 3-question challenge for sensitive operations
- All answers must be SHA-256 hashed + salted
- No plaintext answers stored anywhere
- Q1-Q3 must be answered in order
- Failure on any question → 30-minute vault lockout (all credential access blocked)
- Lockout automatically expires after 30 minutes

**Requirement 1.4: Time-Window Gating**
- Credentials valid for ±5 minutes from last successful authentication
- After 5 minutes of idle time → credentials auto-purged from memory
- Subsequent access outside the window requires full 3-factor re-authentication
- Timestamp of last successful auth stored and checked on every access

**Requirement 1.5: File & Permission Hardening**
- All vault files (`~/.hermes/.edith/*`) must be mode 0600 (user read/write only)
- No world-readable or group-readable files
- Directory permissions 0700 (user read/write/execute only)
- File names must not reveal contents (obfuscated naming)

**Requirement 1.6: Access Logging & Audit Trail**
- All vault access attempts logged (success + failure)
- Verification protocol attempts logged (including failures)
- Lockout events logged with timestamp + reason
- Audit log stored centrally in `~/.hermes/logs/security_events/`

### Framework Decision Requirements

**Requirement 2.1: 30-Day Rule Quantification**
- System must detect recurring tasks (frequency ≥ 2 occurrences in 90-day window)
- Effort estimation must be derived from task description or historical data
- If effort ≤ 30 days, auto-design must be triggered automatically
- Output must include: automation architecture, phase breakdown, time saved estimate

**Requirement 2.2: Minimal Context Confidence Threshold**
- Confidence scoring must be reproducible & auditable (logged decision trace)
- Minimum confidence threshold is 0.75 (75% certainty)
- Confidence score components documented: pattern match, contextual signals, explicit mention, risk
- If confidence < 0.75, system must ask clarifying questions; no guessing

**Requirement 2.3: Intent Inference Pattern Matching**
- Pattern matching must search historical context (sessions, tasks, decisions)
- Pattern strength scoring: frequency (0–0.35) + recency (0–0.25) + consistency (0–0.15) + relevance (0–0.25)
- Minimum pattern strength threshold is 0.75 (75% match quality)
- If pattern strength ≥ 0.75, deliver on best match automatically
- If pattern strength < 0.75, ask user preference (with top 3 patterns shown)

**Requirement 2.4: Silence Protocol Implementation**
- Idle monitoring must run continuously (check every 60 seconds)
- Autonomy threshold is 60+ minutes of idle time (no user input)
- Precondition: Work queue must be explicitly populated (no speculative execution)
- Autonomy execution requires all task dependencies to be satisfied
- System must log each autonomy decision with reason + timestamp

**Requirement 2.5: Execution-First MVP Shipping**
- MVP feasibility scoring: feature coverage (≥20%, weight 0.40) + user value (weight 0.30) + deployment safety (weight 0.30)
- MVP score threshold is 0.75 (75% confidence in MVP adequacy)
- Shipping timeline threshold is ≤ 24 hours
- If both thresholds met, ship immediately (no planning delays)
- If either threshold not met, propose phased delivery plan instead

**Requirement 2.6: Rule Codification & Transparency**
- All 5 rules must be codified in code, not learned behavior
- Decision logic must be explicitly documented & auditable
- Threshold values must be hardcoded constants (not tuned dynamically)
- Every rule application must log: rule name, inputs, threshold check, decision output, confidence score
- Framework repo (Tanzim_Frameworks) must be published with complete rule definitions

---

## DECISION THRESHOLDS (QUANTIFIED)

### Security Thresholds

| Parameter | Value | Unit | Enforced By |
|-----------|-------|------|-------------|
| Hardware UUID match | 100% | Exact match | System startup |
| Passphrase entropy | ≥ 12 characters | Required length | Implementation |
| Bcrypt cost factor | 10 | Iterations | `bcrypt-10` |
| Time-window duration | ±5 | Minutes | Runtime clock |
| Auto-purge timeout | 5 | Minutes idle | Memory management |
| Verification lockout | 30 | Minutes | Security policy |
| File permissions (vault) | 0600 | Unix mode | File system |

### Framework Thresholds

| Parameter | Value | Unit | Enforced By |
|-----------|-------|------|-------------|
| Confidence threshold | 0.75 | Ratio (0–1) | Minimal Context rule |
| Pattern strength threshold | 0.75 | Ratio (0–1) | Intent Inference rule |
| Recurring task frequency | ≥ 2 | Occurrences/90 days | 30-Day Rule detector |
| Effort estimate max | 30 | Days | 30-Day Rule trigger |
| Silence protocol idle | > 60 | Minutes | Silence Protocol rule |
| MVP score threshold | 0.75 | Ratio (0–1) | Execution-First rule |
| MVP shipping timeline | ≤ 24 | Hours | Execution-First rule |
| MVP feature coverage | ≥ 0.20 | Ratio (0–1) | MVP scoring |
| Confidence components weight | Sum = 1.0 | Normalized | Scoring algorithm |

---

## ARCHITECTURE PILLARS

### Pillar 1: Security Hardening (EDITH Vault)

**Goals:**
1. Centralize all credentials in single secure vault
2. Prevent credential theft via three-factor authentication
3. Enforce time-based credential expiration (prevent stale access)
4. Detect & block unauthorized access attempts (verification protocol)
5. Make credential access auditable & transparent

**Key Components:**
- Hardware UUID binding (system-specific identifier)
- Passphrase authentication (bcrypt-10, constant-time comparison)
- Time-window gating (±5 min, 5 min auto-purge)
- Verification protocol (3-question SHA-256 challenge)
- AES-256-GCM encryption (authenticated, modern standard)
- Obfuscated file naming (reconnaissance prevention)
- File permission hardening (0600 mode)
- Centralized audit logging

**Threat Model Addressed:**
- Hardware theft → UUID binding prevents vault access on stolen device
- Credential theft → AES-256-GCM encryption prevents plaintext extraction
- Brute force → Bcrypt-10 + time-window gating slow down attackers
- Unauthorized access → Verification protocol gates sensitive operations
- Stale credential reuse → Auto-purge after 5 min idle
- Timing attacks → Constant-time passphrase comparison

### Pillar 2: Operating System Alignment (Personal Framework)

**Goals:**
1. Codify explicit decision rules (no hidden inference)
2. Quantify all decision thresholds (transparency)
3. Enable autonomous operation with clear boundaries
4. Reduce user clarification overhead (bias toward action at ≥0.75 confidence)
5. Ship fast & iterate on live work (execution-first)

**Key Components:**
- 30-Day Rule (auto-design recurring tasks ≤ 30 days)
- Minimal Context (execute at confidence ≥ 0.75; ask if lower)
- Intent Inference (deliver on best pattern match ≥ 0.75 strength)
- Silence Protocol (autonomy after 60+ min idle + explicit work queue)
- Execution-First (ship MVP ≥ 0.75 score + ≤ 24h timeline)

**Decision Boundaries:**
- Confidence/strength thresholds are **0.75** (3/4 certainty)
- Effort thresholds are **≤ 30 days** (automation sweet spot)
- Idle thresholds are **> 60 minutes** (autonomy trigger)
- Shipping thresholds are **≤ 24 hours** (MVP velocity)
- All thresholds are **hardcoded constants**, not tuned dynamically

**Bias & Philosophy:**
- **Bias toward action** — Execute at 0.75+ confidence; ask if lower
- **Bias toward shipping** — Deploy MVP at 0.75 score; iterate live
- **Bias toward autonomy** — Continue on explicit work queue; require 60+ min idle
- **No speculative execution** — Autonomy only from explicit work queue, never speculative

---

## CURRENT STATE → FRIDAY 2.0 MIGRATION PATH

### Current Baseline

| Component | Status | Issue |
|-----------|--------|-------|
| Credentials | Scattered across files | No centralized vault; inconsistent encryption |
| Decision rules | Implicit (learned behavior) | Hidden inference; hard to audit |
| Framework | Personal (not codified) | Rules in practice, not in code |
| Verification | None | No gating on sensitive operations |
| Security | Basic encryption | No three-factor authentication; no time-window gating |

### Friday 2.0 Target

| Component | Status | Improvement |
|-----------|--------|-------------|
| Credentials | EDITH vault (centralized) | Single source of truth; unified AES-256-GCM encryption |
| Decision rules | Codified with thresholds | Explicit in code; 0.75 confidence gates; auditable |
| Framework | Published (Tanzim_Frameworks) | Rules versioned in GitHub; decision logic transparent |
| Verification | 3-question challenge | SHA-256 hashed Q&A; 30-min lockout on failure |
| Security | Three-factor + time-gating | Hardware binding + passphrase + time-window + verification |

### Migration Checklist

- [x] Design EDITH vault architecture (three-factor, AES-256-GCM)
- [x] Design verification protocol (3-question SHA-256 challenge)
- [x] Codify 5 framework rules with quantified thresholds
- [x] Design confidence scoring algorithm (0.75 threshold)
- [x] Design pattern strength scoring (0.75 threshold)
- [x] Design MVP feasibility scoring (0.75 score + ≤ 24h)
- [ ] Implement EDITH vault in code
- [ ] Migrate credentials to EDITH (encrypt existing OAuth + PAT)
- [ ] Implement verification protocol (Q1-Q3 challenge)
- [ ] Implement 5 framework rules in operating system
- [ ] Publish Tanzim_Frameworks repo with rule definitions
- [ ] Complete Phase 1–4 testing & validation
- [ ] Deploy to production (go-live)

---

## EXTRACTED REQUIREMENTS FROM DESIGN DOCS

### From Credentials.pdf
- Google OAuth (5 services): gmail, drive, docs, sheets, chat
- GitHub PAT: repo, gist, user, workflow scopes
- EDITH vault: Three-factor access, AES-256-GCM encryption
- Verification questions: 3 SHA-256 hashed (Real Madrid, Pepper Potts, Myself)

### From 02_HIGH-LEVEL-DESIGN.pdf
- **Pillar 1 (Security):** Three-factor vault, verification protocol, AES-256-GCM encryption, obfuscated naming
- **Pillar 2 (Framework):** 30-day rule, minimal context (≥0.75), intent inference, silence protocol (60+ min idle), execution-first
- **Implementation goals:** Trust (explicit rules), autonomy (clear thresholds), security (encrypted & gated), clarity (published framework)
- **Timeline:** 4 weeks (4 phases, 1 week each)

### From 01_SNAPSHOT.pdf
- Current: 8.95 GB memory, 5 integrations live, 77/79 skills unused
- Friction: 98% skill library overhead, no explicit decision rules, scattered credentials, no verification protocol

### From 03_LEVEL-DESIGN.pdf
- **EDITH three-factor:** Hardware UUID + Passphrase (bcrypt-10) + Time-window (±5 min, 5 min auto-purge)
- **Credential storage:** Google OAuth (AES-256-GCM), GitHub PAT (AES-256-GCM), Verification hashes (SHA-256 + salt)
- **Verification protocol:** Q1-Q3 in order, 30-min lockout on failure
- **Personal framework:** 5 rules with quantified thresholds, codified in operating system

### From 04_MEMO.pdf
- **Deliverables:** EDITH vault (designed), Verification protocol (designed), Personal framework (codified), Integrations (live)
- **Implementation phases:** Phase 1 (EDITH) → Phase 2 (Framework) → Phase 3 (Consolidation) → Phase 4 (Testing)
- **Next steps:** Security sign-off, framework validation, integration smoke test, go-live

---

## KEY REFERENCES & LINKS

**Design Documents Location:**
- `/home/hermes/friday-2.0/01_SNAPSHOT.pdf`
- `/home/hermes/friday-2.0/02_HIGH-LEVEL-DESIGN.pdf`
- `/home/hermes/friday-2.0/03_LEVEL-DESIGN.pdf`
- `/home/hermes/friday-2.0/04_MEMO.pdf`
- `/home/hermes/friday-2.0/Credentials.pdf`

**Implementation Specifications (Generated):**
- `/home/hermes/FRIDAY_2.0_IMPLEMENTATION_SPECIFICATION.md`
- `/home/hermes/FRIDAY_2.0_TECHNICAL_ARCHITECTURE.md`
- `/home/hermes/FRIDAY_2.0_DESIGN_DECISIONS.md` (this document)

**Repository:**
- `Tanzim_Frameworks` (GitHub private) — Decision rules & framework schema

---

**Document Status:** Design Phase Complete  
**Extraction Date:** June 09, 2026  
**Ready for:** Phase 1 Implementation (EDITH Hardening & Verification Protocol)
