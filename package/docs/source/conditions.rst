Conditions
==========

So far, we've talked about how to make custom commands, but the commands we write are limited to running 
exactly as written. This is workable, but severely limits the power of the interpreter, while also requiring 
the user to write more code that all does largely the same job. This is where conditions come in.

Conditionals
------------

In the ``InterpreterCommand``, instructions are made of two parts: the command, and the conditional. The command
is the behaviour, and the conditional affects if or how long it runs. Conditionals are defined by a conditional 
keyword, followed by a condition.

Here's a list of the valid conditional keywords. 

``if``
    If the condition is true, the command will run as normal. Tested once before the command runs.

``unless``
    If the condition is false, the command will run as normal. Tested once before the command runs.

``while``
    While the condition is true, the command will run as normal. Ends the command when the command becomes false.
    Tested before every iteration, as long as the command runs.

``until``
    While the condition is false, the command will run as normal. Ends the command when the command becomes true.
    Tested before every iteration, as long as the command runs.

These keywords are baked into the runtime, so they can't be used as command or condition keywords or as the syntax of 
commands or other conditions.

Conditions
----------

Conditionals are the framework for making decisions, but conditions are the decisions being made. Similar to commands,
conditions are derived from the base class ``ConditionBase``. However, because conditions tend to fall in a small 
number of categories, we will focus less on creating conditions and more on the pre-built condition classes that 
are provided by default.

For reference, the library provides conditions for numeric, string, and boolean conditions, in addition to timing
and relative value tracking. We'll detail each of the provided classes below.

If none of the pre-built classes work for you, we cover creating your own condition in :doc:`advanced/conditions`.


What now?
^^^^^^^^^

This is all a bit abstract, but that is for good reason. Conditions themselves are a bit more abstract, and generally there
are only a handful of operations you'll do in conditions, like equality, comparisons, use raw booleans, and comparing against
a timer. Since these cases are so common, there are pre-made classes built into the library that do these comparisons for you.
All you need to do is provide the input, which we'll describe how to do below by example.


Example Condition
-----------------

Using our :ref:`simple-robot-definition`, let's register a condition that checks for a target angle.

Now, we have two options here: we can write our own condition that handles all of this, or we can use one of the 
built-in comparison classes to do the test for use. Using the built-ins is simplest, and will cover a majority
of use cases.

.. note::
    We won't be describing how to create custom conditions here, but if you find that the existing 
    conditions don't cover your needs, that's covered in :doc:`advanced/conditions`.

Here's how we might create our condition. 

.. code-block:: python

    # This is the same file as we originally registered our commands in.
    # we need to import our pre-made condition
    import interpretercommand.conditions.numeric as ncond

    # ...
    # Down after we created our interpreter variable
    self.interpreter.register_condition("angle", ncond.NumericComparisonCondition, self.drive_subsystem.get_angle)
    
And that's it (they say as though any of this is self-explanatory)!

Some of this does look familiar though. Similar to ``register``, we need to give the condition a name and a class
to use for its tests. The last part is a little different though. Essentially, the Condition class is just the logic,
but we still need a source of input. That's what the last argument does. It must be some kind of callable object (i.e. 
a function or a class that overrides ``__call__()``) that takes no arguments and returns the value we want to compare
against. In this case, we use the ``get_angle`` method of our drive subsystem, which returns the angle we want to 
compare against.

Let's assume we have a command that allows us to rotate the robot continuously (this is left as an exercise to the 
reader). Now, using conditions, we can write an instruction that can turn the robot to (about) a given angle. Here's 
an example of turning to 90 degrees

.. code-block::
    
    rotate clockwise until angle >= 90

This is really simple and clear to read, and it does exactly what you expect it to do. And this is the power of the 
interpreter. With just a little extra work - not much more than writing the necessary components of the equivalent 
``SequentialCommandGroup`` - we can make a system that is arbitrarily flexible, and easy to tune.

.. _built-in-conditions:

Built-In Conditions
-------------------

Here's a comprehensive list of all of the built-in condition classes, including what you need to use them.

Numeric Conditions
^^^^^^^^^^^^^^^^^^

These conditions operate on numeric values. Floats are expected, but other numeric types should be valid.
To access these, you need to import ``interpretercommand.conditions.numeric``.

``NumericEqualityCondition``
    Compares a numeric value using equality operators. For real values, you should prefer ``NumericComparisonCondition`` s.

    ``==`` and ``=`` are used for equality. ``!=`` and ``=/=`` are used for inequality.

``NumericComparisonCondition``
    Compares a numeric value using comparison operators. These are the standard operators used in programming (i.e. 
    ``<``, ``>``, ``<=``, ``=>``).

String Conditions
^^^^^^^^^^^^^^^^^

These conditions check string values. They operate very similarly to the numeric types.
To access these, you need to import ``interpretercommand.conditions.string``.

``StringEqualityCondition``
    Compares are string value using equality operators. ``==`` and ``=`` are used for equality. ``!=`` and ``=/=`` are 
    used for inequality.

``StringLengthEqualityCondition`` / ``StringLengthComparisonCondition``
    These both take a string as input, then test against the string's length in exactly the same way as their 
    respective numeric conditions. 

Boolean Conditions
^^^^^^^^^^^^^^^^^^

This family is meant for more complex checks than can be expressed using the other condition classes. These operate the 
same way as the numeric and string conditions, but their input function is expected to return a boolean. This allows
the user to express more complex ideas like compound conditions (`and`/ `or`) without strictly needing to make a new 
condition class.

To access these, you need to import ``interpretercommand.conditions.boolean``.

``BooleanCondition``
    This does exactly what it says on the tin. It's true if the the test is true, false otherwise.

When you import the boolean conditions, two conditions, ``true`` and ``false``, are automatically registered to 
the interpreter, and they both behave exactly as you would expect. These are rarely useful in practice, but can be 
handy for testing purposes.

.. _time-conditions:

Time Conditions
^^^^^^^^^^^^^^^

It's often useful to only run a command for a certain amount of time. That is what this is for.
To access these, you need to import ``interpretercommand.conditions.time``.

``TimerCondition``
    Returns true when a certain amount of time has elapsed, as specified in the program. The syntax for this 
    condition is ``<n> second[s]``, preceded by whatever keyword you use to register it.

This condition is special because you need to use a specific function to initialize it, namely ``TimerCondition.make_timer()``.
This is also different because you have to call the function, as you want the callable it returns, not the function
itself.

Here is an example of a time condition being registered.

.. code-block:: python

    import interpretercommand.conditions.time as time_con

    # ...

    self.interpreter.register_condition("elapsed", time_con.TimerCondition, time_con.TimerCondition.make_timer())

It's a bit of a mouthful, but you'll likely only need one time condition per interpreter, as they're all disjoint and similar.
Adding a second would likely add no more value on top of a single timer condition.

Relative Conditions
^^^^^^^^^^^^^^^^^^^

This is the most abstract of the lot, largely because it would be generally useless if it were any more specific.
This condition family measures the change in some data source from when the condition started being evaluated.
This is useful for any relative data type, but especially for basic odometry.

``RelativeCondition``
    Given a data source, uses the tests from ``NumericComparisonCondition`` to compare the mathematical distance 
    between the current data and when it started being tested.

Similar to ``TimerCondition``, you need to use a special class, ``RelativeCondition.RelativeData``, to work.
You can use the function ``RelativeCondition.new_data`` to get that type. It takes a data source, which can return 
data of any type, and a function that returns a ``float`` representing the distance between the starting point and
the current point.

Here's an example of it in action, with a drive system that has odometry built in, using WPILib's ``Translation2d``.

.. code-block:: python

    import interpretercommand.condition.relative as rel_con

    # ...

    distance_data = rel_con.RelativeCondition.new_data(self.drive_subsystem.get_position, wpilib.Translation2d.distance)

    self.interpreter.register_condition("distance", rel_con.RelativeCondition, distance_data)

Not as straightforward as some of the other conditions, but as long as you're comfortable with first-class functions, you 
should be fine.

Revisiting ``DriveTimeInstruction``
-----------------------------------

Now that we've talked about conditions, let's revisit our ``DriveTimeInstruction`` from the 
:ref:`section on commands <full-command-example>`. In that Command, we handled the logic of termination internally, but
we can handle it in a functionally similar way by using a condition with a more generic command.

First, we would need to simplify the Command and remove the time controls from it, like so:

.. code-block:: python

    class DriveInstruction(ic.InstructionCommand):
        drive_subsystem: DriveSubsystem
        speed: float

        def __init__(self, subsystem: DriveSubsystem, speed: float):
            super.__init__()

            self.drive_subsystem = subsystem
            self.speed = speed

            self.addRequirements(subsystem)
        
        def execute(self) -> None:
            self.drive_subsystem.drive(self.speed, 0)
        
        def isFinished(self) -> bool:
            return False
    
        @staticmethod
        def syntax() -> str:
            return "(at|@) <speed>"
        
        @staticmethod
        def validate_arguments(args: list[str]) -> bool:
            try:
                assert len(args) == 2
                assert args[0] == "at" or args[0] == "@"
                assert -1 <= float(args[1]) <= 1
            except (ValueError, AssertionError):
                return False
            else:
                return True
    
        @staticmethod
        def parse_arguments(args: list[str]) -> list[Any]:
            return [float(args[1])]

Now, using a built-in timer condition that we registered in the :ref:`example above <time-conditions>`, we could express the 
``DriveTimeInstruction`` driving at half speed for 1 second as

.. code-block::

    drive at 0.5 until elapsed 1 second

This is admittedly a little harder to read than ``drive at 0.5 for 1 second``, but the benefit is that time controls are 
now handled by a single condition, instead of being distributed between commands and conditions.


Closing Thoughts
----------------

Conditions are a somewhat complicated concept, by necessity, but you'll rarely need to write your own, in favor of just using 
the pre-made conditions. Even for complex comparisons, ``RelativeCondition`` can do a lot of heavy lifting, without needing
to write a whole new condition.

Because conditions exist, it's usually a good idea to make your commands as generic as possible, and let the conditionals 
do the heavy lifting around lifetimes and termination. This allows you to write more flexible languages that are more expressive
than more complex commands could be. However, this is not a hard and fast rule, and it's sometimes more reasonable to have 
the full logic bound into a single command, especially when the terminating condition isn't likely to be used with anything else.
