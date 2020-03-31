'''
NxN squares represented by 3 matrices:
- NxN for captured squares
- N-1xN for horizontal lines
- NxN-1 for vertical lines

issues: non-cascading, capturing unowned squares

'''

import keyboard
from termcolor import colored
import os
import threading

class Board:
    def __init__(self, N):
        self.N = N
        self.caps = [x[:] for x in [[0] * N] * N]       # 0-uncap 1=p1 -1=p2
        self.hort = [x[:] for x in [[0] * N] * (N+1)]   # 0-uncap 1=p1 -1=p2
        self.vert = [x[:] for x in [[0] * (N+1)] * N]   # 0-uncap 1=p1 -1=p2

    def colorC(self, num):
        if num == 0:
            return('X')
        if num == 1:
            return(colored('X','red'))
        if num == -1:
            return(colored('X','green'))
        if num == 2:
            return(colored('●'))

    def colorH(self, num):
        if num == 0:
            return('—')
        if num == 1:
            return(colored('—','red'))
        if num == -1:
            return(colored('—','green'))
        if num == 2:
            return(colored('—','white','on_blue'))
        if num == 3:
            return(colored('—','white','on_yellow'))

    def colorV(self, num):
        if num == 0:
            return('|')
        if num == 1:
            return(colored('|','red'))
        if num == -1:
            return(colored('|','green'))
        if num == 2:
            return(colored('|','white','on_blue'))
        if num == 3:
            return(colored('|','white','on_yellow'))

    def getValue(self, x, y, z):
        if   z == 'u':
            return(self.hort[x][y])
        elif z == 'd':
            return(self.hort[x+1][y])
        elif z == 'l':
            return(self.vert[x][y])
        elif z == 'r':
            return(self.vert[x][y+1])

    def setValue(self, x, y, z, value):
        N = self.N
        if   z == 'u' and x >= 0:
            self.hort[x][y]   = value
        elif z == 'd' and x <= N-1:
            self.hort[x+1][y] = value
        elif z == 'l' and y >= 0:
            self.vert[x][y]   = value
        elif z == 'r' and y <= N-1:
            self.vert[x][y+1] = value

    def __str__(self):
        return self.to_str(self.N, self.vert, self.hort, self.caps)  

    def cursor(self, x, y, z):

        p_line = -2
        p_caps = -2

        #inefficient but simpler than reverting changes
        c = [row[:] for row in self.caps]
        v = [row[:] for row in self.vert]
        h = [row[:] for row in self.hort]

        c[x][y] = 2
        if   z == 'u':
            h[x][y] = 2   if h[x][y]   == 0 else 3
        elif z == 'd':
            h[x+1][y] = 2 if h[x+1][y] == 0 else 3
        elif z == 'l':
            v[x][y] = 2   if v[x][y]   == 0 else 3
        elif z == 'r':
            v[x][y+1] = 2 if v[x][y+1] == 0 else 3

        return self.to_str(self.N, v, h, c)
        
    def to_str(self, N, vert, hort, caps):
        
        out  = ''
        for i in range(N):

            out += '  '
            for j in range(N):
                out += '{}   '.format( self.colorH(hort[i][j]))

            out += '\n'
            for j in range(N):
                out += '{} '.format( self.colorV(vert[i][j]))
                out += '{} '.format( self.colorC(caps[i][j]))

            out += self.colorV(vert[i][-1]) + '\n'
        out += '  '
        for j in range(N):
            out += '{}   '.format(self.colorH(hort[-1][j]))
        
        return out

class Game:
    def __init__(self, N):
        
        self.board  = Board(N)
        self.player = -1
        self.cursor = (0,0,'u')
        self.alt    = False
        self.exit   = False
        self.new    = []

    def getMove(self):

        enter_release = threading.Event()

        def handler(event):

            if event.name == None: event.name = 'null'

            x,y,z = self.cursor
            N     = self.board.N
            key   = event.name

            if event.event_type == 'down' and "alt" in key:
                self.alt = True

            if event.event_type == 'up':

                if 'alt' in key:
                    self.alt = False

                if not self.alt:
                    if   key == 'up'    and x > 0   : x -= 1
                    elif key == 'down'  and x < N-1 : x += 1
                    elif key == 'left'  and y > 0   : y -= 1
                    elif key == 'right' and y < N-1 : y += 1

                else:
                    if   key == 'up':    z = 'u'
                    elif key == 'down':  z = 'd'
                    elif key == 'left':  z = 'l'
                    elif key == 'right': z = 'r'
                
                self.cursor = (x,y,z)
                clear()
                #print('{},{}'.format(x,y)) # for debug
                print(self.board.cursor(x, y, z))

                if key == 'esc':
                    clear()
                    print('exiting game...')
                    self.exit = True
                    enter_release.set()

                #for debug - caputre shortcut
                if key in ['r','g'] and self.board.caps[x][y] == 0:
                    value = 1 if key == 'r' else -1
                    self.cursor = (x, y, value)
                    enter_release.set()

                #end move
                if key == 'enter' and self.board.getValue(x, y, z) == 0:
                    enter_release.set()
        
        keyboard.hook(handler, suppress=True)
        enter_release.wait()
        keyboard.unhook_all()
        return        

    def processMove(self):

        x,y,z = self.cursor

        #for debug
        if z in [1,-1]:
            self.board.setValue(x, y, 'u', z)
            self.board.setValue(x, y, 'd', z)
            self.board.setValue(x, y, 'l', z)
            self.board.setValue(x, y, 'r', z)
            self.board.caps[x][y] = z
            self.new.append((x,y))

        #normal move
        else:
            self.board.setValue(x, y, z, self.player)

    def updateBoard(self):

        #VAR SETUP
        N    = self.board.N
        caps = self.board.caps
        hort = self.board.hort
        vert = self.board.vert
        new  = self.new

        #INITIAL CAPTURE
        for i in range(N):
            for j in range(N):
                u = hort[i][j]
                d = hort[i+1][j]
                l = vert[i][j]
                r = vert[i][j+1]
                if 0 not in [u,d,l,r] and caps[i][j] == 0:
                    new.append((i,j))
                    self.board.caps[i][j] = self.player
                    print("({},{}) captured!".format(i,j))
        
        #STEALING
        def trySteal(self, i, j):
            change = False
            #get values in adjacent squares
            u = caps[i-1][j] if i > 0   else 0
            d = caps[i+1][j] if i < N-1 else 0
            l = caps[i][j-1] if j > 0   else 0
            r = caps[i][j+1] if j < N-1 else 0
            #count squares owned by each player
            red_count = [u,d,l,r].count(1)
            grn_count = [u,d,l,r].count(-1)
            #red capture
            if ((red_count - grn_count) >= 2 and caps[i][j] == -1):
                change = True
                self.board.caps[i][j] = 1
                print("({},{}) stolen!".format(i,j))
            #green capture
            if ((grn_count - red_count) >= 2 and caps[i][j] == 1):
                change = True
                self.board.caps[i][j] = -1
                print("({},{}) stolen!".format(i,j)) 
            #return value
            return change
        #process steal of new
        cont = True
        while(cont):   
            cont = False
            for i, j in new:
                cont = trySteal(self, i, j)
        #process steal of old
        cont = True
        while(cont):   
            cont = False
            for i in range(N):
                for j in range(N):
                    cont = trySteal(self, i, j)

        #END OF GAME
        p1_count = 0
        p2_count = 0
        for i in range(N):
            for j in range(N):
                if caps[i][j] == 1:
                    p1_count += 1
                elif caps[i][j] == -1:
                    p2_count += 1
        if p1_count + p2_count == (N * N):
            if p1_count == p2_count:
                print('Game Over - Tie : {} to {}'.format(p1_count, p2_count))
            if p1_count > p2_count:
                print('Game Over - Red Wins : {} to {}'.format(p1_count, p2_count))
            if p1_count < p2_count:
                print('Game Over - Green Wins : {} to {}'.format(p2_count, p1_count))
            self.exit = True
        self.new = []

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

#----MAIN-----#
print('Please input size of NxN grid: N = ', end='')
size = int(input())
game = Game(size)
print('Use arrow keys to select line, alt+arrow to change box\nPlayer 1 press any key to start, esc at any time to exit')
while(True):

    game.player *= -1 #change player
    game.getMove()

    if(game.exit): exit(1)

    clear()
    game.processMove()
    game.updateBoard()
    print(game.board)

    if(game.exit): 
        print('press enter to exit')
        input()
        exit(1)

    game.cursor = (0,0,'u')
    print("Green's turn") if game.player == 1 else print("Red's turn")