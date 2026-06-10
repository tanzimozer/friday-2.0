#!/usr/bin/env python3
"""
OPT-5: Parallel Execution Engine for Friday 2.0
Runs independent operations concurrently to reduce overall latency.
"""

import time
from typing import Tuple, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError


class ParallelExecutor:
    """Execute independent operations concurrently with fallback to sequential."""
    
    def __init__(self, timeout_seconds: int = 3, max_workers: int = 2):
        """
        Initialize parallel executor.
        
        Args:
            timeout_seconds: Max time to wait for concurrent operations
            max_workers: Number of worker threads (default 2 for typical use)
        """
        self.timeout = timeout_seconds
        self.max_workers = max_workers
        self.metrics = {
            'parallel_attempts': 0,
            'parallel_successes': 0,
            'sequential_fallbacks': 0,
            'total_concurrent_ms': 0,
            'total_sequential_ms': 0
        }
    
    def execute_parallel(
        self,
        operation_1: Callable,
        operation_2: Callable,
        op1_name: str = "Operation 1",
        op2_name: str = "Operation 2"
    ) -> Tuple[Any, Any, bool]:
        """
        Execute two independent operations concurrently.
        Falls back to sequential if parallelization fails.
        
        Args:
            operation_1: First operation (callable, no args)
            operation_2: Second operation (callable, no args)
            op1_name: Name for logging
            op2_name: Name for logging
        
        Returns:
            (result_1, result_2, was_parallel: bool)
        """
        self.metrics['parallel_attempts'] += 1
        
        try:
            # Try parallel execution
            start = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_1 = executor.submit(operation_1)
                future_2 = executor.submit(operation_2)
                
                # Wait for both with timeout
                result_1 = future_1.result(timeout=self.timeout)
                result_2 = future_2.result(timeout=self.timeout)
            
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.metrics['parallel_successes'] += 1
            self.metrics['total_concurrent_ms'] += elapsed_ms
            
            return result_1, result_2, True
        
        except (FuturesTimeoutError, Exception) as e:
            # Fall back to sequential
            self.metrics['sequential_fallbacks'] += 1
            
            start = time.perf_counter()
            result_1 = operation_1()
            result_2 = operation_2()
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.metrics['total_sequential_ms'] += elapsed_ms
            
            return result_1, result_2, False
    
    def get_metrics(self) -> dict:
        """Return performance metrics from parallelization."""
        success_rate = 0
        if self.metrics['parallel_attempts'] > 0:
            success_rate = round(
                self.metrics['parallel_successes'] / self.metrics['parallel_attempts'] * 100, 1
            )
        
        return {
            'parallel_success_rate': f"{success_rate}%",
            'parallel_attempts': self.metrics['parallel_attempts'],
            'sequential_fallbacks': self.metrics['sequential_fallbacks'],
            'avg_concurrent_ms': round(
                self.metrics['total_concurrent_ms'] / max(1, self.metrics['parallel_successes']), 2
            ) if self.metrics['parallel_successes'] > 0 else 0,
            'avg_sequential_ms': round(
                self.metrics['total_sequential_ms'] / max(1, self.metrics['sequential_fallbacks']), 2
            ) if self.metrics['sequential_fallbacks'] > 0 else 0
        }


# Global executor instance
_executor = ParallelExecutor(timeout_seconds=3, max_workers=2)


def parallel_verify_and_check_personality(
    vault,
    auth_service: str,
    personality_input: str
) -> Tuple[dict, dict, bool]:
    """
    Parallel: Authenticate (vault credential) and check personality simultaneously.
    
    Args:
        vault: EDITHVault instance
        auth_service: Service to authenticate (e.g., 'google')
        personality_input: Text to analyze for personality traits
    
    Returns:
        (credential_dict, personality_dict, was_parallel: bool)
    
    Example:
        cred, personality, parallel = parallel_verify_and_check_personality(
            vault, 'google', "The render is complete. Ostentatious, as intended."
        )
        if parallel:
            print("✓ Parallel execution (faster)")
        else:
            print("⚠ Sequential fallback")
    """
    from jarvis import JARVIS
    
    def get_cred():
        return vault.get_credential(auth_service, verify=False)
    
    def check_personality():
        jarvis = JARVIS()
        return jarvis.check_personality(personality_input)
    
    cred, personality, was_parallel = _executor.execute_parallel(
        get_cred,
        check_personality,
        op1_name=f"Vault.get_credential({auth_service})",
        op2_name="JARVIS.check_personality"
    )
    
    return cred, personality, was_parallel


def get_parallel_metrics() -> dict:
    """Get performance metrics from parallelization."""
    return _executor.get_metrics()


if __name__ == "__main__":
    # Test harness
    print("═══════════════════════════════════════════════════════════════")
    print("OPT-5: Parallel Executor — Test Harness")
    print("═══════════════════════════════════════════════════════════════\n")
    
    executor = ParallelExecutor(timeout_seconds=2, max_workers=2)
    
    # Simulate two operations
    def op1():
        time.sleep(0.05)  # 50ms
        return "credential_token_abc123"
    
    def op2():
        time.sleep(0.03)  # 30ms
        return {"traits": ["deadpan", "anticipatory"], "score": 72}
    
    print("Test: Running 2 ops concurrently")
    print("  Op1: 50ms (vault credential)")
    print("  Op2: 30ms (personality check)")
    print("  Expected: ~50ms (concurrent) vs ~80ms (sequential)\n")
    
    result1, result2, was_parallel = executor.execute_parallel(op1, op2)
    
    print(f"Results: {result1}, {result2}")
    print(f"Parallel: {was_parallel}")
    print(f"\nMetrics: {executor.get_metrics()}")
    print("\n✓ OPT-5 Parallel Executor Ready")
