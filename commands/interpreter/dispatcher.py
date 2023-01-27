import commands2
from typing import Any, Type

from .exceptions import EmptyDispatchError
from .interpreter import ModularCommand

class DispatcherBase(commands2.CommandBase):
    """Dispatcher class for use with `InterpretCommand`. Cannot be used directly.
    
    In order to create a dispatcher, create a subclass of `DispatcherBase`, and register
    branches in the constructor using `register_target`, before calling `super().__init__()`.
    When the DispatcherBase subclass in instantiated within an `InterpretCommand`, it gives 
    the target keyword as the first argument, and the rest of the arguments are sent to 
    the appropriate command for instantiation, per usual.

    Subclasses that have requirements must include them as parameters to their constructors in order for 
    them to be registered with `InterpretCommand`.

    Subclasses of `DispatcherBase` should not override the methods stipulated by `CommandBase` 
    without good reason.
    """

    branches: dict[str, tuple[Type[commands2.CommandBase], list[Any]]]
    target: commands2.CommandBase

    # Any requirements as parameters must be handled in subclasses
    def __init__(self, branch: str, *tokens: Any) -> None:
        if len(self.branches) == 0:
            raise EmptyDispatchError("Dispatcher has no branches to target")

        klass, args = self.branches[branch]

        if issubclass(klass, ModularCommand):
            tokens = klass.parse_arguments(tokens)
        self.target = klass(*args, *tokens)

        super().__init__()

    def register_target(self, key: str, command: Type[commands2.CommandBase], *args: Any) -> "DispatcherBase":
        """Call in the constructor of `DispatcherBase` subclasses to register Dispatch targets."""
        if not hasattr(self, "branches"):
            self.branches = {}
        self.branches[key] = (command, list(args))

    def initialize(self) -> None:
        self.target.initialize()
    
    def execute(self) -> None:
        self.target.execute()
    
    def end(self, interrupted: bool) -> None:
        self.target.end(interrupted)
    
    def isFinished(self) -> bool:
        return self.target.isFinished()