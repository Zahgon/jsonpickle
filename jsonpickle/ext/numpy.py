from __future__ import annotations

import ast
import json
import sys
import warnings
import zlib
from types import ModuleType
from typing import Any, NoReturn, cast

import numpy as np

# do the annotations import so python doesn't complain about numpy type hints missing if numpy isn't installed


_np_version: tuple[int, ...] = tuple(int(x) for x in np.__version__.split(".")[:3])
# numpy.typing was introduced in 1.20.0
if _np_version >= (1, 20, 0):
    from numpy.typing import ArrayLike, DTypeLike, NDArray
else:
    NDArray = Any  # type: ignore[assignment,misc]
    ArrayLike = Any  # type: ignore[assignment,misc]
    DTypeLike = Any  # type: ignore[assignment,misc]


from ..handlers import BaseHandler, register, unregister
from ..util import b64decode, b64encode, importable_name, loadclass

__all__ = ["register_handlers", "unregister_handlers"]

native_byteorder: str = "<" if sys.byteorder == "little" else ">"


# considered typing arr as ArrayLike but then we get a mypy error with no attribute dtype
def get_byteorder(arr: ArrayLike) -> str:
    """translate equals sign to native order"""
    pass


class NumpyBaseHandler(BaseHandler):
    def flatten_dtype(self, dtype: DTypeLike, data: dict[str, Any]) -> None:
        pass

    def restore_dtype(self, data: dict[str, Any]) -> np.dtype:  # type: ignore[type-arg]
        pass


class NumpyDTypeHandler(NumpyBaseHandler):
    def flatten(self, obj: DTypeLike, data: dict[str, Any]) -> dict[str, Any]:
        pass

    def restore(self, data: dict[str, Any]) -> DTypeLike:
        pass


class NumpyGenericHandler(NumpyBaseHandler):
    def flatten(self, obj: NDArray[Any], data: dict[str, Any]) -> dict[str, Any]:
        pass

    def restore(self, data: dict[str, Any]) -> dict[str, Any]:
        pass


class NumpyDatetimeHandler(NumpyGenericHandler):
    """Extend NumpyGenericHandler to handle nanosecond-resolution datetime64"""

    def restore(self, data: dict[str, Any]) -> dict[str, Any]:
        pass


class UnpickleableNumpyGenericHandler(NumpyGenericHandler):
    """
    From issue #381, this is used for simplifying the output of numpy arrays
    when unpicklable=False (the default is True).
    """

    # TODO: narrow return value down from Any
    def flatten(self, obj: NDArray[Any], data: dict[str, Any]) -> Any:
        pass

    def restore(self, data: dict[str, Any]) -> NoReturn:
        raise NotImplementedError


class NumpyNDArrayHandler(NumpyBaseHandler):
    """Stores arrays as text representation, without regard for views"""

    def flatten_flags(self, obj: NDArray[Any], data: dict[str, Any]) -> None:
        pass

    def restore_flags(self, data: dict[str, Any], arr: NDArray[Any]) -> None:
        pass

    def flatten(self, obj: NDArray[Any], data: dict[str, Any]) -> dict[str, Any]:
        pass

    def restore(self, data: dict[str, Any]) -> NDArray[Any]:
        pass


class NumpyNDArrayHandlerBinary(NumpyNDArrayHandler):
    """stores arrays with size greater than 'size_threshold' as
    (optionally) compressed base64

    Notes
    -----
    This would be easier to implement using np.save/np.load, but
    that would be less language-agnostic
    """

    def __init__(
        self, size_threshold: int = 16, compression: ModuleType = zlib
    ) -> None:
        """
        :param size_threshold: nonnegative int or None
            valid values for 'size_threshold' are all nonnegative
            integers and None
            if size_threshold is None, values are always stored as nested lists
        :param compression: a compression module or None
            valid values for 'compression' are {zlib, bz2, None}
            if compression is None, no compression is applied
        """
        self.size_threshold = size_threshold
        self.compression = compression

    def flatten_byteorder(self, obj: NDArray[Any], data: dict[str, Any]) -> None:
        pass

    def restore_byteorder(self, data: dict[str, Any], arr: NDArray[Any]) -> None:
        pass

    def flatten(self, obj: NDArray[Any], data: dict[str, Any]) -> dict[str, Any]:
        """encode numpy to json"""
        pass

    def restore(self, data: dict[str, Any]) -> NDArray[Any]:
        """decode numpy from json"""
        pass


class NumpyNDArrayHandlerView(NumpyNDArrayHandlerBinary):
    """Pickles references inside ndarrays, or array-views

    Notes
    -----
    The current implementation has some restrictions.

    'base' arrays, or arrays which are viewed by other arrays,
    must be f-or-c-contiguous.
    This is not such a large restriction in practice, because all
    numpy array creation is c-contiguous by default.
    Relaxing this restriction would be nice though; especially if
    it can be done without bloating the design too much.

    Furthermore, ndarrays which are views of array-like objects
    implementing __array_interface__,
    but which are not themselves nd-arrays, are deepcopied with
    a warning (by default),
    as we cannot guarantee whatever custom logic such classes
    implement is correctly reproduced.
    """

    def __init__(
        self,
        mode: str = "warn",
        size_threshold: int = 16,
        compression: ModuleType = zlib,
    ) -> None:
        """
        :param mode: {'warn', 'raise', 'ignore'}
            How to react when encountering array-like objects whose
            references we cannot safely serialize
        :param size_threshold: nonnegative int or None
            valid values for 'size_threshold' are all nonnegative
            integers and None
            if size_threshold is None, values are always stored as nested lists
        :param compression: a compression module or None
            valid values for 'compression' are {zlib, bz2, None}
            if compression is None, no compression is applied
        """
        super().__init__(size_threshold, compression)
        self.mode = mode

    def flatten(self, obj: NDArray[Any], data: dict[str, Any]) -> dict[str, Any]:
        """encode numpy to json"""
        pass

    def restore(self, data: dict[str, Any]) -> NDArray[Any]:
        """decode numpy from json"""
        pass


class NumpyUfuncHandler(BaseHandler):
    def flatten(self, obj: np.ufunc, data: dict[str, Any]) -> dict[str, Any]:
        pass

    def restore(self, obj: dict[str, Any]) -> np.ufunc:
        # it seems proper practice to make mypy happy that it can't return None here
        # is to use the cast
        pass


def register_handlers(
    ndarray_mode: str = "warn",
    ndarray_size_threshold: int = 16,
    ndarray_compression: ModuleType = zlib,
) -> None:
    """Register handlers for numpy types

    :param ndarray_abc_xyz: Forward constructor arguments to NumpyNDArrayHandlerView.
        Options with an 'ndarray_' prefix correspond to the same-named
        NumpyNDArrayHandlerView constructor options, sans the 'ndarray_' prefix.
    """
    pass


def unregister_handlers() -> None:
    """Remove numpy handlers from the handler registry"""
    pass
