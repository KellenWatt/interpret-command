import commands2
import commands.interpreter as interpreter

from typing import Any

from subsystems.drive import DriveSubsystem

from wpilib import Timer


class DriveTimeCommand(interpreter.InstructionCommand):
    @staticmethod
    def validate_arguments(args: list[str]) -> bool:
        try:
            assert len(args) == 3 or len(args) == 5
            assert args[0] == "for"
            float(args[1])
            assert args[2] == "seconds" or args[2] == "second"

            if len(args) == 5:
                assert args[3] == "at" or args[3] == "@"
                float(args[4])
        except (ValueError, AssertionError):
            return False
        
        return True
    @staticmethod
    def parse_arguments(args: list[str]) -> list[Any]:
        if len(args) == 3:
            return [float(args[1])]
        else:
            return [float(args[1]), float(args[4])]

    drive: DriveSubsystem
    duration: float
    speed: float
    timer: Timer

    def __init__(self, subsystem: DriveSubsystem, duration: float, speed: float = 0.5) -> None:
        super().__init__()

        self.drive = subsystem
        self.duration = duration
        self.speed = speed
        self.timer = Timer()

        self.addRequirements(self.drive)
    
    def initialize(self) -> None:
        self.timer.reset()
        self.timer.start()
    
    
    def execute(self) -> None:
        self.drive.drive(0, self.speed, 0)
    
    def end(self, interrupted: bool) -> None:
        self.drive.fullstop()
        
        self.timer.stop()
    
    def isFinished(self) -> bool:
        return self.timer.get() >= self.duration

