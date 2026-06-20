#!/usr/bin/env python3
"""
Comprehensive integration test for CheckpointManager.

Tests all methods including:
- capture_checkpoint() — saves Memory state
- load_checkpoint() — restores Memory state
- list_checkpoints() — enumerates recent checkpoints
- prune_old_checkpoints() — removes old checkpoints
- Full capture/load cycle validation
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from checkpoint_manager import CheckpointManager, CHECKPOINT_DIR, MEMORY_FILE

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}  {text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    """Print info message."""
    print(f"{Colors.YELLOW}→ {text}{Colors.RESET}")

def cleanup_test_environment():
    """Clean up checkpoints from previous test runs."""
    if CHECKPOINT_DIR.exists():
        import shutil
        shutil.rmtree(CHECKPOINT_DIR)
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()
    print_info("Test environment cleaned up")

def test_initialization():
    """Test 1: Manager initialization and directory creation."""
    print_header("TEST 1: CheckpointManager Initialization")
    
    manager = CheckpointManager()
    
    # Check that directory was created
    assert CHECKPOINT_DIR.exists(), "Checkpoint directory not created"
    print_success(f"Checkpoint directory created: {CHECKPOINT_DIR}")
    
    # Check that index was created/loaded
    assert manager.index is not None, "Index not loaded"
    assert "checkpoints" in manager.index, "Index missing 'checkpoints' key"
    assert "version" in manager.index, "Index missing 'version' key"
    print_success(f"Index initialized with version {manager.index['version']}")
    
    return manager

def test_capture_checkpoint(manager):
    """Test 2: Capture checkpoint functionality."""
    print_header("TEST 2: Capture Checkpoint")
    
    # Create a test memory file
    test_memory = """# Memory State Test
    
## Active Tasks
- Task 1: Integration testing
- Task 2: Checkpoint verification

## Team Contacts
- Alice: alice@example.com
- Bob: bob@example.com

## Projects
- Friday 2.0: In progress
- EDITH Vault: Completed
"""
    
    with open(MEMORY_FILE, 'w') as f:
        f.write(test_memory)
    
    print_info(f"Test memory file created: {len(test_memory)} bytes")
    
    # Capture checkpoint
    session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    checkpoint_path = manager.capture_checkpoint(
        session_id=session_id,
        context={
            "tokens_used": 50000,
            "duration_seconds": 1800,
            "test": True
        }
    )
    
    assert Path(checkpoint_path).exists(), "Checkpoint file not created"
    print_success(f"Checkpoint captured: {Path(checkpoint_path).name}")
    
    # Verify checkpoint file structure
    with open(checkpoint_path) as f:
        checkpoint_data = json.load(f)
    
    assert checkpoint_data["session_id"] == session_id, "Session ID mismatch"
    assert "captured_at" in checkpoint_data, "Missing captured_at"
    assert checkpoint_data["memory_snapshot"] == test_memory, "Memory snapshot mismatch"
    assert "metadata" in checkpoint_data, "Missing metadata"
    assert checkpoint_data["metadata"]["memory_size_bytes"] == len(test_memory.encode()), \
        "Memory size mismatch"
    
    print_success(f"Checkpoint structure verified (session: {session_id})")
    print_success(f"  - Memory size: {checkpoint_data['metadata']['memory_size_bytes']} bytes")
    print_success(f"  - Memory lines: {checkpoint_data['metadata']['memory_lines']}")
    print_success(f"  - Captured at: {checkpoint_data['captured_at']}")
    
    return checkpoint_path, test_memory

def test_index_update(manager, checkpoint_path):
    """Test 3: Index update after capture."""
    print_header("TEST 3: Index Update Verification")
    
    # Reload index to verify persistence
    manager2 = CheckpointManager()
    assert len(manager2.index["checkpoints"]) > 0, "Checkpoint not in index"
    
    latest_checkpoint = manager2.index["checkpoints"][-1]
    print_success(f"Latest checkpoint in index: {latest_checkpoint['filename']}")
    print_success(f"  - Session ID: {latest_checkpoint['session_id']}")
    print_success(f"  - Timestamp: {latest_checkpoint['timestamp']}")
    print_success(f"  - Size: {latest_checkpoint['size_bytes']} bytes")

def test_load_checkpoint(manager, original_memory):
    """Test 4: Load checkpoint functionality."""
    print_header("TEST 4: Load Checkpoint")
    
    # Modify memory file (simulate session changes)
    new_memory = """# Modified Memory
This should be overwritten when loading checkpoint.
"""
    
    with open(MEMORY_FILE, 'w') as f:
        f.write(new_memory)
    
    print_info("Memory file modified to test restoration")
    
    # Load the most recent checkpoint
    result = manager.load_checkpoint()
    
    assert result["success"], f"Load failed: {result.get('error')}"
    print_success(f"Checkpoint loaded successfully")
    print_success(f"  - Checkpoint: {result['checkpoint']}")
    print_success(f"  - Restored bytes: {result['restored_bytes']}")
    print_success(f"  - Session ID: {result['session_id']}")
    print_success(f"  - Captured at: {result['captured_at']}")
    
    # Verify memory was restored
    with open(MEMORY_FILE) as f:
        restored_memory = f.read()
    
    assert restored_memory == original_memory, "Memory not restored correctly"
    print_success("Memory restored to original checkpoint state")

def test_load_specific_checkpoint(manager):
    """Test 5: Load specific checkpoint by ID."""
    print_header("TEST 5: Load Specific Checkpoint")
    
    # Create another checkpoint with different content
    test_memory2 = "# Second Checkpoint Test\nDifferent content"
    with open(MEMORY_FILE, 'w') as f:
        f.write(test_memory2)
    
    session_id2 = f"test_session_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    checkpoint_path2 = manager.capture_checkpoint(session_id=session_id2)
    checkpoint_filename2 = Path(checkpoint_path2).name
    
    print_info(f"Second checkpoint created: {checkpoint_filename2}")
    
    # Get all checkpoint filenames and their stored content
    checkpoints_info = []
    for cp_meta in manager.index["checkpoints"]:
        cp_path = CHECKPOINT_DIR / cp_meta["filename"]
        with open(cp_path) as f:
            cp_data = json.load(f)
        checkpoints_info.append((cp_meta["filename"], cp_data["memory_snapshot"]))
    
    # Load first checkpoint
    first_checkpoint = manager.index["checkpoints"][0]["filename"]
    expected_content = checkpoints_info[0][1]
    
    result = manager.load_checkpoint(checkpoint_id=first_checkpoint)
    assert result["success"], "Failed to load specific checkpoint"
    assert result["checkpoint"] == first_checkpoint, "Wrong checkpoint loaded"
    
    print_success(f"Specific checkpoint loaded: {first_checkpoint}")
    
    # Verify memory content
    with open(MEMORY_FILE) as f:
        content = f.read()
    
    assert content == expected_content, "Memory not restored to first checkpoint"
    print_success("Memory correctly restored to first checkpoint")

def test_list_checkpoints(manager):
    """Test 6: List checkpoints functionality."""
    print_header("TEST 6: List Checkpoints")
    
    checkpoints = manager.list_checkpoints(limit=10)
    
    assert isinstance(checkpoints, list), "list_checkpoints returned non-list"
    assert len(checkpoints) > 0, "No checkpoints in list"
    
    print_success(f"Retrieved {len(checkpoints)} checkpoint(s)")
    
    for i, cp in enumerate(checkpoints, 1):
        print_info(f"  Checkpoint {i}: {cp['filename']}")
        print_info(f"    - Session: {cp['session_id']}")
        print_info(f"    - Size: {cp['size_bytes']} bytes")
        print_info(f"    - Time: {cp['timestamp']}")

def test_prune_old_checkpoints(manager):
    """Test 7: Prune old checkpoints."""
    print_header("TEST 7: Prune Old Checkpoints")
    
    # Create checkpoints with old timestamps for testing
    print_info("Simulating old checkpoints for pruning test...")
    
    initial_count = len(manager.index["checkpoints"])
    
    # Manually add an old checkpoint entry (without file) to test prune logic
    old_timestamp = (datetime.now() - timedelta(days=31)).isoformat()
    manager.index["checkpoints"].insert(0, {
        "filename": "checkpoint_old_20260511_000000_oldtest00.json",
        "session_id": "old_session",
        "timestamp": old_timestamp,
        "size_bytes": 1000
    })
    manager._save_index()
    
    print_info(f"Added simulated old checkpoint (date: {old_timestamp})")
    
    # Prune checkpoints older than 30 days
    result = manager.prune_old_checkpoints(keep_days=30)
    
    print_success(f"Pruning completed")
    print_success(f"  - Deleted: {result['deleted']} checkpoint(s)")
    print_success(f"  - Freed: {result['freed_bytes']} bytes")
    print_success(f"  - Remaining: {result['remaining']} checkpoint(s)")
    print_success(f"  - Retention period: {result['retention_days']} days")

def test_error_handling(manager):
    """Test 8: Error handling for edge cases."""
    print_header("TEST 8: Error Handling")
    
    # Test load with no checkpoints
    manager_empty = CheckpointManager()
    manager_empty.index["checkpoints"] = []
    manager_empty._save_index()
    
    result = manager_empty.load_checkpoint()
    assert not result["success"], "Should fail with no checkpoints"
    assert "error" in result, "Error message missing"
    print_success("Correctly handles load with no checkpoints")
    
    # Test load with non-existent checkpoint
    result = manager.load_checkpoint(checkpoint_id="non_existent_file.json")
    assert not result["success"], "Should fail with non-existent checkpoint"
    print_success("Correctly handles non-existent checkpoint")

def test_full_cycle(manager):
    """Test 9: Full capture/load cycle with data integrity."""
    print_header("TEST 9: Full Capture/Load Cycle")
    
    # Step 1: Create diverse memory content
    original_content = """# Comprehensive Memory Snapshot
## Project Status
- Friday 2.0: 85% complete
- EDITH Integration: 100% complete
- Session Checkpointing: 90% complete

## Team Information
Name: Alice Johnson
Email: alice@friday.ai
Role: Lead Architect
Last Contact: 2026-06-11

## API Keys (Encrypted)
- OpenAI: encrypted_key_1234567890
- GitHub: encrypted_key_0987654321

## Notes
- Checkpoint system integration in progress
- All methods tested and functional
- Ready for production deployment

## Statistics
- Total lines: 25
- Total tokens used this session: 120000
- Session duration: 45 minutes
- Memory size: 650 bytes
"""
    
    with open(MEMORY_FILE, 'w') as f:
        f.write(original_content)
    
    print_info("Created comprehensive test memory")
    
    # Step 2: Capture checkpoint
    session_id = f"full_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    checkpoint_path = manager.capture_checkpoint(
        session_id=session_id,
        context={
            "test_type": "full_cycle",
            "content_bytes": len(original_content.encode()),
            "integrity_check": "enabled"
        }
    )
    
    print_success(f"Step 1: Checkpoint captured")
    
    # Step 3: Verify checkpoint contains exact data
    with open(checkpoint_path) as f:
        checkpoint_data = json.load(f)
    
    assert checkpoint_data["memory_snapshot"] == original_content, \
        "Captured data doesn't match original"
    print_success(f"Step 2: Captured data verified (integrity check passed)")
    
    # Step 4: Corrupt the memory file
    corrupted_content = "# CORRUPTED\nThis data should be replaced"
    with open(MEMORY_FILE, 'w') as f:
        f.write(corrupted_content)
    
    print_info("Step 3: Memory file corrupted for test")
    
    # Step 5: Load checkpoint and verify restoration
    result = manager.load_checkpoint(checkpoint_id=Path(checkpoint_path).name)
    assert result["success"], "Load failed"
    
    with open(MEMORY_FILE) as f:
        restored_content = f.read()
    
    assert restored_content == original_content, "Restoration failed"
    print_success(f"Step 4: Checkpoint loaded and memory restored")
    print_success(f"Step 5: Data integrity verified (100% match)")

def run_all_tests():
    """Run all integration tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔" + "="*68 + "╗")
    print("║  CHECKPOINT MANAGER INTEGRATION TEST SUITE                      ║")
    print("║  Friday 2.0 Runtime Integration Verification                    ║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.RESET}")
    
    try:
        # Clean environment
        cleanup_test_environment()
        
        # Run all tests
        manager = test_initialization()
        checkpoint_path, test_memory = test_capture_checkpoint(manager)
        test_index_update(manager, checkpoint_path)
        test_load_checkpoint(manager, test_memory)
        
        # Reload manager for subsequent tests
        manager = CheckpointManager()
        
        test_load_specific_checkpoint(manager)
        test_list_checkpoints(manager)
        test_prune_old_checkpoints(manager)
        test_error_handling(manager)
        
        # Reload manager for full cycle
        manager = CheckpointManager()
        test_full_cycle(manager)
        
        # Final summary
        print_header("TEST SUMMARY")
        print_success("All 9 test groups passed successfully!")
        print_success(f"Checkpoint directory: {CHECKPOINT_DIR}")
        print_success(f"Memory file: {MEMORY_FILE}")
        print_success(f"Total checkpoints: {len(manager.list_checkpoints(limit=100))}")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}╔" + "="*68 + "╗")
        print("║  INTEGRATION SUCCESSFUL - READY FOR PRODUCTION             ║")
        print("╚" + "="*68 + "╝")
        print(f"{Colors.RESET}\n")
        
        return 0
        
    except AssertionError as e:
        print_header("TEST FAILURE")
        print_error(f"Assertion failed: {str(e)}")
        return 1
    except Exception as e:
        print_header("TEST ERROR")
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
