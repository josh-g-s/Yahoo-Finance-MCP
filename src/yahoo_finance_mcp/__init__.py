import asyncio
from .server import main


def run():
    """Entry point for the yahoo-finance-mcp command."""
    asyncio.run(main())


# For backwards compatibility
__all__ = ["main", "run"]
