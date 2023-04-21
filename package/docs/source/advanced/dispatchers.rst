Sharing Names: Dispatchers
==========================

When using the interpreter, you'll probably find very quickly that it's hard to come up with readable, 
human-friendly command names. For example, "drive" is a very common name. Some programs may find it useful
to have "forward" and "reverse" variants. As is, we would have to have some variant of "driveforward", 
"drive-forward", or "drive_forward", or some variant of that. This works, but it somewhat negates the
human-friendly aspect. We would much rather have something like "drive forward", but the interpreter 
only reads the first token, and "drive forward" is two tokens. We could write ``"drive forward"``, in quotes, 
but again, that hurts the human-friendly part.

The solution to our problem is to use a dispatcher. Conceptually, a dispatcher is something that has an 
identifier, like a name or a number, that once sent a message and another identifier, can *dispatch* that message
to something in a subgroup under its influence using that identifier. An example is a phone number extension inside 
a company: the phone number is the unique address of the company, and the extension is the identifier to reach 
something inside of the company. IP addresses on computer networks work in a very similar way, as do apartment 
numbers in apartment buildings.

In our hypothetical example, we could associate some kind of dispatcher with the keyword "drive" that wouldn't
do anything by itself, but it would dispatch based on whether it got "forward" or "backward", and run different
commands as a result.

``DispatcherBase``
------------------

The solution the interpreter uses is yet another "Base" class, this time called ``DispatcherBase``. 

We still need to create a class and inherit from it, but this time, we don't need to write any specific static 
methods. Instead, all we need to do is override the ``__init__()`` method, and call a few specific class methods 
in it that create our dispatch group.

Here's an example of how we could write our earlier "drive forward/backward" example. We will assume we have 
separate commands for driving forward and backward (in reality, these would probably be the same).

.. code-block:: python
    
    class DriveDispatcher(ic.DispatcherBase):
        def __init__(self, subsystem: DriveSubsystem, *args):
            self.register_target("forward", DriveForwardCommand, subsystem)
            self.register_target("backward", DriveBackwardCommand, subsystem)

            super().__init__(*args)

Then all we need to do is register the dispatcher like any other command, like so:

.. code-block:: python
    
    self.interpreter.register("drive", DriveDispatcher, drive_subsystem)

And there you go! Now you can write "drive forward", and "drive backward" in your program, and it will run the 
appropriate command! It's a little more work, but it makes your language much easier to understand for everybody,
including programmers. Now, let's break down what each of these lines do.

First, we make a class that subclasses ``DispatcherBase``. Then we make several calls to ``register_target``. This 
function has the same syntax as ``InterpreterCommand.register``, so there's nothing new here. Finally, we make 
sure to call ``super().__init__(*args)``. This is the single most important line, as this is what does the dispatching.
Once we create an instance of our dispatcher, it behaves like the command it's being dispatched to, acting only as 
a transparent container. The ``*args`` part is what passes the arguments to the internal command, so don't forget it!

As long as you hold to this pattern, there's not much to think about. It essentially works the same as registering 
normal commands, except the dispatcher looks at the second keyword in a command instead of the first.

.. note::
    ``DispatcherBase`` is ultimately just a subclass of ``CommandBase`` with some special logic to handle abstractions.
    This has two major implications of varying consequence. First, you can technically use it like any other Command,
    though because it does dispatching automatically, this is of limited-to-no use. The other, much more interesting 
    side effect is that you can register a dispatcher to a dispatcher if you want to branch on second-level keywords.
    Technically, this can go forever, but beyond two or three likely has sharply diminishing returns.

Default Branches
^^^^^^^^^^^^^^^^

We mentioned earlier that if you register a dispatcher to a keyword, then that keyword loses meaning outside of 
dispatch. However, this isn't always the most ergonomic solution. In our "drive" example, we may want to register
a command that simply does free driving using the "drive" keyword, without any secondary keywords. Fortunately,
``DispatcherBase`` offers the ``register_default`` method, which registers a command that is run when no other branches
are matched.

We can update our previous example to include this, using a hypothetical Command that does driving.

.. code-block:: python
    
    class DriveDispatcher(ic.DispatcherBase):
        def __init__(self, subsystem: DriveSubsystem, *args):
            self.register_target("forward", DriveForwardCommand, subsystem)
            self.register_target("backward", DriveBackwardCommand, subsystem)

            self.register_default(DriveCommand, subsystem)

            super().__init__(*args)

This looks basically the same as registering a normal branch, but we don't provide a keyword, since the keyword it's 
using is the one that triggers the dispatcher in the first place.
            
Dispatchers for Conditions
--------------------------
 
Presently, there is no support for dispatchers for conditions. That isn't to say that it's not possible, but practice
has suggested there isn't need for condition dispatchers, as most contexts in the domain of FIRST have many more outputs 
than inputs, thus requiring fewer names for inputs than outputs. This makes it easier to come up with intuitive, 
non-conflicting names for conditions than it does for commands.

This may change in future versions.