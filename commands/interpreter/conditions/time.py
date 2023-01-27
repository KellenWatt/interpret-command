from ..interpreter import ConditionBase
from ..exceptions import CommandSyntaxError

from wpilib import Timer
        
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
        time = float[tokens[0]]
        input.start()
        if input.hasElapsed(time):
            input.stop()
            input.reset()
            return True
        return False

    @classmethod
    def make_timer(self) -> ConditionTimer:
        """Convenience constructor for a singleton Timer source. Handy as the source for 
        for a TimerCondition's test.
        """
        return TimerCondition.ConditionTimer()    

