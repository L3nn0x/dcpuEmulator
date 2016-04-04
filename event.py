class Event:
    EVERYONE = "all"
    NONE = "none"

    def __init__(self, to, fr, message):
        self.to = to
        self.fr = fr
        self.message = message

class Listener:
    def __init__(self, name="generic"):
        self.name = name
    
    def notify(self, event):
        pass

class EventBus:
    def __init__(self):
        self.events = []
        self.listenners = {}

    def attach(self, listener):
        self.listeners[listener.name] = listener

    def send(self, event):
        if event.to == Event.NONE:
            return
        if event.to == Event.EVERYONE:
            for k, l in self.listeners.items():
                l.notify(event)
            return
        try:
            self.listeners[event.to].notify(event)
        except KeyError:
            pass
