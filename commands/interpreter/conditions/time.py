from ..interpreter import ConditionBase
from ..exceptions import CommandSyntaxError

from wpilib import Timer

from typing import Any

class TimerCondition(ConditionBase):
    """Expects the Timer to be given from the getter. Note that the Timer
    must be declared outside the getter, and the getter should just return a reference.

    `make_timer` returns a Callable that returns a singleton-like Timer, and is
    recommended when registering this class.
    """

    class ConditionTimer:
        timer: Timer
        def __init__(self) -> None:
            self.timer = Timer()
        
        def __call__(self) -> Timer:
            return self.timer


    @staticmethod
    def test(input: Timer, *tokens: str) -> bool:
        time = float(tokens[0])
        input.start()
        if input.hasElapsed(time):
            input.stop()
            input.reset()
            return True
        return False

    @staticmethod
    def make_timer() -> ConditionTimer:
        """Convenience constructor for a singleton Timer source. Handy as the source for 
        for a TimerCondition's test.
        """
        return TimerCondition.ConditionTimer()    

    @staticmethod
    def validate_arguments(args: list[str]) -> bool:
        try:
            assert 1 <= len(args) <= 2
            float(args[0])
            if len(args) == 2:
                assert args[1] == "second" or args[1] == "seconds"
        except (ValueError, AssertionError):
            return False
        return True

    @staticmethod
    def parse_arguments(args: list[str]) -> list[Any]:
        return [float(args[0])]


