from typing import Any


class AlreadyRegisteredException(Exception):
    pass


class ClassRegistry:

    def __init__(self):
        self._registry = {}

    def register(self, cls: Any, key: str = None):
        """Reigster the class from registry
        Args:
            cls (Any): Class which you want to register.
            key (str, optional): Key corresponding to which the class should register.
        """
        if not key and hasattr(cls, "REGISTERY_KEY"):
            key = getattr(cls, "REGISTERY_KEY")

        if not key:
            raise ValueError(
                "Registry Key missing, either provide one during registration, or add REGISTERY_KEY as class attribute"
            )

        if key in self._registry:
            raise AlreadyRegisteredException(
                f"Key: [{key}] is already registered for [{self._registry[key].__name__}] class"
            )

        self._registry[key] = cls

    def unregister(self, key: str):
        """
        Unreigster the class from registry
        Args:
            key (str): Key corresponding to which the class is registerd
        """
        self._registry.pop(key, None)

    @property
    def registry(self) -> dict:
        """Current Active Registry"""
        return self._registry

    def get(self, key: str):
        """
        Get a class corresponding to registry,
        NOTE: Registry only returns a class, object you have to initiate yourself
            Ex:
            >>> some_class = some_registry.get("some_class")
            >>> object = some_class()
            >>> object.do_something()

        Args:
            key (str): Key corresponding to which the class is registerd
        """
        return self._registry.get(key)
