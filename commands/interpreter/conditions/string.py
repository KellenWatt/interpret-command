from ..interpreter import ConditionBase
from ..exceptions import CommandSyntaxError
from .numeric import NumericComparisonCondition, NumericEqualityCondition

class StringEqualityCondition(ConditionBase):
    @staticmethod
    def test(input: str, *tokens: str) -> bool:
        op = tokens[0]
        comparand = tokens[1]
        if op == "==":
            return input == comparand
        elif op == "!=" or op == "=/=":
            return input != comparand
        else:
            raise CommandSyntaxError("'{}': Invalid operator".format(op))
    
class StringLengthComparisonCondition(NumericComparisonCondition):
    @staticmethod
    def test(input: str, *tokens: str) -> bool:
        return super().test(len(input), *tokens)

class StringLengthEqualityCondition(NumericEqualityCondition):
    @staticmethod
    def test(input: str, *tokens: str) -> bool:
        return super().test(len(input), *tokens)
        