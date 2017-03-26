import multiprocessing
from multiprocessing import Pipe, Lock
from helper import Message
import time

"""
Class which represents a process which main goal is to enter the critical
section several times, while synchronization with othre processes is
solved using the Ricart-Agrawala algorithm.
"""
class Process(multiprocessing.Process):
    def __init__(self, id, clock, lock, input_pipes, output_pipes, process_num, iterations):
        multiprocessing.Process.__init__(self)
        self.id = id  # process id
        self.clock = clock  # process interior logical clock
        self.lock = lock  # shared Lock object for critical snippet execution
        self.inputs = input_pipes  # input pipe end in which we send a message
        self.outputs = output_pipes  # all output pipes ends from which we read messages
        self.queue = []  # query of messages for each process
        self.num = process_num  # number of processes
        self.iterations = iterations  # number of critical section job iterations

    def run(self):
        print "Process", self.id, "is ready."

        for z in range (0, self.iterations):
            demand = Message("DEMAND", self.id, self.clock)
            for input in self.inputs:
                input.send(demand)


            # check other DEMANDS
            for out in self.outputs:
                try:
                    msg = out.recv()
                    if msg is not None:
                        self.queue.append(msg)

                except EOFError:
                    break


            # check all DEMANDS, update local logical closk and send RESPONSE messages
            # if their clock value is lower than the local value
            for message in self.queue:
                self.clock = max(self.clock, message.get_clock()) + 1
                if self.clock > message.get_clock():
                    response = Message("RESPONSE", self.id, message.get_clock())
                    self.inputs[message.get_id() - 2].send(response)


            # wait for all RESPONSES and update local logical clock
            num_responses = 0

            while num_responses < self.num - 1:
                for out in self.outputs:
                    try:
                        msg = out.recv()
                        if msg is not None:
                            self.clock = max(self.clock, msg.get_clock()) + 1
                            num_responses += 1

                    except EOFError:
                        break

            # CRITICAL SECTION
            self.lock.acquire()

            print "Process", self.id, ": entering CRITICAL SECTION."
            time.sleep(1)
            print "Process", self.id, ": doing something in the CRITICAL SECTION."
            time.sleep(1)

            for message in self.queue:
                response = Message("RESPONSE", self.id, message.get_id())
                self.inputs[response.get_id() - 2].send(response)

            self.queue = []

            print "Process", self.id, ": leaving CRITICAL SECTION.\n"
            time.sleep(1)
            self.clock += 1

            self.lock.release()

        print "Process", self.id, "has finished."


if __name__ == '__main__':
    # 1. i 2. proces
    # 1. -> 2.
    out1, in1 = Pipe()
    # 2. -> 1.
    out2, in2 = Pipe()
    # 2. i 3. proces
    # 2. -> 3.
    out3, in3 = Pipe()
    # 3. -> 2.
    out4, in4 = Pipe()
    # 1. i 3. proces
    # 1. -> 3.
    out5, in5 = Pipe()
    # 3. -> 1.
    out6, in6 = Pipe()

    lock = Lock()

    p1 = Process(1, 12, lock, [in1, in5], [out2, out6], 3, 2)
    p2 = Process(2, 7, lock, [in2, in3], [out1, out4], 3, 2)
    p3 = Process(3, 20, lock, [in4, in6], [out3, out5], 3, 2)

    p1.start()
    p2.start()
    p3.start()