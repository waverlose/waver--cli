"""Waver CLI - 直接入口"""

from waver.main import app

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        sys.argv.append("chat")
    app()
