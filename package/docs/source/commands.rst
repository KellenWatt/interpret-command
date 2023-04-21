Commands
========

As we saw in the :ref:`basic InterpreterCommand example <intro-example>` that we could register built-in commands and 
run them from out program. Ultimately though, this isn't much more than a party trick. It's handy for demonstration, 
but isn't very useful in practice. For that, we actually need a system to model against.

.. _simple-robot-definition:

Robot Definition
----------------

For the purposes of this documentation, we'll assume a robot that uses a tank drive, and has an AHRS (gyro). 
The gyro's angle value increases for clockwise rotation.

The drive will have a single subsystem named ``DriveSubsystem``, which contains the drive and gyro, with the 
following methods (listed using Python's type hint syntax).

* ``drive(speed: float, rotation: float) -> None``
* ``get_angle() -> float``

We will also assume that the subsystem's variable's name in the main robot class will be ``drive_subsystem``, and 
the interpreter's name will be ``interpreter``.

Providing the actual implementation for this subsystem is left to the user, as it doesn't matter in this context.

A Custom Command
---------------------

Using the basic robot definition, we can now make some custom Commands that we should be able to use with the interpreter.

One simple Command that we may find useful, especially in autonomous, is driving forward at a certain speed for a period 
of time. This Command may look something like this.

.. code-block:: python

    class DriveTimeCommand(commands2.CommandBase):
        drive_subsystem: DriveSubsystem
        speed: float
        seconds: float
        timer: wpilib.Timer

        def __init__(self, subsystem: DriveSubsystem, speed: float, seconds: float):
            super.__init__()

            self.drive_subsystem = subsystem
            self.speed = speed
            self.seconds = seconds
            self.timer = wpilib.Timer()

            self.addRequirements(subsystem)

        def initialize(self) -> None:
            self.timer.start()
        
        def execute(self) -> None:
            self.drive_subsystem.drive(self.speed, 0)
        
        def end(self, interrupted: bool) -> None:
            self.timer.stop()
            self.timer.reset()
        
        def isFinished(self) -> bool:
            return self.timer.hasElapsed(self.seconds)

Nothing too complicated here, and we won't stop to explain exactly how it works. Just know that it works as explained above.

Using Custom Commands
---------------------------

Now that we have our command, we need to figure out how to register it. However, we quickly find we have two problems. First, 
and easiest to solve, we don't know how to pass multiple values to a command. Second, and more importantly, we have no idea 
how to pass the required subsystem to the command, since we can't pass it via Python primitive (the only values understood by
the typed parser). Let's solve the second, and then the first should quickly become clear.

Passing Static Values
^^^^^^^^^^^^^^^^^^^^^

It's usually the case with custom Commands that we need to pass a subsystem or two, and maybe other constant values into the
command for it to be properly constructed. This is why the ``InterpreterCommand.register`` method takes arbitrarily many
arguments after the class. Every argument passed after the name and the class is passed to the class' constructor in the order 
given. More specifically, these values will always be the same, no matter the values given in the program. 

So if we want to register out ``DriveTimeCommand``, we would write this.

.. code-block:: python

    self.interpreter.register("drive", DriveTimeCommand, self.drive_subsystem).

Now, whenever we have a "drive" command, and need a new instance of ``DriveTimeCommand``, it will be passed the same exact
subsystem.

.. note::
    An important part of Commands is that they have subsystem requirements registered. Since ``InterpreterCommand`` is 
    essentially a command group of sorts, its requirements are based on the requirements of the Commands it contains. 
    
    However, due to the nature of the interpreter, this isn't possible the old-fashioned way. Instead, when you register 
    a command, if any of the static values are a subclass of ``commands2.SubsystemBase``, they'll automatically be 
    registered as a requirement of the containing ``InterpreterCommand``.

    This will not always prove directly useful, however its likely that most interpreters will use most subsystems 
    on a robot, so there will likely be sufficient overlap for this to not be an issue.

Multiple Values in the Program
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We've seen already how to pass a single value to a command, but for our new "drive" command, it needs 2 values (since 
we've already given it the subsystem as a static value). If you don't understand why, try giving any function/constructor
fewer values than it has to have - Python will not be happy with you. So we need 2 values because that's the number 
of non-optional values after we subtract static values.

We said that this is easily fixed, and it couldn't be simpler. All you need to do is pass more values to the command
in the program in a space-separated list. The tokenizer simply splits on spaces, with the exception of quoted strings, 
which allow you to have literal spaces in your values. If you look at the :ref:`basic example <intro-example>`, you'll 
see some quoted values in the program that have spaces in them. Quotes aren't required for strings, but they are required
for strings that contain spaces. 

.. note::
    If you done any kind of shell scripting before, like Bash, PowerShell, or batch scripting, you should be familiar 
    with the basic way tokens are split. It basically works the same way in most cases, with the exception that unterminated
    quotes treat the rest of the line as a single string token, instead of causing an error.

Now that we know how to provide multiple values, here's what calling the "drive" command looks like in a program.

.. code-block:: 

    drive 0.5 1

This line would cause the robot to drive at half speed for 1 second. Simple as that! You'll see that the values are 
exactly what you give to the ``DriveTimeCommand``'s constructor if you were to put it in a more conventional command group.

Customizing Command Syntax
--------------------------

It's great that we can use custom commands in our program, but it has one somewhat major problem: it's not readable. Sure, 
you can read the literal text, but there's no way to know what that instruction means without looking at the source code, 
which partially defeats the purpose of this tool. To make this easier to use, we need to introduce our next tool, the 
``InstructionCommand`` class.

.. _instruction_command:

``InstructionCommand`` and You
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to introduce extra syntax to our commands, we need to introduce another layer on top of the existing Command. 
The way we do that is by subclassing the ``InstructionCommand`` class. Python checks the type of the given Command, 
and if it's a subclass of ``InstructionCommand``, it allows for some extra safety and convenience features to be used.


The general convention for subclasses of ``InstructionCommand`` is to name them the same way you would name a Command, 
but following the name with "Instruction" instead of "Command". So if we changed our ``DriveTimeCommand`` to subclass 
``InstructionCommand`` instead of ``CommandBase``, we would call it "DriveTimeInstruction". We will refer to this 
in the future instead of ``DriveTimeCommand``.

In order to properly subclass ``InstructionCommand``, you need to implement three static methods, detailed below.

.. note::
    If you're unfamiliar with static methods in Python, you're not alone. They aren't a commonly used feature (and aren't 
    strictly necessary here). Essentially what they do is get rid of the ``self`` parameter to the function.

    To mark a method as static, precede it with the ``@staticmethod`` annotation.

.. note::
    ``InstructionCommand`` is itself a subclass of ``CommandBase``, so there's no cost to subclassing it instead for your
    normal commands, aside from defining the extra methods. 

``syntax()``
^^^^^^^^^^^^

This method defines the syntax of the command, and returns it as a string. At present, this is nothing more than a 
convenience feature to describe the syntax in a (relatively) human-friendly manner.

Here's how we could define the syntax for the ``DriveTimeInstruction``.

.. code-block:: python

    @staticmethod
    def syntax() -> str:
        return "(at|@) <speed> for <seconds> second[s]"

There aren't any hard and fast rules for how to write syntax, but the convention is as follows:

* text in angle brackets ("<>") is expected to be a substitution for some single value. You can choose to include 
  type information if you are so inclined, but a useful name goes a long way by itself.
* text not in angle brackets is a literal, expected to be that exact string
* text in parentheses, separated by vertical bars ("|") mean exactly one of of the options within the parentheses.
* text in square brackets ("[]") is optional. There can be multiple tokens inside square brackets.
* text in curly brackets ("{}") is repeated 1 or more times. There can be multiple tokens inside curly brackets.


You'll notice that nowhere in the ``syntax`` method do mention the word "drive" that we registered the command with.
Remember that Commands and their command are technically completely distinct, so the ``InstructionCommand`` you make 
has no knowledge of how its registered. However, this information is rendered as full commands using 
``InterpreterCommand.summary()``. In this case, this command's entry would look something like ``drive at <speed> for 
<seconds>``.

``validate_arguments()``
^^^^^^^^^^^^^^^^^^^^^^^^

This method checks whether arguments given to a command are correct. This is used when the program is loaded to make
sure it's valid, but not run it yet. This is primarily intended to make sure that you don't get unexpected type 
or syntax errors while the program is running. 

The function takes a list of tokens, specifically the values given to the command after its keyword. It returns a ``bool``
indicating whether the tokens are valid or not.

Here's an example of how we could define the method for ``DriveTimeInstruction``.

.. code-block:: python

    @staticmethod
    def validate_arguments(args: list[str]) -> bool:
        try:
            assert len(args) == 4
            assert args[0] == "at" or args[0] == "@"
            assert -1 <= float(args[1]) <= 1
            assert args[2] == "for"
            float(args[3])
            assert args[4] == "seconds" or args[4] == "seconds"
        except (ValueError, AssertionError):
            return False
        else:
            return True

The basic idea of the function is to go through all of the arguments of the function, and make sure they comply with the
syntax of the command. While ``syntax`` describes the syntax of the command, ``validate_arguments`` actually defines 
the syntax in a checkable way.

This approach checks values by using exceptions to indicate if the arguments are valid. There are two main approaches here, 
casting and assertion. In Python, when you try to cast a value to a type that can't represent it, a ``ValueError`` is raised.
We use that here to indicate when a string can't be converted to a float. For literal strings or limited values, we can use
``assert`` and comparisons to check values that can't be checked by casts.

.. note::
    All approaches to validation that match the method's signature are equivalent. The use of ``assert`` and casting in the 
    above example is one of the more human-readable approaches, but the use of exception isn't the most efficient.

    Another option is regex matching and ``if``-``elif`` chains

``parse_arguments()``
^^^^^^^^^^^^^^^^^^^^^

This method is used to translate tokens into values that are actually expected by the underlying Command constructor. 
You can assume that all values passed into the function will be valid, since this method is always called after 
the arguments are validated by ``validate_arguments``. All you need to do here is the conversion.

Here's what this would look like for ``DriveTimeInstruction``.

.. code-block:: python

    @staticmethod
    def parse_arguments(args: list[str]) -> list[Any]:
        return [float(args[1]), float(args[3])]

You can see here that we essentially ignore the "at"/"@" and the "for" because the Command doesn't care, only the human does.
We can also see here that because there's no magic auto-parsing, we could re-order the values in the syntax and then parse 
them in the correct order here, if it were useful for making the command more readable.

Note that there is no requirement about the structure of the output, other than it be sufficient to pass to the Command's
constructor. Everything else is up to the user.

.. note:: 
    Technically, it would be more accurate to give ``parse_arguments`` argument the type ``list[Any]`` because the general 
    parser could turn the tokens into any type, and those values are handed to the function. However, we use the signature 
    ``list[str]`` as a reminder that the inputs should be treated as strings unless you know for a fact which parser you are
    using.



.. _full-command-example:

Putting It All Together
^^^^^^^^^^^^^^^^^^^^^^^

For completion, here's all of the snippets we've written so far put together.

.. code-block:: python

    class DriveTimeInstruction(ic.InstructionCommand):
        drive_subsystem: DriveSubsystem
        speed: float
        seconds: float
        timer: wpilib.Timer

        def __init__(self, subsystem: DriveSubsystem, speed: float, seconds: float):
            super.__init__()

            self.drive_subsystem = subsystem
            self.speed = speed
            self.seconds = seconds
            self.timer = wpilib.Timer()

            self.addRequirements(subsystem)

        def initialize(self) -> None:
            self.timer.start()
        
        def execute(self) -> None:
            self.drive_subsystem.drive(self.speed, 0)
        
        def end(self, interrupted: bool) -> None:
            self.timer.stop()
            self.timer.reset()
        
        def isFinished(self) -> bool:
            return self.timer.hasElapsed(self.seconds)
    
        @staticmethod
        def syntax() -> str:
            return "(at|@) <speed> for <seconds> second[s]"
        
        @staticmethod
        def validate_arguments(args: list[str]) -> bool:
            try:
                assert len(args) == 4
                assert args[0] == "at" or args[0] == "@"
                assert -1 <= float(args[1]) <= 1
                assert args[2] == "for"
                float(args[3])
                assert args[4] == "seconds" or args[4] == "seconds"
            except (ValueError, AssertionError):
                return False
            else:
                return True
    
        @staticmethod
        def parse_arguments(args: list[str]) -> list[Any]:
            return [float(args[1]), float(args[3])]

With all of this in place, we don't need to write ``drive 0.5 1`` to run the command. Instead we can use the much 
more verbose

.. code-block::

    drive at 0.5 for 1 second

Which has a much more obvious meaning!

Breaking It Up!
^^^^^^^^^^^^^^^

You'll notice that all of the code in the main Command methods is identical the code in ``DriveTimeCommand``. 
We can hand-wave this and say that we just changed the class' name and add the methods, but in a real project, 
you may already have your Commands defined and modifying them all to fit this template can be unwieldy or make 
it harder to understand what they do. 

One way to solve this is to take advantage of Python's `multiple inheritance <https://www.geeksforgeeks.org/multiple-inheritance-in-python>`_.
Since ``CommandBase`` and ``InstructionCommand`` have no overlap, in terms of required methods, they can both 
be safely listed as superclasses of your command's class. The one requirement is that you list the base Command
as the first parent, followed by ``InstructionCommand``. This has to do with how ``super()`` resolves parentage.

Here's what our ``DriveTimeInstruction`` class would look like using this approach.

.. code-block:: python

    class DriveTimeInstruction(DriveTimeCommand, ic.InstructionCommand):
        # No need to define __init__(), since DriveTimeCommand already provides it.

        @staticmethod
        def syntax() -> str:
            return "(at|@) <speed> for <seconds>"
        
        @staticmethod
        def validate_arguments(args: list[str]) -> bool:
            try:
                assert len(args) == 4
                assert args[0] == "at" or args[0] == "@"
                assert -1 <= float(args[1]) <= 1
                assert args[2] == "for"
                float(args[3])
            except (ValueError, AssertionError):
                return False
            else:
                return True
    
        @staticmethod
        def parse_arguments(args: list[str]) -> list[Any]:
            return [float(args[1]), float(args[3])]

Now we've split our class into two parts: one that's just the Command and its logic, and another that handles everything
associated with the interpreter, all while still adhering to the `DRY principle <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_.

Whether you want to split up your command's definitions up or keep it all in one place is a matter of personal opinion,
and may differ from project to project. Just pick one method and stick with it, since both are generally identical. 
