from typing import Any, Callable
import re


def identity_parser(tokens: list[str]) -> list[str]:
    """Do-nothing parser. Takes a list of tokens and returns it directly."""
    return tokens



_token_converters: list[tuple[re.Pattern, Callable[[str], Any]]] = []
def register_token_type(pattern: re.Pattern, converter: Callable[[str], Any]):
    """Registers a new token type for the typed_parser. Requires a compiled regex, and some kind 
    of callable that converts the token to a value of the registered type.
    """
    if not isinstance(pattern, re.Pattern):
        raise TypeError("pattern must be an `re.Pattern` instance")
    if not callable(converter):
        raise TypeError("converter must be callable")
    _token_converters.append((pattern, converter))

number = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")
register_token_type(number, float)

boolean = re.compile("^([tT]rue|[fF]alse)$")
register_token_type(boolean, (lambda t: t == "true" or t == "True"))

def _convert_token(token: str) -> Any:
    for reg, conv in _token_converters:
        if reg.match(token):
            return conv(token)
    
    return token


def typed_parser(tokens: list[str]) -> list[Any]:
    """Attempts to convert a list of tokens to a list of typed values, based on appearance 
    (e.g. a number will be turned into a `float`, "true" will be converted to a `bool`, etc.).
    If the parser doesn't recognize a type for a token, it returns it as it was (a string).
    
    By default, decimal numbers and booleans are recognized.

    In most situations, this should be compatible with ModularCommands that are expected to work with
    `identity_parser`
    """
    return [_convert_token(t) for t in tokens]
