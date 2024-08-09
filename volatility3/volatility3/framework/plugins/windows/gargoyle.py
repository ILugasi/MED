# This file is Copyright 2024 Volatility Foundation and licensed under the Volatility Software License 1.0
# which is available at https://www.volatilityfoundation.org/license/vsl-v1.0
#

import logging
import io
import struct

from typing import Iterator, List, Tuple, Iterable

import pefile

from volatility3.framework import (
    exceptions,
    renderers,
    interfaces,
    constants,
    symbols,
)
from volatility3.framework.configuration import requirements
from volatility3.framework.objects import utility
from volatility3.framework.renderers import format_hints
from volatility3.framework.symbols.windows import versions
from volatility3.framework.symbols import intermed
from volatility3.framework.symbols.windows.extensions import pe
from volatility3.plugins.windows import malfind, timers

from unicorn import *
from unicorn.x86_const import *

vollog = logging.getLogger(__name__)
FORMAT_LIST = [
    ("PID", int),
    ("Process", str),
    ("Handler", format_hints.Hex),
    ("Adjusted page permissions", str),
    ("Branched to code after altering page permission", str),
    ("Probable payload", format_hints.Hex),
    ("Prolog", interfaces.renderers.Disassembly),
]

class timerResult():
    def __init__(self, context, process, thread, timerRoutine, is_64bit):
        self.thread = thread
        self.process = process
        self.routine = timerRoutine
        self.didROP = "Unknown"
        self.didAdjustPerms = "Unknown"
        self.didJumpToAdjusted = "Unknown"
        self.adjustedAddresses = []
        self.probablePayload = 0
        self.prolog = "Unknown"

        proc_layer_name = process.add_process_layer()
        proc_layer = context.layers[proc_layer_name]
        instrStream = proc_layer.read(timerRoutine, 5)

        # if we're on a 64 bit kernel, we may still need 32 bit disasm due to wow64
        if is_64bit and not process.get_is_wow64():
            architecture = "intel64"
        else:
            architecture = "intel"

        if not instrStream:
            print("Process %s '%s': Can't read instruction stream at %s; perhaps it is paged out" % (
            hex(int(process.obj_offset)), process.ImageFileName, hex(timerRoutine)))
        else:
            self.prolog = interfaces.renderers.Disassembly(instrStream, timerRoutine, architecture)


class Gargoyle(interfaces.plugins.PluginInterface):
    """Detect gargoyle evasion technique payload in memory"""

    _required_framework_version = (2, 0, 0)
    _version = (1, 0, 0)

    @classmethod
    def get_requirements(cls) -> List[interfaces.configuration.RequirementInterface]:
        return [
            requirements.ModuleRequirement(
                name="kernel",
                description="Windows kernel",
                architectures=["Intel32", "Intel64"],
            ),
            requirements.ListRequirement(
                name="pid",
                element_type=int,
                description="Process IDs to include (all other processes are excluded)",
                optional=True,
            ),
            requirements.BooleanRequirement(
                name="dump",
                description="Extract payloads",
                default=False,
                optional=True,
            ),
            requirements.BooleanRequirement(
                name="verbose",
                description="Show verbose information",
                default=False,
                optional=True,
            ),
            requirements.VersionRequirement(
                name="timers", component=timers.Timers, version=(1, 0, 0)
            ),
        ]

    def dbgMsg(self, *args):
        if self.config["verbose"]:
            print(" ".join(map(str, args)))

    # This is called when Unicorn needs to access some memory that isn't mapped yet.
    # We simply map the memory, copy in its contents from the debuggee, and return.
    # Our main loop will retry. We signal errors by setting self.emulationFaulted.
    def badmemWrapped(self, uc, access, address, size, value, user_data):
        self.dbgMsg("Access to unmapped memory %s" % hex(address))

        if self.pas == None:
            self.dbgMsg("Unable to handle memory mapping with no active process")
            raise MemoryError

        # Unicorn will only successfully map page-aligned addresses, so map the whole page.
        pageSize = 0x1000
        pageBase = address & (~(pageSize - 1))
        uc.mem_map(pageBase, pageSize)

        # Read from the debuggee..
        pageCts = self.pas.read(pageBase, pageSize)
        if pageCts == None:
            self.dbgMsg("Unable to read %s bytes at %s" % (hex(pageSize), hex(pageBase)))
            raise MemoryError

        # And write to Unicorn.
        uc.mem_write(pageBase, pageCts)
        self.dbgMsg("Mapped %s bytes at base %s" % (hex(pageSize), hex(pageBase)))

        return True

    def badmem(self, uc, access, address, size, value, user_data):
        try:
            return self.badmemWrapped(uc, access, address, size, value, user_data)
        except Exception as e:
            self.emulationFaulted = e
            raise

    def isKernelSpace(self, DllBase):
        kernel = self.context.modules[self.config["kernel"]]
        symbol_table = kernel.symbol_table_name

        is_64bit = symbols.symbol_table_is_64bit(self.context, symbol_table)

        if is_64bit:
            return DllBase < 0x8000000000000000
        else:
            # TODO: support 3GB address mode, if it's worth it
            return DllBase < 0x80000000

    def _get_pefile_obj(
            self, pe_table_name: str, layer_name: str, base_address: int, dllName: str
    ) -> pefile.PE:
        """
        Attempts to pefile object from the bytes of the PE file

        Args:
            pe_table_name: name of the pe types table
            layer_name: name of the process layer
            base_address: base address of dll in process
            dllName: the name of the dll

        Returns:
            the constructed pefile object
        """
        pe_data = io.BytesIO()

        try:
            dos_header = self.context.object(
                pe_table_name + constants.BANG + "_IMAGE_DOS_HEADER",
                offset=base_address,
                layer_name=layer_name,
            )

            for offset, data in dos_header.reconstruct():
                pe_data.seek(offset)
                pe_data.write(data)

            pe_ret = pefile.PE(data=pe_data.getvalue(), fast_load=True)

        except exceptions.InvalidAddressException:
            vollog.debug(f"Unable to reconstruct {dllName} in memory")
            pe_ret = None

        return pe_ret

    def findExportInModuleList(self, process, moduleList, moduleName, exportName):
        moduleNameLowercase = moduleName.lower()
        exportNameLowercase = exportName.lower()

        for m in moduleList:
            try:
                dllName = m.BaseDllName.String.lower()
            except:
                continue
            if dllName == moduleNameLowercase:
                # Cache per-process (since a module may appear in a different process at a different base). For kernel modules
                # there's no need to be per-process, so don't bother.
                if self.isKernelSpace(m.DllBase):
                    cacheKey = "%s!%s (kernel)" % (moduleNameLowercase, exportNameLowercase)
                else:
                    cacheKey = "%s!%s %s" % (moduleNameLowercase, exportNameLowercase, hex(m.DllBase))
                if cacheKey in self.exportCache.keys():
                    return self.exportCache[cacheKey]

                pe_table_name = intermed.IntermediateSymbolTable.create(
                    self.context, self.config_path, "windows", "pe", class_types=pe.class_types
                )

                proc_layer_name = process.add_process_layer()
                dll_pe_file = self._get_pefile_obj(pe_table_name, proc_layer_name, m.DllBase, dllName)
                if not dll_pe_file:
                    return None

                dll_pe_file.parse_data_directories(
                    directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]]
                )

                for export in dll_pe_file.DIRECTORY_ENTRY_EXPORT.symbols:
                    exported_function_name = export.name.decode('utf-8').lower()
                    if exported_function_name == exportNameLowercase:
                        toReturn = m.DllBase + export.address
                        self.dbgMsg("Found %s ! %s at %s (%s)" % (
                        dllName, exported_function_name, hex(toReturn), hex(m.DllBase)))
                        self.exportCache[cacheKey] = toReturn
                        return toReturn

        return None

    def findExport(self, process, moduleName, exportName):
        if process.get_is_wow64():
            # WoW64 processes are treated specially, since we must get 32bit modules via the 32bit PEB.
            print("Wow64 processes are not supported right now")
            return None
        else:
            # Not a WoW64 process, so just get the modules normally.
            modList = process.mem_order_modules()

        exp = self.findExportInModuleList(process, modList, moduleName, exportName)
        if exp == None:
            print("Unable to find export %s!%s in process %s" % (
            moduleName, exportName, utility.array_to_string(process.ImageFileName)))
        return exp

    def examine(self, process, thread, routine, apc, timer, symbol_table, is_64bit) -> Iterator[timerResult]:
        # We will now emulate through the instruction stream, starting at the APC handler, and see if anything fishy
        # goes on. Specifically, we will see if the APC calls VirtualProtect. If it does, we will see if it also
        # tries to jump to the newly-VirtualProtect'ed memory - a sure sign of Gargoyle-ness.
        VirtualProtect = self.findExport(process, "KERNEL32.DLL", "VirtualProtect")
        VirtualProtectEx = self.findExport(process, "KERNEL32.DLL", "VirtualProtectEx")
        # We'll need to set the process address space so that our badmem callback can use it later on.
        proc_layer_name = process.add_process_layer()
        self.pas = self.context.layers[proc_layer_name]

        result = timerResult(self.context, process, thread, routine, is_64bit)
        self.dbgMsg("Timer %s APC %s routine %s in process %s ('%s') thread %s" % (
        hex(int(timer.vol.offset)), hex(int(apc.vol.offset)), hex(routine), hex(int(process.vol.offset)),
        utility.array_to_string(process.ImageFileName), hex(thread.StartAddress)))


        if (is_64bit):
            unicornEng = Uc(UC_ARCH_X86, UC_MODE_64)
        else:
            unicornEng = Uc(UC_ARCH_X86, UC_MODE_32)
        
        if (is_64bit):
            instruction_pointer= UC_X86_REG_RIP
            stack_pointer = UC_X86_REG_RSP
        else:
            instruction_pointer= UC_X86_REG_EIP
            stack_pointer = UC_X86_REG_ESP
        SYSCALL_OPCODE = bytearray(b'\x0f\x05')
        # Populate the context from which to start emulating.
        # We use an arbitrary ESP, with a magic value to signify that the APC handler has returned.
        initialStackBase = 0x00000000f0000000
        unicornEng.mem_map(initialStackBase, 2 * 1024 * 1024)
        unicornEng.mem_write(initialStackBase + 0x100 + 0, b"\xbe\xba\xde\xc0")

        # We push the argument which the APC handler is given        
        if (is_64bit):
            unicornEng.reg_write(UC_X86_REG_RCX, apc.NormalContext)
        else:
            routine_param = self.pas.read(apc.NormalContext.vol.offset, apc.NormalContext._data_format.length)
            unicornEng.mem_write(initialStackBase + 0x100 + apc.NormalContext._data_format.length, routine_param)
        
        unicornEng.reg_write(stack_pointer, initialStackBase + 0x100)

        # Set up our handlers, which will map memory on-demand from the debuggee
        unicornEng.hook_add(UC_HOOK_MEM_READ_UNMAPPED, self.badmem)
        unicornEng.hook_add(UC_HOOK_MEM_WRITE_INVALID, self.badmem)
        unicornEng.hook_add(UC_HOOK_MEM_FETCH_UNMAPPED, self.badmem)

        # Now, lets emulate some instructions! We won't get many, because Unicorn can't emulate a lot of things (like
        # segment-prefixed instructions, as used by wow64) but we'll get enough to detect most ROP chains.
        instrEmulated = 0
        nextIns = routine
        memoryRange = None
        


        while instrEmulated < 10000:
            if self.config["verbose"]:
                print("Before instruction %d at %s:" % (instrEmulated, hex(nextIns)))
                print("CS:IP = %s:%s SS:SP = %s:%s" % (
                hex(unicornEng.reg_read(UC_X86_REG_CS)), hex(unicornEng.reg_read(UC_X86_REG_EIP)),
                hex(unicornEng.reg_read(UC_X86_REG_SS)), hex(unicornEng.reg_read(UC_X86_REG_ESP))))

            # Attempt to emulate a single instruction

            try:
                unicornEng.emu_start(nextIns, nextIns + 0x10, count=1)
            except unicorn.UcError as e1:
                self.dbgMsg(f"Unicorn (or badmem function) throw an exception: {e1}")
                break

            # Great, we emulated an instruction. Move on to the next instruction.
            nextIns = unicornEng.reg_read(instruction_pointer)
            try:
                if (is_64bit and 
                    unicornEng.mem_read(nextIns,2) == SYSCALL_OPCODE and
                    unicornEng.reg_read(UC_X86_REG_RAX) == 0x43):
                    context = self.context.object(symbol_table + constants.BANG + "_CONTEXT", proc_layer_name, apc.NormalContext)
                    nextIns = context.Rip
                    unicornEng.reg_write(UC_X86_REG_RAX, context.Rax)
                    unicornEng.reg_write(UC_X86_REG_RBX, context.Rbx)
                    unicornEng.reg_write(UC_X86_REG_RCX, context.Rcx)
                    unicornEng.reg_write(UC_X86_REG_RDX, context.Rdx)
                    unicornEng.reg_write(UC_X86_REG_R8, context.R8)
                    unicornEng.reg_write(UC_X86_REG_R9, context.R9)
                    unicornEng.reg_write(UC_X86_REG_R10, context.R10)
                    unicornEng.reg_write(UC_X86_REG_R11, context.R11)
                    unicornEng.reg_write(UC_X86_REG_R12, context.R12)
                    unicornEng.reg_write(UC_X86_REG_R13, context.R13)
                    unicornEng.reg_write(UC_X86_REG_R14, context.R14)
                    unicornEng.reg_write(UC_X86_REG_R15, context.R15)
            except unicorn.UcError as e1:
                self.dbgMsg(f"read invalid: {e1}")
        
            instrEmulated = instrEmulated + 1

            # If we're now at our magic address, then our APC has completed executing entirely. That's all, folks.
            if nextIns == 0xc0debabe:
                break

            # Now we can check for some suspicious circumstance.
            esp = unicornEng.reg_read(stack_pointer)
            if esp == int(apc.NormalContext):
                result.didROP = "True"
                self.dbgMsg("APC has performed stack pivot; new stack is its context pointer")
                if VirtualProtect == None:
                    # If we didn't find VirtualProtect, we can't go any further. I guess a stack pivot is a pretty big
                    # red flag anyway.
                    break
            if VirtualProtectEx != None:
                if nextIns == VirtualProtectEx:
                    if(is_64bit):
                            result.probablePayload = unicornEng.reg_read(UC_X86_REG_RCX)
                    result.didAdjustPerms = "True"

                    # Read the arguments to VirtualProtect, and the return address, from the stack
                    returnAddress = struct.unpack("I", unicornEng.mem_read(esp - 0, 4))[0]
                    memoryRange = struct.unpack("I", unicornEng.mem_read(esp + 8, 4))[0]

                    result.adjustedAddresses.append(memoryRange)
                    self.dbgMsg("VirtualProtectEx: Timer routine is adjusting memory permissions of range %s" % hex(
                        memoryRange))
                    # Set the return address to whatever VirtualProtect would've returned to
                    nextIns = returnAddress
                    unicornEng.reg_write(instruction_pointer, returnAddress)
                    # Pop five args plus the return address off the (32bit) stack

                    unicornEng.reg_write(stack_pointer, esp + (6*4))
                if VirtualProtect != None:
                    if nextIns == VirtualProtect:
                        if(is_64bit):
                            result.probablePayload = unicornEng.reg_read(UC_X86_REG_RCX)
                        result.didAdjustPerms = "True"

                        # Read the arguments to VirtualProtect, and the return address, from the stack
                        returnAddress = struct.unpack("I", unicornEng.mem_read(esp - 0, 4))[0]
                        memoryRange = struct.unpack("I", unicornEng.mem_read(esp + 4, 4))[0]

                        result.adjustedAddresses.append(memoryRange)
                        self.dbgMsg("VirtualProtect: Timer routine is adjusting memory permissions of range %s" % hex(
                            memoryRange))
                        # Set the return address to whatever VirtualProtect would've returned to
                        nextIns = returnAddress
                        unicornEng.reg_write(instruction_pointer, returnAddress)
                        # Pop four args plus the return address off the (32bit) stack
                        unicornEng.reg_write(stack_pointer, esp + (5 * 4))
                if nextIns in result.adjustedAddresses:
                    result.didJumpToAdjusted = "True"

                    result.probablePayload = nextIns
                    self.dbgMsg("Timer routine is jumping to newly-executable code at %s!" % hex(memoryRange))

                    break
        if result.probablePayload != 0:
            yield result

    def _generator(self) -> Iterator[timerResult]:
        self.exportCache = {}

        kernel = self.context.modules[self.config["kernel"]]
        symbol_table = kernel.symbol_table_name

        is_64bit = symbols.symbol_table_is_64bit(self.context, symbol_table)

        for _, timer_data in timers.Timers(self.context, self.config_path)._generator():
            timer_offset = timer_data[0]
            timer = kernel.object(
                object_type="_ETIMER",
                offset=timer_offset,
                absolute=True,
            )
            self.dbgMsg("Timer at {0}".format(hex(int(timer_offset))))

            is_windows_vista = versions.is_vista_or_later(self.context, symbol_table) and \
                               (not versions.is_windows_8_or_later(self.context, symbol_table)) and \
                               (not versions.is_windows_7(self.context, symbol_table))
            if is_64bit and (versions.is_xp_or_2003(self.context, symbol_table) or is_windows_vista):
                apc = kernel.object("_KAPC_WOW64", offset=timer.TimerApc.vol.offset, absolute=True)
            else:
                apc = kernel.object("_KAPC", offset=timer.TimerApc.vol.offset, absolute=True)

            routine = int(apc.NormalRoutine)
            thread = kernel.object("_ETHREAD", offset=int(apc.Thread), absolute=True)
            if (not thread.is_valid()) or (routine == 0):
                # This APC has no user-mode payload.
                continue

            process = thread.owning_process()
            if not process.is_valid():
                # This usually happens when a timer is not pointing to a valid thread. I'm not sure why this happens -
                # I guess there's some flag in the timer which states that it isn't valid, or the timer/timer list is
                # # being manipulated when we dump.
                self.dbgMsg('Timer %s : warning: Thread ID %s has no owning process, skipping' % (
                hex(int(timer_offset)), hex(int(thread.Cid.UniqueThread))))
                continue

            # If this is a WoW64 APC - ie, an APC queued by a 32-bit thread on a 64-bit windows install - then we must
            # 'decode' the NormalRoutine by shifting and negating it.
            # We detect these WoW64-style APCs by comparing the top half of the 64bit address, except bit zero, to  0xffffffff. I'm not
            # sure if this is reliable, but it seems to work.
            if (((routine >> 32) | 0x01) == 0xffffffff):
                routine32bit = (-(routine >> 2)) & 0xffffffff
                self.dbgMsg("WoW64-style APC routine decoded %s to %s" % (hex(routine), hex(routine32bit)))
                routine = routine32bit

            for result in self.examine(process, thread, routine, apc, timer,symbol_table, is_64bit):
                # make sure this matches FORMAT_LIST
                yield (
                    0,
                    (
                        result.process.UniqueProcessId,
                        result.process.ImageFileName.cast(
                            "string",
                            max_length=result.process.ImageFileName.vol.count,
                            errors="replace",
                        ),
                        format_hints.Hex(result.routine),
                        str(result.didAdjustPerms),
                        str(result.didJumpToAdjusted),
                        format_hints.Hex(result.probablePayload),
                        result.prolog
                    ),
                )

    def run(self):
        return renderers.TreeGrid(
            FORMAT_LIST,
            self._generator(),
        )

