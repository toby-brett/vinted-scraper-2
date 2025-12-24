import asyncio
import sys

def debug_loop():
    try:
        loop = asyncio.get_running_loop()
        print(f"--- ACTIVE LOOP DETECTED ---")
        print(f"Loop: {loop}")
        # This will show you the stack trace of what started the loop
        import traceback
        traceback.print_stack()
    except RuntimeError:
        print("--- No active asyncio loop detected ---")

debug_loop()