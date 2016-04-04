from cpu import Cpu
from timer import Timer

with open("data.bin", "rb") as f:
    cpu = Cpu(f.read())
    cpuTimed = Timer(cpu.tick, 1, 1)
    cpuTimed.start()
    cpuTimed.join()
