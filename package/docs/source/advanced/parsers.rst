Customizing Parsing
===================

A feature of the interpreter is that its general purpose parser can be changed. But first, we need to talk about how 
parsing is structured in this interpreter.

What is a Parser?
-----------------

In a general context, a parser is an algorithm that takes a list of tokens and outputs a structure that gives
meaning to those tokens.

In the case of this library, the parser is split into two parts, the general purpose parser and command-specific 
parsers. The general purpose parser is a callable that takes a list of strings, representing a single line/instruction.
This parser is called for each and every instruction, and returns a list of processed tokens, by default converting 
values it recognizes into their respective types, and otherwise leaving them as strings. This parser can be anything 
that behaves like a function that takes a ``list[str]`` and returns a ``list[Any]``.

The command-specific parser is represented by ``parse_arguments``. This part of the parsing is intended to remove
the syntactical extras, leaving only the necessary data, formatted in a way that is constructor-friendly. We already
covered how this works when we talked about writing an :ref:`InstructionCommand <instruction_command>`, so we won't be 
covering this here.

Built-ins
---------

At present, there are two parsers provided with the library: ``identity_parser``, and ``typed_parser``. These live in 
the ``interpretercommand.parsers`` library.

``identity_parser``
^^^^^^^^^^^^^^^^^^^

This is basically a no-op. It does no processing on the token list, and returns it as-is. It used to be the default, 
but now exists mainly as a historical artefact, in case somebody finds use for it.

``typed_parser``
^^^^^^^^^^^^^^^^

This parser tests each token against a list of patterns associated with types. If the token matches one of the patterns,
it is converted to that type in an output list. This parser is the default, as it allows for the use of built-in 
Commands without building an ``InstructionCommand`` proxy.

Presently, the parser only recognizes ``bool`` and ``float``, with ``str`` being the fallback if it fails to recognize 
another type. You can add a type to the parser by calling the function ``register_token_type`` (comes from the same 
place as the built-in parsers), which takes a `regex <https://docs.python.org/3/howto/regex.html>`_ and a callable
that converts the token into the appropriate type, given a string. 

Making a Custom Parser
----------------------

For a vast majority of basic use, you'll probably only need ``typed_parser``, possibly with a custom type or two.
However, it has one significant weakness, and that is that it only operates on single tokens. However, it's possible
that you may run into a situation where it's useful to operate on multiple tokens at once. This is the primary case 
where you may want to write a custom parser.

Here we'll go through the process of writing a parser that's capable of processing comments. This is sometimes the 
job of the tokenizer for a language, but since the tokenizer here is fixed for simplicity, it falls on the parser. 
We'll make the comments work like Python ones, where everything following a pound/hash/octothorpe ("#") is ignored.

This isn't a lesson on how to write a parser in general, so we won't cover how to get to the solution. Instead, we'll 
just show you the code and highlight the important parts.

.. code-block:: python

    # This could also be a class that overrides __call__(). This could be useful for more complex parsers.
    def comment_parser(tokens: list[str]) -> list[Any]:
        # Prepare an output list
        output = []

        # Store successive tokens until we find a comment, then discard everything after it.
        for t in tokens:
            if t.startswith("#"):
                break
            output.append(t)
        
        # return our token list.
        return output
    
And it's just that simple. It's important to note here that the only thing this parser does is strip comments. Otherwise,
it's no different to the ``identity_parser``. However, since all parsers for this environment are inherently callable, we 
could theoretically nest a parser inside another, just by calling it on the other's results. For example, we could call
``typed_parser`` on ``output``, and that would have the effect of creating a compound parser that strips comments and
converts tokens to values.

.. note::
    This parser has one bug where it will treat quoted strings that start with "#" as starting comments, which is not 
    desirable. Solving this, while not complicated, is beyond the scope of this example, and is likely such a rare case 
    in practice that it isn't worth accounting for.

Using the Parser
----------------

Changing parsers is relatively simple, but can only be done upon constructing your ``InterpreterCommand``. All you need
to do is supply the ``parser`` option, and set it equal to the parser you want to use. So to use our new ``comment_parser``,
we would write

.. code-block:: python

    self.interpreter = ic.InterpreterCommand(parser = comment_parser)

And you're done!
            