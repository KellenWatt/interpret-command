import wpilib
import commands2
import commands2.button as button
from wpilib import SmartDashboard as sd
from wpilib import Timer

from subsystems.drive import DriveSubsystem

from commands.interpreter import InterpretCommand
from commands.interpreter.parsers import typed_parser
from commands.interpreter.dispatcher import DispatcherBase
from commands.drivetime import DriveTimeCommand
from commands.drivetimereverse import DriveTimeReverseCommand
from commands.drive import DriveCommand

from commands.interpreter.conditions.time import TimerCondition
from commands.interpreter.conditions.numeric import NumericComparisonCondition
from commands.interpreter.conditions.boolean import register_default_boolean_conditions
register_default_boolean_conditions()

class DriveDispatcher(DispatcherBase):
    def __init__(self, subsystem: DriveSubsystem, *args):
        self.register_target("forward", DriveTimeCommand, subsystem)
        self.register_target("reverse", DriveTimeReverseCommand, subsystem)
        self.register_default(DriveCommand, subsystem)

        super().__init__(*args)

    

class InterpretRobot(wpilib.TimedRobot):

    controller: button.CommandXboxController
    drive_subsystem: DriveSubsystem

    def robotInit(self) -> None:

        self.timer = Timer()
        self.timer.start()    
    
        self.drive_subsystem = DriveSubsystem()
        self.controller = button.CommandXboxController(0)

        self.responsive_command = InterpretCommand(parser = typed_parser)
        self.responsive_command.register("print", commands2.PrintCommand)
        self.responsive_command.register("wait", commands2.WaitCommand)
        self.responsive_command.register("drive", DriveDispatcher, self.drive_subsystem)
        self.responsive_command.register("time", commands2.InstantCommand, lambda: print(self.timer.get()))

        self.responsive_command.register_condition("elapsed", TimerCondition, TimerCondition.make_timer())
        self.responsive_command.register_condition("angle", NumericComparisonCondition, self.drive_subsystem.angle)

        self.controller.Y().onTrue(commands2.InstantCommand(lambda: self.responsive_command.load_program(self.code_box.getString(""))))
        self.controller.start().onTrue(self.responsive_command)    

        self.drive_subsystem.setDefaultCommand(commands2.RunCommand(lambda: self.drive_subsystem.drive(0,0,0), self.drive_subsystem))
        
        self.code_box = sd.getEntry("Interpreter Code")
        self.updateButton = sd.getEntry("Update")

        self.controller.back().onTrue(commands2.InstantCommand(lambda: self.code_box.setString(self.responsive_command.summary())))


    def robotPeriodic(self) -> None:
        
        # if self.updateButton.getBoolean(False):
        #     self.updateButton.setBoolean(False)
        #     self.instructions = self.code_box.getString("invalid")V
        commands2.CommandScheduler.getInstance().run()
        


    def autonomousPeriodic(self) -> None:
        pass

    def teleopInit(self) -> None:
        self.updateButton.setBoolean(False)
        self.code_box.setPersistent()

if __name__ == "__main__":
    wpilib.run(InterpretRobot)
