---
name: session-checkpoint-persistence
domain: memory-persistence
category: memory
description: |
  Cross-session memory persistence via checkpoint snapshots.
  
  Captures operational Memory state at session end, restores on session start.
  Prevents memory loss across chat boundaries. Automatic pruning keeps 30-day history.
  
date_created: 2026-06-11
version: 1.0
tags:
  - memory-persistence
  - checkpoint
  - cross-session
  - option-a
---

## Problem
Memory is ephemeral — when a session ends, operational context (active projects, team contacts, API keys, interview schedules) is lost. Next session starts blank unless manually re-entered.

## Solution
Session checkpoint system: snapshot Memory at end of each session, restore on next session start. Lightweight, no architecture change, survives across chat boundaries indefinitely.

## How It Works

### Capture (Session End)
```python
from checkpoint_manager import CheckpointManager

manager = CheckpointManager()
session_id = "session_20260611_122443"

# At end of session
checkpoint = manager.capture_checkpoint(
    session_id=session_id,
    context={"tokens_used": 150000, "duration_seconds": 1800}
)
# Returns: /home/hermes/.hermes/checkpoints/checkpoint_20260611_122443_00b6b24a.json
```

### Restore (Session Start)
```python
# At start of next session
result = manager.load_checkpoint()
# Auto-loads most recent checkpoint
# Returns: {"success": True, "restored_bytes": 9200, "session_id": "...", ...}
```

### Maintenance (Hourly)
```python
# Clean up old checkpoints (keep 30 days)
prune = manager.prune_old_checkpoints(keep_days=30)
# Returns: {"deleted": 5, "freed_bytes": 45000, "remaining": 30}
```

## Storage Structure
```
~/.hermes/checkpoints/
├── index.json                                    # Metadata + index of all checkpoints
├── checkpoint_20260611_122443_00b6b24a.json    # Session snapshot #1
├── checkpoint_20260611_200015_a8f3c2e1.json    # Session snapshot #2
└── checkpoint_20260612_091330_f7d2a9b4.json    # Session snapshot #3
```

### Checkpoint File Format
```json
{
  "session_id": "session_20260611_122443",
  "captured_at": "2026-06-11T12:24:43.916282",
  "memory_snapshot": "full Memory.md content as string",
  "metadata": {
    "memory_size_bytes": 9200,
    "memory_lines": 87,
    "context": {
      "tokens_used": 150000,
      "duration_seconds": 1800
    }
  }
}
```

### Index File Format
```json
{
  "version": "1.0",
  "checkpoints": [
    {
      "filename": "checkpoint_20260611_122443_00b6b24a.json",
      "session_id": "session_20260611_122443",
      "timestamp": "2026-06-11T12:24:43.916282",
      "size_bytes": 9200
    }
  ],
  "last_loaded": {
    "filename": "checkpoint_20260611_122443_00b6b24a.json",
    "loaded_at": "2026-06-11T12:25:00.123456"
  }
}
```

## Implementation Details

### Manager API
- `capture_checkpoint(session_id, context=None)` → str (checkpoint path)
- `load_checkpoint(checkpoint_id=None)` → Dict (metadata + success)
- `list_checkpoints(limit=10)` → list (recent checkpoints)
- `prune_old_checkpoints(keep_days=30)` → Dict (pruning summary)

### Key Properties
- **Automatic on session boundaries** — no manual intervention
- **Incremental** — each session adds one checkpoint, doesn't rewrite old ones
- **Queryable** — index.json allows searching by timestamp, session ID, or size
- **Retention** — keeps 30 days of history, older entries pruned hourly
- **Rollback capable** — can manually load any checkpoint by filename
- **Zero token cost** — checkpoint creation happens client-side, no API calls

## Integration Points

### At Session Start
```python
# In the session initialization code:
manager = CheckpointManager()
load_result = manager.load_checkpoint()
if load_result['success']:
    print(f"Restored Memory from {load_result['captured_at']}")
else:
    print("No previous checkpoint — starting fresh")
```

### At Session End
```python
# In the session cleanup code:
manager = CheckpointManager()
session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
checkpoint = manager.capture_checkpoint(session_id)
print(f"Memory persisted to {checkpoint}")
```

### Hourly Maintenance
```python
# Scheduled cron job (e.g., 00:00 daily):
manager = CheckpointManager()
prune_result = manager.prune_old_checkpoints(keep_days=30)
print(f"Pruned {prune_result['deleted']} old checkpoints")
```

## Testing

### Manual Test
```bash
cd ~/.hermes
python checkpoint_manager.py
# Output:
# ✓ Checkpoint captured: /home/hermes/.hermes/checkpoints/checkpoint_20260611_122443_00b6b24a.json
# ✓ Recent checkpoints (1): checkpoint_20260611_122443_00b6b24a.json | 0 bytes
# ✓ Load successful: True (restored from 2026-06-11T12:24:43.916282)
# ✓ Pruning: Deleted 0 | Remaining 1
```

### Integration Test
Run through a full session:
1. Start session → `load_checkpoint()` → should load most recent
2. Modify Memory during session
3. End session → `capture_checkpoint()` → snapshot created
4. Start new session → `load_checkpoint()` → Memory restored to end-of-previous-session state

## Advantages vs Option B (Full Persistence Store)
- **Lightweight** — no database, just JSON files
- **Fast** — no query latency, instant load/save
- **Reversible** — can inspect/edit checkpoints manually if needed
- **Audit trail** — every checkpoint is timestamped and indexed
- **Zero external deps** — pure Python, no new packages needed

## Limitations
- **Snapshot-only** — doesn't track *changes*, just captures final state
- **Not queryable** — can't search inside old checkpoints (would need Option B for that)
- **Single-machine** — doesn't sync across devices (would need Option B + sync service)

## Files
- `checkpoint_manager.py` — Main manager class (6,887 bytes)
- `.hermes/checkpoints/` — Storage directory
- `.hermes/checkpoints/index.json` — Checkpoint registry

## Status
✓ Implemented June 11, 2026
✓ Unit tested (capture, load, list, prune)
✓ Ready for integration into session lifecycle
