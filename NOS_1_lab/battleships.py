import multiprocessing
import random
import time
from random import randint

"""
Randomly puts the selected number of battleships onto the battlefield.
"""
def put_battleships(array, number):
    count = 0
    for i in range(4):
        for j in range(4):
            if random.random() < 0.5 and count < number:
                array[i][j] = 1
                count += 1
            else:
                array[i][j] = 0

"""
Prints the battleships belonging to the function caller.
"""
def print_battleships(array, hits):
    for i in range(4):
        if i > 0 and i < 4:
            print('\n-------')
        for j in range(4):
            if j > 0 and j < 4:
                print('|', end='')
            if array[i][j] == 1 and hits[i][j] == 1:
                print('X', end='')
            else:
                print(array[i][j], end='')

    print('\n')

"""
Class which represents a process used in the battleships game.
"""
class Player(multiprocessing.Process):
    def __init__(self, task_queue, id):
        multiprocessing.Process.__init__(self)
        self.queue = task_queue
        self.array = [[0 for z in range(4)] for k in range(4)]
        self.hits = [[0 for z in range(4)] for k in range(4)]
        self.guesses = [[0 for z in range(4)] for k in range(4)]
        self.ship_number = 6
        self.id = id

        put_battleships(self.array, self.ship_number)

        print('Battleships of process %s' % self.name)
        print_battleships(self.array, self.hits)

    def run(self):
        while True:
            nextMessage = self.queue.get()

            if nextMessage is None:
                self.queue.task_done()
                break

            id = nextMessage.get_player_id()
            x, y = nextMessage.get_coordinates()

            if id != self.id:
                self.queue.task_done()
                self.queue.put(Message(x, y, id))
                time.sleep(0.1)
                continue

            print('%s\'s turn:\n' % self.name)

            firstCorrection = True
            if self.hits[x][y] == 1:
                firstCorrection = False

            self.hits[x][y] = 1

            if self.array[x][y] == 1:
                if firstCorrection:
                    self.ship_number -= 1
                print('(%s, %s) is a hit!\n' % (x, y))

                if (self.ship_number == 0):
                    print("The game is over, player with id %s has won!" % id)
                    self.queue.put(None)
                    self.queue.put(None)
                    break
            else:
                print('(%s, %s) is a miss!\n' % (x, y))

            print_battleships(self.array, self.hits)

            while True:
                x = randint(0, 3)
                y = randint(0, 3)

                if self.guesses[x][y] == 0:
                    self.guesses[x][y] = 1
                    break

            print('Remaining ships: %s' % self.ship_number)
            print('Targeting (%s, %s)' % (x, y))
            print('----------------\n')

            id = 1 - self.id

            self.queue.task_done()
            self.queue.put(Message(x, y, id))
            time.sleep(0.1)

        return

"""
Class which represents a message that processes send to each other.
"""
class Message(object):
    def __init__(self, x, y, id):
        self.x = x
        self.y = y
        self.id = id

    def __call__(self):
        return self.x, self.y

    def __str__(self):
        return '(%s, %s)' % (self.x, self.y)

    def get_coordinates(self):
        return self.x, self.y

    def get_player_id(self):
        return self.id


if __name__ == '__main__':
    messageQueue = multiprocessing.JoinableQueue()

    num_players = 2
    print('Creating %d players\n' % num_players)
    players = [Player(messageQueue, i)
                 for i in range(num_players)]

    for player in players:
        player.start()

    messageQueue.put(Message(randint(0, 3), randint(0, 3), randint(0, 1)))

    messageQueue.join()