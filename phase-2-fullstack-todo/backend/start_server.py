#!/usr/bin/env python3
"""Simple server starter script to bypass uvicorn reload issues."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
