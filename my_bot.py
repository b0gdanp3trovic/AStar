import asyncio
import random
import search
import math
from core.bot import Bot
from core.networking_client import connect
from core.enums import Direction


# Example Python 3 bot implementation for Planet Lia Bounce Evasion.
class MyBot(Bot):

    # Called only once before the match starts. It holds the
    # data that you may need before the game starts.
    def setup(self, initial_data):
        self.initial_data = initial_data
        self.x = initial_data["yourUnit"]["x"]
        self.y = initial_data["yourUnit"]["y"]
        self.currentNumOfCoins = 0
        self.currentNumOfCoinsNotChanges = 0
        self.foundCoin = False
        self.limit = 5
        
        self.currentMove = 0
        self.currentX = initial_data["yourUnit"]["x"]
        self.currentY = initial_data["yourUnit"]["y"]
        self.currentCoin_x = self.find_nearest_coin(self.initial_data)[0]
        self.currentCoin_y = self.find_nearest_coin(self.initial_data)[1]
        self.state = initial_data
        self.path = search.A(self)
        self.pathIndex = 0

        self.checked_saw_length = 0





        # Print out the map
        for y in range(initial_data["mapHeight"] - 1, -1, -1):
            for x in range(0, initial_data["mapWidth"]):
                print("_" if initial_data["map"][y][x] else "#", end='')
            print()

    # Called repeatedly while the match is generating. Each
    # time you receive the current match state and can use
    # response object to issue your commands.
    def update(self, state, response):
        # Find and send your unit to a random direction that
        # moves it to a valid field on the map
        # TODO: Remove this code and implement a proper path finding!
        self.state = state
        self.foundCoin = True
        if(self.state["yourUnit"]["points"] > self.currentNumOfCoins):
            self.currentNumOfCoins = self.state["yourUnit"]["points"]
            self.currentNumOfCoinsNotChanges = 0
        else:
            self.currentNumOfCoinsNotChanges += 1
        if(self.foundCoin):
            self.x = self.currentX
            self.y = self.currentY
            self.foundCoin = False
            self.find_nearest_coin(state)
            self.path = []
            self.path = search.A(self, self.limit)
            self.pathIndex = 0
            
            
        if(self.path):
            if(self.pathIndex < len(self.path)):
                move, cost = self.path[self.pathIndex]
                if(move[0] == 1 and move[1] == 1):
                    if(self.initial_data["map"][self.currentY + 1][self.currentX]):
                        response.move_unit(Direction.UP)
                        response.move_unit(Direction.RIGHT)
                    else:
                        response.move_unit(Direction.RIGHT)
                        response.move_unit(Direction.UP)
                    self.currentX += 1
                    self.currentY += 1
                if(move[0] == 0 and move[1] == 1):
                    response.move_unit(Direction.UP)
                    self.currentY += 1
                if(move[0] == 1 and move[1] == 0):
                    response.move_unit(Direction.RIGHT)
                    self.currentX += 1

                if(move[0] == -1 and move[1] == -1):
                    if(self.initial_data["map"][self.currentY - 1][self.currentX]):
                        response.move_unit(Direction.DOWN)
                        response.move_unit(Direction.LEFT)
                    else:
                        response.move_unit(Direction.LEFT)
                        response.move_unit(Direction.DOWN)
                    self.currentX -= 1
                    self.currentY -= 1
                if(move[0] == 0 and move[1] == -1):
                    response.move_unit(Direction.DOWN)
                    self.currentY -= 1
                if(move[0] == -1 and move[1] == 0):
                    response.move_unit(Direction.LEFT)
                    self.currentX -= 1
                if(move[0] == -1 and move[1] == 1):
                    if(self.initial_data["map"][self.currentY][self.currentX-1]):
                        response.move_unit(Direction.LEFT)
                        response.move_unit(Direction.UP)
                    else:
                        response.move_unit(Direction.UP)
                        response.move_unit(Direction.LEFT)
                    self.currentX -= 1
                    self.currentY +=1
                if(move[0] == 1 and move[1] == -1):
                    if(self.initial_data["map"][self.currentY][self.currentX+1]):
                        response.move_unit(Direction.RIGHT)
                        response.move_unit(Direction.DOWN)
                    else:
                        response.move_unit(Direction.DOWN)
                        response.move_unit(Direction.RIGHT)
                    self.currentX +=1
                    self.currentY -=1
                self.pathIndex += 1

        if(self.currentX == self.currentCoin_x and self.currentY == self.currentCoin_y):
            self.foundCoin = True
            self.x = self.currentX
            self.y = self.currentY
            self.path = []
            self.pathIndex = 0

    def check_for_saws(self, state):
        x_check = self.currentX
        y_check = self.currentY
        self.checked_saw_length = len(state["saws"])
        for saw in state["saws"]:
            saw_x = saw["x"]
            saw_y = saw["y"]
            if(self.intersection(saw)):
                continue

        
    def find_nearest_coin(self, state):
        min_distance = 9999
        x = -1
        y = -1
        for i in range(0,len(state["coins"])):
            coin = state["coins"][i]
            distance = abs(self.currentX - coin["x"]) + abs(self.currentY - coin["y"])
            if(distance < min_distance):
                min_distance = distance
                x = coin["x"]
                y = coin["y"]
        self.currentCoin_x = x
        self.currentCoin_y = y
        return [x,y]

    def closest_coin_to_opponent(self,state, my_x, my_y):
        min_distance = 999
        x = -1
        y = -1
        for i in range(0, len(state["coins"])):
            coin = state["coins"][i]
            op_x = state["opponentUnit"]["x"]
            op_y = state["opponentUnit"]["y"]
            distance = abs(op_x - coin["x"]) + abs(op_y - coin["y"])
            if(distance < min_distance):
                min_distance = distance
                x = coin["x"]
                y = coin["y"]
        if(my_x == x and my_y == y):
            return True
        return False

    
    def generate_moves(self):
        x = self.x
        y = self.y
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_x = x + dr
                new_y = y + dc
                map_width = self.initial_data["mapWidth"]
                map_height = self.initial_data["mapHeight"]
                if new_x >= 0 and new_y >= 0 and new_x < map_width and new_y < map_height and self.initial_data["map"][new_y][new_x]:
                    if(dr == -1 and dc == -1):
                        if(x-1 >= 0 and y-1>= 0 and x-1<map_width and y-1 < map_height):
                            if(not(self.initial_data["map"][y][x-1]) and not(self.initial_data["map"][y-1][x])):
                                continue  
                    if(dr == -1 and dc == 1):
                        if(x-1 >= 0 and y+1>= 0 and x-1<map_width and y+1 < map_height):
                            if(not(self.initial_data["map"][y][x-1]) and not(self.initial_data["map"][y+1][x])):
                                continue
                    if(dr == 1 and dc == 1):
                        if(x+1 >= 0 and y+1>= 0 and x+1<map_width and y+1 < map_height):
                            if(not(self.initial_data["map"][y][x+1]) and not(self.initial_data["map"][y+1][x])):
                                continue
                    if(dr == 1 and dc == -1):
                        if(x+1 >= 0 and y-1>= 0 and x+1<map_width and y-1 < map_height):
                            if(not(self.initial_data["map"][y][x+1]) and not(self.initial_data["map"][y-1][x])):
                                continue
                    move = [dr, dc]
                    cost = math.sqrt(dr**2 + dc**2)
                    moves.append((move, cost))
        return moves
    
    def min_distance_to_saw(self):
        min_distance = 99
        for saw in self.state["saws"]:
            saw_x = saw["x"]
            saw_y = saw["y"]
            distance = abs(self.x - saw_x) + abs(self.y - saw_y)
            if(distance < min_distance):
                min_distance = distance
        return min_distance

    def distance_to_player(self):
        return (abs(self.x - self.state["opponentUnit"]["x"]) + abs(self.y - self.state["opponentUnit"]["y"])) > 5

    def min_distance_to_coin(self):
        return abs(self.x - self.currentCoin_x) + abs(self.y - self.currentCoin_y)




    def min_distance_saw(self):
        min_distance = 99
        min_x = 99
        min_y = 99
        for saw in self.state["saws"]:
            saw_x = saw["x"]
            saw_y = saw["y"]
            distance = abs(self.x - saw_x) + abs(self.y - saw_y)
            if(distance < min_distance):
                min_distance = distance
                min_x = saw_x
                min_y = saw_y
        return [min_x,min_y]        

    def saw_risk(self):
        suma = 0
        for saw in self.state["saws"]:
            saw_x = saw["x"]
            saw_y = saw["y"]
            direct = saw["direction"]
            dis_x =self.x-saw_x
            dis_y =self.y-saw_y
            dist = abs(self.x - saw_x) + abs(self.y - saw_y)
            if(abs(self.x - saw_x) == abs(self.y - saw_y) and abs(self.x - saw_x) == self.currentMove):
                suma -= 1.4*dist
        return -suma

    def saw_risk1(self):
        [saw_x, saw_y] = self.min_distance_saw()
        dis_x =self.x-saw_x
        dis_y =self.y-saw_y     
        if(abs(self.x - saw_x) == abs(self.y - saw_y) and abs(self.x - saw_x) == self.currentMove):
            return 2
        return 0

    def on_half(self):
        if(self.x > 9):
            if(self.x <= 9):
                return 1
        if(self.x < 9):
            if(self.x >= 9):
                return 1
        return 0


    def ID(self):
        return tuple([self.x, self.y])

    def evaluate(self):
        if("time" in self.state):
            if(self.state["time"] > 1200):
                return 150*self.min_distance_to_coin() + 4*self.saw_risk()
        if(self.currentNumOfCoinsNotChanges > 150):
            self.limit = 15
            return 15*self.min_distance_to_coin() + 4*self.saw_risk()
        self.limit = 5
        return  4*self.min_distance_to_coin() + 4*self.saw_risk()

    def solved(self):
        return (self.min_distance_to_coin() == 0)

    def move(self, move):
        self.currentMove += 1
        self.x += move[0]
        self.y += move[1]

    def undo_move(self, move):
        self.currentMove -= 1
        self.x -= move[0]
        self.y -= move[1]


        

# Connects your bot to match generator, don't change it.
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(connect(MyBot()))
