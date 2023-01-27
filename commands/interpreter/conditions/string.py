from ..interpreter import ConditionBase
from ..exceptions import CommandSyntaxError
from .numeric import NumericComparisonCondition, NumericEqualityCondition

from typing import Any

class StringEqualityCondition(ConditionBase):
    @staticmethod
    def test(input: str, *tokens: str) -> bool:
        op = tokens[0]
        comparand = tokens[1]
        if op == "=" or op == "==":
            return input == comparand
        elif op == "!=" or op == "=/=":
            return input != comparand
        else:
            raise CommandSyntaxError("'{}': Invalid operator".format(op))
    
    @staticmethod
    def validate_arguments(args: list[str]) -> bool:
        try:
            assert len(args) == 2
            assert args[0] in ["=", "==", "!=", "=/="]
            float(args[1])
        except (ValueError, AssertionError):
            return False
        return True
    
    @staticmethod
    def parse_arguments(args: list[str]) -> list[Any]:
        return [a for a in args]
    
class StringLengthComparisonCondition(NumericComparisonCondition):
    @staticmethod
    def test(input: str, *tokens: str) -> bool:
        return super().test(len(input), *tokens)

class StringLengthEqualityCondition(NumericEqualityCondition):
    @staticmethod
    def test(input: str, *tokens: str) -> bool:
        return super().test(len(input), *tokens)
        