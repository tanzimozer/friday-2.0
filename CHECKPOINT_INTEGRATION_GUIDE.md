# Friday 2.0 Checkpoint Manager — Runtime Integration Guide

## Overview

The Checkpoint Manager provides persistent cross-session memory for Friday 2.0. Memory snapshots are captured at session end and automatically restored at session start, eliminating context loss between chat sessions.

**Status**: ✓ Fully integrated and tested (June 11, 2026)

---

## Architecture

### Components

1. **checkpoint_manager.py** — Core manager class
   - `capture_checkpoint()` — Save current Memory state
   - `load_checkpoint()` — Restore Memory from checkpoint
   - `list_checkpoints()` — Enumerate recent snapshots
   - `prune_old_checkpoints()` — Clean up old checkpoints (30-day retention)

2. **checkpoint_integration.py** — Runtime integration layer
   - `CheckpointIntegration` class
   - Session lifecycle hooks (on_session_start, on_session_end, on_hourly_maintenance)
   - Status reporting and recovery utilities

3. **test_checkpoint_integration.py** — Comprehensive test suite
   - 9 test groups covering all methods
   - Capture/load cycle verification
   - Error handling and edge cases
   - Data integrity validation

---

## Usage in Friday 2.0 Runtime

### Quick Start

```python
from checkpoint_integration import CheckpointIntegration

# Initialize at runtime startup
checkpoint = CheckpointIntegration()

# Load previous session's Memory at startup
checkpoint.on_session_start()

# ... runtime operations ...

# Save Memory state at shutdown
checkpoint.on_session_end(context={
    "tokens_used": 85000,
    "duration_seconds": 1200
})

# Periodically prune old checkpoints (e.g., hourly cron job)
checkpoint.on_hourly_maintenance()
```

### Full Integration Example

```python
#!/usr/bin/env python3
"""Friday 2.0 main runtime with checkpoint integration."""

import logging
from checkpoint_integration import CheckpointIntegration
from framework import PersonalFramework
from edith import EDITHVault

def main():
    # Setup
    checkpoint = CheckpointIntegration()
    framework = PersonalFramework()
    vault = EDITHVault()
    
    # Session initialization
    print("Friday 2.0 initializing...")
    load_result = checkpoint.on_session_start()
    
    if load_result["success"]:
        print(f"✓ Restored Memory from {load_result['captured_at']}")
    else:
        print("✓ Starting fresh session")
    
    # Main loop
    print("Entering runtime loop...")
    try:
        while True:
            # Get user input
            user_input = input("> ")
            
            # Process with framework
            result = framework.process_input(user_input)
            
            # Output response
            print(result)
            
            # Checkpoint status
            if user_input.lower() in ["status", "checkpoint status"]:
                status = checkpoint.get_status()
                print(json.dumps(status, indent=2))
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    
    finally:
        # Session cleanup
        checkpoint.on_session_end(context={
            "exit_reason": "user_interrupt",
            "framework_state": framework.get_state()
        })
        print("✓ Session saved")

if __name__ == "__main__":
    main()
```

---

## Storage Structure

```
~/.hermes/
├── .checkpoints/                              # Checkpoint storage directory
│   ├── index.json                             # Checkpoint registry
│   ├── checkpoint_20260611_123416_916133ff.json
│   ├── checkpoint_20260611_123426_420fd074.json
│   └── checkpoint_20260611_123442_913ac290.json
└── memory.md                                  # Active Memory file
```

### Checkpoint File Format

```json
{
  "session_id": "session_20260611_123416",
  "captured_at": "2026-06-11T12:34:16.909007",
  "memory_snapshot": "# Full Memory content as string...",
  "metadata": {
    "memory_size_bytes": 609,
    "memory_lines": 45,
    "context": {
      "tokens_used": 85000,
      "duration_seconds": 1200,
      "framework": "Friday 2.0"
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
      "filename": "checkpoint_20260611_123416_916133ff.json",
      "session_id": "session_20260611_123416",
      "timestamp": "2026-06-11T12:34:16.909007",
      "size_bytes": 609
    },
    {
      "filename": "checkpoint_20260611_123426_420fd074.json",
      "session_id": "session_20260611_123426",
      "timestamp": "2026-06-11T12:34:26.558023",
      "size_bytes": 237
    }
  ],
  "last_loaded": {
    "filename": "checkpoint_20260611_123426_420fd074.json",
    "loaded_at": "2026-06-11T12:34:42.001618"
  }
}
```

---

## API Reference

### CheckpointManager

#### capture_checkpoint(session_id, context=None) → str
Capture current Memory state as a checkpoint.

**Parameters:**
- `session_id` (str): Unique session identifier
- `context` (dict, optional): Additional metadata (tokens, duration, etc.)

**Returns:** Checkpoint file path (string)

**Example:**
```python
manager = CheckpointManager()
path = manager.capture_checkpoint(
    session_id="session_20260611_123416",
    context={"tokens_used": 85000, "duration_seconds": 1200}
)
# Returns: /home/hermes/.hermes/checkpoints/checkpoint_20260611_123416_916133ff.json
```

#### load_checkpoint(checkpoint_id=None) → Dict
Load a checkpoint and restore Memory.

**Parameters:**
- `checkpoint_id` (str, optional): Specific checkpoint filename. If None, loads most recent.

**Returns:** Dictionary with success status, checkpoint info, or error

**Example:**
```python
result = manager.load_checkpoint()
# Returns: {
#   "success": True,
#   "checkpoint": "checkpoint_20260611_123426_420fd074.json",
#   "restored_bytes": 237,
#   "session_id": "session_20260611_123426",
#   "captured_at": "2026-06-11T12:34:26.558023"
# }
```

#### list_checkpoints(limit=10) → list
Return list of most recent checkpoints.

**Parameters:**
- `limit` (int): Maximum number of checkpoints to return (default 10)

**Returns:** List of checkpoint metadata dicts

**Example:**
```python
checkpoints = manager.list_checkpoints(limit=5)
# Returns: [
#   {
#     "filename": "checkpoint_20260611_123416_916133ff.json",
#     "session_id": "session_20260611_123416",
#     "timestamp": "2026-06-11T12:34:16.909007",
#     "size_bytes": 609
#   },
#   ...
# ]
```

#### prune_old_checkpoints(keep_days=30) → Dict
Delete checkpoints older than keep_days.

**Parameters:**
- `keep_days` (int): Retention period in days (default 30)

**Returns:** Pruning summary with deleted count and freed space

**Example:**
```python
result = manager.prune_old_checkpoints(keep_days=30)
# Returns: {
#   "deleted": 5,
#   "freed_bytes": 45000,
#   "remaining": 30,
#   "retention_days": 30
# }
```

### CheckpointIntegration

#### on_session_start() → Dict
Load checkpoint at session start.

**Returns:** Load result (success, checkpoint info, or error)

#### on_session_end(context=None) → str
Capture checkpoint at session end.

**Parameters:**
- `context` (dict, optional): Session metadata (tokens, duration, etc.)

**Returns:** Checkpoint file path

#### on_hourly_maintenance(keep_days=30) → Dict
Execute hourly maintenance (prune old checkpoints).

**Parameters:**
- `keep_days` (int): Retention period (default 30)

**Returns:** Pruning summary

#### get_status() → Dict
Get current checkpoint integration status.

**Returns:** Dictionary with session info, checkpoint stats, memory info

#### list_recent_checkpoints(limit=10) → list
List recent checkpoints.

**Parameters:**
- `limit` (int): Maximum number to return

**Returns:** List of checkpoint metadata

#### restore_checkpoint(checkpoint_id) → Dict
Restore a specific checkpoint (manual recovery).

**Parameters:**
- `checkpoint_id` (str): Checkpoint filename

**Returns:** Restoration result

---

## Testing

### Run Integration Test Suite

```bash
cd /home/hermes/friday-2.0
python test_checkpoint_integration.py
```

**Output:**
```
╔════════════════════════════════════════════════════════════════╗
║  CHECKPOINT MANAGER INTEGRATION TEST SUITE                    ║
║  Friday 2.0 Runtime Integration Verification                  ║
╚════════════════════════════════════════════════════════════════╝

✓ TEST 1: CheckpointManager Initialization
✓ TEST 2: Capture Checkpoint
✓ TEST 3: Index Update Verification
✓ TEST 4: Load Checkpoint
✓ TEST 5: Load Specific Checkpoint
✓ TEST 6: List Checkpoints
✓ TEST 7: Prune Old Checkpoints
✓ TEST 8: Error Handling
✓ TEST 9: Full Capture/Load Cycle

✓ All 9 test groups passed successfully!
```

### Test Coverage

- ✓ Directory creation and initialization
- ✓ Checkpoint capture with metadata
- ✓ Index persistence and updates
- ✓ Memory restoration (most recent)
- ✓ Specific checkpoint restoration
- ✓ Checkpoint enumeration
- ✓ Old checkpoint pruning
- ✓ Error handling (no checkpoints, missing files)
- ✓ Full capture/load cycle with integrity verification

---

## Integration with Scheduler

### Hourly Checkpoint Pruning

Add to cron or scheduler (e.g., daily at midnight):

```python
from schedule_task import schedule_task

schedule_task(
    action="create",
    name="checkpoint-hourly-prune",
    schedule="0 * * * *",  # Every hour at minute 0
    prompt="""
    from checkpoint_integration import CheckpointIntegration
    integration = CheckpointIntegration()
    result = integration.on_hourly_maintenance(keep_days=30)
    print(f"Pruning result: {result}")
    """
)
```

---

## Troubleshooting

### No Checkpoints Found

If `load_checkpoint()` returns `{"success": False, "error": "No checkpoints available"}`:

1. This is normal for the first session — Memory starts fresh
2. After first session ends, `capture_checkpoint()` will create the first checkpoint
3. Subsequent sessions will restore from this checkpoint

### Memory File Not Restoring

If Memory isn't restored after `load_checkpoint()`:

1. Check that `~/.hermes/memory.md` exists and is readable
2. Verify checkpoint directory: `ls -la ~/.hermes/checkpoints/`
3. Manually restore a checkpoint:
   ```python
   integration = CheckpointIntegration()
   integration.restore_checkpoint("checkpoint_20260611_123416_916133ff.json")
   ```

### Checkpoint Directory Permission Error

If you get "Permission denied" errors:

```bash
chmod 755 ~/.hermes/checkpoints
chmod 644 ~/.hermes/checkpoints/index.json
chmod 644 ~/.hermes/checkpoints/checkpoint_*.json
```

---

## Files

- **checkpoint_manager.py** — Core manager class (197 lines, 6.9 KB)
- **checkpoint_integration.py** — Runtime integration module (268 lines, 7.2 KB)
- **test_checkpoint_integration.py** — Test suite (468 lines, 14.6 KB)
- **SESSION_CHECKPOINT_PERSISTENCE_SKILL.md** — Skill documentation
- **CHECKPOINT_INTEGRATION_GUIDE.md** — This file

---

## Status

✓ **Implementation Complete** — June 11, 2026
✓ **All Tests Passing** — 9/9 test groups
✓ **Integration Verified** — Runtime lifecycle hooks tested
✓ **Ready for Production** — Zero external dependencies

---

## Related Skills

- `session-checkpoint-persistence` — Detailed skill documentation
- `friday-2-0-architecture` — System architecture
- `framework` — Personal framework integration

---

## License

Friday 2.0 — Proprietary
