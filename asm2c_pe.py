from asm2c import Program
import pefile


class ProgramPE(Program):
    def __init__(self, file_path):
        super().__init__()

        pe = pefile.PE(file_path)

        eop = pe.OPTIONAL_HEADER.AddressOfEntryPoint
        code_section = pe.get_section_by_rva(eop)

        self.code_dump = code_section.get_data()
        self.code_addr = pe.OPTIONAL_HEADER.ImageBase + code_section.VirtualAddress