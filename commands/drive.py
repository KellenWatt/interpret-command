from commands.interpreter import ModularCommand

from typing import Any
from subsystems.drive import DriveSubsystem


class DriveCommand(ModularCommand):
    @staticmethod
    def validate_arguments(args: list[str]) -> bool:
        try:
            assert len(args) >= 1 and len(args) <= 3
            float(args[0])
            if len(args) == 2:
                float(args[1])
            if len(args) == 3:
                float(args[2])
        except (ValueError, AssertionError):
            return False
        return True

    @staticmethod
    def parse_arguments(args: list[str]) -> list[Any]:
        return [float(a) for a in args]

    drive: DriveSubsystem
    x_speed: float
    y_speed: float
    rot_speed: float

    def __init__(self, subsystem: DriveSubsystem, *args: float): 
        super().__init__()

        self.x_speed = 0
        self.y_speed = 0
        self.rot_speed = 0
        if len(args) == 1:
            self.y_speed = args[0]
        elif len(args) <= 2:
            self.x_speed = args[0]
            self.y_speed = args[1]
        if len(args) == 3:
            self.rot_speed = args[2]

        self.drive = subsystem

        self.addRequirements(subsystem)

    def execute(self) -> None:
        self.drive.drive(self.x_speed, self.y_speed, self.rot_speed)
    
    def end(self, interrupted: bool) -> None:
        self.drive.fullstop()
    
    def isFinished(self) -> bool:
        return False
        


