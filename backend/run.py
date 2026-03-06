"""Use this to start the server on Windows instead of running uvicorn directly.
Sets WindowsProactorEventLoopPolicy before uvicorn creates its event loop,
which is required for Playwright to spawn subprocess processes.
"""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
