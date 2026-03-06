"""Ensures WindowsProactorEventLoopPolicy is active in the current thread on Windows.

sync_playwright creates its own event loop internally via asyncio.new_event_loop().
That call uses the current policy to decide which loop type to create.
Setting WindowsProactorEventLoopPolicy before sync_playwright starts ensures it
gets a ProactorEventLoop, which supports subprocess creation on Windows.
"""
import sys


def ensure_proactor_loop() -> None:
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
