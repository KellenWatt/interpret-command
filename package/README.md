# Interpreter Command

An overcomplicated solution to the question "How could we easily make multiple autonomous routines?"

The interpreter command provides a way to create a Domain Specific Language (DSL) that can run any sequence 
of commands at runtime. Ostensibly, this to write a command sequence for autonomous execution; however, this 
can be used to create a command sequence for any purpose (whether the hit to efficiency is worth it is up to 
the user).

## Installation

#### Python
Windows:
```batch
py -3 install interpreter-command
```
MacOS/Linux:
```bash
python3 install interpreter-command
```

## Usage
All you need to do to create an InterpretCommand is to instantiate the
class in your language of choice, register commands to it, and 
register your fully-realized InterpretCommand object the same way you
would register any other command. At any time, you can load a new 
program and replace the current one.

#### Python
```python
# WARNING: This example will not work as-is
import wpilib
import interpretercommand as ic
import commands2

class MyRobot(wpilib.TimedRobot):
    # ... 
    def robotInit(self):
        # Creating the interpreter
        self.interpreter = ic.InterpretCommand()

        # Registering the commands
        self.interpreter.register("say", commands2.PrintCommand)
        self.interpreter.register("drive", SomeDriveCommand, drive_subsystem) # parameters: x, y, z
        
    # ...
    def autonomousInit(self):
        self.interpreter.schedule()

    def teleopInit(self):
        self.interpreter.cancel()
```

Now you could write a program like
```
say "hello"
say "world"
drive 0, 0.4, 0
```
which would print "hello\nworld", then drive the robot in the Y 
direction at 40% speed until the command is canceled, assuming
`SomeDriveCommand` does nothing but drive continuously using its
inputs.

### Further Information
For more information, 

## License
This project is licensed under the MIT License. If this doesn't work for you, feel free to create an issue requesting it.

## Caveat
This library is specifically designed to work with [RobotPy](https://robotpy.readthedocs.io/en/stable/) 
and [WPILib](https://docs.wpilib.org/en/stable/index.html). The concept may work well with other robotics 
frameworks, but this library is not compatible.