"""
    Module which contains extra classes
    needed for the main program.
"""

"""
Class which represents a message used for communication between
processes using pipelines.
"""
class Message(object):
    def __init__(self, type, id, clock):
        self.type = type
        self.id = id
        self.clock = clock

    def get_id(self):
        return self.id

    def get_type(self):
        return self.type

    def get_clock(self):
        return self.clock

def get_correct_process(id, other):
    if id == 1:
        if other == 2:
            return 0
        else:
            return 1
    elif id == 2:
        if other == 1:
            return 0
        else:
            return 1
    elif id == 3:
        if other == 1:
            return 0
        else:
            return 1