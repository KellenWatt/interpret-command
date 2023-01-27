from ..interpreter import ConditionBase
from ..exceptions import CommandSyntaxError

from typing import Any

class NumericComparisonCondition(ConditionBase):
    @staticmethod
    def test(input: float, *tokens: str) -> bool:
        op = tokens[0]
        comparand = float(tokens[1])
        if op == "<":
            return input < comparand
        elif op == ">":
            return input > comparand
        elif op == "<=":
            return input <= comparand
        elif op == ">=":
            return input >= comparand
        else:
            raise CommandSyntaxError("No valid comparison found")
    
    @staticmethod
    def validate_arguments(args: list[str]) -> bool:
        try:
            assert len(args) == 2
            assert args[0] in ["<", ">", "<=", ">="]
            float(args[1])
        except (ValueError, AssertionError):
            return False
        return True
    
    @staticmethod
    def parse_arguments(args: list[str]) -> list[Any]:
        return [args[0], float(args[1])]

class NumericEqualityCondition(ConditionBase):
    @staticmethod
    def test(input: float, *tokens: str) -> bool:
        op = tokens[0]
        comparand = float(tokens[1])
        if op == "=" or op == "==":
            return input == comparand
        elif op == "!=" or op == "=/=":
            return input != comparand
        else:
            raise CommandSyntaxError("No valid comparison found")
    
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
        return [args[0], float(args[1])]