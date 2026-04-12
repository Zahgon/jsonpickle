# Copyright (C) 2008 John Paulett (john -at- paulett.org)
# Copyright (C) 2009-2024 David Aguilar (davvid -at- gmail.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
import decimal
import inspect
import itertools
import sys
import types
import warnings
from itertools import chain, islice
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Type, Union

from . import handlers, tags, util
from .backend import JSONBackend, json


def encode(
    value: Any,
    unpicklable: bool = True,
    make_refs: bool = True,
    keys: bool = False,
    max_depth: Optional[int] = None,
    reset: bool = True,
    backend: Optional[JSONBackend] = None,
    warn: bool = False,
    context: Optional["Pickler"] = None,
    max_iter: Optional[int] = None,
    use_decimal: bool = False,
    numeric_keys: bool = False,
    use_base85: bool = False,
    fail_safe: Optional[Callable[[Exception], Any]] = None,
    indent: Optional[int] = None,
    separators: Optional[Any] = None,
    include_properties: bool = False,
    handle_readonly: bool = False,
    handler_context: Any = None,
) -> str:
    """Return a JSON formatted representation of value, a Python object.

    :param unpicklable: If set to ``False`` then the output will not contain the
        information necessary to turn the JSON data back into Python objects,
        but a simpler JSON stream is produced. It's recommended to set this
        parameter to ``False`` when your code does not rely on two objects
        having the same ``id()`` value, and when it is sufficient for those two
        objects to be equal by ``==``, such as when serializing sklearn
        instances. If you experience (de)serialization being incorrect when you
        use numpy, pandas, or sklearn handlers, this should be set to ``False``.
        If you want the output to not include the dtype for numpy arrays, add::

            jsonpickle.register(
                numpy.generic, UnpicklableNumpyGenericHandler, base=True
            )

        before your pickling code.
    :param make_refs: If set to False jsonpickle's referencing support is
        disabled.  Objects that are id()-identical won't be preserved across
        encode()/decode(), but the resulting JSON stream will be conceptually
        simpler.  jsonpickle detects cyclical objects and will break the cycle
        by calling repr() instead of recursing when make_refs is set False.
    :param keys: If set to True then jsonpickle will encode non-string
        dictionary keys instead of coercing them into strings via `repr()`.
        This is typically what you want if you need to support Integer or
        objects as dictionary keys.
    :param max_depth: If set to a non-negative integer then jsonpickle will
        not recurse deeper than 'max_depth' steps into the object.  Anything
        deeper than 'max_depth' is represented using a Python repr() of the
        object.
    :param reset: Custom pickle handlers that use the `Pickler.flatten` method or
        `jsonpickle.encode` function must call `encode` with `reset=False`
        in order to retain object references during pickling.
        This flag is not typically used outside of a custom handler or
        `__getstate__` implementation.
    :param backend: If set to an instance of jsonpickle.backend.JSONBackend,
        jsonpickle will use that backend for deserialization.
    :param warn: If set to True then jsonpickle will warn when it
        returns None for an object which it cannot pickle
        (e.g. file descriptors).
    :param context: Supply a pre-built Pickler or Unpickler object to the
        `jsonpickle.encode` and `jsonpickle.decode` machinery instead
        of creating a new instance. The `context` represents the currently
        active Pickler and Unpickler objects when custom handlers are
        invoked by jsonpickle.
    :param max_iter: If set to a non-negative integer then jsonpickle will
        consume at most `max_iter` items when pickling iterators.
    :param use_decimal: If set to True jsonpickle will allow Decimal
        instances to pass-through, with the assumption that the simplejson
        backend will be used in `use_decimal` mode.  In order to use this mode
        you will need to configure simplejson::

            jsonpickle.set_encoder_options('simplejson',
                                           use_decimal=True, sort_keys=True)
            jsonpickle.set_decoder_options('simplejson',
                                           use_decimal=True)
            jsonpickle.set_preferred_backend('simplejson')

        NOTE: A side-effect of the above settings is that float values will be
        converted to Decimal when converting to json.
    :param numeric_keys: Only use this option if the backend supports integer
        dict keys natively.  This flag tells jsonpickle to leave numeric keys
        as-is rather than conforming them to json-friendly strings.
        Using ``keys=True`` is the typical solution for integer keys, so only
        use this if you have a specific use case where you want to allow the
        backend to handle serialization of numeric dict keys.
    :param use_base85:
        If possible, use base85 to encode binary data. Base85 bloats binary data
        by 1/4 as opposed to base64, which expands it by 1/3. This argument is
        ignored on Python 2 because it doesn't support it.
    :param fail_safe: If set to a function exceptions are ignored when pickling
        and if a exception happens the function is called and the return value
        is used as the value for the object that caused the error
    :param indent: When `indent` is a non-negative integer, then JSON array
        elements and object members will be pretty-printed with that indent
        level.  An indent level of 0 will only insert newlines. ``None`` is
        the most compact representation.  Since the default item separator is
        ``(', ', ': ')``,  the output might include trailing whitespace when
        ``indent`` is specified.  You can use ``separators=(',', ': ')`` to
        avoid this.  This value is passed directly to the active JSON backend
        library and not used by jsonpickle directly.
    :param separators:
        If ``separators`` is an ``(item_separator, dict_separator)`` tuple
        then it will be used instead of the default ``(', ', ': ')``
        separators.  ``(',', ':')`` is the most compact JSON representation.
        This value is passed directly to the active JSON backend library and
        not used by jsonpickle directly.
    :param include_properties:
        Include the names and values of class properties in the generated json.
        Properties are unpickled properly regardless of this setting, this is
        meant to be used if processing the json outside of Python. Certain types
        such as sets will not pickle due to not having a native-json equivalent.
        Defaults to ``False``.
    :param handle_readonly:
        Handle objects with readonly methods, such as Django's SafeString. This
        basically prevents jsonpickle from raising an exception for such objects.
        You MUST set ``handle_readonly=True`` for the decoding if you encode with
        this flag set to ``True``.
    :param handler_context:
        Pass custom context to a custom handler. This can be used to customize
        behavior at runtime based off data. Defaults to ``None``. An example can
        be found in the examples/ directory on GitHub.

    >>> encode('my string') == '"my string"'
    True
    >>> encode(36) == '36'
    True
    >>> encode({'foo': True}) == '{"foo": true}'
    True
    >>> encode({'foo': [1, 2, [3, 4]]}, max_depth=1)
    '{"foo": "[1, 2, [3, 4]]"}'

    """
    pass


def _in_cycle(
    obj: Any, objs: Dict[int, int], max_reached: bool, make_refs: bool
) -> bool:
    """Detect cyclic structures that would lead to infinite recursion"""
    pass


def _mktyperef(obj: Type[Any]) -> Dict[str, str]:
    """Return a typeref dictionary

    >>> _mktyperef(AssertionError) == {'py/type': 'builtins.AssertionError'}
    True

    """
    pass


def _wrap_string_slot(string: Union[str, Sequence[str]]) -> Sequence[str]:
    """Converts __slots__ = 'a' into __slots__ = ('a',)"""
    pass


class Pickler:
    def __init__(
        self,
        unpicklable: bool = True,
        make_refs: bool = True,
        max_depth: Optional[int] = None,
        backend: Optional[JSONBackend] = None,
        keys: bool = False,
        warn: bool = False,
        max_iter: Optional[int] = None,
        numeric_keys: bool = False,
        use_decimal: bool = False,
        use_base85: bool = False,
        fail_safe: Optional[Callable[[Exception], Any]] = None,
        include_properties: bool = False,
        handle_readonly: bool = False,
        original_object: Optional[Any] = None,
        handler_context: Any = None,
    ) -> None:
        self.unpicklable = unpicklable
        self.make_refs = make_refs
        self.backend = backend or json
        self.keys = keys
        self.warn = warn
        self.numeric_keys = numeric_keys
        self.use_base85 = use_base85
        # The current recursion depth
        self._depth = -1
        # The maximal recursion depth
        self._max_depth = max_depth
        # Maps id(obj) to reference IDs
        self._objs = {}
        # Avoids garbage collection
        self._seen = []
        # maximum amount of items to take from a pickled iterator
        self._max_iter = max_iter
        # Whether to allow decimals to pass-through
        self._use_decimal = use_decimal
        # A cache of objects that have already been flattened.
        self._flattened = {}
        # Used for util._is_readonly, see +483
        self.handle_readonly = handle_readonly
        # Custom context passed through to custom handlers, see #452
        self.handler_context = handler_context

        if self.use_base85:
            self._bytes_tag = tags.B85
            self._bytes_encoder = util.b85encode
        else:
            self._bytes_tag = tags.B64
            self._bytes_encoder = util.b64encode

        # ignore exceptions
        self.fail_safe = fail_safe
        self.include_properties = include_properties

        self._original_object = original_object

    def _determine_sort_keys(self) -> bool:
        pass

    def _sort_attrs(self, obj: Any) -> Any:
        pass

    def reset(self) -> None:
        pass

    def _push(self) -> None:
        """Steps down one level in the namespace."""
        pass

    def _pop(self, value: Any) -> Any:
        """Step up one level in the namespace and return the value.
        If we're at the root, reset the pickler's state.
        """
        pass

    def _log_ref(self, obj: Any) -> bool:
        """
        Log a reference to an in-memory object.
        Return True if this object is new and was assigned
        a new ID. Otherwise return False.
        """
        pass

    def _mkref(self, obj: Any) -> bool:
        """
        Log a reference to an in-memory object, and return
        if that object should be considered newly logged.
        """
        pass

    def _getref(self, obj: Any) -> Dict[str, int]:
        """Return a "py/id" entry for the specified object"""
        pass

    def _flatten(self, obj: Any) -> Any:
        """Flatten an object and its guts into a json-safe representation"""
        pass

    def flatten(self, obj: Any, reset: bool = True) -> Any:
        """Takes an object and returns a JSON-safe representation of it.

        Simply returns any of the basic builtin datatypes

        >>> p = Pickler()
        >>> p.flatten('hello world') == 'hello world'
        True
        >>> p.flatten(49)
        49
        >>> p.flatten(350.0)
        350.0
        >>> p.flatten(True)
        True
        >>> p.flatten(False)
        False
        >>> r = p.flatten(None)
        >>> r is None
        True
        >>> p.flatten(False)
        False
        >>> p.flatten([1, 2, 3, 4])
        [1, 2, 3, 4]
        >>> p.flatten((1,2,))[tags.TUPLE]
        [1, 2]
        >>> p.flatten({'key': 'value'}) == {'key': 'value'}
        True
        """
        pass

    def _flatten_bytestring(self, obj: bytes) -> Dict[str, str]:
        pass

    def _flatten_impl(self, obj: Any) -> Any:
        #########################################
        # if obj is nonrecursive return immediately
        # for performance reasons we don't want to do recursive checks
        pass

    def _max_reached(self) -> bool:
        pass

    def _pickle_warning(self, obj: Any) -> None:
        pass

    def _flatten_obj(self, obj: Any) -> Any:
        pass

    def _list_recurse(self, obj: Iterable[Any]) -> List[Any]:
        pass

    def _flatten_function(self, obj: Callable[..., Any]) -> Optional[Dict[str, str]]:
        pass

    def _getstate(self, obj: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def _flatten_key_value_pair(
        self, k: Any, v: Any, data: Dict[Union[str, Any], Any]
    ) -> Dict[Union[str, Any], Any]:
        """Flatten a key/value pair into the passed-in dictionary."""
        pass

    def _call_handler_flatten(
        self, handler: handlers.BaseHandler, obj: Any, data: Dict[str, Any]
    ) -> Any:
        pass

    def _flatten_obj_attrs(
        self,
        obj: Any,
        attrs: Iterable[str],
        data: Dict[str, Any],
        exclude: Iterable[str] = (),
    ) -> bool:
        pass

    def _flatten_properties(
        self,
        obj: Any,
        data: Dict[str, Any],
        allslots: Optional[Iterable[Sequence[str]]] = None,
    ) -> Dict[str, Any]:
        pass

    def _flatten_newstyle_with_slots(
        self,
        obj: Any,
        data: Dict[str, Any],
        exclude: Iterable[str] = (),
    ) -> Dict[str, Any]:
        """Return a json-friendly dict for new-style objects with __slots__."""
        pass

    def _flatten_obj_instance(
        self, obj: Any
    ) -> Optional[Union[Dict[str, Any], List[Any], Any]]:
        """Recursively flatten an instance and return a json-friendly dict"""
        pass

    def _ref_obj_instance(self, obj: Any) -> Optional[Union[Dict[str, Any], List[Any]]]:
        """Reference an existing object or flatten if new"""
        pass

    def _escape_key(self, k: Any) -> str:
        pass

    def _flatten_non_string_key_value_pair(
        self, k: Any, v: Any, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Flatten only non-string key/value pairs"""
        pass

    def _flatten_string_key_value_pair(
        self, k: str, v: Any, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Flatten string key/value pairs only."""
        pass

    def _flatten_dict_obj(
        self,
        obj: dict[Any, Any],
        data: Optional[Dict[Any, Any]] = None,
        exclude: Iterable[Any] = (),
    ) -> Dict[str, Any]:
        """Recursively call flatten() and return json-friendly dict"""
        pass

    def _get_flattener(self, obj: Any) -> Optional[Callable[[Any], Any]]:
        pass

    def _flatten_sequence_obj(
        self, obj: Iterable[Any], data: Dict[str, Any]
    ) -> Union[Dict[str, Any], List[Any]]:
        """Return a json-friendly dict for a sequence subclass."""
        pass
