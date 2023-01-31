class ExecutionError(Exception):
    """Raised when there is some problem in the execution of an InterpretCommand."""
    
class InstructionNotFoundError(Exception):
    """Raised when an unregistered instruction has been encountered."""

class CommandSyntaxError(Exception):
    """Raised when a ModularCommand does not have valid arguments."""

class TokenizingError(Exception):
    """Raised when the tokenizer finds invalid syntax. Generally when missing closing quote"""

class DispatcherError(Exception):
    """Raised when there is a generic problem in a Dispatcher"""

class EmptyDispatchError(DispatcherError):
    """Raised when a DispatcherBase is instantiated directly, without being subclassed."""
