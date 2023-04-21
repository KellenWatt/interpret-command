Basics
======

At its core, the interpreter-command provides three things: A lexer, a parser, and a runtime. It's the user's job to 
provide the language. In this chapter, we'll cover each of these, and how to make a basic language.

Terminology
-----------
Throughout these docs, we'll refer to various concepts of the interpreter command, and each has a very specific meaning.

Interpreter
    The whole contents of the interpreter-command library, put together.

Program
    A series of instructions that has been given to the interpreter.

Instruction
    A line of code that is composed of a command and optionally a conditional

Command
    The action of an instruction, or the part that does some kind of work.

    This is technically distinct from a Command in RobotPy, even if Commands are the underlying concept for commands. 
    Any mentions of command using this meaning will always be lower case; the Command class will be referenced in upper case.

Conditional
    Part of an instruction that dictates how the command is run. Always starts with ``if``, ``unless``, ``while,``, or ``until``, 
    followed by a condition. This design is governed by the runtime, and cannot be changed.

Condition
    The actual user-provided test. The syntax of this is governed by the user.

Keyword
    A word that holds a special meaning in a language. In for both conditions and commands, the first word in the segment is 
    treated as a keyword and determines what command or condition is used for that instruction.

Optional Terminology
^^^^^^^^^^^^^^^^^^^^
These definitions are useful for fully understanding the interpreter, but aren't necessary for basic usage.

Lexer
    A function (or function-like object) or set or rules that splits the input into tokens. These tokens are then given directly
    to the parser.

Token
    A string of characters. This is the smallest unit of a program that still provides meaning.

Parser
    The part of the interpreter that gives tokens meaning. This includes syntax handling and converting tokens into 
    appropriate values. 

    Specifically, this library provides the ability to customize the way tokens are parsed into values (numbers, bools, etc.). 
    The actual grammar of conditionals is governed by the runtime, and cannot be changed. In a later section, we'll 
    cover how to customize parsing in greater detail.

Runtime
    The part of the interpreter that actually executes the program. In short, the runtime iterates over a list of instructions,
    running each sequentially, if the condition allows it.

Domain Specific Language (DSL)
    A type of language that is intended for a specific, limited use case. Contrast with general-purpose languages, like 
    Python, C#, Java, etc., which can be used to access all parts of a computer. Common examples of DSLs are HTML, Markdown, 
    pure SQL, and Mathematica. They are intended to present a specific topic (domain) in a format that's easier to write and 
    understand than doing so in a general-purpose language.

.. _intro-example:

The ``InterpreterCommand``
--------------------------

The core of the interpreter is the ``InterpreterCommand`` class. This class provides the three main components provided by the 
library, and is the means by which the user can define the language.

Here's a short example that creates a simple, robot-agnostic language using built-in Commands. We'll run the command in 
autonomous, but it could be run anywhere a command could be run. We'll explore each of the pieces afterward.

.. code-block:: python

    import wpilib
    import commands2
    import interpretercommand as ic
    import interpretercommand.parsers as parsers

    class InterpreterBot(wpilib.TimedRobot):
        auto_cmd: ic.InterpreterCommand

        def robotInit(self) -> None:
            # Creating the command, like any other, but not doing anything with it yet
            self.auto_cmd = ic.InterpreterCommand()
            
            # Registering simple Commands with keywords
            self.auto_cmd.register("print", commands2.PrintCommand)
            self.auto_cmd.register("wait", commands2.WaitCommand)
        
        def robotPeriodic(self) -> None:
            commands2.CommandScheduler.getInstance().run()
        
        def autonomousInit(self) -> None:
            # This is an example program. Any combination of 'print' and 'wait' would work.
            program = """print "Hello, world!"
                wait 2.5

                print "My name is InterpretBot"
                wait 1
                print "And I can change this code whenever!"
                """

            self.auto_cmd.load_program(program)

            self.auto_cmd.schedule()
        
        def teleopInit(self) -> None:
            if self.auto_cmd.isScheduled():
                self.auto_cmd.cancel()

    if __name__ == "__main__":
        wpilib.run(InterpreterBot)
    
And that's it! Notice that a lot of this program is boilerplate robot code, so there isn't a ton you have to do to make 
simple languages. So let's break this down to see how it works.

.. note::
    This will be the only complete example. Other examples will leave out all parts of the program that aren't different
    or parts that shouldn't require explanation, likely due to being part of the command-based framework from WPILib.

.. code-block:: python
    
    self.auto_cmd = ic.InterpreterCommand(parser = parsers.typed_parser)

This does nothing more than set up a basic, empty interpreter. Technically, this is valid, but it doesn't have any commands
registered yet, so anything other than an empty program won't run.

.. code-block:: python

    self.auto_cmd.register("print", commands2.PrintCommand)
    self.auto_cmd.register("wait", commands2.WaitCommand)

These lines registers two commands: ``print`` and ``wait``. We use the built in classes, since they already do exactly what we 
want them to do. However, there are two important things to note here. You'll note we aren't creating instances of the classes,
instead just passing their names in as values. This is something that you can do in Python: treat a class like a value, and 
store it in a variable. 

The second thing has to do with actually passing values to these classes so that they're useful, but we'll cover that in a moment.

.. code-block:: python

    def robotPeriodic(self) -> None:
        commands2.CommandScheduler.getInstance().run()

``InterpreterCommand`` is technically just like any other Command. More accurately it works like a glorified ``SequentialCommandGroup``.
As such, we only need to run the command scheduler, the same way would for any other Commands.

.. code-block:: python

    program = """print "Hello, world!"
        wait 2.5

        print "My name is InterpretBot"
        wait 1
        print "And I can change this code whenever!"
        """

    self.auto_cmd.load_program(program)

This creates a normal variable named "program", and then loads it into the interpreter using ``load_program``. This program will 
print "Hello, world!", wait 2.5 seconds, print "My name is InterpretBot", wait another second, and finally print "And I can 
change this code whenever!" before finishing. This is a very simple program (and about all we can do in a robot-agnostic manner),
but it shows a lot of important basics to actually using the language.


First, we see the basic lexical structure of programs is line-based. That is, each instruction is on its own line. As of the 
time of writing, instructions cannot be separated across lines, though this may be possible in the future.

Second, we see that all of the instructions start with a word that we used when we were registering commands. This isn't a 
coincidence, as the names you use to register a command is used as a keyword in the language, in order to determine which 
command to run. Additionally, there is an empty line, but it doesn't appear to do anything because empty lines are ignored by
the interpreter.

Third, we noted before that when we registered the commands, we didn't give any values to tell them what to do. For example, 
``PrintCommand`` prints the given string, but we gave it no string. But when we use ``print`` in the interpreter, we see 
that we have a value following it. In a nutshell, that value is given to ``PrintCommand``'s constructor, and the resulting 
Command object is then run. The same goes for ``WaitCommand``, but with a number instead of a string.
We go into more detail about how this works and how you can customize that behaviour in :doc:`conditions`.


Next, let's talk about how to make our interpreter a little more useful.