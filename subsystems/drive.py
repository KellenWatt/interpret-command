from commands2 import SubsystemBase

import rev
from navx import AHRS as NavxGyro

from wpilib.drive import MecanumDrive
import wpilib

class DriveSubsystem(SubsystemBase):
    front_left: rev.CANSparkMax
    front_right: rev.CANSparkMax
    rear_left: rev.CANSparkMax
    rear_right: rev.CANSparkMax

    drive_train: MecanumDrive

    gyro: NavxGyro

    def __init__(self):
        self.front_left = rev.CANSparkMax(4, rev.CANSparkMax.MotorType.kBrushless)
        self.rear_left = rev.CANSparkMax(1, rev.CANSparkMax.MotorType.kBrushless)
        self.front_right = rev.CANSparkMax(2, rev.CANSparkMax.MotorType.kBrushless)
        self.front_right.setInverted(True)
        self.rear_right = rev.CANSparkMax(3, rev.CANSparkMax.MotorType.kBrushless)
        self.rear_right.setInverted(True)

        self.drive_train = MecanumDrive(self.front_left, self.rear_left, self.front_right, self.rear_right)

        self.gyro = NavxGyro(wpilib.SPI.Port.kMXP)
    
        super().__init__()
    
    def drive(self, x_speed: int, y_speed: int, rot: int) -> None:
        # Here we are invoking the MecanumDrive's own drive method, since we don't need to 
        # reinvent the wheel.
        self.drive_train.driveCartesian(y_speed, x_speed, rot)

    def fullstop(self) -> None:
        # This completely stops all motion on the robot, which is useful, since without 
        # telling it to stop, the robot will just keep driving.
        self.drive_train.stopMotor()

    def angle(self) -> float:
        # Get the Yaw angle from the gyro (rotation around Z-axis).
        return self.gyro.getAngle()

    def reset(self) -> None:
        # Set the gyro's current angle to zero.
        self.gyro.zeroYaw()