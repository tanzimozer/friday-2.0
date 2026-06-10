# FRIDAY 2.0: QUICK REFERENCE CARD
**Date:** June 09, 2026 | **Status:** Ready for Implementation

---

## 5 MAJOR CHANGES AT A GLANCE

### 1. EDITH 2.0 VAULT (Hardware-Bound)
```
Three-Factor Authentication:
  Factor 1: Hardware UUID    (system-specific, 100% match required)
  Factor 2: Passphrase       (bcrypt-10, constant-time comparison)
  Factor 3: Time-Window      (±5 min from last auth, 5 min auto-purge)

Encryption:  AES-256-GCM (all credentials at rest)
Verification: 3-question SHA-256 challenge (lockout 30 min on failure)
Permissions: 0600 vault files, 0700 vault directory
```

### 2. PERSONAL FRAMEWORK: 30-DAY RULE
```
Trigger:    Recurring task with effort ≤ 30 days
Action:     Auto-design automation
Output:     Architecture, phases, timeline, implementation queue
Example:    "Weekly report generator" → Design automation
```

### 3. PERSONAL FRAMEWORK: MINIMAL CONTEXT (0.75 Confidence)
```
Trigger:    Rough notes, incomplete requirements
Threshold:  Confidence ≥ 0.75 (75% certainty)
Action ≥0.75: Execute on inferred intent
Action <0.75: Ask clarifying questions

Confidence = Pattern(0.40) + Context(0.25) + Explicit(0.25) + Risk(0.10)
```

### 4. PERSONAL FRAMEWORK: INTENT INFERENCE (0.75 Pattern Strength)
```
Trigger:    Pattern observed in historical context
Threshold:  Pattern strength ≥ 0.75
Action ≥0.75: Deliver on best historical match
Action <0.75: Ask user preference

Pattern Strength = Frequency(0.35) + Recency(0.25) + Consistency(0.15) + Relevance(0.25)
```

### 5. PERSONAL FRAMEWORK: SILENCE PROTOCOL (60+ min idle) + EXECUTION-FIRST
```
Silence Protocol:
  Trigger:  Idle > 60 minutes + work queue not empty
  Action:   Continue autonomously (no user input needed)
  Require:  Explicit work queue (no speculative execution)

Execution-First:
  Trigger:  New task requested
  Threshold: MVP score ≥0.75 + timeline ≤24 hours
  Action ≥threshold: Ship MVP immediately
  Action <threshold: Propose phased delivery

MVP Score = Feature Coverage(0.40) + User Value(0.30) + Safety(0.30)
```

---

## DECISION THRESHOLDS (Quantified)

| Rule | Threshold | Unit | Meaning |
|------|-----------|------|---------|
| **Confidence** | 0.75 | Ratio (0–1) | Execute if 75% certain of intent |
| **Pattern Strength** | 0.75 | Ratio (0–1) | Match historical pattern if 75% strong |
| **MVP Score** | 0.75 | Ratio (0–1) | Ship MVP if 75% ready |
| **Effort Estimate** | ≤ 30 | Days | Auto-design if task ≤ 30 days |
| **Idle Time** | > 60 | Minutes | Auto-execute queued work after 60+ min idle |
| **Shipping Timeline** | ≤ 24 | Hours | Ship immediately if can deliver MVP in 24h |
| **Feature Coverage** | ≥ 20% | % of full scope | MVP must cover ≥20% of desired features |
| **Hardware UUID** | 100% | Exact match | Vault inaccessible on different hardware |
| **Time-Window** | ± 5 | Minutes | Credentials valid ±5 min from last auth |
| **Auto-Purge** | 5 | Minutes idle | Credentials purged from memory after 5 min idle |
| **Lockout Period** | 30 | Minutes | Vault locked for 30 min on verification failure |

---

## SECURITY REQUIREMENTS

### EDITH Vault Checklist
- [x] Three-factor authentication (UUID + passphrase + time-window)
- [x] AES-256-GCM encryption (all credentials at rest)
- [x] Bcrypt-10 passphrase hashing (constant-time comparison)
- [x] Time-window gating (±5 min, 5 min auto-purge)
- [x] Verification protocol (3-question SHA-256 challenge)
- [x] 30-minute lockout on verification failure
- [x] File permissions hardening (0600 files, 0700 directory)
- [x] Obfuscated file naming (no plaintext hints)
- [x] Centralized audit logging (all access attempts)

### Framework Rules Checklist
- [x] 30-Day Rule codified (recurring detection + auto-design)
- [x] Minimal Context codified (confidence ≥0.75)
- [x] Intent Inference codified (pattern strength ≥0.75)
- [x] Silence Protocol codified (idle >60 min, explicit work queue)
- [x] Execution-First codified (MVP ≥0.75 score, ≤24h timeline)
- [x] All thresholds quantified & hardcoded
- [x] All decisions logged & auditable
- [x] Framework rules published (Tanzim_Frameworks repo)

---

## ARCHITECTURE LAYERS

```
Claude Max (Sonnet 4.6)
  │
  ├─ SECURITY LAYER (EDITH Vault)
  │   └─ Three-factor auth → Credentials (AES-256-GCM)
  │       └─ Verification protocol → Sensitive ops
  │
  ├─ FRAMEWORK LAYER (5 Rules)
  │   ├─ 30-Day Rule (auto-design)
  │   ├─ Minimal Context (≥0.75 confidence)
  │   ├─ Intent Inference (≥0.75 pattern)
  │   ├─ Silence Protocol (>60 min idle)
  │   └─ Execution-First (≥0.75 MVP, ≤24h)
  │
  └─ INTEGRATION LAYER (APIs)
      ├─ Google OAuth (Gmail, Drive, Docs, Sheets, Chat)
      └─ GitHub PAT (Repo, Gist, User, Workflow)
```

---

## IMPLEMENTATION TIMELINE

| Phase | Work | Duration | Status |
|-------|------|----------|--------|
| **1** | EDITH hardening + verification | 1 week | Ready to start |
| **2** | Framework rules + integration | 1 week | Depends on Phase 1 |
| **3** | Memory consolidation + audit | 1 week | Depends on Phase 2 |
| **4** | Testing + go-live | 1 week | Depends on Phase 3 |

**Total: 4 weeks to full deployment**

---

## SUCCESS METRICS

```
EDITH:        100% credentials encrypted (AES-256-GCM)
Verification: 100% Q1-Q3 challenge for sensitive ops
Framework:    5/5 rules active & operational
Decision Quality: Confidence ≥0.75 (false positive rate <5%)
Autonomy:     Silence protocol executes all queued work
MVP Velocity: Ship MVP ≤24 hours
Memory:       -50 KB overhead (skill consolidation)
Integration:  100% API uptime (7 APIs + 1 PAT)
```

---

## FILE LOCATIONS

| File | Purpose | Size |
|------|---------|------|
| `/home/hermes/FRIDAY_2.0_INDEX.md` | Master index & overview | 19 KB |
| `/home/hermes/FRIDAY_2.0_IMPLEMENTATION_SPECIFICATION.md` | Operational guide (complete) | 19 KB |
| `/home/hermes/FRIDAY_2.0_TECHNICAL_ARCHITECTURE.md` | Technical design & pseudocode | 25 KB |
| `/home/hermes/FRIDAY_2.0_DESIGN_DECISIONS.md` | Design decisions & requirements | 16 KB |
| **Total** | Complete specification set | **79 KB** |

---

## KEY INSIGHT: The 0.75 Threshold

All framework decision thresholds are **0.75 (75% certainty)**:

- **Confidence ≥ 0.75** → Execute on minimal context
- **Pattern Strength ≥ 0.75** → Deliver on historical match
- **MVP Score ≥ 0.75** → Ship immediately
- **Risk Assessment** → Low-risk ops add 0.10 to confidence

**Philosophy:** Bias toward action. Execute at 75% confidence. Ask only if <75%.

---

## NEXT IMMEDIATE STEPS

1. **Review specifications** (30 min)
   - Read `FRIDAY_2.0_INDEX.md` (executive overview)
   - Skim `FRIDAY_2.0_IMPLEMENTATION_SPECIFICATION.md` (operational guide)

2. **Approve architecture & thresholds** (15 min)
   - Confirm all 5 major changes are captured
   - Confirm all quantified thresholds are acceptable

3. **Begin Phase 1: EDITH Hardening** (1 week)
   - Implement three-factor authentication
   - Deploy AES-256-GCM encryption
   - Activate verification protocol

4. **Proceed through Phases 2–4** (3 weeks)
   - Framework rules codification
   - Memory consolidation
   - Testing & go-live

---

**Status:** ✅ Specifications Complete — Ready for Implementation  
**Date:** June 09, 2026  
**Scope:** Complete extraction & specification of Friday 2.0 design
