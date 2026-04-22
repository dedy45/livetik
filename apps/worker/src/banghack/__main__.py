"""Module entry for `python -m banghack`."""
from .main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
