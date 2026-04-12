# Copyright (C) 2008 John Paulett (john -at- paulett.org)
# Copyright (C) 2009-2024 David Aguilar (davvid -at- gmail.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
import dataclasses
import warnings
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from . import errors, handlers, tags, util
from .backend import JSONBackend, json

# class names to class objects (or sequence of classes)
ClassesType = Optional[Union[Type[Any], Dict[str, Type[Any]], Sequence[Type[Any]]]]
# handler for missing classes: either a policy name or a callback
MissingHandler = Union[str, Callable[[str], Any]]


def decode(
    string: str,
    backend: Optional[JSONBackend] = None,
    # we get a lot of errors when typing with TypeVar
    context: Optional["Unpickler"] = None,
    keys: bool = False,
    reset: bool = True,
    safe: bool = True,
    classes: Optional[ClassesType] = None,
    v1_decode: bool = False,
    on_missing: MissingHandler = "ignore",
    handle_readonly: bool = False,
    handler_context: Any = None,
) -> Any:
    """Convert a JSON string into a Python object.

    :param backend: If set to an instance of jsonpickle.backend.JSONBackend, jsonpickle
        will use that backend for deserialization.

    :param context: Supply a pre-built Pickler or Unpickler object to the
        `jsonpickle.encode` and `jsonpickle.decode` machinery instead
        of creating a new instance. The `context` represents the currently
        active Pickler and Unpickler objects when custom handlers are
        invoked by jsonpickle.

    :param keys: If set to True then jsonpickle will decode non-string dictionary keys
        into python objects via the jsonpickle protocol.

    :param reset: Custom pickle handlers that use the `Pickler.flatten` method or
        `jsonpickle.encode` function must call `encode` with `reset=False`
        in order to retain object references during pickling.
        This flag is not typically used outside of a custom handler or
        `__getstate__` implementation.

    :param safe: If set to ``False``, use of ``eval()`` for backwards-compatible (pre-0.7.0)
        deserialization of repr-serialized objects is enabled. Defaults to ``True``.
        The default value was ``False`` in jsonpickle v3 and changed to ``True`` in jsonpickle v4.

        .. warning::

            ``eval()`` is used when set to ``False`` and is not secure against
            malicious inputs. You should avoid setting ``safe=False``.

    :param classes: If set to a single class, or a sequence (list, set, tuple) of
        classes, then the classes will be made available when constructing objects.
        If set to a dictionary of class names to class objects, the class object
        will be provided to jsonpickle to deserialize the class name into.
        This can be used to give jsonpickle access to local classes that are not
        available through the global module import scope, and the dict method can
        be used to deserialize encoded objects into a new class. An example of using
        this argument can be found in examples/changing_class_path.py on GitHub.

    :param v1_decode: If set to True it enables you to decode objects serialized in
        jsonpickle v1. Please do not attempt to re-encode the objects in the v1 format!
        Version 2's format fixes issue #255, and allows dictionary identity to be
        preserved through an encode/decode cycle.

    :param on_missing: If set to 'error', it will raise an error if the class it's
        decoding is not found. If set to 'warn', it will warn you in said case.
        If set to a non-awaitable function, it will call said callback function
        with the class name (a string) as the only parameter. Strings passed to
        `on_missing` are lowercased automatically.

    :param handle_readonly: If set to True, the Unpickler will handle objects encoded
        with 'handle_readonly' properly. Do not set this flag for objects not encoded
        with 'handle_readonly' set to True.

    :param handler_context:
        Pass custom context to a custom handler. This can be used to customize
        behavior at runtime based off data. Defaults to ``None``. An example can
        be found in the examples/ directory on GitHub.

    >>> decode('"my string"') == 'my string'
    True
    >>> decode('36')
    36
    """
    pass


def _safe_hasattr(obj: Any, attr: str) -> bool:
    """Workaround unreliable hasattr() availability on sqlalchemy objects"""
    pass


def _is_json_key(key: Any) -> bool:
    """Has this key a special object that has been encoded to JSON?"""
    pass


class _Proxy:
    """Proxies are dummy objects that are later replaced by real instances

    The `restore()` function has to solve a tricky problem when pickling
    objects with cyclical references -- the parent instance does not yet
    exist.

    The problem is that `__getnewargs__()`, `__getstate__()`, custom handlers,
    and cyclical objects graphs are allowed to reference the yet-to-be-created
    object via the referencing machinery.

    In other words, objects are allowed to depend on themselves for
    construction!

    We solve this problem by placing dummy Proxy objects into the referencing
    machinery so that we can construct the child objects before constructing
    the parent.  Objects are initially created with Proxy attribute values
    instead of real references.

    We collect all objects that contain references to proxies and run
    a final sweep over them to swap in the real instance.  This is done
    at the very end of the top-level `restore()`.

    The `instance` attribute below is replaced with the real instance
    after `__new__()` has been used to construct the object and is used
    when swapping proxies with real instances.

    """

    def __init__(self) -> None:
        self.instance = None

    def get(self) -> Any:
        return self.instance

    def reset(self, instance: Any) -> None:
        pass


class _IDProxy(_Proxy):
    def __init__(self, objs: List[Any], index: int) -> None:
        self._index = index
        self._objs = objs

    def get(self) -> Any:
        try:
            return self._objs[self._index]
        except IndexError:
            return None


def _obj_setattr(obj: Any, attr: str, proxy: _Proxy) -> None:
    """Use setattr to update a proxy entry"""
    pass


def _obj_setvalue(obj: Any, idx: Any, proxy: _Proxy) -> None:
    """Use obj[key] assignments to update a proxy entry"""
    pass


def has_tag(obj: Any, tag: str) -> bool:
    """Helper class that tests to see if the obj is a dictionary
    and contains a particular key/tag.

    >>> obj = {'test': 1}
    >>> has_tag(obj, 'test')
    True
    >>> has_tag(obj, 'fail')
    False

    >>> has_tag(42, 'fail')
    False

    """
    pass


def getargs(obj: Dict[str, Any], classes: Optional[Dict[str, Type[Any]]] = None) -> Any:
    """Return arguments suitable for __new__()"""
    pass


class _trivialclassic:
    """
    A trivial class that can be instantiated with no args
    """


def make_blank_classic(cls: Type[Any]) -> Any:
    """
    Implement the mandated strategy for dealing with classic classes
    which cannot be instantiated without __getinitargs__ because they
    take parameters
    """
    pass


def loadrepr(reprstr: str) -> Any:
    """Returns an instance of the object from the object's repr() string.
    It involves the dynamic specification of code.

    .. warning::

        This function is unsafe and uses `eval()`.

    >>> obj = loadrepr('datetime/datetime.datetime.now()')
    >>> obj.__class__.__name__
    'datetime'

    """
    pass


def _loadmodule(module_str: str) -> Optional[Any]:
    """Returns a reference to a module.

    >>> fn = _loadmodule('datetime/datetime.datetime.fromtimestamp')
    >>> fn.__name__
    'fromtimestamp'

    """
    pass


def has_tag_dict(obj: Any, tag: str) -> bool:
    """Helper class that tests to see if the obj is a dictionary
    and contains a particular key/tag.

    >>> obj = {'test': 1}
    >>> has_tag(obj, 'test')
    True
    >>> has_tag(obj, 'fail')
    False

    >>> has_tag(42, 'fail')
    False

    """
    pass


def _passthrough(value: Any) -> Any:
    """A function that returns its input as-is"""
    pass


class Unpickler:
    def __init__(
        self,
        backend: Optional[JSONBackend] = None,
        keys: bool = False,
        safe: bool = True,
        v1_decode: bool = False,
        on_missing: MissingHandler = "ignore",
        handle_readonly: bool = False,
        handler_context: Any = None,
    ) -> None:
        self.backend = backend or json
        self.keys = keys
        self.safe = safe
        self.v1_decode = v1_decode
        self.on_missing = on_missing
        self.handle_readonly = handle_readonly
        # Custom context passed through to custom handlers, see #452
        self.handler_context = handler_context

        self.reset()

    def reset(self) -> None:
        """Resets the object's internal state."""
        pass

    def _swap_proxies(self) -> None:
        """Replace proxies with their corresponding instances"""
        pass

    def _restore(
        self, obj: Any, _passthrough: Callable[[Any], Any] = _passthrough
    ) -> Any:
        # if obj isn't in these types, neither it nor nothing in it can have a tag
        # don't change the tuple of types to a set, it won't work with isinstance
        pass

    def restore(
        self, obj: Any, reset: bool = True, classes: Optional[ClassesType] = None
    ) -> Any:
        """Restores a flattened object to its original python state.

        Simply returns any of the basic builtin types

        >>> u = Unpickler()
        >>> u.restore('hello world') == 'hello world'
        True
        >>> u.restore({'key': 'value'}) == {'key': 'value'}
        True

        """
        pass

    def register_classes(self, classes: ClassesType) -> None:
        """Register one or more classes

        :param classes: sequence of classes or a single class to register

        """
        pass

    def _restore_base64(self, obj: Dict[str, Any]) -> bytes:
        pass

    def _restore_base85(self, obj: Dict[str, Any]) -> bytes:
        pass

    def _refname(self) -> str:
        """Calculates the name of the current location in the JSON stack.

        This is called as jsonpickle traverses the object structure to
        create references to previously-traversed objects.  This allows
        cyclical data structures such as doubly-linked lists.
        jsonpickle ensures that duplicate python references to the same
        object results in only a single JSON object definition and
        special reference tags to represent each reference.

        >>> u = Unpickler()
        >>> u._namestack = []
        >>> u._refname() == '/'
        True
        >>> u._namestack = ['a']
        >>> u._refname() == '/a'
        True
        >>> u._namestack = ['a', 'b']
        >>> u._refname() == '/a/b'
        True

        """
        pass

    def _mkref(self, obj: Any) -> Any:
        pass

    def _restore_list(self, obj: List[Any]) -> List[Any]:
        pass

    def _restore_iterator(self, obj: Dict[str, Any]) -> Iterator[Any]:
        pass

    def _swapref(self, proxy: _Proxy, instance: Any) -> None:
        pass

    def _restore_reduce(self, obj: Dict[str, Any]) -> Any:
        """
        Supports restoring with all elements of __reduce__ as per pep 307.
        Assumes that iterator items (the last two) are represented as lists
        as per pickler implementation.
        """
        pass

    def _restore_id(self, obj: Dict[str, Any]) -> Any:
        pass

    def _restore_type(self, obj: Dict[str, Any]) -> Any:
        pass

    def _restore_module(self, obj: Dict[str, Any]) -> Any:
        pass

    def _restore_repr_safe(self, obj: Dict[str, Any]) -> Any:
        pass

    def _restore_repr(self, obj: Dict[str, Any]) -> Any:
        pass

    def _loadfactory(self, obj: Dict[str, Any]) -> Optional[Any]:
        pass

    def _process_missing(self, class_name: str) -> None:
        # most common case comes first
        pass

    def _restore_pickled_key(self, key: str) -> Any:
        """Restore a possibly pickled key"""
        pass

    def _restore_key_fn(
        self, _passthrough: Callable[[Any], Any] = _passthrough
    ) -> Callable[[Any], Any]:
        """Return a callable that restores keys

        This function is responsible for restoring non-string keys
        when we are decoding with `keys=True`.

        """
        pass

    def _restore_from_dict(
        self,
        obj: Dict[str, Any],
        instance: Any,
        ignorereserved: bool = True,
        restore_dict_items: bool = True,
    ) -> Any:
        pass

    def _restore_state(self, obj: Dict[str, Any], instance: Any) -> Any:
        pass

    def _restore_object_instance_variables(
        self, obj: Dict[str, Any], instance: Any
    ) -> Any:
        pass

    def _restore_object_instance(
        self, obj: Dict[str, Any], cls: Type[Any], class_name: str = ""
    ) -> Any:
        # This is a placeholder proxy object which allows child objects to
        # reference the parent object before it has been instantiated.
        pass

    def _restore_object(self, obj: Dict[str, Any]) -> Any:
        pass

    def _restore_function(self, obj: Dict[str, Any]) -> Any:
        pass

    def _restore_set(self, obj: Dict[str, Any]) -> Set[Any]:
        pass

    def _restore_dict(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def _restore_tuple(self, obj: Dict[str, Any]) -> Tuple[Any, ...]:
        pass

    def _restore_tags(
        self, obj: Any, _passthrough: Callable[[Any], Any] = _passthrough
    ) -> Callable[[Any], Any]:
        """Return the restoration function for the specified object"""
        pass

    def _call_handler_restore(
        self, handler: handlers.BaseHandler, obj: Dict[str, Any]
    ) -> Any:
        pass
