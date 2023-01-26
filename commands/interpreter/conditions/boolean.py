from ..interpreter import ConditionBase
from ..exceptions import CommandSyntaxError

import commands.interpreter

import commands2

class BooleanCondition(ConditionBase):
    @staticmethod
    def test(input: bool, *tokens: str) -> bool:
        if len(tokens) != 0:
            raise CommandSyntaxError("No other arguments allowed. Given: {}".format(tokens))
        return input

class TrueCondition(BooleanCondition):
    @staticmethod
    def test(input: bool, *tokens: str) -> bool:
        return super(TrueCondition, TrueCondition).test(True, *tokens)

class FalseCondition(BooleanCondition):
    @staticmethod
    def test(input: bool, *tokens: str) -> bool:
        return super(FalseCondition, FalseCondition).test(False, *tokens)

old_interpreter_init = commands.interpreter.InterpretCommand.__init__
def _register_boolean_init_(self: commands.interpreter.InterpretCommand, requirements: list[commands2.SubsystemBase] = []):
    old_interpreter_init(self, requirements)
    self.register_condition("true", TrueCondition, lambda: None)
    self.register_condition("false", FalseCondition, lambda: None)

commands.interpreter.InterpretCommand.__init__ = _register_boolean_init_


