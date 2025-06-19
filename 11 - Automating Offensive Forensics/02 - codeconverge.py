from immlib import *

class cc_hook(LogBpHook):
    def __init__(self):
        LogBpHook.__init__(self)
        self.imm = Debugger()

    def run(self, regs):
        eip = regs['EIP']
        self.imm.log("Breakpoint hit at: 0x%08X" % eip, eip)
        self.imm.deleteBreakpoint(eip)
        return

def main(args):
    imm = Debugger()

    # Locate the loaded module (e.g., calc.exe)
    calc = imm.getModule("calc.exe")
    if not calc:
        return "[!] calc.exe module not found."

    base_address = calc.getCodebase()
    imm.analyseCode(base_address)
    functions = imm.getAllFunctions(base_address)

    hooker = cc_hook()
    count = 0
    for function in functions:
        hooker.add("%08X" % function, function)
        count += 1

    return "[*] Tracking %d functions in calc.exe." % count
