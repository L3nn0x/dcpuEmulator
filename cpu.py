from component import Component

class Cpu(Component):
    def __init__(self, binary = None):
        super().__init__()
        self.name = "cpu"
        self.memory = [0] * 0xFFFF
        if binary:
            print(binary)
            for i in range(0, len(binary), 2):
                self.memory[int(i/2)] = ((binary[i+1] << 8) | binary[i])
        self.regs = [0, 0, 0, 0, 0, 0, 0, 0] # A, B, C, X, Y, Z, I, J
        self.pc = 0
        self.sp = 0
        self.ex = 0
        self.ia = 0
        self.waiting = 1
        self.opcodes = {
                0 : self.nop,
                }

    def nop(self):
        self.waiting = 1
        self.pc += 1

    def printState(self):
        print(*list(zip("ABCXYZIJ", self.regs)), "PC", self.pc, "SP", self.sp, "Ex", self.ex, "IA", self.ia)

    def tick(self):
        try:
            self.waiting -= 1
            if self.waiting > 0:
                return
            self.opcodes[self.memory[self.pc]]()
        except KeyError:
            print("Error unkown opcode {0} at memory location {1}".format(format(self.memory[self.pc], '02x'), format(self.pc, '02x')))
            self.printState()
            return True
