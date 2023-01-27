from ..interpreter import ConditionBase
from ..exceptions import CommandSyntaxError


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