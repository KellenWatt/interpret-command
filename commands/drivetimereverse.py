from .drivetime import DriveTimeCommand

class DriveTimeReverseCommand(DriveTimeCommand):
    def execute(self) -> None:
        self.drive.drive(0, -self.speed, 0)