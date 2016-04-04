import time
from threading import Thread

class Timer(Thread):
    def __init__(self, function, hz, batch=1000):
        super().__init__()
        self.batch = batch
        self.avg = 0
        self.behind = 0
        self.interval = self.batch/hz
        self.function = function
        self.ok = True
        self.turns = 0

    def run(self):
        while self.ok:
            last = time.time()
            for i in range(self.batch):
                if self.function():
                    self.stop()
                    break
            current = time.time() - last
            dt = self.interval - current
            if dt <= 0:
                self.behind += 1
            else:
                time.sleep(dt)
            self.avg += time.time() - last
            self.turns += 1

    # total mb executions, total nb behind schedule, average running Hz
    def getStats(self):
        if self.turns == 0:
            return 0, 0, 0
        return self.turns*self.batch, self.behind*self.batch, 1/(self.avg/(self.turns*self.batch))

    def stop(self):
        self.ok = False

    def tick(self):
        return self.function()
