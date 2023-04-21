Custom Conditions
=================

.. warning::

    If you're on this page looking for how to write a condition, and you haven't used them before, 
    there's a good chance you shouldn't be here. The :ref:`built-in-conditions` will do a lot of the 
    work you want done, albeit maybe not with the exact syntax you want.


As mentioned in :doc:`conditions`, conditions work very similar to commands, in that they inherit from
a base class, and they define their own syntax. The only additional behaviour is that conditions also have 
a ``test`` method that is used to evaluate the condition at runtime. The other methods required are the same 
as ``InstructionCommand`` and are :ref:`detailed here <instruction_command>`, so we won't cover them here.

``test()``
----------
This method is extremely straightforward. All it does is, given some input to test against, returns a value based on the 
condition as written in the program. The signature of the function is as follows.

.. code-block:: python

    @staticmethod
    def test(input: Any, *tokens: Any) -> bool:
        # do some kind of test using the tokens

The ``input`` parameter is provided by the function provided when the condition is registered, and the ``tokens`` are 
the values returned by ``parse_arguments`` (which, again, works the same way it does for commands).

An Example
----------

To show you how to make a condition, we'll make one that does equality comparison on any type (theoretically). 
Specifically, we'll check the equality as in Python's ``is`` operator.

.. note::

    Technically, ``is`` and ``==`` don't have exactly the same meaning in Python. ``==`` is meant to imply value 
    equality, while ``is`` means identity (the objects have the same address). Take a look at the following example to 
    show the difference.

    .. code-block:: python

        class A:
            def __init__(self, n):
                self.n = n

            # This is the method called by `==`
            def __eq__(self, other):
                return self.n == self.other)

        foo = A(1)
        bar = A(1)

        print(foo == bar)
        print(foo is bar)

    These two ``print`` statements will print ``True`` and ``False``, respectively.

As we said before, most cases are already covered by the built-in conditions. In this case, this behaviour is practically
covered by ``NumericEqualityCondition`` and ``StringEqualityCondition``. However, we'll write this condition, even if it 
isn't strictly useful in practice. We'll write the code, then explain it. If you're familiar with ``InstructionCommand``, 
this should be fairly straightforward.

.. code-block:: python

    class IsCondition(ic.ConditionBase):
        @staticmethod
        def validate_arguments(args: list[str]) -> bool:
            try:
                assert len(args) == 2 or len(args) == 3
                assert args[0] == "is"
                if len(args) == 3:
                    assert args[1] == "not" 
                float(args[-1])
            except (ValueError, AssertionError):
                return False
            return True
        
        @staticmethod
        def parse_arguments(args: last[str]) -> list[Any]:
            return [float(args[-1]), len(args) == 3]

        @staticmethod
        def syntax() -> str:
            return "is [not] <value>"
        
        @staticmethod
        def test(input: float, *args: str) -> bool:
            invert = args[1]
            val = args[0]

            return not invert and val is input

You'll notice a few things. First, this looks pretty similar to defining a command, because it largely works the 
same. Second, you'll notice there's no ``__init__`` method. This is because condition constructors
are expected by the interpreter to have a certain signature, and ``CommandBase`` provides the signature and logic. 

Now we can register this the same way we would the built-ins, and we have a condition that checks for identity.
