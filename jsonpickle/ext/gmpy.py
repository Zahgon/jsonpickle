try:
    import gmpy2 as gmpy  # type: ignore[import-untyped]
except ImportError:
    gmpy = None

from typing import Any, Dict

from ..handlers import BaseHandler, HandlerReturn, register, unregister

__all__ = ["register_handlers", "unregister_handlers"]


class GmpyMPZHandler(BaseHandler):
    def flatten(self, obj: gmpy.mpz, data: Dict[str, Any]) -> HandlerReturn:
        pass

    def restore(self, data: Dict[str, Any]) -> gmpy.mpz:
        pass


def register_handlers() -> None:
    pass


def unregister_handlers() -> None:
    pass
