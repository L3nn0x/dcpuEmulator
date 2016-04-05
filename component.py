from event import Listener

class Component(Listener):
    def __init__(self):
        super().__init__()

    def tick(self):
        pass

    def showStatus(self, visitor):
        pass
