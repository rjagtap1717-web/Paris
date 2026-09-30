import os
import time
from pathlib import Path

LOCK_DIR = Path(__file__).resolve().parent.parent / "memory" / "locks"

def acquire_lock(resource_name: str, timeout: int = 10) -> bool:
    """Acquires a cross-process lock for a specific resource (e.g. 'excel', 'browser')."""
    if not LOCK_DIR.exists():
        LOCK_DIR.mkdir(parents=True, exist_ok=True)
        
    lock_file = LOCK_DIR / f"{resource_name}.lock"
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            # os.O_CREAT | os.O_EXCL ensures atomic creation. It fails if the file already exists.
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(0.5)
            
    return False
    
def release_lock(resource_name: str):
    """Releases the cross-process lock."""
    lock_file = LOCK_DIR / f"{resource_name}.lock"
    try:
        lock_file.unlink(missing_ok=True)
    except Exception:
        pass
