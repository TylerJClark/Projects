class Game():
    def __init__(self,show,player=1,row=6,column=7,player1=False,player2=False,watch=False):
        
        self.board=[]
        for i in range(row):
            self.board.append([])
        self.turns = 1
        self.currentPlayer=player
        self.player=player
        self.showBoard=show
        self.done=False
        self.rows=row
        self.columns=column
        self.AI1=player1
        self.AI2=player2
        self.watch=watch
        self.Next=True
        self.skip=False
        self.ff=False
        self.end=False
        self.hvh=True
        self.probs=[]
        for i in range(column):
            self.probs.append(float(0))
        for i in range(row):
            for j in range(column):
                self.board[i].append(float(0))
        if self.showBoard:
            import threading
            
            thread1=threading.Thread(target=self.boardGui).start()
    """def test1(self):
        print(self.rows)

    def test2(self):
        import time
        self.rows+=1
        self.test1()"""
            
                                     

    def emptyBoard(self):
        for i in range(self.rows):
            for j in range(self.columns):
                self.board[i][j]=float(0)

    def startGame(self):
        self.currentPlayer=self.player
        self.turns = 1
        self.done=False
        self.emptyBoard()
        return self.board,self.columns

    def step(self,action):
        reward=float(0)
        row,column =self.dropToken(action)
        win =self.checkWin(row,column)
        if not win:
            if self.currentPlayer==1:
                self.currentPlayer=2
            else:
                self.currentPlayer=1
            full=self.checkFull()
            if full:
                reward=float(0)
                self.done=True
            else:
                self.turns+=1
            return self.board,reward,self.done
        else:
            self.done=True
            board=[]
            for i in range(self.rows):
                board.append([])
            for i in range(self.rows):
                for j in range(self.columns):
                    board[i].append(float(3))
            if self.currentPlayer == 1:
                reward = float(1)
            else:
                reward = float(-1)
            return board,reward,self.done
                

    def dropToken(self,column):
        row=0
        found=False
        for i in range(self.rows):
            if self.board[i][column]==0:
                found=True
                if self.currentPlayer==1:
                    self.board[i][column]=float(1)
                else:
                    self.board[i][column]=float(-1)
                break
            row +=1
        if not found:
            return -1,-1
        else:
            return row,column

    def checkFull(self):
        full=True
        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j] ==0:
                    full = False
                    break
            if not full:
                break
        return full

    def checkWin(self,row,column):
        player = self.board[row][column]
        ##### Left and Right  ####
        tokens=1
        for i in range(3):
            if column-(i+1) >=0:
                if self.board[row][column-(i+1)] == player:
                    tokens +=1
                else:
                    break
        for i in range(3):
            if column+(i+1) <self.columns:
                if self.board[row][column+(i+1)] == player:
                    tokens +=1
                else:
                    break
        if tokens >= 4:
            return True

        ##### Down  ####
        tokens=1
        for i in range(3):
            if row-(i+1) >=0:
                if self.board[row-(i+1)][column] == player:
                    tokens +=1
                else:
                    break
        if tokens >= 4:
            return True

        ##### Up Left and Down Right  ####
        tokens=1
        for i in range(3):
            if column-(i+1) >=0 and row+(i+1)<self.rows:
                if self.board[row+(i+1)][column-(i+1)] == player:
                    tokens +=1
                else:
                    break
        for i in range(3):
            if column+(i+1) <self.columns and row-(i+1)>=0:
                if self.board[row-(i+1)][column+(i+1)] == player:
                    tokens +=1
                else:
                    break
        if tokens >= 4:
            return True

        ##### Up Right and Down Left  ####
        tokens=1
        for i in range(3):
            if column-(i+1) >=0 and row-(i+1)>=0:
                if self.board[row-(i+1)][column-(i+1)] == player:
                    tokens +=1
                else:
                    break
        for i in range(3):
            if column+(i+1) <self.columns and row+(i+1)<self.rows:
                if self.board[row+(i+1)][column+(i+1)] == player:
                    tokens +=1
                else:
                    break
        if tokens >= 4:
            return True

        return False   

    """def printBoard(self):
        for i in range(self.rows -1,-1,-1):
            line=""
            for j in range(self.columns):
                if self.board[i][j] == 1:
                    line+="1"
                elif self.board[i][j] == 2:
                    line+="2"
                else:
                    line+="0"
            print(line)"""

    def getMoves(self):
        moves=[]
        for i in range(self.columns):
            for j in range(self.rows):
                if self.board[j][i]==0:
                    moves.append(i)
                    break
        return moves
    def getDone(self):
        return self.done

    def getSkip(self):
        return self.skip

    """def turn(self):
        found=False
        while not found:
            choice = int(-1)
            while choice <0 or choice >self.columns-1:
                choice=int(input("Player "+str(self.currentPlayer)+", what coulum do you want to drop a token into?"))-1
            moves= self.getMoves()
            if choice not in moves:
                print("That column is full, choose another column")
            else:
                found=True
        self.step(choice)"""

    def boardGui(self):
        import pygame
        import math
        from ButtonLib import Button
        print("")#magical print statement
        pygame.init()
        pygame.font.init()
        fonts = pygame.font.get_fonts()
        fps = 60
        self.font=pygame.font.SysFont(fonts[30],27)
        screen = pygame.display.set_mode((1280,720),pygame.FULLSCREEN)
        screenWidth,screenHeight = pygame.display.get_surface().get_size()
        screen.fill((255, 253, 208))
        pygame.display.flip()
        running = True
        clock = pygame.time.Clock()
        buttonQuit = Button(1060,30,200,80,(255,0,0),(255,50,50),True,(0,0,0),"Quit",70)
        nextButton = Button(1060,120,200,80,(200,20,100),(255,50,50),True,(0,0,0),"Next",70)
        skipButton = Button(1160,210,70,50,(200,20,100),(255,50,50),True,(0,0,0),">>>",70)
        fastForward= Button(1060,210,70,50,(200,20,100),(255,50,50),True,(0,0,0),">>",70)

        while running:
            ###########run events############
            clock.tick(fps)
            mouseUp=False
            pos = pygame.mouse.get_pos()
            press = pygame.mouse.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    mouseUp=True
            if buttonQuit.click(pos,mouseUp):
                running=False
                playing=False
                pygame.quit()
                self.hvh=False
                break
            if self.end:
                running=False
                pygame.quit()
                break
            if nextButton.click(pos,mouseUp) and self.watch:
                self.Next=False
            if skipButton.click(pos,mouseUp) and self.watch:
                self.skip = not self.skip
                self.ff = False
            if fastForward.click(pos,mouseUp)and self.watch:
                self.ff = not self.ff
                self.skip=False
            #######calculate information#####
            screen.fill((255, 253, 208))
            if not self.done:
                if self.currentPlayer ==1:
                    if self.AI1 == False:
                        moves= self.getMoves()
                        text= self.font.render("Player 1's turn",1,(0,0,0))#creates the text
                        screen.blit(text,(4,4))
                        xSeperation = math.trunc(850/self.columns)
                        for i in range(self.columns):
                            if i in moves:
                                columnButton=Button(100+xSeperation*i,80,xSeperation,30,(192,192,192),(255,0,0),True,(0,0,0),"Drop token",70,15)
                                columnButton.hovering(pos)
                                columnButton.create(screen)
                                if columnButton.click(pos,mouseUp):
                                    self.step(i)
                    else:
                        text= self.font.render("Computer 1's turn",1,(0,0,0))#creates the text
                        screen.blit(text,(4,4))
                        if self.watch:
                            xSeperation = math.trunc(850/self.columns)
                            for i in range(self.columns):
                                text=self.font.render(str(self.probs[i]),1,(0,0,0))
                                screen.blit(text,(120+xSeperation*i,80))
                else:
                    if self.AI2 == False:
                        moves= self.getMoves()
                        text= self.font.render("Player 2's turn",1,(0,0,0))#creates the text
                        screen.blit(text,(4,4))
                        xSeperation = math.trunc(850/self.columns)
                        for i in range(self.columns):
                            if i in moves:
                                columnButton=Button(100+xSeperation*i,80,xSeperation,30,(192,192,192),(0,100,100),True,(0,0,0),"Drop token",70,15)
                                columnButton.hovering(pos)
                                columnButton.create(screen)
                                if columnButton.click(pos,mouseUp):
                                    self.step(i)
                    else:
                        text= self.font.render("Computer 2's turn",1,(0,0,0))#creates the text
                        screen.blit(text,(4,4))
                        if self.watch:
                            xSeperation = math.trunc(850/self.columns)
                            for i in range(self.columns):
                                    text=self.font.render(str(self.probs[i]),1,(0,0,0))
                                    screen.blit(text,(120+xSeperation*i,80))
            else:
                text= self.font.render("Player "+str(self.currentPlayer)+" wins!",1,(0,0,0))#creates the text
                screen.blit(text,(4,4))
                if self.watch:
                    xSeperation = math.trunc(850/self.columns)
                    for i in range(self.columns):
                        text=self.font.render(str(self.probs[i]),1,(0,0,0))
                        screen.blit(text,(120+xSeperation*i,80))
            ####### draw board ##############
            self.drawBoard(screen)
            buttonQuit.create(screen)
            if self.watch:
                nextButton.create(screen)
                skipButton.create(screen)
                fastForward.create(screen)
            if not self.end:
                pygame.display.flip()

    def getDone(self):
        return self.done

    def getNext(self):
        return self.Next

    def setNext(self,Input):
        self.Next=Input

    def stopGui(self):
        self.end=True

    def getFF(self):
        return self.ff

    def getHvh(self):
        return self.hvh

    def sendProbs(self,probArray):
        self.probs=probArray

    def drawBoard(self,screen):
        import pygame
        import math
        pygame.draw.rect(screen,(0,0,255),(100,120,900,550),0)
        pygame.draw.rect(screen,(0,0,255),(50,670,120,50),0)
        pygame.draw.rect(screen,(0,0,255),(930,670,120,50),0)
        xSeperation = math.trunc((850/self.columns)/2)
        ySeperation = math.trunc((500/self.rows)/2)
        #print(self.rows)
        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j] == 0:
                    colour = (255,253,208)
                elif self.board[i][j] ==1:
                    colour=(255,0,0)
                else:
                    colour=(255,255,0)
                if j==0 and i==0:
                    pygame.draw.circle(screen,colour,(j*xSeperation+105+xSeperation,670-(i*ySeperation+60)),ySeperation)
                elif j==0 and i!=0:
                    pygame.draw.circle(screen,colour,(j*xSeperation+105+xSeperation,670-(i*ySeperation*2+60+3*i)),ySeperation)
                elif j!=0 and i==0:
                    pygame.draw.circle(screen,colour,(j*2*xSeperation+105+xSeperation,670-(i*ySeperation+60)),ySeperation)
                elif j!=0 and i!=0:
                    pygame.draw.circle(screen,colour,(j*2*xSeperation+105+xSeperation,670-(i*ySeperation*2+60+3*i)),ySeperation)
                    
        
class trainGame():
    def __init__(self,row=6,column=7,watch=False):
        self.game1 = Game(watch,1,row,column,watch=watch,player1=True,player2=True)
        self.game2 = Game(False,2,row,column,player1=True,player2=True)
        self.game1State = []
        self.game1Reward=0
        self.game1Done=False
        self.game2State = []
        self.game2Reward=0
        self.game2Done=False
        self.current=1
        self.size=row*column
        self.watch=watch
        self.probs=[]

    def startGame(self):
        self.current=1
        board,actions=self.game1.startGame()
        self.game2.startGame()
        return board,actions,self.size
    
    def step(self,action):
        self.game1State,self.game1Reward,self.game1Done = self.game1.step(action)
        self.game2State,self.game2Reward,self.game2Done = self.game2.step(action)
        if self.current==1:
            self.current=2
            return self.game2State[:],self.game1Reward,self.game1Done,self.getMoves(),self.game1State[:]
        else:
            self.current=1
            return self.game1State[:],self.game2Reward,self.game2Done,self.getMoves(),self.game2State[:]
    def getMoves(self):
        return self.game1.getMoves()

    def getFinalReward(self):
        if self.current==1:
            return self.game1Reward
        else:
            return self.game2Reward
        
    def getFinalState(self):
        if self.current==2:
            return self.game1State
        else:
            return self.game2State

    def getNext(self):
        if ((self.game1.getSkip() == False)
            and (self.game1.getFF()==False)):
            return self.game1.getNext()
        else:
            return False

    def setNext(self,Input):
        self.game1.setNext(Input)

    def stopGui(self):
        self.game1.stopGui()

    def getFF(self):
        return self.game1.getFF()

    def sendProb(self,probArray):
        if probArray != None:
            self.probs=probArray
            self.game1.sendProbs(self.probs)

if __name__=="__main__":
    """while True:
        x.startGame()
        while True:
            x.step(3)
            time.sleep(1)"""
    x=trainGame(watch=True)
    #x=Game(True)

