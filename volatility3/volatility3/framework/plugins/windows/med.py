import logging
from volatility3.framework import renderers, interfaces, symbols
from volatility3.framework.configuration import requirements
from volatility3.plugins.windows import pslist, vadinfo, gargoyle
from volatility3.framework.renderers import format_hints
from volatility3.framework.symbols import intermed
from volatility3.framework.symbols.windows.extensions import pe
# Define WinNT protections
winnt_protections = {
    "PAGE_NOACCESS": 0x01,
    "PAGE_READONLY": 0x02,
    "PAGE_READWRITE": 0x04,
    "PAGE_WRITECOPY": 0x08,
    "PAGE_EXECUTE": 0x10,
    "PAGE_EXECUTE_READ": 0x20,
    "PAGE_EXECUTE_READWRITE": 0x40,
    "PAGE_EXECUTE_WRITECOPY": 0x80,
    "PAGE_GUARD": 0x100,
    "PAGE_NOCACHE": 0x200,
    "PAGE_WRITECOMBINE": 0x400,
    "PAGE_TARGETS_INVALID": 0x40000000,
}

class MED(interfaces.plugins.PluginInterface):
    """Find detection evasion injections"""

    _required_framework_version = (2, 0, 0)
    _version = (1, 0, 0)

    @classmethod
    def get_requirements(cls):
        return [
            requirements.ModuleRequirement(
                name="kernel",
                description="Windows kernel",
                architectures=["Intel32", "Intel64"],
            ),
            requirements.ListRequirement(name='scanners', element_type=str, description='Detection scanners to run', optional=True),
            requirements.BooleanRequirement(name="dump", description="Extract suspicious processes", default=False, optional=True),
            requirements.StringRequirement(name='log_file_path', description="Path to the log file", optional=True)
        ]

    def config_logger(self, log_file_path):
        """Configure logging to a file."""
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _generator(self):
        """This function calls the Gargoyle plugin and processes its results."""

        kernel = self.context.modules[self.config["kernel"]]
        pe_table_name = intermed.IntermediateSymbolTable.create(
            self.context, self.config_path, "windows", "pe", class_types=pe.class_types
        )
        for _, gargoyle_data in gargoyle.Gargoyle(self.context, self.config_path)._generator():
            result_dict = {gargoyle.FORMAT_LIST[i][0]: gargoyle_data[i] for i in range(len(gargoyle_data))}

            # Fetch the VAD for the probable payload address
            pid = int(result_dict["PID"])
            process = next((proc for proc in pslist.PsList.list_processes(self.context, kernel.layer_name, kernel.symbol_table_name) if proc.UniqueProcessId == pid), None)

            if not process:
                continue

            proc_layer_name = process.add_process_layer()
            proc_layer = self.context.layers[proc_layer_name]

            process_info = {
                "Process": result_dict["Process"],
                "Pid": pid,
                "Address": hex(result_dict["Probable payload"]),
                "Vad Tag": "N/A",
                "Protection": "N/A",
                "Hexdump": [],
            }
            vad_output="None"
            executable_output = "None"
            for vad in vadinfo.VadInfo(self.context, self.config_path).list_vads(process):
                if vad.get_start() <= result_dict["Probable payload"] < vad.get_end():
                    process_info["Vad Tag"] = str(vad.get_tag())
                    process_info["Protection"] = vad.get_protection(vadinfo.VadInfo(self.context, self.config_path).protect_values(self.context, kernel.layer_name, kernel.symbol_table_name), winnt_protections)
                    memory_data = proc_layer.read(vad.get_start(), vad.get_end() - vad.get_start())
                    process_info["Hexdump"] = format_hints.HexBytes(memory_data[16])
                    is_32bit_arch = not symbols.symbol_table_is_64bit(
                        self.context, kernel.symbol_table_name
                    )
                    if is_32bit_arch or process.get_is_wow64():
                        architecture = "intel"
                    else:
                        architecture = "intel64"

                    disasm = interfaces.renderers.Disassembly(
                        memory_data[:16], vad.get_start(), architecture
                    )
                    if self.config["dump"]:
                        f = vadinfo.VadInfo(self.context, self.config_path).vad_dump(self.context, process,vad,self.open)
                        f.close()
                        vad_output = f.preferred_filename
                        f2 = pslist.PsList.process_dump(self.context,
                                                         kernel.symbol_table_name,
                                                         pe_table_name,
                                                         process,
                                                         self.open,)
                        f2.close()
                        executable_output =f2.preferred_filename
                    break

            yield (0, [
                str(process.UniqueProcessId),
                process.ImageFileName.cast(
                    "string",
                    max_length=process.ImageFileName.vol.count,
                    errors="replace",
                ),
                renderers.format_hints.Hex(int(process_info["Address"], 16)),
                str(process_info["Vad Tag"]),
                str(process_info["Protection"]),
                process_info["Hexdump"],
                vad_output,
                executable_output,
                disasm
            ])

    def run(self):
        return renderers.TreeGrid([
            ("PID", str),
            ("Process", str),
            ("Address", renderers.format_hints.Hex),
            ("Vad Tag", str),
            ("Protection", str),
            ("Hexdump", format_hints.HexBytes),
            ("Vad Dump File",str),
            ("Executable File",str),
            ("Disassembly", interfaces.renderers.Disassembly)
        ], self._generator())
