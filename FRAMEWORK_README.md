# Personal Framework Module (framework.py)

## Overview

The Personal Framework is a comprehensive decision-rules engine that codifies 5 core principles with explicit quantified logic and comprehensive logging. It provides a unified orchestrator for managing personal productivity, decision-making, and project execution through data-driven principles.

**Location:** `/home/hermes/framework.py`  
**Logging:** `/home/hermes/framework_decisions.log`

---

## 5 Core Principles

### 1. 30-Day Recurring Task Design

**Purpose:** Establish sustainable recurring tasks on a 30-day cycle.

**Key Components:**
- `RecurringTask`: Data class representing a single recurring task
- `RecurringTaskManager`: Manages all recurring tasks

**Quantified Logic:**
```
interval_days = 30 (fixed)
next_due = last_executed + timedelta(days=30)
is_due() = datetime.now() >= next_due
```

**Metrics Tracked:**
- Task ID, name, description
- Creation date, last execution, next due date
- Completion count (cumulative executions)

**Example:**
```python
manager = RecurringTaskManager()
task = manager.create_task(
    "review_goals",
    "Monthly Goal Review",
    "Review and adjust 30-day goals"
)
manager.execute_task("review_goals")
due_tasks = manager.get_due_tasks()
```

---

### 2. Minimal Context with 0.75 Confidence Threshold

**Purpose:** Process only high-confidence context signals to minimize noise.

**Key Components:**
- `ContextSignal`: Represents a single context signal with confidence metric
- `MinimalContextProcessor`: Evaluates signals against confidence threshold

**Quantified Logic:**
```
CONFIDENCE_THRESHOLD = 0.75
passes_threshold = confidence >= 0.75
confidence_gap = confidence - 0.75
aggregated_confidence = sum(confidences) / len(signals)
```

**Decision Rule:**
- Individual signal: **ACCEPTED** if confidence ≥ 0.75, **REJECTED** if < 0.75
- Aggregated signals: Average confidence must ≥ 0.75

**Metrics Tracked:**
- Signal ID, type, value, timestamp
- Confidence score (0.0-1.0 scale)
- Source of signal
- Confidence gap (distance from threshold)

**Example:**
```python
processor = MinimalContextProcessor()
passes, metrics = processor.process_signal(
    "signal_001",
    "user_intent",
    "schedule_meeting",
    confidence=0.92,
    source="nlp_parser"
)
# ACCEPTED: 0.92 >= 0.75

avg_conf, agg = processor.aggregate_confidence(["signal_001", "signal_002"])
```

---

### 3. Intent Inference from Patterns

**Purpose:** Automatically infer user intent from recurring behavioral patterns.

**Key Components:**
- `PatternOccurrence`: Represents a single pattern instance
- `IntentInferenceEngine`: Tracks patterns and infers intent

**Quantified Logic:**
```
min_occurrences = 3 (default threshold)
lookback_window = 30 days
pattern_confidence = min(occurrence_count / max_possible, 1.0)
  where max_possible = 30 (≈1 per day)
  
inferred_intent = (occurrence_count >= min_occurrences) AND 
                  (pattern within 30-day window)
```

**Decision Rule:**
- Pattern must have ≥ 3 occurrences within last 30 days
- Confidence = occurrence_count / 30 (capped at 1.0)

**Metrics Tracked:**
- Pattern ID and occurrence count
- Timestamps of all occurrences
- Recent context data (last 3 occurrences)
- Inferred intent status

**Example:**
```python
engine = IntentInferenceEngine()
# Record pattern 4 times
for i in range(4):
    engine.record_pattern(
        "daily_standup",
        {"time": "09:00", "duration_min": 15}
    )

inferred, metrics = engine.infer_intent("daily_standup", min_occurrences=3)
# True: 4 occurrences >= 3 threshold
```

---

### 4. Silence Protocol at 60 Min Idle

**Purpose:** Automatically enter silence mode when idle for 60+ minutes.

**Key Components:**
- `IdleState`: Enum (ACTIVE, IDLE, SILENT)
- `ActivityLog`: Records individual activities
- `SilenceProtocol`: Monitors idle time and manages state transitions

**Quantified Logic:**
```
IDLE_THRESHOLD_MINUTES = 60

State Determination:
  idle_minutes = (now - last_activity).total_seconds() / 60
  
  if idle_minutes < 30:
    state = ACTIVE
  elif idle_minutes < 60:
    state = IDLE
  else:
    state = SILENT (silence protocol engaged)

silence_protocol_engaged = (state == SILENT) AND SILENCE_ENABLED
```

**Decision Rule:**
- **ACTIVE:** Last activity < 30 minutes ago
- **IDLE:** Last activity 30-60 minutes ago
- **SILENT:** Last activity ≥ 60 minutes ago → Silence protocol automatically engages

**Metrics Tracked:**
- Activity ID, type, description
- Timestamps of all activities
- Current idle state
- Idle minutes (precise measurement)
- Silence protocol engagement status

**Example:**
```python
protocol = SilenceProtocol()
protocol.record_activity("act_001", "api_call", "Fetched user data")

state, metrics = protocol.check_idle_state()
# state = ACTIVE (0 min idle)
# silence_protocol_engaged = False

# After 60+ minutes of no activity:
# state = SILENT
# silence_protocol_engaged = True
```

---

### 5. Execution-First MVP Shipping

**Purpose:** Ship Minimum Viable Products with execution-first mindset.

**Key Components:**
- `Feature`: Represents a feature in MVP
- `MVPRelease`: Represents a release with multiple features
- `ExecutionFirstMVPShipper`: Manages MVP readiness and shipping

**Quantified Logic:**
```
core_feature_completion = sum(completion % of core features) / count(core features)

Ready to Ship Criteria:
  1. core_feature_completion >= 0.80 (80%)
  2. At least one core feature at completion == 1.0 (100%)
  
ship_decision = (core_completion >= 0.80) AND 
                (max(core_features) == 1.0)
```

**Decision Rule:**
- MVP is **READY TO SHIP** when:
  - Core feature average completion ≥ 80%
  - At least one core feature is 100% complete
- Non-core features do NOT block shipping
- Once shipped, status = RELEASED

**Metrics Tracked:**
- Release ID, version, creation timestamp
- Feature list (name, completion %, core status)
- Release status (PLANNING, IN_DEVELOPMENT, MVP_READY, SHIPPED, LIVE)
- Ship timestamp (if shipped)
- Core feature average completion

**Example:**
```python
shipper = ExecutionFirstMVPShipper()
release = shipper.create_mvp_release("v1_0_0", "1.0.0", [
    {
        "feature_id": "auth",
        "name": "Authentication",
        "is_core": True,
        "completion_percentage": 1.0
    },
    {
        "feature_id": "api",
        "name": "REST API",
        "is_core": True,
        "completion_percentage": 0.85
    },
    {
        "feature_id": "dashboard",
        "name": "Dashboard",
        "is_core": False,
        "completion_percentage": 0.50
    }
])

shipper.update_feature_completion("v1_0_0", "api", 1.0)
# core_completion = (1.0 + 1.0) / 2 = 1.0 (100%)

ready, metrics = shipper.evaluate_ship_readiness("v1_0_0")
# ready = True (1.0 >= 0.80 AND has 100% feature)

if ready:
    shipped = shipper.ship_release("v1_0_0")
    # Status: SHIPPED, timestamp recorded
```

---

## Unified Framework Orchestrator

### PersonalFramework Class

The `PersonalFramework` class unifies all 5 principles into a single orchestrator.

```python
framework = PersonalFramework()

# Access individual principle managers
framework.recurring_tasks      # RecurringTaskManager
framework.minimal_context      # MinimalContextProcessor
framework.intent_inference     # IntentInferenceEngine
framework.silence_protocol     # SilenceProtocol
framework.mvp_shipping        # ExecutionFirstMVPShipper

# Get overall health metrics
health = framework.get_framework_health()
```

**Unified Health Report Includes:**
- Framework uptime (seconds)
- Stats for each of the 5 principles
- Overall system metrics

---

## Logging System

### FrameworkLogger Class

All decisions are logged with quantified metrics to `/home/hermes/framework_decisions.log`

**Log Levels:**
- **INFO:** Framework decisions with metrics
- **DEBUG:** Detailed operations and status checks
- **WARNING:** Anomalies or threshold violations

**Log Format:**
```
timestamp - PersonalFramework - LEVEL - [principle_name] decision | Metrics: {json_metrics}
```

**Example Log Entry:**
```
2026-06-09 17:41:08,227 - PersonalFramework - INFO - [30-day Recurring Task Design] 
Created task: Monthly Goal Review | Metrics: 
{"task_id": "review_goals", "interval_days": 30, "created_at": "2026-06-09T17:41:08.227307"}
```

---

## Usage Examples

### Complete Integration Example

```python
from framework import PersonalFramework

# Initialize framework
fw = PersonalFramework()

# 1. Create 30-day recurring tasks
fw.recurring_tasks.create_task(
    "weekly_review",
    "Weekly Review",
    "Review completed tasks and plan next week"
)

# 2. Process context signals
passes, metrics = fw.minimal_context.process_signal(
    "sig_001",
    "user_command",
    "create_project",
    confidence=0.88,
    source="voice_assistant"
)

# 3. Record behavioral patterns
fw.intent_inference.record_pattern(
    "evening_coding",
    {"start_time": "19:00", "duration_min": 120}
)

# 4. Record user activity
fw.silence_protocol.record_activity(
    "work_session_001",
    "development",
    "Coding on feature X"
)

# 5. Manage MVP releases
release = fw.mvp_shipping.create_mvp_release(
    "v2_0_0",
    "2.0.0",
    [
        {
            "feature_id": "auth_v2",
            "name": "OAuth Integration",
            "is_core": True,
            "completion_percentage": 0.90
        }
    ]
)

# Get comprehensive framework health
health = fw.get_framework_health()
print(health)
```

---

## Data Structures

### RecurringTask
```python
@dataclass
class RecurringTask:
    task_id: str
    name: str
    description: str
    created_at: datetime
    interval_days: int = 30
    last_executed: Optional[datetime] = None
    next_due: Optional[datetime] = None
    completion_count: int = 0
```

### ContextSignal
```python
@dataclass
class ContextSignal:
    signal_id: str
    signal_type: str
    value: Any
    timestamp: datetime
    confidence: float        # 0.0-1.0, threshold=0.75
    source: str
```

### PatternOccurrence
```python
@dataclass
class PatternOccurrence:
    pattern_id: str
    timestamp: datetime
    context: Dict[str, Any]
```

### ActivityLog
```python
@dataclass
class ActivityLog:
    activity_id: str
    timestamp: datetime
    activity_type: str
    description: str
```

### Feature
```python
@dataclass
class Feature:
    feature_id: str
    name: str
    description: str
    is_core: bool
    completion_percentage: float  # 0.0-1.0
```

### MVPRelease
```python
@dataclass
class MVPRelease:
    release_id: str
    version: str
    created_at: datetime
    features: List[Feature]
    status: ReleaseStatus = ReleaseStatus.PLANNING
    shipped_at: Optional[datetime] = None
```

---

## Key Metrics & Thresholds

| Principle | Metric | Threshold/Value | Unit |
|-----------|--------|-----------------|------|
| Recurring Tasks | Interval | 30 | days |
| Minimal Context | Confidence | ≥0.75 | ratio |
| Intent Inference | Min Occurrences | 3 | count |
| Intent Inference | Lookback Window | 30 | days |
| Silence Protocol | Idle Threshold | 60 | minutes |
| Silence Protocol | Active State | <30 | minutes idle |
| Silence Protocol | Idle State | 30-60 | minutes idle |
| MVP Shipping | Min Core Completion | 0.80 | ratio |
| MVP Shipping | Complete Feature Required | ≥1.0 | ratio |

---

## Testing & Validation

Run the built-in demonstration:

```bash
cd /home/hermes
python framework.py
```

Output includes:
- Demonstration of all 5 principles
- Quantified decision examples
- Framework health summary
- All decisions logged to `framework_decisions.log`

---

## Architecture Notes

### Principles Architecture
- **Modular Design:** Each principle is independently implemented
- **Composable:** Principles work together through unified orchestrator
- **Quantified:** All decisions have explicit numeric logic
- **Logged:** Every decision recorded with metrics

### Decision Logic Patterns
1. **Threshold-Based:** Minimal Context (0.75), MVP Shipping (0.80)
2. **Time-Based:** Recurring Tasks (30 days), Silence Protocol (60 min), Intent (30-day window)
3. **Count-Based:** Intent Inference (≥3 occurrences)
4. **Aggregation:** Multiple signals averaged for final decision

### Extension Points
- Add new `RecurringTask` types
- Create custom `ContextSignal` sources
- Define new `PatternOccurrence` types
- Extend `ReleaseStatus` enum
- Customize logger handlers

---

## Performance Characteristics

- **Memory:** O(n) where n = number of tracked items
- **Task Lookup:** O(1) dictionary-based
- **Signal Aggregation:** O(n) linear scan
- **Pattern Inference:** O(n) filtering within 30-day window
- **Idle Check:** O(1) timestamp comparison
- **MVP Readiness:** O(f) where f = features count

---

## Future Enhancements

- Persistent storage (database backend)
- Machine learning integration for pattern confidence
- Real-time alerting for threshold violations
- Dashboard visualization of metrics
- Integration with calendar/scheduling systems
- A/B testing framework for decision logic
- Predictive task scheduling
- Anomaly detection in activity patterns

---

## File Structure

```
/home/hermes/
├── framework.py                      # Main module (32.8 KB)
├── framework_decisions.log           # Decision log (auto-created)
└── FRAMEWORK_README.md              # This documentation
```

---

## Contact & Support

For questions or improvements, refer to the inline code documentation and test the principles with the `main()` function.

**Last Updated:** June 9, 2026  
**Version:** 1.0.0
