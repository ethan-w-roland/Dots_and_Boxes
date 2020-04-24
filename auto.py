#test random strategy
import random, time, os
from project import Game

num_iter = 100
results = []

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def run(size):
    #first player is red
    for i in range(num_iter):
        game = Game(size)
        game.player = 1
        game.auto = True
        while(not game.exit):

            poss = game.board.getStrategicLines()
            move = random.choice(poss)

            game.cursor = move
            game.processMove()
            game.updateBoard()

            # clear()
            # print(game.board)
            # time.sleep(.1)
            # input()

            game.cursor = (0,0,'u')
            game.player *= -1 #change player

        results.append(game.winner)
        # time.sleep(2)

    red_wins = results.count(1)
    grn_wins = results.count(-1)
    non_wins = results.count(0)

    red_prc = 100 * red_wins / len(results)
    grn_prc = 100 * grn_wins / len(results)
    tie_prc = 100 * non_wins / len(results)

    comparison = 'red:green:ties = {}:{}:{}'.format(red_prc, grn_prc, tie_prc)

    fo = open("output.txt","w")
    out = ''
    # out += comparison + '\n'
    for res in results:
        out += str(res) + '\n'
    fo.write(out)
    fo.close() 

    print(comparison)

while(True):
    size = int(input('board size: '))
    run(size)
    results = []
