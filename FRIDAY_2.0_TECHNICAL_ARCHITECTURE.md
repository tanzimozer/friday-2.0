# FRIDAY 2.0 TECHNICAL ARCHITECTURE
**Version:** 2.0  
**Date:** June 09, 2026  
**Status:** Design Phase Complete

---

## SYSTEM ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLAUDE MAX (SONNET 4.6)                     │
│                   Inference Engine & Orchestrator                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        v                  v                  v
┌──────────────────┐ ┌─────────────────┐ ┌──────────────────┐
│  SECURITY LAYER  │ │ FRAMEWORK LAYER │ │ INTEGRATION LAYER│
│   (EDITH 2.0)    │ │   (5 Rules)     │ │  (7 APIs + 1 PAT)│
└──────────────────┘ └─────────────────┘ └──────────────────┘
```

---

## PILLAR 1: SECURITY LAYER (EDITH 2.0 VAULT)

### Three-Factor Authentication Flow

```
┌─────────────────────────────────────────────────────────────┐
│          EDITH Vault Access Request                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ┌──────v──────┐
                    │   FACTOR 1   │
                    │ Hardware UUID│
                    │    Check     │
                    └──────┬───────┘
                           │ UUID matches?
                    ┌──────v──────┐
                    │   FACTOR 2   │
                    │  Passphrase  │
                    │   Validation │
                    │  (bcrypt-10) │
                    └──────┬───────┘
                           │ Passphrase correct?
                    ┌──────v──────┐
                    │   FACTOR 3   │
                    │ Time-Window  │
                    │  Gate (±5min)│
                    └──────┬───────┘
                           │ Within window?
                    ┌──────v──────────┐
                    │ UNLOCK VAULT    │
                    │ Decrypt & load  │
                    │ credentials     │
                    └─────────────────┘
```

### Credential Storage Architecture

```
~/.hermes/.edith/
├── hardware_uuid                    [System-specific identifier]
├── passphrase_hash                  [bcrypt-10(passphrase + salt)]
├── google_oauth_vault               [AES-256-GCM encrypted JSON]
│   ├── access_token (auto-refresh)
│   ├── refresh_token
│   └── scopes: gmail, drive, docs, sheets, chat
├── github_pat_vault                 [AES-256-GCM encrypted JSON]
│   ├── token
│   └── scopes: repo, gist, user, workflow
├── verification_hashes.json         [SHA-256 + salt (plaintext never stored)]
│   ├── Q1_hash: SHA-256(Real Madrid + salt)
│   ├── Q2_hash: SHA-256(Pepper Potts + salt)
│   └── Q3_hash: SHA-256(Myself + salt)
└── timestamp_last_auth              [Last successful unlock (±5 min window)]

File Permissions: 0600 (user read/write only)
Encryption: AES-256-GCM (authenticated encryption)
Access Log: Centralized, audit trail for compliance
```

### Time-Window Gating Implementation

```
GATE LOGIC:
  time_last_auth = read(timestamp_last_auth)
  time_current = now()
  delta = time_current - time_last_auth

  IF delta <= 5_minutes THEN
    credentials_valid = true
    credentials_expire_at = time_current + 5_minutes
  ELSE IF delta > 5_minutes AND delta <= 10_minutes THEN
    credentials_valid = false
    status = "EXPIRED (manual re-auth required)"
    purge_credentials()
  ELSE
    credentials_valid = false
    status = "STALE (re-enter passphrase)"
    purge_credentials()
  END

BEHAVIOR:
  - On idle > 5 min: Auto-purge all loaded credentials from memory
  - On re-access: Require full 3-factor authentication
  - On continuous activity: Refresh window on each successful operation
```

### Verification Protocol (3-Question Challenge)

```
VERIFICATION FLOW:
  prompt_user("Q1: Favorite football team?")
  response_1 = user_input()
  hash_1 = SHA-256(response_1 + salt)
  
  IF hash_1 != vault_Q1_hash THEN
    lockout_30_minutes()
    return FAILURE
  END
  
  prompt_user("Q2: Favorite character?")
  response_2 = user_input()
  hash_2 = SHA-256(response_2 + salt)
  
  IF hash_2 != vault_Q2_hash THEN
    lockout_30_minutes()
    return FAILURE
  END
  
  prompt_user("Q3: Favorite person?")
  response_3 = user_input()
  hash_3 = SHA-256(response_3 + salt)
  
  IF hash_3 != vault_Q3_hash THEN
    lockout_30_minutes()
    return FAILURE
  END
  
  return SUCCESS (all 3 verified)

LOCKOUT RULE:
  Failure on any question → 30-minute vault lock
  No credential access during lockout
  Automatic unlock after 30 minutes
```

---

## PILLAR 2: FRAMEWORK LAYER (5-CORE RULES)

### Decision Engine Architecture

```
┌─────────────────────────────────────────────────────────┐
│         PERSONAL FRAMEWORK DECISION ENGINE               │
│          (5 Rules, Quantified Thresholds)               │
└────────┬────────────────────────────────────────────────┘
         │
    ┌────v────┬────────┬──────────┬──────────────┐
    │          │        │          │              │
    v          v        v          v              v
┌──────────┐ ┌──────┐ ┌──────┐ ┌──────────┐ ┌──────────┐
│ 30-Day  │ │Min.  │ │Intent│ │ Silence  │ │Execution│
│  Rule   │ │Context│ │Infer │ │Protocol  │ │  First  │
└────┬─────┘ └───┬──┘ └───┬──┘ └────┬─────┘ └────┬─────┘
     │           │        │         │           │
     │  Trigger  │        │ Trigger │ Trigger   │
     ├──────────┬┴────────┴──┬──────┴──┬────────┤
     │          │            │        │        │
     v          v            v        v        v
┌────────────────────────────────────────────────┐
│       Confidence Scoring Engine                │
│  (Computes decision thresholds in real-time)   │
└────────────────────────────────────────────────┘
     │
     v
┌────────────────────────────────────────────────┐
│    Decision Output (Action + Confidence)       │
│  - Execute with confidence score               │
│  - Ask clarifying question                     │
│  - Continue autonomously                       │
│  - Ship MVP or propose plan                    │
└────────────────────────────────────────────────┘
```

### Rule 1: 30-Day Rule (Recurring Task Auto-Design)

```
DETECTOR:
  given: task_description
  is_recurring = detect_pattern(task_history, task_description)
  IF is_recurring:
    effort_estimate = estimate_effort(task_description)
    IF effort_estimate <= 30_days:
      return TRIGGER_30_DAY_RULE
    END
  END

ACTION:
  design_automation(task)
  architecture = design_phase(task)
  phases = breakdown_into_phases(task)
  timeline = estimate_timeline(phases)
  queue_implementation(phases)
  
OUTPUT:
  - Automation design doc
  - Phase breakdown
  - Time saved estimate
  - Implementation queue
```

### Rule 2: Minimal Context (Confidence ≥ 0.75)

```
CONFIDENCE_SCORE_COMPONENTS:
  
  score = 0.0
  
  # Pattern matching (0.0–0.40 points)
  IF task_type_in_history:
    score += 0.25 + (frequency_ratio * 0.15)
  END
  
  # Contextual signals (0.0–0.25 points)
  IF domain_inference_strong:
    score += 0.15 + (domain_confidence * 0.10)
  END
  
  # Explicit mention (0.0–0.25 points)
  IF intent_words_detected:
    score += intent_confidence * 0.25
  END
  
  # Risk assessment (0.0–0.10 points)
  IF risk_level == "low":
    score += 0.10
  ELSE IF risk_level == "medium":
    score += 0.05
  END
  
  return score

DECISION_LOGIC:
  confidence_score = compute_confidence_score(task_input)
  
  IF confidence_score >= 0.75:
    execute_on_best_match(inferred_intent)
    log("confidence={confidence_score:.2f}, action=execute")
  ELSE:
    ask_clarifying_questions(ambiguous_fields)
    log("confidence={confidence_score:.2f}, action=ask")
    await_explicit_response()
  END
```

### Rule 3: Intent Inference (Pattern Strength ≥ 0.75)

```
PATTERN_MATCHING:
  historical_patterns = query_session_history(task_type)
  ranked_patterns = []
  
  FOR each pattern IN historical_patterns:
    strength = 0.0
    
    # Frequency (0.0–0.35)
    strength += (pattern.count / max_count) * 0.35
    
    # Recency (0.0–0.25)
    days_since = (now() - pattern.last_used).days
    recency_score = max(0, 1.0 - (days_since / 30))
    strength += recency_score * 0.25
    
    # Consistency (0.0–0.15)
    consistency = 1.0 - (pattern.variance / max_variance)
    strength += consistency * 0.15
    
    # Contextual relevance (0.0–0.25)
    relevance = semantic_similarity(task_input, pattern.description)
    strength += relevance * 0.25
    
    ranked_patterns.append((pattern, strength))
  END
  
  ranked_patterns.sort_by_strength()
  return ranked_patterns

DECISION_LOGIC:
  patterns = find_matching_patterns(user_request)
  IF patterns.length > 0:
    best_match = patterns[0]
    IF best_match.strength >= 0.75:
      deliver_matching_output(best_match)
      log("pattern_match={best_match.name}, strength={best_match.strength:.2f}")
    ELSE:
      ask_user_preference(top_3_patterns)
      cache_user_choice()
      log("pattern_strength_low={best_match.strength:.2f}, asked_preference")
    END
  ELSE:
    ask_user_for_clarification()
  END
```

### Rule 4: Silence Protocol (Idle > 60 min, Work Queue Not Empty)

```
IDLE_MONITOR:
  last_user_input = now()
  
  LOOP every_60_seconds:
    idle_time = (now() - last_user_input).minutes
    
    IF idle_time > 60 AND work_queue.length > 0:
      TRIGGER_SILENCE_PROTOCOL()
    ELSE IF idle_time > 60 AND work_queue.length == 0:
      await_user_input()
    END
  END

SILENCE_PROTOCOL_EXECUTION:
  log_event("silence_protocol_triggered", {
    idle_time_minutes: idle_time,
    work_queue_count: work_queue.length
  })
  
  WHILE work_queue.length > 0:
    next_task = work_queue.pop()
    
    # Check preconditions
    IF not all_dependencies_satisfied(next_task):
      work_queue.push_front(next_task)
      break
    END
    
    log_event("autonomy_execution", {
      task: next_task.name,
      reason: "silence_protocol_idle_threshold"
    })
    
    execute_task(next_task)
    log_completion(next_task)
  END
  
  IF work_queue.length == 0:
    log_event("work_queue_cleared", { reason: "silence_protocol" })
  END

PRECONDITIONS_CHECK:
  all_dependencies_satisfied(task):
    FOR each dependency IN task.dependencies:
      IF not dependency.completed:
        return false
      END
    END
    
    IF not system_resources_available():
      return false
    END
    
    IF user_requested_pause():
      return false
    END
    
    return true
```

### Rule 5: Execution-First (MVP Score ≥ 0.75 + Timeline ≤ 24h)

```
MVP_FEASIBILITY_SCORING:
  mvp_score = 0.0
  
  # Feature coverage (0.0–0.40 points)
  core_features = define_core_features(task)
  feature_coverage = len(core_features) / len(task.all_features)
  IF feature_coverage >= 0.20:
    mvp_score += feature_coverage * 0.40
  END
  
  # User value (0.0–0.30 points)
  user_value = assess_immediate_value(core_features)
  mvp_score += user_value * 0.30
  
  # Deployment safety (0.0–0.30 points)
  risk_level = assess_risk(core_features)
  safety = 1.0 - (risk_level / 10)
  IF risk_level <= 5 (medium or lower):
    mvp_score += safety * 0.30
  END
  
  return mvp_score

SHIP_DECISION_LOGIC:
  mvp_score = compute_mvp_score(task)
  ship_timeline = estimate_shipping_timeline(task)
  
  IF mvp_score >= 0.75 AND ship_timeline <= 24_hours:
    ship_mvp(task)
    log("mvp_shipped", {
      score: mvp_score,
      timeline: ship_timeline,
      features: core_features
    })
    
    # Post-ship iteration loop
    LOOP:
      gather_feedback(mvp)
      plan_improvements(feedback)
      execute_improvements(mvp)
      redeploy(mvp)
    END
  ELSE:
    design_full_scope(task)
    estimate_phased_timeline(task)
    propose_delivery_phases(task)
  END
```

---

## PILLAR 3: INTEGRATION LAYER (APIs & Credentials)

### API Architecture

```
┌─────────────────────────────────────────────┐
│      Claude Max (Orchestration)             │
└────────┬────────────────────────────────────┘
         │
    ┌────┴──────────┬──────────────┐
    │               │              │
    v               v              v
┌──────────────┐ ┌──────────┐ ┌─────────────┐
│ Google APIs  │ │GitHub API│ │ EDITH Vault │
│  (5 services)│ │(REST+GQL)│ │(Credentials)│
└──────────────┘ └──────────┘ └─────────────┘
    │
    ├── Gmail API
    │   └── Read/write email, attachments
    │
    ├── Drive API
    │   └── CRUD files, folders, permissions
    │
    ├── Docs API
    │   └── Create/edit documents
    │
    ├── Sheets API
    │   └── Read/write spreadsheet data
    │
    └── Chat API
        └── Send/receive messages, threads
```

### Service Integration Flow

```
REQUEST:
  user_requests_action(service)
  └─> requires_credentials = true
      └─> UNLOCK_EDITH_VAULT()
          └─> Factor 1: Hardware UUID ✓
          └─> Factor 2: Passphrase ✓
          └─> Factor 3: Time-Window ✓
          └─> VERIFICATION_PROTOCOL()
              └─> Q1: Football team ✓
              └─> Q2: Character ✓
              └─> Q3: Person ✓
          └─> CREDENTIALS_LOADED()
              └─> Google OAuth token
              └─> GitHub PAT
              └─> Timestamp updated

API_CALL:
  service.authenticate(credential)
  request = build_api_request(user_intent)
  response = service.execute(request)
  
  IF response.token_expired:
    refresh_oauth_token()
  END
  
  return process_response(response)

AUTO_PURGE:
  IF idle_time > 5_minutes:
    purge_credentials_from_memory()
    reset_timestamp_last_auth()
  END
```

---

## MEMORY ARCHITECTURE

### Session Memory Layout

```
Total Memory: 8.95 GB

├── Core Memory (120 KB)
│   ├── User identity & preferences
│   ├── Framework rules (5-rule decision engine)
│   ├── Confidence threshold tables
│   └── Service integration metadata
│
├── Personal Framework (50 KB)
│   ├── Historical patterns (30 KB)
│   │   ├── Task frequencies
│   │   ├── Decision history
│   │   └── User preferences
│   │
│   └── Inference models (20 KB)
│       ├── Intent classification
│       ├── Risk assessment
│       └── Domain confidence scores
│
├── Working Memory (30 KB)
│   ├── Current session context
│   ├── Active work queue
│   ├── Real-time decision state
│   └── Idle timer & autonomy state
│
└── Available for Session (remaining ~8.8 GB)
    └── Active conversation, documents, results
```

### Cross-Session Memory (Hindsight)

```
Persistence:
  - Session history: Full transcript + decision logs
  - Pattern recognition: Historical task frequencies
  - User preferences: Explicit choices + inferred patterns
  - Integration metadata: API configurations, auth timestamps
  
Lookup:
  - Session search: FTS5 full-text search
  - Pattern matching: Semantic similarity (historical tasks)
  - Confidence scoring: Aggregate historical data
  
Optimization:
  - Cache hit rate: 75–98% on cross-session lookups
  - Pattern decay: Older patterns weighted lower
  - Memory consolidation: Retire unused skills (Phase 3)
```

---

## DEPLOYMENT ARCHITECTURE

### Local Filesystem Structure

```
~/.hermes/
├── .edith/                          [EDITH Vault — read-only after Phase 1]
│   ├── hardware_uuid                [~200 bytes]
│   ├── passphrase_hash              [~60 bytes]
│   ├── google_oauth_vault           [~5 KB, encrypted]
│   ├── github_pat_vault             [~2 KB, encrypted]
│   ├── verification_hashes.json     [~600 bytes]
│   └── timestamp_last_auth          [~20 bytes]
│
├── memory/                          [Cross-session context]
│   ├── hindsight_sessions/          [Historical transcripts]
│   ├── patterns/                    [Task history & inference models]
│   └── preferences/                 [User choices & metadata]
│
├── skills/                          [Framework rules & utilities]
│   ├── framework_rules/             [5-core decision rules]
│   ├── confidence_scoring/          [Threshold tables]
│   └── integrations/                [API connection utilities]
│
└── logs/                            [Audit trail]
    ├── security_events/             [EDITH access, verifications]
    ├── framework_decisions/         [Rule applications, confidence scores]
    └── integration_events/          [API calls, responses]
```

### System Startup Sequence

```
SYSTEM_START:
  1. Verify hardware_uuid matches system
     └─> IF mismatch: ABORT (vault inaccessible on different hardware)
  
  2. Check timestamp_last_auth
     └─> IF outside ±5 min window: Require full authentication
  
  3. Prompt passphrase (if needed)
     └─> bcrypt-10 constant-time comparison
  
  4. Load credentials from EDITH vault
     └─> AES-256-GCM decryption
  
  5. Initialize framework rules
     └─> Load 5-rule decision engine + confidence tables
  
  6. Load memory context
     └─> Core (120 KB) + Personal framework (50 KB) + Working (30 KB)
  
  7. Initialize integrations
     └─> Verify API connectivity
  
  8. Ready for operation
```

---

## SECURITY THREAT MODEL

### Threats & Mitigations

| Threat | Impact | Mitigation |
|--------|--------|-----------|
| **Hardware theft** | Attacker gains physical access to system | Hardware UUID binding — vault inaccessible on different hardware |
| **Passphrase brute force** | Attacker tries 10^N passwords | bcrypt-10 + constant-time comparison + time-window gating |
| **Credential extraction** | Attacker reads credential files | AES-256-GCM encryption (authenticated, modern) |
| **Verification bypass** | Attacker answers 3 questions | SHA-256 + salt hashing (no plaintext ever stored) |
| **Time-window exploitation** | Attacker accesses credentials after 5 min idle | Auto-purge + re-authentication required |
| **Session hijacking** | Attacker intercepts OAuth token | OAuth tokens stored only in encrypted EDITH vault |
| **Malicious code execution** | Attacker injects commands during autonomy | Silence protocol requires explicit work queue; no speculative execution |

---

## TESTING & VALIDATION STRATEGY

### Phase 1 Security Testing

```
TEST: Hardware UUID Binding
  1. Generate uuid on System A
  2. Copy vault to System B
  3. Attempt access on System B
  4. Expected: Access denied (UUID mismatch)

TEST: Passphrase Verification
  1. Set passphrase "test123"
  2. Attempt login with "test123" → Success
  3. Attempt login with "test124" → Failure (bcrypt comparison)
  4. Attempt login 5+ times → Brute force detection
  5. Expected: Constant-time verification, no timing leaks

TEST: Time-Window Gating
  1. Unlock vault at 10:00 AM
  2. Access credentials (should work until 10:05 AM)
  3. At 10:05 AM: Try to access → Success (still in window)
  4. At 10:06 AM: Try to access → Failure (outside window)
  5. After 30 min idle: Credentials auto-purged
  6. Expected: ±5 min window enforced, auto-purge working

TEST: Verification Protocol
  1. Prompt Q1, Q2, Q3 in order
  2. Correct answer to Q1, Q2, wrong on Q3
  3. Expected: 30-minute lockout
  4. Retry after 30 min: Should work
  5. Expected: Lockout enforced, reset after timeout
```

### Phase 2 Framework Testing

```
TEST: 30-Day Rule
  1. Submit recurring task with 20-day effort estimate
  2. Expected: Auto-design automation triggered
  3. Submit recurring task with 45-day effort estimate
  4. Expected: No automation (manual review path)

TEST: Minimal Context (Confidence ≥ 0.75)
  1. Input: "Run the usual Friday sync" (high-confidence pattern)
  2. Expected: Execute with confidence ≥ 0.75
  3. Input: "Update the vault" (ambiguous, low confidence)
  4. Expected: Ask clarifying questions

TEST: Intent Inference
  1. Historical: "Generate weekly report" (12 past instances)
  2. User: "Do the report" (rough, ambiguous)
  3. Expected: Infer "weekly report" if pattern strength ≥ 0.75
  4. Test with weak pattern (< 0.75): Should ask preference

TEST: Silence Protocol
  1. Queue: [Task A, Task B, Task C]
  2. Simulate 90 min idle
  3. Expected: All 3 tasks auto-execute in sequence
  4. Test with empty queue
  5. Expected: No execution (require explicit queue)

TEST: Execution-First
  1. New task with MVP score 0.82, timeline 6h
  2. Expected: Ship MVP immediately
  3. New task with MVP score 0.65, timeline 2 weeks
  4. Expected: Propose phased delivery instead
```

---

## SUCCESS CRITERIA

| Criteria | Target | Validation |
|----------|--------|-----------|
| **EDITH Vault** | 100% secure credential storage | All credentials AES-256-GCM encrypted, zero plaintext |
| **Three-Factor Auth** | 100% pass rate for legitimate access | Hardware UUID + Passphrase + Time-window all validated |
| **Verification Protocol** | 100% coverage for sensitive ops | Q1-Q3 challenge blocks all unauthorized access |
| **30-Day Rule** | Detects & auto-designs 100% of eligible tasks | < 30-day recurring tasks auto-queued |
| **Minimal Context** | Confidence ≥ 0.75 for execution decisions | False positive rate < 5% |
| **Intent Inference** | Pattern strength scoring accurate | Correctly ranks patterns by relevance & frequency |
| **Silence Protocol** | 100% work queue execution | All queued tasks auto-execute after 60 min idle |
| **Execution-First** | MVP shipped ≤ 24h | Score ≥ 0.75 triggers immediate shipping |
| **Memory Efficiency** | -50 KB overhead (skill consolidation) | 77 unused skills retired, memory reclaimed |
| **Integration Uptime** | 100% API service availability | All 7 APIs + 1 PAT operational without incident |

---

**Document Status:** Design Phase Complete — Ready for Implementation  
**Next Phase:** Phase 1 EDITH Hardening & Verification Protocol  
**Last Updated:** June 09, 2026
