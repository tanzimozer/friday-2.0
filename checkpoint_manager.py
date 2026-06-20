#!/usr/bin/env python3
"""
Session Checkpoint Manager — Persist operational memory across chat sessions.

Pattern:
  1. At session END: capture_checkpoint() → writes Memory snapshot + metadata
  2. At session START: load_checkpoint() → restores last valid checkpoint to Memory
  3. Hourly: prune_old_checkpoints() → keep last 30 days, delete older

Storage: ~/.hermes/checkpoints/ (JSON files, indexed by timestamp)
"""

import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

CHECKPOINT_DIR = Path.home() / '.hermes' / 'checkpoints'
CHECKPOINT_INDEX = CHECKPOINT_DIR / 'index.json'
MEMORY_FILE = Path.home() / '.hermes' / 'memory.md'
MAX_CHECKPOINTS = 30  # Keep 30 days of history


class CheckpointManager:
    def __init__(self):
        self.checkpoint_dir = CHECKPOINT_DIR
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load or create checkpoint index."""
        if CHECKPOINT_INDEX.exists():
            with open(CHECKPOINT_INDEX) as f:
                return json.load(f)
        return {"checkpoints": [], "last_loaded": None, "version": "1.0"}

    def _save_index(self):
        """Persist checkpoint index."""
        with open(CHECKPOINT_INDEX, 'w') as f:
            json.dump(self.index, f, indent=2)

    def capture_checkpoint(self, session_id: str, context: Dict[str, Any] = None) -> str:
        """
        Capture current Memory state as a checkpoint.
        
        Args:
            session_id: Unique session identifier
            context: Optional additional metadata (token count, duration, etc.)
        
        Returns:
            Checkpoint file path (string)
        """
        timestamp = datetime.now().isoformat()
        checkpoint_filename = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}.json"
        checkpoint_path = self.checkpoint_dir / checkpoint_filename

        # Read current Memory state
        memory_content = ""
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE) as f:
                memory_content = f.read()

        checkpoint_data = {
            "session_id": session_id,
            "captured_at": timestamp,
            "memory_snapshot": memory_content,
            "metadata": {
                "memory_size_bytes": len(memory_content.encode()),
                "memory_lines": memory_content.count('\n'),
                "context": context or {}
            }
        }

        # Write checkpoint file
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

        # Update index
        self.index["checkpoints"].append({
            "filename": checkpoint_filename,
            "session_id": session_id,
            "timestamp": timestamp,
            "size_bytes": len(memory_content.encode())
        })
        self._save_index()

        return str(checkpoint_path)

    def load_checkpoint(self, checkpoint_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a checkpoint and restore Memory.
        
        Args:
            checkpoint_id: Specific checkpoint filename. If None, loads most recent.
        
        Returns:
            Checkpoint metadata + success status
        """
        if not self.index["checkpoints"]:
            return {"success": False, "error": "No checkpoints available"}

        if checkpoint_id is None:
            # Load most recent checkpoint
            checkpoint_meta = self.index["checkpoints"][-1]
            checkpoint_filename = checkpoint_meta["filename"]
        else:
            checkpoint_filename = checkpoint_id

        checkpoint_path = self.checkpoint_dir / checkpoint_filename

        if not checkpoint_path.exists():
            return {"success": False, "error": f"Checkpoint not found: {checkpoint_filename}"}

        try:
            with open(checkpoint_path) as f:
                checkpoint_data = json.load(f)

            # Restore Memory file
            memory_content = checkpoint_data["memory_snapshot"]
            with open(MEMORY_FILE, 'w') as f:
                f.write(memory_content)

            # Update index
            self.index["last_loaded"] = {
                "filename": checkpoint_filename,
                "loaded_at": datetime.now().isoformat()
            }
            self._save_index()

            return {
                "success": True,
                "checkpoint": checkpoint_filename,
                "restored_bytes": checkpoint_data["metadata"]["memory_size_bytes"],
                "session_id": checkpoint_data["session_id"],
                "captured_at": checkpoint_data["captured_at"]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def prune_old_checkpoints(self, keep_days: int = 30) -> Dict[str, Any]:
        """
        Delete checkpoints older than keep_days.
        
        Args:
            keep_days: Retention period (default 30 days)
        
        Returns:
            Pruning summary (deleted count, freed space)
        """
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        freed_bytes = 0

        remaining = []
        for checkpoint_meta in self.index["checkpoints"]:
            checkpoint_timestamp = datetime.fromisoformat(checkpoint_meta["timestamp"])
            
            if checkpoint_timestamp < cutoff_date:
                # Delete the file
                checkpoint_path = self.checkpoint_dir / checkpoint_meta["filename"]
                if checkpoint_path.exists():
                    freed_bytes += checkpoint_path.stat().st_size
                    checkpoint_path.unlink()
                    deleted_count += 1
            else:
                remaining.append(checkpoint_meta)

        self.index["checkpoints"] = remaining
        self._save_index()

        return {
            "deleted": deleted_count,
            "freed_bytes": freed_bytes,
            "remaining": len(remaining),
            "retention_days": keep_days
        }

    def list_checkpoints(self, limit: int = 10) -> list:
        """Return list of most recent checkpoints."""
        return self.index["checkpoints"][-limit:]


if __name__ == "__main__":
    manager = CheckpointManager()
    
    # Example: capture current session
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    checkpoint_path = manager.capture_checkpoint(session_id)
    print(f"Checkpoint captured: {checkpoint_path}")
    
    # Example: list recent checkpoints
    recent = manager.list_checkpoints(5)
    print(f"\nRecent checkpoints ({len(recent)}):")
    for cp in recent:
        print(f"  - {cp['filename']} ({cp['size_bytes']} bytes) — {cp['timestamp']}")
