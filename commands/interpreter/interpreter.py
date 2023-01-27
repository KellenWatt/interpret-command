import wpilib
import commands2 as commands
import itertools

from typing import Callable, Type, Any
from dataclasses import dataclass

from .exceptions import *

class ConditionBase:
    getter: Callable
    tokens: tuple[str]
    invert: bool
    def __init__(self, getter: Callable[[], Any], invert: bool, type: str, *tokens: str):
        self.getter = getter
        self.tokens = tokens
        self.invert = invert
        self.type = type

    def _result(self) -> bool:
        res = self.test(self.getter(), *self.tokens)
        return (res and not self.invert) or (not res and self.invert)

    def _is_continuous(self) -> bool:
        return self.type == "continuous"

    def _is_initial(self) -> bool:
        return self.type == "initial"

    @staticmethod
    def test(input: Any, *tokens: str) -> bool:
        raise NotImplementedError()

class ModularCommand(commands.CommandBase):
    """Base class for Commands accepted by InterpretCommand.
    Allows for instruction arguments to be handled earlier, resulting in a more predictable program.

    Requires subclasses to implement `parse_arguments`.

    `validate_arguments` is useful for sanity-checking arguments before execution.
    """
    def parse_arguments(args: list[str]) -> list[Any]:
        """Parse arguments provided by the interpreter.

        Takes a list of strings - the tokens provided by the interpreter - and returns a list of values 
        those tokens translate to. These values will then be passed to the constructor for the ModularCommand,
        using the splat (*) operator.
        If the command does not need any more information to run than an instance, it can be passed an 
        empty list of tokens and return an empty list of values. The returned list does not need to be 
        the same length as the input.

        This is used by the parser as a convenience feature. All information having to do with lists, aside
        from expansion are entirely controlled by the user.
        """
        raise NotImplementedError()
    
    def validate_arguments(args: list[str]) -> bool:
        """Check that given arguments are valid. Returns True by default.

        Implementations can check whether the arguments provided by the interpreter are valid,
        before the program is run, in order to prevent any syntax errors, without compiling.
        """
        return True


@dataclass
class CompiledInstruction:
    command: commands.CommandBase
    condition: ConditionBase | None

    def hasCondition(self) -> bool:
        return self.condition is not None



class InterpretCommand(commands.CommandBase):
    """A robot command that allows for modular execution of sub-commands.

    Command classes can be registered to a unique keyword, then an interpreter will parse text
    loaded into it (the 'program') into those commands, passing any additional arguments to the 
    commands to alter their behaviour.

    Any class derived from CommandBase should work fine, but a special interface called ModularCommand
    has been provided that allows for additional validation and parsing during compilation.

    Programs can be handled in 3 different ways: pure interpretation, JIT compilation, and pre-compilation.
    A purely interpreted program will be reinterpreted every time it is run. This is useful for programs that
    will only be run once or at most infrequently. JIT compiled programs will be compiled as executed, and the
    resulting commands will be cached for later use, which is useful for programs that will be run frequently, 
    especially longer ones. Pre-compiled programs are compiled before execution, and only the resulting commands
    are referenced during execution. This is most useful for short programs that need to run quickly. Longer 
    programs will incur a high initial cost, which will likely cause the robot to overrun its loop time. Of the
    3 approaches, JIT is the most generally recommended, and is the default. Compilation is 
    only recommended if you see a meaningful performance bottleneck with JIT. Interpretation is most recommended
    when the loaded program will change frequently, and any program will only be run once or twice.

    Please don't try to use this command in a command group. It will probably work, but will likely be prone to
    odd bugs. Whatever you're trying to accomplish can be done by registering the other commands in the group to 
    this command, then incorporating them into your program.
    """
    instruction_set: dict[str, tuple[commands.CommandBase, list[str]]]
    condition_set: dict[str, tuple[ConditionBase, Callable[[], Any]]]
    instructions: list[str]

    jit_compiled: bool

    step: int
    current_command: CompiledInstruction
    command_sequence: list[CompiledInstruction]

    def __init__(self, requirements: list[commands.SubsystemBase] = []) -> None:
        super().__init__()
        self.instruction_set = {}
        self.condition_set = {}
        self.instructions = []
    
        self.jit_compiled = True
        self.command_sequence = []

        self.addRequirements(requirements)
        self.reset()
    
    def register(self, keyword: str, command: Type[commands.CommandBase], *args) -> None:
        """Registers a command to a keyword. Any additional arguments to the command constructor can be provided here.
        If any of the arguments are instances of SubsystemBase, they are assumed to be requirements for that command, 
        and are added to this class.
        
        Instruction is a unique word that identifies the command. For instance, to control a drivetrain, 
        the instruction might be "drive" or "move".

        Any subsystem requirements for the registered command should be included via `requirements`. This will not 
        set the requirements on that command, but it sets them on this InterpretCommand. Subcommands do not need to
        have requirements set, since they are implicitly set by this command.
        """
        if not isinstance(command, Type):
            raise TypeError("provided command must be in class form")
        self.instruction_set[keyword] = (command, args)
        reqs = [a for a in args if isinstance(a, commands.SubsystemBase)]
        self.addRequirements(reqs)

    def register_condition(self, keyword: str, condition: Type[ConditionBase], getter: Callable[[], Any]):
        if not isinstance(condition, Type):
            raise TypeError("provided condition must be in class form")
        self.condition_set[keyword] = (condition, getter)

    
    def check_instruction(self, inst) -> None:
        """Checks if an instruction has been registered. If it hasn't, raises an InstructionNotFoundError. 
        
        If the associated instruction exists, and is a subclass of ModularCommand, the arguments in the 
        instruction will be validated, according the class' implementation of `validate_arguments`.
        """
        if " if " in inst:
            instruction = inst.split(" if ")[0]
        elif " unless " in inst:
            instruction = inst.split(" unless ")[0]
        elif " while " in inst:
            instruction = inst.split(" while ")[0]
        elif " until " in inst:
            instruction = inst.split(" until ")[0]
        else:
            instruction = inst
        key, *tokens = instruction.split(" ")
        if key not in self.instruction_set:
            raise InstructionNotFoundError("'{}' is not a registered instruction".format(inst))
        klass, _ = self.instruction_set[key]
        if issubclass(klass, ModularCommand):
            
            if not klass.validate_arguments(tokens):
                raise CommandSyntaxError("'{}' is not a valid argument set for '{}'".format(tokens, klass.__name__))
    
    def load_program(self, instructions: str | list[str] | Callable[[], str | list[str]], compile: bool = False, jit: bool = True) -> None:
        """Set the program to be run, performing basic syntax checking on instructions.
        
        If the command is currently scheduled, an ExecutionError will be raised.
        
        Can take either a string, a list of strings, or callable that can produce either of those.
        - Plain strings will be treated as an unparsed program, and will be split across lines and periods, in that order.
        - Lists of strings will be treated as a parsed program, and will be used directly.
        - Callables will be called, and then the result will be handled according to the above rules.

        The `jit` flag indicates whether the program should be JIT-compiled. This is the same as calling `enable_jit_compiler`
        after loading the program. Note that this does reset the JIT flag internally, so if your program had JIT enabled 
        before, but you don't tell it to here, it won't be enabled. This has functionally no effect if the compile flag is set.
    
        The `compile` flag indicates whether the program should be pre-compiled. When set to True, this is the same calling 
        `compile` after loading the program.
        """
        if self.isScheduled():
            raise ExecutionError("Can't set a new instruction set when the interpreter is running")
        
        if callable(instructions):
            instructions = instructions()
            if not isinstance(instructions, str) and not isinstance(instructions, list):
                raise ValueError("instruction callable must return str or list[str]")

        if isinstance(instructions, str):
            insts = [inst.split(";") for inst in instructions.split("\n")]
            insts = itertools.chain.from_iterable(insts)

            self.instructions = [i.strip() for i in insts if len(i.strip()) > 0]
        elif isinstance(instructions, list):
            self.instructions = instructions

        for inst in self.instructions:
            self.check_instruction(inst)

        if compile:
            self.compile()
        self.jit_compiled = jit


    def enable_jit_compiler(self, enable: bool = True) -> None:
        """Enables Just-In-Time compilation. Necessary commands will be created as encountered, and then cached.

        This is recommended for programs that will be re-run often, as it prevents
        recompiling the program every time. Each step of the program has to be 
        compiled anyway, so this prevents unnecessary work, if that work might have 
        a meaningful cost. 

        This has no effect if the program is pre-compiled at any point before execution.
        """
        self.jit_compiled = enable


    def _compile_instruction(self, instruction: str) -> CompiledInstruction:
        inverted = False
        condition_type = "initial"
        if " if " in instruction:
            inst, *condition = instruction.split(" if ", maxsplit=1)
        elif " unless " in instruction:
            inst, *condition = instruction.split(" unless ", maxsplit=1)
            inverted = True
        elif " while " in instruction:
            inst, *condition = instruction.split(" while ", maxsplit=1)
            condition_type = "continuous"
        elif " until " in instruction:
            inst, *condition = instruction.split(" until ", maxsplit=1)
            condition_type = "continuous"
            inverted = True
        else:
            inst, condition = instruction, None

        cmd = self._compile_command(inst)

        cond = None
        if condition != None and len(condition) != 0:
            if len(condition) != 0:
                cond = self._compile_condition(*condition, inverted, condition_type)
            else:
                raise CommandSyntaxError("Conditional does not have a condition")

        return CompiledInstruction(cmd, cond)
        
    
    def _compile_command(self, command: str) -> commands.CommandBase:
        key, *tokens = command.split(" ")
        klass, args = self.instruction_set[key]
        if issubclass(klass, ModularCommand):
            tokens = klass.parse_arguments(tokens)
        return klass(*args, *tokens)


    def _compile_condition(self, condition: str, inverted: bool, type: str) -> ConditionBase:
        key, *tokens = condition.split(" ")
        klass, f = self.condition_set[key]
        return klass(f, inverted, type, *tokens)
        

    def compile(self) -> None:
        """Compiles the loaded program into command form. This is not necessary to run the code.
        
        You may want to refrain from calling this unless your program is small (for some definition).
        This is because this compiles everything in one cycle, including parsing instructions and 
        generating commands. This can get expensive for larger programs, and cause the robot to 
        overrun loop time.

        In interpreter or JIT mode, the same work is done, but the cost is likely to be distributed 
        over human time scales, making it less significant.
        """
        if len(self.command_sequence) != 0: 
            self.command_sequence = []

        for inst in self.instructions:
            result = self._compile_instruction(self, inst)
            self.command_sequence.append(result)

    
    def reset(self) -> None:
        """Resets the interpreter to its initial state. If the command is currently running, it is canceled.
        
        If running in JIT mode, work done until the reset is cached.
        """
        if self.isScheduled():
            self.cancel()

        self.current_command = None
        self.step = -1

    def initialize(self) -> None:
        pass
    
    def execute(self) -> None:
        if self.current_command == None or self.current_command.command.isFinished():
            self.step += 1
            
            while not self.isFinished():
                if len(self.command_sequence) > self.step:
                    cmd = self.command_sequence[self.step]
                else:
                    cmd = self._compile_instruction(self.instructions[self.step])
                    # command has to get compiled either way, but we only store it if using JIT
                    if self.jit_compiled:
                        self.command_sequence.append(cmd)

                if not cmd.hasCondition() or cmd.condition._result():
                    break
                self.step += 1
            else:
                # We are, in fact, finished
                return

            self.current_command = cmd
            self.current_command.command.initialize()

        self.current_command.command.execute()
        if self.current_command.command.isFinished():
            self.current_command.command.end(False)

    def end(self, interrupted: bool) -> None:
        if interrupted and self.current_command != None:
            self.current_command.command.cancel()
        self.reset()

    def isFinished(self) -> bool:
        if len(self.command_sequence) == len(self.instructions):
            # we either pre-compiled or fully jit-compiled
            return self.step >= len(self.command_sequence)
        else:
            # just interpreting or not fully jit-compiled
            return self.step >= len(self.instructions)


