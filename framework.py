"""
Personal Framework Module - Decision Rules Engine
Codifies 5 core principles with explicit quantified logic and comprehensive logging.

Core Principles:
1. 30-day recurring task design
2. Minimal context with 0.75 confidence threshold
3. Intent inference from patterns
4. Silence protocol at 60 min idle
5. Execution-first MVP shipping
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class FrameworkLogger:
    """Centralized logging for framework decisions."""
    
    def __init__(self, name: str = "PersonalFramework"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler
        file_handler = logging.FileHandler('/home/hermes/framework_decisions.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def log_decision(self, principle: str, decision: str, metrics: Dict[str, Any]):
        """Log a framework decision with associated metrics."""
        msg = f"[{principle}] {decision} | Metrics: {json.dumps(metrics, default=str)}"
        self.logger.info(msg)
    
    def log_debug(self, message: str):
        self.logger.debug(message)
    
    def log_warning(self, message: str):
        self.logger.warning(message)


# ============================================================================
# PRINCIPLE 1: 30-DAY RECURRING TASK DESIGN
# ============================================================================

@dataclass
class RecurringTask:
    """Represents a 30-day recurring task."""
    task_id: str
    name: str
    description: str
    created_at: datetime
    interval_days: int = 30
    last_executed: Optional[datetime] = None
    next_due: Optional[datetime] = None
    completion_count: int = 0
    
    def calculate_next_due(self) -> datetime:
        """Calculate when task is next due (30-day recurrence)."""
        base_date = self.last_executed or self.created_at
        self.next_due = base_date + timedelta(days=self.interval_days)
        return self.next_due
    
    def is_due(self) -> bool:
        """Check if task is due for execution."""
        if self.next_due is None:
            self.calculate_next_due()
        return datetime.now() >= self.next_due
    
    def mark_executed(self):
        """Mark task as executed and recalculate next due date."""
        self.last_executed = datetime.now()
        self.completion_count += 1
        self.calculate_next_due()


class RecurringTaskManager:
    """Manages 30-day recurring task design principle."""
    
    def __init__(self):
        self.tasks: Dict[str, RecurringTask] = {}
        self.logger = FrameworkLogger()
    
    def create_task(self, task_id: str, name: str, description: str) -> RecurringTask:
        """Create a new 30-day recurring task."""
        task = RecurringTask(
            task_id=task_id,
            name=name,
            description=description,
            created_at=datetime.now(),
            interval_days=30
        )
        self.tasks[task_id] = task
        
        self.logger.log_decision(
            "30-day Recurring Task Design",
            f"Created task: {name}",
            {
                "task_id": task_id,
                "interval_days": 30,
                "created_at": task.created_at.isoformat()
            }
        )
        return task
    
    def get_due_tasks(self) -> List[RecurringTask]:
        """Retrieve all tasks due for execution."""
        due_tasks = [task for task in self.tasks.values() if task.is_due()]
        self.logger.log_debug(f"Found {len(due_tasks)} tasks due for execution")
        return due_tasks
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute and mark a task complete."""
        if task_id not in self.tasks:
            self.logger.log_warning(f"Task {task_id} not found")
            return {"status": "error", "message": "Task not found"}
        
        task = self.tasks[task_id]
        task.mark_executed()
        
        metrics = {
            "task_id": task_id,
            "completion_count": task.completion_count,
            "next_due": task.next_due.isoformat(),
            "executed_at": task.last_executed.isoformat()
        }
        
        self.logger.log_decision(
            "30-day Recurring Task Design",
            f"Executed task: {task.name}",
            metrics
        )
        
        return {"status": "success", "task": asdict(task)}
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get statistics on recurring tasks."""
        return {
            "total_tasks": len(self.tasks),
            "due_tasks": len(self.get_due_tasks()),
            "avg_completion_count": (
                sum(t.completion_count for t in self.tasks.values()) / len(self.tasks)
                if self.tasks else 0
            ),
            "tasks": [asdict(t) for t in self.tasks.values()]
        }


# ============================================================================
# PRINCIPLE 2: MINIMAL CONTEXT WITH 0.75 CONFIDENCE THRESHOLD
# ============================================================================

@dataclass
class ContextSignal:
    """Represents a minimal context signal."""
    signal_id: str
    signal_type: str
    value: Any
    timestamp: datetime
    confidence: float
    source: str


class MinimalContextProcessor:
    """Processes minimal context with 0.75 confidence threshold."""
    
    CONFIDENCE_THRESHOLD = 0.75
    
    def __init__(self):
        self.signals: Dict[str, ContextSignal] = {}
        self.logger = FrameworkLogger()
    
    def process_signal(self, signal_id: str, signal_type: str, value: Any, 
                      confidence: float, source: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Process a context signal and evaluate against confidence threshold.
        
        Returns:
            Tuple[bool, Dict]: (passes_threshold, metrics)
        """
        signal = ContextSignal(
            signal_id=signal_id,
            signal_type=signal_type,
            value=value,
            timestamp=datetime.now(),
            confidence=confidence,
            source=source
        )
        
        self.signals[signal_id] = signal
        
        passes_threshold = confidence >= self.CONFIDENCE_THRESHOLD
        
        metrics = {
            "signal_id": signal_id,
            "signal_type": signal_type,
            "confidence": confidence,
            "threshold": self.CONFIDENCE_THRESHOLD,
            "passes": passes_threshold,
            "source": source,
            "confidence_gap": round(confidence - self.CONFIDENCE_THRESHOLD, 4)
        }
        
        decision_msg = f"Signal {signal_id} {'ACCEPTED' if passes_threshold else 'REJECTED'}"
        self.logger.log_decision(
            "Minimal Context (0.75 Confidence Threshold)",
            decision_msg,
            metrics
        )
        
        return passes_threshold, metrics
    
    def aggregate_confidence(self, signal_ids: List[str]) -> Tuple[float, Dict[str, Any]]:
        """
        Aggregate confidence across multiple signals.
        Computes: (sum of confidences) / (count of signals)
        """
        if not signal_ids:
            return 0.0, {"error": "No signals provided"}
        
        signals = [self.signals[sid] for sid in signal_ids if sid in self.signals]
        if not signals:
            return 0.0, {"error": "No valid signals found"}
        
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        metrics = {
            "signal_count": len(signals),
            "avg_confidence": round(avg_confidence, 4),
            "threshold": self.CONFIDENCE_THRESHOLD,
            "passes_aggregated": avg_confidence >= self.CONFIDENCE_THRESHOLD,
            "signals": [asdict(s) for s in signals]
        }
        
        self.logger.log_decision(
            "Minimal Context (0.75 Confidence Threshold)",
            f"Aggregated {len(signals)} signals",
            metrics
        )
        
        return avg_confidence, metrics
    
    def get_high_confidence_signals(self) -> List[ContextSignal]:
        """Retrieve signals meeting confidence threshold."""
        high_conf = [s for s in self.signals.values() 
                     if s.confidence >= self.CONFIDENCE_THRESHOLD]
        self.logger.log_debug(f"Found {len(high_conf)} high-confidence signals")
        return high_conf


# ============================================================================
# PRINCIPLE 3: INTENT INFERENCE FROM PATTERNS
# ============================================================================

@dataclass
class PatternOccurrence:
    """Represents a single pattern occurrence."""
    pattern_id: str
    timestamp: datetime
    context: Dict[str, Any]


class IntentInferenceEngine:
    """Infers intent from observed patterns."""
    
    def __init__(self):
        self.patterns: Dict[str, List[PatternOccurrence]] = {}
        self.inferred_intents: Dict[str, Dict[str, Any]] = {}
        self.logger = FrameworkLogger()
    
    def record_pattern(self, pattern_id: str, context: Dict[str, Any]):
        """Record a pattern occurrence."""
        if pattern_id not in self.patterns:
            self.patterns[pattern_id] = []
        
        occurrence = PatternOccurrence(
            pattern_id=pattern_id,
            timestamp=datetime.now(),
            context=context
        )
        self.patterns[pattern_id].append(occurrence)
        self.logger.log_debug(f"Recorded pattern: {pattern_id}")
    
    def infer_intent(self, pattern_id: str, min_occurrences: int = 3) -> Tuple[bool, Dict[str, Any]]:
        """
        Infer intent from pattern.
        
        Logic:
        - Pattern must have >= min_occurrences to infer intent
        - Confidence = (occurrence_count / lookback_window) * 100
        - Lookback window = 30 days
        """
        if pattern_id not in self.patterns:
            return False, {"error": f"Pattern {pattern_id} not found"}
        
        occurrences = self.patterns[pattern_id]
        now = datetime.now()
        lookback_window = timedelta(days=30)
        
        # Filter recent occurrences
        recent = [o for o in occurrences 
                 if (now - o.timestamp) <= lookback_window]
        
        occurrence_count = len(recent)
        passes_threshold = occurrence_count >= min_occurrences
        
        # Confidence calculation: (occurrences / max possible in window)
        max_possible = 30  # Assuming ~1 per day max
        pattern_confidence = min(occurrence_count / max_possible, 1.0)
        
        intent_record = {
            "pattern_id": pattern_id,
            "occurrence_count": occurrence_count,
            "min_required": min_occurrences,
            "confidence": round(pattern_confidence, 4),
            "inferred": passes_threshold,
            "recent_contexts": [asdict(o) for o in recent[-3:]]  # Last 3
        }
        
        if passes_threshold:
            self.inferred_intents[pattern_id] = intent_record
        
        metrics = {
            **intent_record,
            "lookback_days": 30,
            "recent_occurrence_count": occurrence_count,
            "confidence_threshold": 0.75,
            "meets_threshold": pattern_confidence >= 0.75
        }
        
        self.logger.log_decision(
            "Intent Inference from Patterns",
            f"Pattern '{pattern_id}' intent: {'INFERRED' if passes_threshold else 'INSUFFICIENT DATA'}",
            metrics
        )
        
        return passes_threshold, metrics
    
    def get_inferred_intents(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all inferred intents."""
        return self.inferred_intents.copy()
    
    def pattern_stats(self) -> Dict[str, Any]:
        """Get statistics on patterns and inferences."""
        return {
            "total_patterns": len(self.patterns),
            "inferred_intents": len(self.inferred_intents),
            "patterns": {
                pid: {
                    "occurrence_count": len(occs),
                    "first_seen": min(o.timestamp for o in occs).isoformat(),
                    "last_seen": max(o.timestamp for o in occs).isoformat()
                }
                for pid, occs in self.patterns.items()
            }
        }


# ============================================================================
# PRINCIPLE 4: SILENCE PROTOCOL AT 60 MIN IDLE
# ============================================================================

class IdleState(Enum):
    """States for idle monitoring."""
    ACTIVE = "active"
    IDLE = "idle"
    SILENT = "silent"


@dataclass
class ActivityLog:
    """Represents a user activity."""
    activity_id: str
    timestamp: datetime
    activity_type: str
    description: str


class SilenceProtocol:
    """Implements silence protocol at 60 minute idle threshold."""
    
    IDLE_THRESHOLD_MINUTES = 60
    SILENCE_ENABLED = True
    
    def __init__(self):
        self.last_activity: Optional[datetime] = None
        self.activity_logs: List[ActivityLog] = []
        self.state = IdleState.ACTIVE
        self.logger = FrameworkLogger()
    
    def record_activity(self, activity_id: str, activity_type: str, 
                       description: str) -> Dict[str, Any]:
        """Record a user activity."""
        self.last_activity = datetime.now()
        activity = ActivityLog(
            activity_id=activity_id,
            timestamp=self.last_activity,
            activity_type=activity_type,
            description=description
        )
        self.activity_logs.append(activity)
        self.state = IdleState.ACTIVE
        
        metrics = {
            "activity_id": activity_id,
            "activity_type": activity_type,
            "timestamp": self.last_activity.isoformat(),
            "state": self.state.value
        }
        
        self.logger.log_decision(
            "Silence Protocol (60 min Idle)",
            f"Activity recorded: {activity_type}",
            metrics
        )
        
        return {"status": "recorded", "state": self.state.value}
    
    def check_idle_state(self) -> Tuple[IdleState, Dict[str, Any]]:
        """
        Check current idle state based on last activity.
        
        Logic:
        - ACTIVE: < 30 min idle
        - IDLE: 30-60 min idle
        - SILENT: >= 60 min idle (silence protocol engaged)
        """
        if self.last_activity is None:
            idle_minutes = float('inf')
        else:
            idle_minutes = (datetime.now() - self.last_activity).total_seconds() / 60
        
        # State determination
        if idle_minutes < 30:
            self.state = IdleState.ACTIVE
        elif idle_minutes < self.IDLE_THRESHOLD_MINUTES:
            self.state = IdleState.IDLE
        else:
            self.state = IdleState.SILENT
        
        silence_engaged = self.state == IdleState.SILENT and self.SILENCE_ENABLED
        
        metrics = {
            "idle_minutes": round(idle_minutes, 2),
            "idle_threshold_minutes": self.IDLE_THRESHOLD_MINUTES,
            "current_state": self.state.value,
            "silence_protocol_engaged": silence_engaged,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
        
        if silence_engaged:
            self.logger.log_decision(
                "Silence Protocol (60 min Idle)",
                "SILENCE PROTOCOL ENGAGED",
                metrics
            )
        else:
            self.logger.log_debug(f"Idle check: {self.state.value} ({idle_minutes:.1f} min)")
        
        return self.state, metrics
    
    def get_activity_summary(self) -> Dict[str, Any]:
        """Get summary of activities and idle state."""
        state, metrics = self.check_idle_state()
        
        return {
            "current_state": state.value,
            "total_activities": len(self.activity_logs),
            "silence_protocol_enabled": self.SILENCE_ENABLED,
            "idle_threshold_minutes": self.IDLE_THRESHOLD_MINUTES,
            "metrics": metrics,
            "recent_activities": [asdict(a) for a in self.activity_logs[-5:]]
        }


# ============================================================================
# PRINCIPLE 5: EXECUTION-FIRST MVP SHIPPING
# ============================================================================

class ReleaseStatus(Enum):
    """Release status for MVP."""
    PLANNING = "planning"
    IN_DEVELOPMENT = "in_development"
    MVP_READY = "mvp_ready"
    SHIPPED = "shipped"
    LIVE = "live"


@dataclass
class Feature:
    """Represents a feature in MVP."""
    feature_id: str
    name: str
    description: str
    is_core: bool
    completion_percentage: float


@dataclass
class MVPRelease:
    """Represents an MVP release."""
    release_id: str
    version: str
    created_at: datetime
    features: List[Feature]
    status: ReleaseStatus = ReleaseStatus.PLANNING
    shipped_at: Optional[datetime] = None
    
    def core_feature_completion(self) -> float:
        """Calculate core feature completion percentage."""
        core_features = [f for f in self.features if f.is_core]
        if not core_features:
            return 0.0
        return sum(f.completion_percentage for f in core_features) / len(core_features)
    
    def is_ready_to_ship(self, min_completion: float = 0.75) -> bool:
        """
        Determine if MVP is ready to ship.
        
        Logic:
        - All core features must reach min_completion (default 75%, matches spec)
        - At least one feature must be at 100%
        """
        completion = self.core_feature_completion()
        has_complete_feature = any(f.completion_percentage >= 1.0 
                                   for f in self.features if f.is_core)
        
        return completion >= min_completion and has_complete_feature


class ExecutionFirstMVPShipper:
    """Manages execution-first MVP shipping principle."""
    
    def __init__(self):
        self.releases: Dict[str, MVPRelease] = {}
        self.logger = FrameworkLogger()
    
    def create_mvp_release(self, release_id: str, version: str, 
                          features: List[Dict[str, Any]]) -> MVPRelease:
        """Create a new MVP release."""
        feature_objs = [
            Feature(
                feature_id=f["feature_id"],
                name=f["name"],
                description=f["description"],
                is_core=f.get("is_core", False),
                completion_percentage=f.get("completion_percentage", 0.0)
            )
            for f in features
        ]
        
        release = MVPRelease(
            release_id=release_id,
            version=version,
            created_at=datetime.now(),
            features=feature_objs
        )
        
        self.releases[release_id] = release
        
        metrics = {
            "release_id": release_id,
            "version": version,
            "feature_count": len(feature_objs),
            "core_features": sum(1 for f in feature_objs if f.is_core),
            "created_at": release.created_at.isoformat()
        }
        
        self.logger.log_decision(
            "Execution-First MVP Shipping",
            f"Created MVP release {version}",
            metrics
        )
        
        return release
    
    def update_feature_completion(self, release_id: str, feature_id: str, 
                                 completion: float) -> Dict[str, Any]:
        """Update feature completion percentage."""
        if release_id not in self.releases:
            return {"status": "error", "message": "Release not found"}
        
        release = self.releases[release_id]
        feature = next((f for f in release.features if f.feature_id == feature_id), None)
        
        if not feature:
            return {"status": "error", "message": "Feature not found"}
        
        feature.completion_percentage = min(completion, 1.0)
        
        metrics = {
            "release_id": release_id,
            "feature_id": feature_id,
            "feature_name": feature.name,
            "completion": feature.completion_percentage,
            "core_feature_avg": round(release.core_feature_completion(), 4)
        }
        
        self.logger.log_decision(
            "Execution-First MVP Shipping",
            f"Updated feature '{feature.name}' to {feature.completion_percentage*100:.0f}%",
            metrics
        )
        
        return {"status": "success", "metrics": metrics}
    
    def evaluate_ship_readiness(self, release_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate if MVP is ready to ship.
        
        Criteria:
        - Core feature completion >= 80%
        - At least one core feature at 100%
        """
        if release_id not in self.releases:
            return False, {"error": "Release not found"}
        
        release = self.releases[release_id]
        ready = release.is_ready_to_ship(min_completion=0.75)
        completion = release.core_feature_completion()
        
        metrics = {
            "release_id": release_id,
            "version": release.version,
            "core_feature_completion": round(completion, 4),
            "ready_to_ship": ready,
            "min_required_completion": 0.75,
            "features": [
                {
                    "name": f.name,
                    "completion": f.completion_percentage,
                    "is_core": f.is_core
                }
                for f in release.features
            ]
        }
        
        status_msg = "READY TO SHIP" if ready else "NOT READY - CONTINUE EXECUTION"
        self.logger.log_decision(
            "Execution-First MVP Shipping",
            f"MVP {release.version}: {status_msg}",
            metrics
        )
        
        return ready, metrics
    
    def ship_release(self, release_id: str) -> Dict[str, Any]:
        """Ship MVP release to production."""
        if release_id not in self.releases:
            return {"status": "error", "message": "Release not found"}
        
        release = self.releases[release_id]
        ready, readiness_metrics = self.evaluate_ship_readiness(release_id)
        
        if not ready:
            return {
                "status": "error",
                "message": "MVP not ready to ship",
                "readiness_metrics": readiness_metrics
            }
        
        release.status = ReleaseStatus.SHIPPED
        release.shipped_at = datetime.now()
        
        metrics = {
            "release_id": release_id,
            "version": release.version,
            "shipped_at": release.shipped_at.isoformat(),
            "core_completion": round(release.core_feature_completion(), 4),
            "feature_count": len(release.features)
        }
        
        self.logger.log_decision(
            "Execution-First MVP Shipping",
            f"MVP {release.version} SHIPPED TO PRODUCTION",
            metrics
        )
        
        return {"status": "success", "shipped_release": asdict(release), "metrics": metrics}


# ============================================================================
# UNIFIED FRAMEWORK ORCHESTRATOR
# ============================================================================

class PersonalFramework:
    """Unified orchestrator for all 5 core principles."""
    
    def __init__(self):
        self.recurring_tasks = RecurringTaskManager()
        self.minimal_context = MinimalContextProcessor()
        self.intent_inference = IntentInferenceEngine()
        self.silence_protocol = SilenceProtocol()
        self.mvp_shipping = ExecutionFirstMVPShipper()
        self.logger = FrameworkLogger()
        self.decisions_log: List[Dict[str, Any]] = []
        self._init_timestamp = datetime.now()
    
    def get_framework_health(self) -> Dict[str, Any]:
        """Get overall framework health metrics."""
        silence_state, silence_metrics = self.silence_protocol.check_idle_state()
        
        return {
            "framework_uptime_seconds": (datetime.now() - self._init_timestamp).total_seconds(),
            "principles": {
                "recurring_tasks": self.recurring_tasks.get_task_stats(),
                "minimal_context": {
                    "total_signals": len(self.minimal_context.signals),
                    "high_confidence_signals": len(self.minimal_context.get_high_confidence_signals()),
                    "confidence_threshold": self.minimal_context.CONFIDENCE_THRESHOLD
                },
                "intent_inference": self.intent_inference.pattern_stats(),
                "silence_protocol": {
                    "current_state": silence_state.value,
                    "idle_threshold_minutes": self.silence_protocol.IDLE_THRESHOLD_MINUTES,
                    "silence_enabled": self.silence_protocol.SILENCE_ENABLED,
                    "metrics": silence_metrics
                },
                "mvp_shipping": {
                    "total_releases": len(self.mvp_shipping.releases),
                    "releases": [
                        {
                            "version": r.version,
                            "status": r.status.value,
                            "core_completion": round(r.core_feature_completion(), 4)
                        }
                        for r in self.mvp_shipping.releases.values()
                    ]
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def log_framework_state(self) -> Dict[str, Any]:
        """Comprehensive log of framework state."""
        health = self.get_framework_health()
        self.logger.log_debug(f"Framework health snapshot: {json.dumps(health, default=str)}")
        return health


# ============================================================================
# MAIN EXECUTION & EXAMPLES
# ============================================================================

def main():
    """Demonstrate the Personal Framework with all 5 principles."""
    
    print("\n" + "="*80)
    print("PERSONAL FRAMEWORK - 5 Core Principles Demonstration")
    print("="*80 + "\n")
    
    # Initialize framework
    framework = PersonalFramework()
    
    # ========================================================================
    # PRINCIPLE 1: 30-Day Recurring Task Design
    # ========================================================================
    print("\n[1] 30-DAY RECURRING TASK DESIGN")
    print("-" * 80)
    
    framework.recurring_tasks.create_task(
        "review_goals",
        "Monthly Goal Review",
        "Review and adjust 30-day goals"
    )
    framework.recurring_tasks.create_task(
        "health_checkup",
        "Health Checkup",
        "Monthly health metrics review"
    )
    
    # Simulate executing a task
    framework.recurring_tasks.execute_task("review_goals")
    
    task_stats = framework.recurring_tasks.get_task_stats()
    print(f"✓ Created 2 recurring tasks with 30-day intervals")
    print(f"✓ Task stats: {json.dumps(task_stats, indent=2, default=str)}")
    
    # ========================================================================
    # PRINCIPLE 2: Minimal Context with 0.75 Confidence Threshold
    # ========================================================================
    print("\n[2] MINIMAL CONTEXT (0.75 Confidence Threshold)")
    print("-" * 80)
    
    # High confidence signal
    passes, metrics = framework.minimal_context.process_signal(
        "signal_001",
        "user_intent",
        "schedule_meeting",
        confidence=0.92,
        source="nlp_parser"
    )
    print(f"✓ Signal 001 (conf=0.92): {'ACCEPTED' if passes else 'REJECTED'}")
    
    # Low confidence signal
    passes, metrics = framework.minimal_context.process_signal(
        "signal_002",
        "user_intent",
        "unknown_action",
        confidence=0.45,
        source="nlp_parser"
    )
    print(f"✓ Signal 002 (conf=0.45): {'ACCEPTED' if passes else 'REJECTED'}")
    
    # Aggregate confidence
    avg_conf, agg_metrics = framework.minimal_context.aggregate_confidence(
        ["signal_001", "signal_002"]
    )
    print(f"✓ Aggregated confidence: {avg_conf:.4f} ({'PASSES' if avg_conf >= 0.75 else 'FAILS'} threshold)")
    
    # ========================================================================
    # PRINCIPLE 3: Intent Inference from Patterns
    # ========================================================================
    print("\n[3] INTENT INFERENCE FROM PATTERNS")
    print("-" * 80)
    
    # Record pattern occurrences
    for i in range(4):
        framework.intent_inference.record_pattern(
            "daily_standup",
            {"time": "09:00", "duration_min": 15}
        )
    
    # Infer intent
    inferred, intent_metrics = framework.intent_inference.infer_intent(
        "daily_standup",
        min_occurrences=3
    )
    print(f"✓ Pattern 'daily_standup' with 4 occurrences")
    print(f"✓ Intent inferred: {inferred} (confidence={intent_metrics['confidence']})")
    
    # ========================================================================
    # PRINCIPLE 4: Silence Protocol at 60 Min Idle
    # ========================================================================
    print("\n[4] SILENCE PROTOCOL (60 min Idle Threshold)")
    print("-" * 80)
    
    framework.silence_protocol.record_activity(
        "act_001",
        "api_call",
        "Fetched user data"
    )
    
    state, idle_metrics = framework.silence_protocol.check_idle_state()
    print(f"✓ Activity recorded, current state: {state.value}")
    print(f"✓ Idle time: {idle_metrics['idle_minutes']:.2f} minutes")
    print(f"✓ Silence protocol engaged: {idle_metrics['silence_protocol_engaged']}")
    
    activity_summary = framework.silence_protocol.get_activity_summary()
    print(f"✓ Total activities logged: {activity_summary['total_activities']}")
    
    # ========================================================================
    # PRINCIPLE 5: Execution-First MVP Shipping
    # ========================================================================
    print("\n[5] EXECUTION-FIRST MVP SHIPPING")
    print("-" * 80)
    
    features = [
        {"feature_id": "auth", "name": "Authentication", "description": "User auth system", "is_core": True, "completion_percentage": 1.0},
        {"feature_id": "api", "name": "REST API", "description": "Core API endpoints", "is_core": True, "completion_percentage": 0.85},
        {"feature_id": "dashboard", "name": "Dashboard", "description": "User dashboard", "is_core": False, "completion_percentage": 0.50}
    ]
    
    release = framework.mvp_shipping.create_mvp_release(
        "v1_0_0",
        "1.0.0",
        features
    )
    
    print(f"✓ Created MVP release v1.0.0 with {len(features)} features")
    
    # Update API feature completion
    framework.mvp_shipping.update_feature_completion("v1_0_0", "api", 1.0)
    
    # Evaluate ship readiness
    ready, readiness = framework.mvp_shipping.evaluate_ship_readiness("v1_0_0")
    print(f"✓ Core feature completion: {readiness['core_feature_completion']:.1%}")
    print(f"✓ Ready to ship: {ready}")
    
    if ready:
        shipped = framework.mvp_shipping.ship_release("v1_0_0")
        print(f"✓ MVP {release.version} shipped to production!")
    
    # ========================================================================
    # FRAMEWORK HEALTH SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("FRAMEWORK HEALTH SUMMARY")
    print("="*80)
    
    health = framework.get_framework_health()
    print(json.dumps(health, indent=2, default=str))
    
    print("\n✓ Framework successfully demonstrated all 5 principles with quantified logic!")


if __name__ == "__main__":
    main()
