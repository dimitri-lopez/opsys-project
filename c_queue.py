

class Queue():
    def __init__(self):
        self.queue = []

    def append(self, p):
        self.queue.append(p)

    def pop(self, index):
        return self.queue.pop(index)

    def is_empty(self):
        if len(self.queue) == 0:
            return True
        else:
            return False

    def __str__(self):
        str = "[Q:"
        if len(self.queue) == 0:
            str += " empty"
        else:
            for i in self.queue:
                str += " "+i.pid
        str += "]"
        return str