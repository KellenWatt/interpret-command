from ..interpreter import ConditionBase
from typing import Any, Callable, Self
from .numeric import NumericComparisonCondition


class RelativeCondition(NumericComparisonCondition):
    """A condition for measuring data against some relative point. Ideal for tests that don't care about 
    the start or end point - just the distance in between.

    The `diff` function is set up similar to `__sub__`, that is the newest data is the LHS, and the 
    start point is RHS. In fact, for plain numeric data, `__sub__` could be the function used.
    """
    
    class RelativeData:
        start: Any
        source: Callable[[], Any]
        diff: Callable[[Any, Any], float]

        def __init__(self, source: Callable[[], Any], diff: Callable[[Any, Any], float]) -> None:
            self.source = source
            self.diff = diff

        def __call__(self) -> float:
            if not hasattr(self, "start"):
                self.start = self.source()
            
            return self.diff(self.source(), self.start)


    @staticmethod
    def new_data(source: Callable[[], Any], diff: Callable[[Any, Any], Any]) -> RelativeData:
        """Similar to a call to RelativeCondition.RelativeData, but possibly more palatable in certain contexts."""
        return RelativeCondition.RelativeData(source, diff)
    