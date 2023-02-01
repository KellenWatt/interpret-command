from ..interpreter import ConditionBase
from ..exceptions import CommandSyntaxError
import commands.interpreter

from typing import Any

class BooleanCondition(ConditionBase):
    @staticmethod
    def test(input: bool, *tokens: str) -> bool:
        if len(tokens) != 0:
            raise CommandSyntaxError("No other arguments allowed. Given: {}".format(tokens))
        return input
    
    @staticmethod
    def parse_arguments(args: list[str]) -> list[Any]:
        return args
    
    @staticmethod
    def validate_arguments(args: list[str]) -> bool:
        return len(args) == 0
        

class TrueCondition(BooleanCondition):
    @staticmethod
    def test(input: bool, *tokens: str) -> bool:
        return super(TrueCondition, TrueCondition).test(True, *tokens)

class FalseCondition(BooleanCondition):
    @staticmethod
    def test(input: bool, *tokens: str) -> bool:
        return super(FalseCondition, FalseCondition).test(False, *tokens)

def register_default_boolean_conditions() -> None:
    old_interpreter_init = commands.interpreter.InterpretCommand.__init__
    def _register_boolean_init_(self: commands.interpreter.InterpretCommand, *args, **kwargs):
        old_interpreter_init(self, *args, **kwargs)
        self.register_condition("true", TrueCondition, lambda: None)
        self.register_condition("false", FalseCondition, lambda: None)

    commands.interpreter.InterpretCommand.__init__ = _register_boolean_init_



