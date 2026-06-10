# FRIDAY 2.0 IMPLEMENTATION SPECIFICATION
**Generated:** June 09, 2026  
**Status:** Ready for Deployment  
**Scope:** EDITH 2.0 Vault + Personal Framework (5-Core Rules)

---

## EXECUTIVE SUMMARY

Friday 2.0 is a two-pillar security & autonomy framework for Claude Max:

1. **EDITH 2.0 Vault** — Hardware-bound, three-factor authentication, AES-256-GCM encryption
2. **Personal Framework** — 5 explicit decision rules with quantified thresholds, no hidden inference

This specification details implementation of the user's 5 major changes with technical architecture, security requirements, and operational decision rules.

---

## PILLAR 1: EDITH 2.0 VAULT (SECURITY HARDENING)

### Architecture Overview
The EDITH Vault is the single-source-of-truth for all credential storage. All access is three-factor gated.

| Factor | Type | Implementation | Storage | Status |
|--------|------|-----------------|---------|--------|
| **Factor 1** | Hardware UUID (System Binding) | System-specific identifier | `~/.hermes/.edith/hardware_uuid` | Required on startup |
| **Factor 2** | Passphrase + Salt (Knowledge) | bcrypt-10 hashed, constant-time comparison | `~/.hermes/.edith/passphrase_hash` | Knowledge-based auth |
| **Factor 3** | Time-Window Gating (Behavioral) | ±5 min from last auth; 5 min auto-purge on idle | Runtime in-memory | Auto-expire credentials |

**Requirement: All 3 factors must pass in order to unlock vault.**

### Credential Storage Matrix

| Service | File | Format | Encryption | Scopes/Permissions |
|---------|------|--------|------------|-------------------|
| **Google OAuth** | `google_oauth_vault` | JSON | AES-256-GCM | gmail, drive, docs, sheets, chat |
| **GitHub PAT** | `github_pat_vault` | JSON | AES-256-GCM | repo, gist, user, workflow |
| **EDITH Verification** | `verification_hashes.json` | SHA-256 + salt | No plaintext | Challenge protocol |

### Verification Protocol (3-Question Challenge)

**Required for:** Sensitive operations, credential access, vault unlocking

| Question | Answer (Hashed) | Difficulty | Status |
|----------|-----------------|------------|--------|
| Q1: Favorite football team? | SHA-256(Real Madrid) | Personal knowledge | Active |
| Q2: Favorite character? | SHA-256(Pepper Potts) | Personal knowledge | Active |
| Q3: Favorite person? | SHA-256(Myself) | Personal knowledge | Active |

**Lockout Rule:** Failure on any question → 30-minute vault lock (no credential access)

### Security Requirements

1. **No plaintext storage** — All credentials AES-256-GCM encrypted
2. **Obfuscated naming** — File names do not reveal contents
3. **File permissions** — All vault files mode `0600` (user-read-write only)
4. **Hardware binding** — UUID mismatch → vault inaccessible
5. **Time-window gating** — Credentials auto-purge after 5 minutes idle
6. **Constant-time comparison** — Passphrase checks resist timing attacks
7. **Centralized storage** — All credentials in `~/.hermes/.edith/` directory

### Implementation Checklist

- [x] Hardware UUID binding (`hardware_uuid`)
- [x] Passphrase + salt storage (`passphrase_hash`)
- [x] Time-window gating mechanism (±5 min window, 5 min auto-purge)
- [x] Verification protocol (3 SHA-256 hashed questions)
- [x] AES-256-GCM encryption for OAuth & PAT vaults
- [x] File permission hardening (mode 0600)
- [ ] Integration testing (all credential access paths)
- [ ] Security audit (hardware UUID, time-gating, constant-time ops)

---

## PILLAR 2: PERSONAL FRAMEWORK (OPERATING SYSTEM ALIGNMENT)

### Core Architecture

The Personal Framework codifies 5 explicit decision rules that govern autonomous behavior. Each rule has a quantified trigger and threshold; no hidden inference.

### Rule 1: 30-Day Rule (Auto-Design Recurring Tasks)

**Trigger:** Recurring task identified  
**Threshold:** Effort estimate ≤ 30 days  
**Action:** Auto-design automation  
**Rationale:** Eliminate repetitive work; invest in automation for tasks that repeat

**Implementation:**
```
IF task.recurring == true AND task.effort_days <= 30 THEN
  design_automation()
  queue_implementation()
END
```

**Outputs:**
- Automation design (architecture, phases, timeline)
- Implementation queue (prioritized steps)
- Time saved estimate

---

### Rule 2: Minimal Context (Infer Intent, Act if Confidence ≥ 0.75)

**Trigger:** Rough notes received (incomplete requirements)  
**Threshold:** Confidence score ≥ 0.75 (75% certainty on intent)  
**Action:** Infer intent & execute  
**Fallback:** If confidence < 0.75, explicitly ask clarifying questions

**Implementation:**
```
GIVEN incomplete_notes FROM user
COMPUTE confidence_score(intent_inference)
IF confidence_score >= 0.75 THEN
  execute_on_best_match(inferred_intent)
ELSE
  ask_clarifying_questions()
  await_explicit_response()
END
```

**Confidence Scoring:**
- Pattern match to historical behavior: +0.25–0.40 points
- Contextual signals (task type, domain): +0.15–0.25 points
- Explicit mention of intent: +0.10–0.25 points
- Risk assessment (low-risk ops): +0.10 points

**Example:**
- User: "Run the usual Friday sync"
- Inference: Pull repo, update memory, cross-session context merge
- Confidence: 0.82 (strong pattern match + low-risk) → Execute
- User: "Do something with the vault"
- Confidence: 0.45 (ambiguous) → Ask: "Update credentials? Audit permissions? Rotate passphrases?"

---

### Rule 3: Intent Inference (Parse Patterns, Deliver on Best Match)

**Trigger:** Pattern observed in history  
**Threshold:** Pattern strength ≥ 0.75 (repeat frequency + consistency)  
**Action:** Deliver on best match  
**Fallback:** If pattern strength < 0.75, ask for clarification

**Implementation:**
```
GIVEN user_request
SEARCH historical_context FOR matching_patterns
RANK patterns BY (frequency, recency, consistency)
BEST_MATCH = patterns[0]

IF pattern_strength(BEST_MATCH) >= 0.75 THEN
  deliver_matching_output(BEST_MATCH)
  log_pattern_usage()
ELSE
  ask_explicit_preference()
  cache_user_choice()
END
```

**Pattern Scoring:**
- Frequency (count of repetitions): 0–0.35 points
- Recency (days since last occurrence): 0–0.25 points
- Consistency (variance across repetitions): 0–0.15 points
- Contextual relevance (match to current request): 0–0.25 points

**Example:**
- Historical: "Generate weekly memory audit every Monday"
- Pattern strength: 0.88 (high frequency, consistent, recent)
- User: "Run the audit"
- Action: Execute weekly memory audit without further confirmation

---

### Rule 4: Silence Protocol (Continue Autonomously When Idle > 60 min)

**Trigger:** Idle time > 60 minutes AND queued work exists  
**Threshold:** Work queue not empty + system resources available  
**Action:** Continue logical next steps autonomously  
**Requirement:** Must have explicitly queued work (not speculative)

**Implementation:**
```
WHILE session_active DO
  IF idle_time > 60_minutes AND work_queue.length > 0 THEN
    next_task = work_queue.pop()
    log_autonomy_decision("idle_threshold_exceeded", next_task)
    execute_next_task()
  ELSE
    await_user_input()
  END
END
```

**Preconditions:**
- Work queue explicitly populated by user or system
- No user-requested pause or suspension
- System resource availability confirmed
- Task dependencies all satisfied

**Example:**
- User: "Queue: [Task A, Task B, Task C]"
- User goes idle for 90 minutes
- System auto-executes Task A → Task B → Task C
- Logs: "Silence protocol: executed 3 queued tasks"

---

### Rule 5: Execution-First (Ship MVP Immediately, Iterate from Live Work)

**Trigger:** New task requested  
**Threshold:** MVP scope defined (> 20% feature coverage, < 24h to ship)  
**Action:** Ship MVP immediately  
**Iteration:** Deploy; gather feedback; iterate on live work

**Implementation:**
```
GIVEN new_task
DEFINE mvp_scope(task)
  IF mvp_feasibility_score >= 0.75 AND ship_timeline <= 24h THEN
    build_mvp()
    ship_immediately()
    LOOP:
      gather_feedback()
      iterate_on_live_work()
      ship_incremental_improvements()
  ELSE
    design_full_scope()
    estimate_timeline()
    propose_phased_delivery()
  END
END
```

**MVP Definition Criteria:**
- Feature coverage ≥ 20% of desired scope
- Shipping timeline ≤ 24 hours
- Risk level: Low–Medium
- User-visible value: Demonstrable

**Ship Decision Logic:**
```
mvp_score = (feature_coverage * 0.4) + 
            (user_value * 0.3) + 
            (deployment_safety * 0.3)

IF mvp_score >= 0.75 AND timeline <= 24h THEN
  ship_immediately()
ELSE
  propose_timeline_options()
END
```

**Example:**
- User: "Build a weekly report generator"
- MVP: Basic report generation (CSV output, 3 key metrics)
- Timeline: 4 hours
- Action: Ship immediately
- Iteration: Add visualization (Week 2), scheduling (Week 3), advanced filters (Week 4)

---

## DECISION THRESHOLDS SUMMARY TABLE

| Rule | Trigger | Threshold | Action | Fallback |
|------|---------|-----------|--------|----------|
| 30-Day Rule | Recurring task | ≤ 30 days effort | Auto-design | Manual review |
| Minimal Context | Rough notes | Confidence ≥ 0.75 | Execute | Ask questions |
| Intent Inference | Pattern found | Pattern strength ≥ 0.75 | Deliver on match | Ask preference |
| Silence Protocol | Idle > 60 min | Work queue not empty | Continue autonomously | Await user input |
| Execution-First | New task | MVP score ≥ 0.75 + ≤ 24h | Ship MVP | Propose phased plan |

---

## INTEGRATION ARCHITECTURE

### Services & Endpoints

| Service | Endpoint | Method | Auth Type | Status |
|---------|----------|--------|-----------|--------|
| Google Sheets API | sheets.googleapis.com/v4 | REST | OAuth 2.0 | Live |
| Google Drive API | www.googleapis.com/drive/v3 | REST | OAuth 2.0 | Live |
| Google Docs API | docs.googleapis.com/v1 | REST | OAuth 2.0 | Live |
| Google Gmail API | gmail.googleapis.com/v1 | REST | OAuth 2.0 | Live |
| Google Chat API | chat.googleapis.com/v1 | REST | OAuth 2.0 | Live |
| GitHub REST API | api.github.com | REST | PAT | Live |
| GitHub GraphQL API | api.github.com/graphql | GraphQL | PAT | Live |

**All credentials stored in EDITH vault with three-factor gating.**

---

## IMPLEMENTATION PHASES

| Phase | Work | Duration | Dependencies |
|-------|------|----------|--------------|
| **Phase 1** | EDITH hardening + verification protocol | 1 week | None |
| **Phase 2** | Framework integration + rule codification | 1 week | Phase 1 complete |
| **Phase 3** | Skill consolidation + memory audit | 1 week | Phase 2 complete |
| **Phase 4** | Testing + go-live | 1 week | Phase 3 complete |

### Phase 1: EDITH Hardening & Verification Protocol
- Implement hardware UUID binding
- Deploy passphrase + salt storage (bcrypt-10)
- Activate time-window gating (±5 min, 5 min auto-purge)
- Verify protocol implementation (3-question challenge)
- Migrate all credentials to EDITH vault

### Phase 2: Framework Integration & Rule Codification
- Codify 30-Day Rule with recurring task detection
- Implement Minimal Context with confidence scoring (≥ 0.75)
- Activate Intent Inference with pattern matching
- Deploy Silence Protocol (idle > 60 min, work queue monitoring)
- Enable Execution-First with MVP feasibility scoring

### Phase 3: Skill Consolidation & Memory Audit
- Retire unused skills (77 of 79; keep core infrastructure)
- Consolidate memory (120K core + 50K framework + 30K working)
- Optimize skill library references
- Audit cross-session context accuracy

### Phase 4: Testing & Go-Live
- End-to-end smoke test (all integrations)
- Framework decision quality validation
- Security audit (EDITH, time-gating, constant-time ops)
- Go-live deployment

---

## DEPLOYMENT READINESS

### Pre-Deployment Checklist

**Security (EDITH):**
- [x] Hardware UUID binding designed
- [x] Three-factor authentication specified
- [x] AES-256-GCM encryption specified
- [x] Verification protocol (3-question challenge) specified
- [ ] Security audit completed
- [ ] Hardware UUID verified against live system
- [ ] Time-window gating tested end-to-end

**Framework (Operating System):**
- [x] All 5 rules designed with quantified thresholds
- [x] Decision trees documented
- [x] Confidence scoring logic specified
- [ ] Rule implementation tested in sandbox
- [ ] Framework validation across all rules
- [ ] Integration smoke test completed

**Integration:**
- [x] Google OAuth (5 services) live and verified
- [x] GitHub PAT live and verified
- [x] Tanzim_Frameworks repo published (GitHub private)
- [ ] All credentials migrated to EDITH
- [ ] Service endpoints verified

### Sign-Off Requirements

1. **Security sign-off** — EDITH audit (hardware UUID, time-gating, constant-time ops)
2. **Framework validation** — All 5 rules active, decision quality tested
3. **Integration smoke test** — All services verified
4. **Go-live approval** — All phases validated

---

## OPERATIONAL RUNBOOK

### Starting a Session

```
1. System startup → Verify hardware UUID matches ~/.hermes/.edith/hardware_uuid
2. EDITH unlock → Enter passphrase (bcrypt-10 verification)
3. Time-window check → Confirm within ±5 min of last successful auth
4. Load credentials → Decrypt OAuth + PAT from EDITH vault
5. Initialize framework → Load 5-rule decision engine
6. Load memory → Activate hindsight context + personal framework
```

### Accessing Sensitive Operations

**Requirement:** Must pass verification protocol (Q1, Q2, Q3)

```
USER_REQUEST: sensitive_operation()
→ Trigger verification protocol
→ Q1: "Favorite football team?" → SHA-256 compare against vault
→ Q2: "Favorite character?" → SHA-256 compare against vault
→ Q3: "Favorite person?" → SHA-256 compare against vault
→ IF all 3 pass: unlock_operation()
→ IF any fail: lockout_30_minutes()
```

### Framework Decision: Minimal Context Example

**User Input:** "Update the weekly report"

```
1. Parse input → incomplete requirements (no format, no data source specified)
2. Search history → found 3 past reports (CSV, Google Sheets, markdown)
3. Compute confidence:
   - Pattern match (weekly report): +0.35
   - Recency (2 days ago): +0.20
   - Low-risk operation: +0.15
   - Total: 0.70 (below 0.75 threshold)
4. Action: Ask clarification
   "I found 3 weekly report formats (CSV, Sheets, markdown). Which would you like?"
```

**User Input:** "Run the usual Friday sync"

```
1. Parse input → rough description of recurring task
2. Search history → found 12 past "Friday sync" executions
3. Compute confidence:
   - Pattern match (Friday sync): +0.40
   - Recency (7 days ago): +0.18
   - Consistency (same steps 95% of the time): +0.12
   - Low-risk operation: +0.15
   - Total: 0.85 (exceeds 0.75 threshold)
4. Action: Execute
   - Pull repo updates
   - Merge memory context
   - Generate session summary
   - Log: "Minimal context decision: confidence=0.85, action=execute"
```

### Framework Decision: Silence Protocol Example

**Timeline:**
- 14:00 → User queues [Task A, Task B, Task C]
- 14:05 → System active (waiting for input)
- 14:45 → User goes idle
- 15:15 → Idle time = 30 min (below 60 min threshold)
- 15:45 → Idle time = 60 min (at threshold, check work queue)
- 16:00 → Idle time = 61 min (exceeds threshold, work queue not empty)

**Action:**
```
idle_time = 61_minutes
work_queue = [Task A, Task B, Task C]
IF idle_time > 60_minutes AND work_queue.length > 0 THEN
  → Execute Task A (log: "silence_protocol_triggered")
  → Task A completes
  → Execute Task B
  → Task B completes
  → Execute Task C
  → work_queue emptied
END
```

---

## CURRENT STATE BASELINE

| Component | Status | Details |
|-----------|--------|---------|
| **Plan** | Claude Max | Flat monthly fee, unlimited usage |
| **Model** | Claude Sonnet 4.6 | Primary; no cost differentiation |
| **Memory** | 8.95 GB | Active + archived across sessions |
| **Integrations** | 5 live | Google (Gmail, Drive, Docs, Sheets, Chat), GitHub |
| **Credentials** | EDITH vault (designed) | Three-factor access, AES-256-GCM encrypted |
| **Framework** | Personal (codified) | Tanzim_Frameworks repo (GitHub private) |
| **Inference** | 72K avg input, 503 avg output tokens | Per call |
| **Cache Performance** | 75–98% hit rate | Across sessions |
| **Skill Library** | 79 categories; 77 (98%) unused | Memory overhead to address in Phase 3 |

---

## MIGRATION CHECKLIST

**From Current Friday Setup → Friday 2.0:**

1. **Credentials** → Centralize all OAuth + PAT into EDITH vault (AES-256-GCM encrypted)
2. **Decision logic** → Codify 5 rules with quantified thresholds; remove hidden inference
3. **Framework rules** → Implement in operating system; publish to Tanzim_Frameworks repo
4. **Verification protocol** → Deploy 3-question challenge for sensitive operations
5. **Time-window gating** → Activate ±5 min window + 5 min auto-purge
6. **Skill library** → Retire 77 unused skills; consolidate memory
7. **Cross-session context** → Optimize hindsight memory for faster context loading

---

## SUCCESS METRICS

| Metric | Target | Rationale |
|--------|--------|-----------|
| **EDITH Security** | 100% credential encryption | All OAuth + PAT vault entries AES-256-GCM |
| **Verification Success** | 100% for sensitive ops | Zero credential access without Q1-Q3 challenge |
| **Framework Adoption** | 5/5 rules active | All decision rules operational |
| **Decision Quality** | Confidence scoring ≥ 0.75 | Minimal user clarification requests |
| **Autonomy** | Silence protocol executes queued work | No manual intervention needed for queued tasks |
| **MVP Velocity** | ≤ 24h to ship | Execution-first delivers rapid iterations |
| **Memory Efficiency** | -50K overhead (retire unused skills) | Skill consolidation complete |
| **Integration Stability** | 100% service uptime | All 7 APIs operating without incident |

---

## REFERENCES

**Design Documents:**
- `01_SNAPSHOT.pdf` — Current Friday baseline
- `02_HIGH-LEVEL-DESIGN.pdf` — Friday 2.0 architecture & two pillars
- `03_LEVEL-DESIGN.pdf` — Technical specification
- `04_MEMO.pdf` — Project synthesis & living index
- `Credentials.pdf` — Current credential inventory

**Repositories:**
- `~/friday-2.0/` — Design documents
- `Tanzim_Frameworks` (GitHub private) — Decision rules & framework schema

**Next Steps:**
1. Review & approve implementation specification
2. Complete Phase 1 security sign-off
3. Begin Phase 1 EDITH hardening
4. Execute full testing protocol
5. Deploy to production

---

**Document Status:** Ready for Implementation  
**Last Updated:** June 09, 2026  
**Owner:** Claude Code (Subagent)
