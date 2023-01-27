class ExecutionError(Exception):
    """Raised when there is some problem in the execution of an InterpretCommand."""
    
class InstructionNotFoundError(Exception):
    """Raised when an unregistered instruction has been encountered."""

class CommandSyntaxError(Exception):
    """Raised when a ModularCommand does not have valid arguments."""

class EmptyDispatchError(Exception):
    """Raised when a DispatcherBase is instantiated directly, without being subclassed."""