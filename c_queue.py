

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
    def size(self):
        return len(self.queue)

    def __str__(self):
        str = "[Q:"
        if len(self.queue) == 0:
            str += " empty"
        else:
            for i in self.queue:
                str += " "+i.pid
        str += "]"
        return str

class SortedQueue():
    def __init__(self, sort_fn):
        self.queue = []
        self.sort_fn = sort_fn

    def add(self, p):
        self.queue.append(p)
        if self.sort_fn is None: self.queue.sort()
        else:                    self.queue.sort(key = self.sort_fn)

    def pop(self, index = 0):
        return self.queue.pop(index)
    def get_next_time(self):
        if len(self.queue) == 0: return -1
        else: return self.queue[0].get_time()
    def peek(self):
        return self.queue[0]

    def is_empty(self):
        if len(self.queue) == 0:
            return True
        else:
            return False
    def size(self):
        return len(self.queue)

    def __str__(self):
        str = "[Q:"
        if len(self.queue) == 0:
            str += " empty"
        else:
            for i in self.queue:
                str += " "+i.pid
        str += "]"
        return str
