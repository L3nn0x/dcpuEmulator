from component import Component

def correct(value, bits, signed = False):
    base = 1 << bits
    value %= base
    return value - base if signed and value.bit_length() == bits else value

class Cpu(Component):
    def __init__(self, binary = None):
        super().__init__()
        self.name = "cpu"
        self.memory = [0] * 0xFFFF
        if binary:
            for i in range(0, len(binary), 2):
                self.memory[int(i/2)] = ((binary[i] << 8) | binary[i+1])
        self.regs = [0] * 8 # A, B, C, X, Y, Z, I, J
        self.pc = 0
        self.sp = 0
        self.ex = 0
        self.ia = 0
        self.waiting = 0
        self.opcodes = {
                0 : self.special,
                0x1 : self.set,
                0x2 : self.add,
                0x3 : self.sub,
                0x4 : self.mul,
                0x5 : self.mli,
                0x6 : self.div,
                }
        self.specialOpcodes = {
                #0 : self.nop,
                }
        self.oldState = self.saveState()

    def nop(self):
        self.waiting = 1
        self.pc += 1

    def special(self):
        try:
            self.specialOpcodes[(self.memory[self.pc] >> 5) & 0x1F]()
        except KeyError:
            print("Error unkown special opcode 0x{0} at memory location 0x{1}".format(format((self.memory[self.pc] >> 5) & 0x1F, '02x'), format(self.pc, '02x')))
            self.printState()
            return True

    def set(self):
        a, b = self.getOp()
        b(a())
        self.waiting += 1
        self.pc += 1

    def add(self):
        a, b = self.getOp()
        value = a()
        value += b()
        tmp = correct(value, 16)
        b(tmp)
        self.ex = 1 if value != tmp else 0
        self.waiting += 2
        self.pc += 1

    def sub(self):
        a, b = self.getOp()
        value = a()
        value2 = b()
        value2 -= value
        tmp = correct(value2, 16, True)
        b(tmp)
        self.ex = 0xFFFF if value2 != tmp else 0
        self.waiting += 2
        self.pc += 1

    def mul(self):
        a, b = self.getOp()
        value = a()
        value2 = b()
        value2 *= value
        tmp = correct(value2, 16)
        b(tmp)
        self.ex = (value2 >> 16) & 0xFFFF
        self.waiting += 2
        self.pc += 1

    def mli(self):
        a, b = self.getOp()
        value = a()
        value2 = b()
        value2 *= value
        tmp = correct(value2, 16, True)
        b(tmp)
        self.ex = (value2 >> 16) & 0xFFFF
        self.waiting += 2
        self.pc += 1

    def div(self):
        a, b = self.getOp()
        value = a()
        value2 = b()
        if value == 0:
            b(0)
            self.ex = 0
            self.waiting += 3
            self.pc += 1
            return
        v = int(value2/value)
        tmp = correct(v, 16)
        b(tmp)
        self.ex = int((v << 16) / value) & 0xFFFF

    def getOp(self, isSpecial = False):
        a, b = (self.memory[self.pc] >> 10), (self.memory[self.pc] >> 5) & 0x1F
        if isSpecial:
            return self.decodeOp(a), None
        return self.decodeOp(a), self.decodeOp(b, False)

    def decodeOp(self, value, isA = True):
        def wrapper(data = None):
            if wrapper._evaluated:
                self.pc = wrapper._pc
                self.sp = wrapper._sp
                self.waiting = wrapper._waiting
            else:
                wrapper._pc = self.pc
                wrapper._sp = self.sp
                wrapper._waiting = self.waiting
                wrapper._evaluated = True
            if value <= 0x7:
                if data != None:
                    self.regs[value] = data
                return self.regs[value]
            elif value <= 0xF:
                if data != None:
                    self.memory[self.regs[0x8 - value]] = data
                return self.memory[self.regs[0x8 - value]]
            elif value <= 0x17:
                self.waiting += 1
                self.pc += 1
                if data != None:
                    self.memory[self.regs[0x10 - value] + self.memory[self.pc]] = data
                return self.memory[self.regs[0x10 - value] + self.memory[self.pc]]
            elif value == 0x18:
                if isA:
                    tmp = self.sp
                    self.sp = correct(self.sp + 1, 16)
                    return self.memory[tmp]
                else:
                    tmp = self.sp
                    if data != None:
                        self.memory[self.sp] = data
                        self.sp = correct(self.sp - 1, 16)
                    return self.memory[tmp]
            elif value == 0x19:
                if data != None:
                    self.memory[self.sp] = data
                return self.memory[self.sp]
            elif value == 0x1A:
                self.waiting += 1
                self.pc += 1
                if data != None:
                    self.memory[self.sp + self.memory[self.pc]] = data
                return self.memory[self.sp + self.memory[self.pc]]
            elif value == 0x1B:
                if data != None:
                    self.sp = data
                return self.sp
            elif value == 0x1C:
                if data != None:
                    self.pc = data
                return self.pc
            elif value == 0x1D:
                if data != None:
                    self.ex = data
                return self.ex
            elif value == 0x1E:
                self.waiting += 1
                self.pc += 1
                if data != None:
                    self.memory[self.memory[self.pc]] = data
                return self.memory[self.memory[self.pc]]
            elif value == 0x1F:
                self.waiting += 1
                self.pc += 1
                return self.memory[self.pc]
            elif value <= 0x3F:
                return value - 0x21
        wrapper._evaluated = False
        return wrapper

    def printState(self):
        print(list(zip("ABCXYZIJ", self.regs)), "PC", self.pc, "SP", self.sp, "Ex", self.ex, "IA", self.ia, "waiting", self.waiting)

    def tick(self):
        try:
            self.waiting -= 1
            if self.waiting > 0:
                return
            self.restoreState(self.oldState)
            self.printState()
            res = self.opcodes[self.memory[self.pc] & 0x1F]()
            self.correctRegs()
            state = self.saveState()
            self.restoreState(self.oldState)
            self.oldState = state
            self.waiting = state["waiting"]
            return res
        except KeyError:
            print("Error unkown opcode 0x{0} at memory location 0x{1}".format(format(self.memory[self.pc] & 0x1F, '02x'), format(self.pc, '02x')))
            self.printState()
            return True

    def saveState(self):
        state = {}
        state["regs"] = self.regs[:]
        state["pc"] = self.pc
        state["sp"] = self.sp
        state["ex"] = self.ex
        state["ia"] = self.ia
        state["waiting"] = self.waiting
        return state

    def restoreState(self, state):
        self.regs = state["regs"][:]
        self.pc = state["pc"]
        self.sp = state["sp"]
        self.ex = state["ex"]
        self.ia = state["ia"]
        self.waiting = state["waiting"]

    def correctRegs(self):
        for i in range(len(self.regs)):
            self.regs[i] = correct(self.regs[i], 16)
        self.pc = correct(self.pc, 16)
        self.sp = correct(self.sp, 16)
        self.ex = correct(self.ex, 16)
        self.ia = correct(self.ia, 16)
