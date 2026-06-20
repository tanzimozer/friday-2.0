#!/usr/bin/env python3
"""
Friday 2.0 Runtime Checkpoint Integration Module

Integrates CheckpointManager into the Friday 2.0 runtime lifecycle:
- Session initialization: load_checkpoint() to restore Memory
- Session cleanup: capture_checkpoint() to persist Memory
- Hourly maintenance: prune_old_checkpoints() to manage storage

This module provides convenient hooks for embedding checkpoint functionality
into the main runtime loop.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from checkpoint_manager import CheckpointManager, MEMORY_FILE, CHECKPOINT_DIR

class CheckpointIntegration:
    """
    Manages checkpoint integration with Friday 2.0 runtime.
    
    Usage:
        integration = CheckpointIntegration()
        
        # At session start
        integration.on_session_start()
        
        # At session end
        integration.on_session_end()
        
        # Periodically (hourly)
        integration.on_hourly_maintenance()
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize checkpoint integration."""
        self.manager = CheckpointManager()
        self.logger = logger or self._setup_logger()
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.load_result = None
        self.capture_result = None
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for checkpoint integration."""
        logger = logging.getLogger("CheckpointIntegration")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def on_session_start(self) -> Dict[str, Any]:
        """
        Load checkpoint at session start.
        
        Returns:
            Dictionary with load results (success, checkpoint info, or error)
        """
        self.logger.info(f"Starting Friday 2.0 session: {self.session_id}")
        
        # Attempt to load most recent checkpoint
        self.load_result = self.manager.load_checkpoint()
        
        if self.load_result["success"]:
            self.logger.info(
                f"✓ Restored Memory from checkpoint: "
                f"{self.load_result['captured_at']} "
                f"({self.load_result['restored_bytes']} bytes)"
            )
        else:
            self.logger.info(
                f"No previous checkpoint found — starting fresh session"
            )
        
        return self.load_result
    
    def on_session_end(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Capture checkpoint at session end.
        
        Args:
            context: Optional metadata (tokens used, duration, etc.)
        
        Returns:
            Checkpoint file path
        """
        self.logger.info("Saving Friday 2.0 session state")
        
        # Prepare context
        checkpoint_context = {
            "session_id": self.session_id,
            "framework": "Friday 2.0",
            "integration": "runtime-checkpoint"
        }
        if context:
            checkpoint_context.update(context)
        
        # Capture checkpoint
        self.capture_result = self.manager.capture_checkpoint(
            session_id=self.session_id,
            context=checkpoint_context
        )
        
        self.logger.info(
            f"✓ Memory persisted: {Path(self.capture_result).name}"
        )
        
        return self.capture_result
    
    def on_hourly_maintenance(self, keep_days: int = 30) -> Dict[str, Any]:
        """
        Execute hourly maintenance (prune old checkpoints).
        
        Args:
            keep_days: Retention period (default 30 days)
        
        Returns:
            Pruning summary
        """
        self.logger.debug(f"Executing hourly checkpoint maintenance")
        
        result = self.manager.prune_old_checkpoints(keep_days=keep_days)
        
        if result["deleted"] > 0:
            self.logger.info(
                f"Pruned {result['deleted']} old checkpoint(s) "
                f"(freed {result['freed_bytes']} bytes, "
                f"{result['remaining']} remaining)"
            )
        else:
            self.logger.debug("No old checkpoints to prune")
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current checkpoint integration status."""
        checkpoints = self.manager.list_checkpoints(limit=100)
        
        return {
            "session_id": self.session_id,
            "checkpoint_dir": str(CHECKPOINT_DIR),
            "memory_file": str(MEMORY_FILE),
            "total_checkpoints": len(checkpoints),
            "last_checkpoint": checkpoints[-1] if checkpoints else None,
            "load_status": self.load_result,
            "memory_file_exists": MEMORY_FILE.exists(),
            "memory_file_size": MEMORY_FILE.stat().st_size if MEMORY_FILE.exists() else 0
        }
    
    def list_recent_checkpoints(self, limit: int = 10) -> list:
        """List recent checkpoints."""
        return self.manager.list_checkpoints(limit=limit)
    
    def restore_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Restore a specific checkpoint (manual recovery).
        
        Args:
            checkpoint_id: Checkpoint filename
        
        Returns:
            Restoration result
        """
        self.logger.info(f"Manually restoring checkpoint: {checkpoint_id}")
        result = self.manager.load_checkpoint(checkpoint_id=checkpoint_id)
        
        if result["success"]:
            self.logger.info(f"✓ Checkpoint restored: {checkpoint_id}")
        else:
            self.logger.error(f"✗ Failed to restore: {result.get('error')}")
        
        return result


# Example usage in main Friday 2.0 runtime
def example_runtime_integration():
    """Example of how to integrate with Friday 2.0 main loop."""
    
    integration = CheckpointIntegration()
    
    # Session startup
    print("=== SESSION START ===")
    load_result = integration.on_session_start()
    print(f"Load result: {load_result}")
    
    # ... runtime operations ...
    print("\n=== RUNTIME OPERATIONS ===")
    print("(session running...)")
    
    # Session cleanup
    print("\n=== SESSION END ===")
    checkpoint_path = integration.on_session_end(
        context={
            "tokens_used": 85000,
            "duration_seconds": 1200,
            "completion_status": "successful"
        }
    )
    print(f"Checkpoint saved to: {checkpoint_path}")
    
    # Status report
    print("\n=== CHECKPOINT STATUS ===")
    status = integration.get_status()
    for key, value in status.items():
        print(f"{key}: {value}")
    
    # Hourly maintenance
    print("\n=== HOURLY MAINTENANCE ===")
    prune_result = integration.on_hourly_maintenance()
    print(f"Pruning result: {prune_result}")


if __name__ == "__main__":
    example_runtime_integration()
