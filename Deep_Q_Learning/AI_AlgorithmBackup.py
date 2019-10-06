import math
import random
import time
#import numpy as np
from collections import namedtuple
#from itertools import count
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import pygame
from ButtonLib import Button
import os
import threading
import Connect4


#to do list

#after watching, cant train
#after watching ai vs ai, human vs human breaks
#add games counter
#add final screen in game
#fix cuda
#add human vs AI
#save network
#fix why the AI isnt learning anything


stopGame = False
createdNetwork = False
policyNetwork = None

def trainGame1v1(game,hiddenLayers,maxEpisodes,maxSteps,
        learningRate,maxMemory,targetUpdate,discountRate,exploreDecay,
        batchSize,rows = 6,columns  = 7,watch = False,ALAP = False):
    
    global stopGame
    global training
    global trainButtonProgress
    global createdNetwork
    global policyNetwork
    global Experience
    global loadAIvAI
    print("trainGame thread opened")
    if game == "connect4":
        import Connect4
        
        manager = envManager(Connect4.trainGame(rows,columns,watch),device)

    
    memory = ReplayMemory(maxMemory)
    
    
    maxActions = manager.getMaxActions()
    maxStates = manager.getMaxStates()

    
    if not createdNetwork:
        policyNetwork = DQN(maxStates,hiddenLayers,maxActions) #creates target and policy
        createdNetwork = True


    #####
    targetNetwork = DQN(maxStates,hiddenLayers,maxActions)
    targetNetwork.load_state_dict(policyNetwork.state_dict())

    targetNetwork.eval() #prevents training on target network

    #optimizer = optim.Adam(params=policyNetwork.parameters(), lr=lr)
 
    myAgent = Agent(myStrategy,maxActions,device)
    ######


     
    for episode in range(maxEpisodes):
        
        manager.reset()
        
        currentState = manager.getState()
        #print(currentState)


        posActions = manager.getActions()
        turn = 0 
        storedStateP0 = currentState
        storedStateP1 = currentState
        storedRewardP0 = None
        storedRewardP1 = None
        #Holds the state until this players next turn
        
        storedActionP0 = None
        storedActionP1 = None
        #Holds the reward until this players next turn
        #print("new game")
        if not watch and not ALAP:
            trainButtonProgress = (episode/maxEpisodes) * 500



        
        #print(policyNetwork.parameters())
        optimizer = optim.Adam(params = policyNetwork.parameters(), lr=learningRate)
        for step in range(maxSteps):
            #print(12312)


            if watch:
                while manager.getAdvanceMove():                    
                    time.sleep(0.2)

                if manager.getFFF():
                    time.sleep(0.5)
                    
                manager.setAdvanceMove()

                
                
            
            if turn == 0: #changes turn
                if storedActionP0 != None:
                    memory.push(Experience(torch.tensor(storedStateP0,device = device).reshape(1,-1), torch.tensor([storedActionP0],device = device),
                                           torch.tensor(currentState,device = device).reshape(1,-1), torch.tensor([storedRewardP0],device = device)))
                    #print(memory)
            else:
                
                if storedActionP1 != None:
                    memory.push(Experience(torch.tensor(storedStateP1,device = device).reshape(1,-1), torch.tensor([storedActionP1],device = device),
                                           torch.tensor(currentState,device = device).reshape(1,-1), torch.tensor([storedRewardP1],device = device)))
                    #print(memory)
                    
            #tp
            if watch:
                chosenAction = myAgent.select_action(currentState,policyNetwork,posActions,0)
                
            else:
                chosenAction = myAgent.select_action(currentState,policyNetwork,posActions,-1)
            
            if turn == 0:
                storedStateP0 = currentState
                storedActionP0 = chosenAction
                
            else:
                storedStateP1 = currentState
                storedActionP1 = chosenAction
                
            
            currentState,reward,done,posActions = manager.take_action(chosenAction)
            #rewards is boolean WHY
            #print("reward",reward)
            #print("done",done)
            
            if turn == 0:
                storedRewardP0 = reward
                turn = 1
                

            else:
                storedRewardP1 = reward
                turn = 0
            
            #ASK is reward for current player or next?
            
            #currentState is other persons State

            #create experience with rewards
            #this is the experience of NOT this time step,
            #but the previous move THIS player took       
            if done:
                #print(torch.tensor(currentState))
                reward = manager.getReward()
                if turn == 0:
                    memory.push(Experience(torch.tensor(storedStateP1,device = device).reshape(1,-1), torch.tensor([storedActionP1],device = device), torch.tensor(torch.tensor(currentState),device = device).reshape(1,-1), torch.tensor(torch.tensor([reward]),device = device)))
                    memory.push(Experience(torch.tensor(storedStateP0,device = device).reshape(1,-1), torch.tensor([storedActionP0],device = device), torch.tensor(torch.tensor(manager.getFinalState()).reshape(1,-1),device = device), torch.tensor(torch.tensor([manager.getFinalReward()],device = device))))
                    #print(memory)
                    
                else:#torch.tensor(state).reshape(1,-1)
                    memory.push(Experience(torch.tensor(storedStateP1,device = device).reshape(1,-1), torch.tensor([storedActionP1],device = device), torch.tensor(manager.getFinalState(),device = device).reshape(1,-1), torch.tensor([manager.getFinalReward()],device = device)))
                    memory.push(Experience(torch.tensor(storedStateP0,device = device).reshape(1,-1), torch.tensor([storedActionP0],device = device), torch.tensor(currentState,device = device).reshape(1,-1), torch.tensor([reward],device = device)))
                    #print(memory)
                break
            
            
            if memory.can_provide_sample(batchSize):
                #print("optimisation")
                experiences = memory.sample(batchSize)
                states, actions, rewards, next_states = extract_tensors(experiences)
                #print(rewards)
                current_q_values = QValues.get_current(policyNetwork, states, actions)
                next_q_values = QValues.get_next(targetNetwork, next_states)
                #print(next_q_values)
                #print(discountRate)
                #print(rewards)
                target_q_values = (next_q_values * discountRate) + rewards
            
                loss = F.mse_loss(current_q_values, target_q_values.unsqueeze(1))
                print("loss:",loss)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                
            if episode % targetUpdate == 0:
                targetNetwork.load_state_dict(policyNetwork.state_dict())

        print("Explore probability",myAgent.rate)
            
        if stopGame:
            print("Training terminated")
            break
        
    print("Training batch Finished")
    training = False
    loadAIvAI = False
    stopGame = False
    if watch:
        manager.stopGUI()
    
def extract_tensors(experiences):
    # Convert batch of Experiences to Experience of batches
    batch = Experience(*zip(*experiences))
    
    #('state', 'action', 'next_state', 'reward'))
    #print(batch.state)
    #print(batch.action)
    #print(batch.state)
    t1 = torch.cat(batch.state)
    #print(t1)
    t2 = torch.cat(batch.action)
    t3 = torch.cat(batch.reward)
    t4 = torch.cat(batch.next_state)
    #print(t3)

    return (t1,t2,t3,t4)


class QValues():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    @staticmethod
    def get_current(policy_net, states, actions):
        #print(states)
        #print(policy_net(states))
        return policy_net(states).gather(dim=1, index=actions.unsqueeze(-1))
    
    @staticmethod
    def get_next(target_net, next_states):
        
        #final_state_locations = next_states.max(dim=1)[0].eq(3).type(torch.bool)
        final_state_locations = next_states.max(dim=1)[0].eq(3).type(torch.ByteTensor)
        #print(final_state_locations)
        
        non_final_state_locations = (final_state_locations == 0)
        non_final_states = next_states[non_final_state_locations]
        
        batch_size = next_states.shape[0]
        values = torch.zeros(batch_size).to(QValues.device)
        #print(non_final_states)
        values[non_final_state_locations] = target_net(non_final_states).max(dim=1)[0].detach()
        #print(values)
        return values


class DQN(nn.Module):
    def __init__(self, inputs, hidden, outputs):
        super().__init__()
        self.layers = []
        
        learnArgs = []
        self.layers.append(nn.Linear(in_features = inputs, out_features = hidden[0]))
        learnArgs.append(nn.Parameter(torch.tensor([float(inputs),float(hidden[0])])))

        #self.myParameters.append(nn.Linear(in_features = inputs, out_features = hidden[0]))
        
        for i in range(len(hidden) - 1):
            self.layers.append(nn.Linear(in_features = hidden[i], out_features = hidden[i+1]) )
            learnArgs.append(nn.Parameter(torch.tensor([float(hidden[i]),float(hidden[i+1])])))
            #self.myParameters.append(nn.Linear(in_features = hidden[i], out_features = hidden[i+1]))


        self.layers.append(nn.Linear(in_features = hidden[-1], out_features = outputs))
        learnArgs.append(nn.Parameter(torch.tensor([float(hidden[-1]),float(outputs)])))

        self.myParameters = nn.ParameterList(learnArgs)
        #self.myParameters.append(nn.Linear(in_features = hidden[-1], out_features = outputs))
        #self.myparameters = nn.ParameterList(Parameter1, Parameter2, ...)
            

    def forward(self, t):
        """newt = [[]]
        for i in range(len(t)):
            for j in t[i]:
                newt[0].append(j)"""
        #t = newt
        #print(t)
        #t = torch.tensor(t)
        #t.clone().detach()
        #print(t)
        #t = t.flatten(start_dim=1)
        #t = t.reshape(1,-1)
        #t = t.squeeze()
        #print(t)
        
        for i in range(len(self.layers) - 1):
            
            t = F.relu(self.layers[i](t))
            
        t = self.layers[-1](t)
        return t

    def forwardSigmoid(self, t):
        t = t.flatten(start_dim=1)
        for i in range(len(self.layers) - 1):
            
            t = F.logsigmoid(self.layers[i](t))
            
        t = self.layers[-1](t)
        return t    

    def forwardTanh(self, t):
        t = t.flatten(start_dim=1)
        for i in range(len(self.layers) - 1):
            
            t = F.hardtanh(self.layers[i](t))
            
        t = self.layers[-1](t)
        return t

class ReplayMemory():
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.push_count = 0


    def push(self, experience):
        if len(self.memory) < self.capacity:
            self.memory.append(experience)
        else:
            self.memory[self.push_count % self.capacity] = experience
        self.push_count += 1


    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def can_provide_sample(self, batch_size):
        return len(self.memory) >= batch_size


class EpsilonGreedyStrategy():
    def __init__(self, start, end, decay):
        self.start = start
        self.end = end
        self.decay = decay

    def get_exploration_rate(self, current_step):
        return self.end + (self.start - self.end) * \
            math.exp(-1. * current_step * self.decay)



class Agent():
    def __init__(self, strategy, num_actions, device):
        self.current_step = 0
        self.strategy = strategy
        self.num_actions = num_actions
        self.device = device
        print(device)

    def select_action(self, state, policy_net,actions,exploitChance = -1):
        if exploitChance == -1:
            self.rate = self.strategy.get_exploration_rate(self.current_step)
        else:
            self.rate = exploitChance
        #print(rate)
        self.current_step += 1

        if self.rate > random.random():
            return random.choice(actions) # explore      
        else:
            with torch.no_grad():
                #print(policy_net(state))
                #print(torch.tensor(state).reshape(1,-1))
                best = int(policy_net(torch.tensor(state).reshape(1,-1)).argmax(dim=1).to(self.device)[0]) # exploit
                if best in actions:
                    return best

                
                ordered = []
                
                choice = policy_net.forward(torch.tensor(state).reshape(1,-1))
                #choice = policy_net.forward(state.clone().detach())
                #print("choice",choice)
                for i in range(len(actions)):
                    ordered.append((float(choice[0][i]),actions[i]))

                ordered = sorted(ordered, key=lambda x: x[0])
                ordered = ordered[::-1]
                #print("order",ordered)

                for i in ordered:
                    if i[1] in actions:
                        return i[1]

                #print(torch.tensor(currentState))
                print("no move found")
                print("ordered",ordered)
                print("actions",actions)


                
class envManager():
    def __init__(self,env, device):
        
        self.device = device
        self.env = env
        self.state,self.maxActions,self.maxStates = self.env.startGame()
        
        self.done = False

    def getFFF(self):
        return self.env.getFF()

    def getAdvanceMove(self):
        #print(self.env.getNext())
        return self.env.getNext()

    def setAdvanceMove(self):
        self.env.setNext(True)

    def stopGUI(self):
        self.env.stopGui()

    def getFinalState(self):
        return self.env.getFinalState()

    def getFinalReward(self):
        return self.env.getFinalReward()

    def getMaxStates(self):
        return self.maxStates

    def getState(self):
        return self.state

    def getMaxActions(self):
        return self.maxActions
    
    def reset(self):
        self.env.startGame()

    def render(self):
        self.env.render()

    def getActions(self):
        return self.env.getMoves()

    def take_action(self, action):  
        self.newState,reward,done,nextActions = self.env.step(action)
        #newState is other players state
        return self.newState,torch.tensor([reward], device=self.device),done,nextActions

    def increment_turn(self):
        self.state = self.newState

    def getReward(self):
        return self.getFinalReward()
        

        

#device = torch.device('cuda:1')


"""jim = DQN(2,[24,32],7)
print(jim.layers)


choice = jim.forward(torch.tensor([[2.,2.]]))
print(choice)

myStrategy = EpsilonGreedyStrategy(1,0.01,0.001)
b = Agent(myStrategy,7,device)

actions = [1,2,3,5,6,7]
print(b.select_action(torch.tensor([[2.,2.]]),jim,actions))

"""
def main(preset):
    print("hi")
    #pygame stuff
    pygame.init()
    pygame.mixer.init() #initialises pygame
    pygame.font.init()
    #myfont = pygame.font.SysFont('Comic Sans MS', 30)
    fps = 30 #the game's frames per second
    global blue
    blue = (0,0,255)
    global grey
    grey = (100,100,100)
    global green
    green = (0,255,0)
    screen = pygame.display.set_mode((1280,720),pygame.FULLSCREEN)
    pygame.display.set_caption("AI Simulation")
    clock = pygame.time.Clock()
    
    
    ############
    
    ALAPing = False
    #e = Experience(1,2,3,4)
    #print(e)
    global Experience
    Experience = namedtuple('Experience',
        ('state', 'action', 'next_state', 'reward'))
    #hyperparameters defualt
    if preset == False:
        maxEpisodes = 100
        maxSteps = 50
        learningRate = 0.001
        maxMemory = 100000
        targetUpdate = 10 #how often target network copies the policy network
        discountRate = 0.99
        exploreDecay = 0.0005
        batchSize = 256
        rows = 6
        columns = 7
        position = "home"
        
    else:#[rows,columns,position,maxEpisodes,maxSteps,learningRate,maxMemory
        #,targetUpdate,discountRate,exploreDecay,batchSize]
        rows = preset[0]
        columns = preset[1]
        position = preset[2]
        maxEpisodes = preset[3]
        maxSteps = preset[4]
        learningRate = preset[5]
        maxMemory = preset[6]
        targetUpdate = preset[7]
        discountRate = preset[8]
        exploreDecay = preset[9]
        batchSize = preset[10]
    
    dmaxEpisodes = 100
    dmaxSteps = 50
    dlearningRate = 0.001
    dmaxMemory = 100000
    dtargetUpdate = 10 #how often target network copies the policy network
    ddiscountRate = 0.99
    dexploreDecay = 0.0005
    dbatchSize = 256
    
    

    
    
    title = pygame.image.load(os.path.join("Project_AI_Title.png")).convert()
    #title = pygame.transform.scale(title, (688, 262))#rotate for other directions
    quitButton = Button(390,460,500,100,grey,blue,True,(0,0,0),text = "Quit")
    startButton = Button(390,310,500,100,grey,blue,True,(0,0,0),text = "Start")
    backButton = Button(10,10,100,100,grey,blue,True,(0,0,0),text = "Back")
    resetButton = Button(10,125,100,100,grey,blue,True,(0,0,0),text = "Reset")
    
    
    
    trainButton = Button(390,250,500,70,grey,blue,True,(0,0,0),text = "Train AI")

    global trainButtonProgress
    trainButtonProgress = 1
    
    trainButtonBackground = Button(390,250,500,70,grey,blue,True,(0,0,0))
    
    trainALAPButton = Button(390,330,500,70,grey,blue,True,(0,0,0),text = "Train AI until stop")
    previewButtonAIvAI = Button(390,410,500,70,grey,blue,True,(0,0,0),text = "Watch AI vs AI")
    previewButtonHvAI = Button(390,490,500,70,grey,blue,True,(0,0,0),text = "Play vs AI")
    previewButtonHvH = Button(390,570,500,70,grey,blue,True,(0,0,0),text = "Play Human vs Human")
    
    
    inputDisplay = Button(1000,255,200,50,grey,blue,True,(0,0,0),text = "Inputs")
    outputDisplay = Button(1000,640,200,50,grey,blue,True,(0,0,0),text = "Outputs")  
    
    dl1 = 32
    dl2 = 24
    dl3 = 0
    dl4 = 0
    dl5 = 0
    dl6 = 0
    
    l1 = dl1
    l2 = dl2
    l3 = dl3
    l4 = dl4
    l5 = dl5
    l6 = dl6
    
    l1Display = Button(1000,310,200,50,grey,blue,True,(0,0,0),text = str(l1))
    l2Display = Button(1000,365,200,50,grey,blue,True,(0,0,0),text = str(l2))
    l3Display = Button(1000,420,200,50,grey,blue,True,(0,0,0),text = str(l3))
    l4Display = Button(1000,475,200,50,grey,blue,True,(0,0,0),text = str(l4))
    l5Display = Button(1000,530,200,50,grey,blue,True,(0,0,0),text = str(l5))
    l6Display = Button(1000,585,200,50,grey,blue,True,(0,0,0),text = str(l6))
    
    l1Increase = Button(1215,310,50,50,grey,blue,True,(0,0,0),text = ">")
    l1Decrease = Button(935,310,50,50,grey,blue,True,(0,0,0),text = "<")
    l2Increase = Button(1215,365,50,50,grey,blue,True,(0,0,0),text = ">")
    l2Decrease = Button(935,365,50,50,grey,blue,True,(0,0,0),text = "<")
    l3Increase = Button(1215,420,50,50,grey,blue,True,(0,0,0),text = ">")
    l3Decrease = Button(935,420,50,50,grey,blue,True,(0,0,0),text = "<")
    l4Increase = Button(1215,475,50,50,grey,blue,True,(0,0,0),text = ">")
    l4Decrease = Button(935,475,50,50,grey,blue,True,(0,0,0),text = "<")
    l5Increase = Button(1215,530,50,50,grey,blue,True,(0,0,0),text = ">")
    l5Decrease = Button(935,530,50,50,grey,blue,True,(0,0,0),text = "<")
    l6Increase = Button(1215,585,50,50,grey,blue,True,(0,0,0),text = ">")
    l6Decrease = Button(935,585,50,50,grey,blue,True,(0,0,0),text = "<")
    
    selectGameButton = Button(490,290,300,100,grey,blue,True,(0,0,0),text = "Select Game")
    
    advanceButton = Button(1150,10,120,120,grey,blue,True,(0,0,0),text = "Advance")
    
    connect4Button = Button(20,430,300,100,grey,blue,True,(0,0,0),text = "Connect 4")
    draughtsButton = Button(335,430,300,100,grey,blue,True,(0,0,0),text = "Draughts")
    chessButton = Button(650,430,300,100,grey,blue,True,(0,0,0),text = "Chess")
    otherGameButton = Button(965,430,300,100,grey,blue,True,(0,0,0),text = "Other Game")
    
    rowsButton = Button(80,365,200,50,grey,blue,True,(0,0,0),text = "Rows:" + str(rows))
    increaseRowButton = Button(295,365,50,50,grey,blue,True,(0,0,0),text = ">")
    decreaseRowButton = Button(15,365,50,50,grey,blue,True,(0,0,0),text = "<")
    
    columnsButton = Button(80,530,200,50,grey,blue,True,(0,0,0),text = "Columns:" + str(columns))
    increaseColumnButton = Button(295,530,50,50,grey,blue,True,(0,0,0),text = ">")
    decreaseColumnButton = Button(15,530,50,50,grey,blue,True,(0,0,0),text = "<")
    
    maxEpisodesButton = Button(490,255,300,50,grey,blue,True,(0,0,0),text = "Max Episodes:" + str(maxEpisodes))
    maxStepsButton = Button(490,310,300,50,grey,blue,True,(0,0,0),text = "Max Steps:" + str(maxSteps))
    learningRateButton = Button(490,365,300,50,grey,blue,True,(0,0,0),text = "Learning Rate:" + str(learningRate))
    maxMemoryButton = Button(490,420,300,50,grey,blue,True,(0,0,0),text = "Max Memory:" + str(maxMemory))
    targetUpdateButton = Button(490,475,300,50,grey,blue,True,(0,0,0),text = "Target Update:" + str(targetUpdate))
    discountRateButton = Button(490,530,300,50,grey,blue,True,(0,0,0),text = "Discount Rate:" + str(discountRate))
    exploreDecayButton = Button(490,585,300,50,grey,blue,True,(0,0,0),text = "Explore Decay:" + str(exploreDecay))
    batchSizeButton = Button(490,640,300,50,grey,blue,True,(0,0,0),text = "Batch Size:" + str(batchSize))
    
    increase11 = Button(805,255,50,50,grey,blue,True,(0,0,0),text = ">")
    increase12 = Button(870,255,50,50,grey,blue,True,(0,0,0),text = ">>")
    decrease11 = Button(425,255,50,50,grey,blue,True,(0,0,0),text = "<")
    decrease12 = Button(360,255,50,50,grey,blue,True,(0,0,0),text = "<<")
    
    increase21 = Button(805,310,50,50,grey,blue,True,(0,0,0),text = ">")
    increase22 = Button(870,310,50,50,grey,blue,True,(0,0,0),text = ">>")
    decrease21 = Button(425,310,50,50,grey,blue,True,(0,0,0),text = "<")
    decrease22 = Button(360,310,50,50,grey,blue,True,(0,0,0),text = "<<")
    
    increase31 = Button(805,365,50,50,grey,blue,True,(0,0,0),text = ">")
    increase32 = Button(870,365,50,50,grey,blue,True,(0,0,0),text = ">>")
    decrease31 = Button(425,365,50,50,grey,blue,True,(0,0,0),text = "<")
    decrease32 = Button(360,365,50,50,grey,blue,True,(0,0,0),text = "<<")
    
    increase41 = Button(805,420,50,50,grey,blue,True,(0,0,0),text = ">")
    increase42 = Button(870,420,50,50,grey,blue,True,(0,0,0),text = ">>")
    decrease41 = Button(425,420,50,50,grey,blue,True,(0,0,0),text = "<")
    decrease42 = Button(360,420,50,50,grey,blue,True,(0,0,0),text = "<<")
    
    increase51 = Button(805,475,50,50,grey,blue,True,(0,0,0),text = ">")
    increase52 = Button(870,475,50,50,grey,blue,True,(0,0,0),text = ">>")
    decrease51 = Button(425,475,50,50,grey,blue,True,(0,0,0),text = "<")
    decrease52 = Button(360,475,50,50,grey,blue,True,(0,0,0),text = "<<")
    
    increase61 = Button(805,530,50,50,grey,blue,True,(0,0,0),text = ">")
    increase62 = Button(870,530,50,50,grey,blue,True,(0,0,0),text = ">>")
    decrease61 = Button(425,530,50,50,grey,blue,True,(0,0,0),text = "<")
    decrease62 = Button(360,530,50,50,grey,blue,True,(0,0,0),text = "<<")
    
    increase71 = Button(805,585,50,50,grey,blue,True,(0,0,0),text = ">")
    increase72 = Button(870,585,50,50,grey,blue,True,(0,0,0),text = ">>")
    decrease71 = Button(425,585,50,50,grey,blue,True,(0,0,0),text = "<")
    decrease72 = Button(360,585,50,50,grey,blue,True,(0,0,0),text = "<<")
    
    increase81 = Button(805,640,50,50,grey,blue,True,(0,0,0),text = ">")
    increase82 = Button(870,640,50,50,grey,blue,True,(0,0,0),text = ">>")
    decrease81 = Button(425,640,50,50,grey,blue,True,(0,0,0),text = "<")
    decrease82 = Button(360,640,50,50,grey,blue,True,(0,0,0),text = "<<")
    
    
    
    global device
    global myStrategy
    device = torch.device('cpu')
    #device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    myStrategy = EpsilonGreedyStrategy(1,0.01,exploreDecay)


    
    setup = True
    running = True
    
    global loadHvH
    loadHvH = False
    global loadAIvAI
    loadAIvAI = False
    global reload
    reload = False
    
    while running:
        clock.tick(fps)
        pygame.display.flip()
        screen.fill((0,0,0))
        screen.blit(title,(188,0))
            
        mouseUp = False
        for event in pygame.event.get():
            #if event.type == pygame.KEYDOWN:
                #pass
            if event.type == pygame.MOUSEBUTTONUP:
                mouseUp = True
    
        pos = pygame.mouse.get_pos()
        
        if position == "home":
            startButton.hovering(pos)
            startButton.create(screen)
            quitButton.hovering(pos)
            quitButton.create(screen)
        
    
            if quitButton.click(pos,mouseUp):
                running = False
                pygame.quit()
    
            if startButton.click(pos,mouseUp):
                position = "gameSelect"
    
        elif position == "gameSelect":
            selectGameButton.create(screen)
            
            backButton.create(screen)
            backButton.hovering(pos)
    
         
    
            connect4Button.create(screen)
            connect4Button.hovering(pos)
    
            draughtsButton.create(screen)
            draughtsButton.hovering(pos)
    
            chessButton.create(screen)
            chessButton.hovering(pos)
    
            otherGameButton.create(screen)
            otherGameButton.hovering(pos)
    
            if backButton.click(pos,mouseUp):
                position = "home"
            
            if connect4Button.click(pos,mouseUp):
                position = "connect4Setup"
    
        elif position == "connect4Setup":
            backButton.create(screen)
            backButton.hovering(pos)
            resetButton.create(screen)
            resetButton.hovering(pos)
            advanceButton.create(screen)
            advanceButton.hovering(pos)   
            
            maxEpisodesButton.create(screen)
    
            increase11.create(screen)
            increase11.hovering(pos)
            if increase11.click(pos,mouseUp):
                maxEpisodes += 1
                maxEpisodesButton = Button(490,255,300,50,grey,blue,True,(0,0,0),text = "Max Episodes:" + str(maxEpisodes))
            increase12.create(screen)
            increase12.hovering(pos)
            if increase12.click(pos,mouseUp):
                maxEpisodes += 50
                maxEpisodesButton = Button(490,255,300,50,grey,blue,True,(0,0,0),text = "Max Episodes:" + str(maxEpisodes))
                
            decrease11.create(screen)
            decrease11.hovering(pos)
            if decrease11.click(pos,mouseUp):
                maxEpisodes -= 1
                if maxEpisodes < 1:
                    maxEpisodes = 1
                maxEpisodesButton = Button(490,255,300,50,grey,blue,True,(0,0,0),text = "Max Episodes:" + str(maxEpisodes))
            decrease12.create(screen)
            decrease12.hovering(pos)
            if decrease12.click(pos,mouseUp):
                maxEpisodes -= 50
                if maxEpisodes < 1:
                    maxEpisodes = 1
                maxEpisodesButton = Button(490,255,300,50,grey,blue,True,(0,0,0),text = "Max Episodes:" + str(maxEpisodes))
    
            maxStepsButton.create(screen)
    
            increase21.create(screen)
            increase21.hovering(pos)
            if increase21.click(pos,mouseUp):
                maxSteps += 1
                maxStepsButton = Button(490,310,300,50,grey,blue,True,(0,0,0),text = "Max Steps:" + str(maxSteps))
            increase22.create(screen)
            increase22.hovering(pos)
            if increase22.click(pos,mouseUp):
                maxSteps += 50
                maxStepsButton = Button(490,310,300,50,grey,blue,True,(0,0,0),text = "Max Steps:" + str(maxSteps))
            decrease21.create(screen)
            decrease21.hovering(pos)
            if decrease21.click(pos,mouseUp):
                maxSteps -= 1
                if maxSteps < 1:
                    maxSteps = 1
                maxStepsButton = Button(490,310,300,50,grey,blue,True,(0,0,0),text = "Max Steps:" + str(maxSteps))
            decrease22.create(screen)
            decrease22.hovering(pos)
            if decrease22.click(pos,mouseUp):
                maxSteps -= 50
                if maxSteps < 1:
                    maxSteps = 1
                maxStepsButton = Button(490,310,300,50,grey,blue,True,(0,0,0),text = "Max Steps:" + str(maxSteps))
    
    
            learningRateButton.create(screen)
    
            increase31.create(screen)
            increase31.hovering(pos)
            if increase31.click(pos,mouseUp):
                learningRate += 0.0001
                if learningRate > 1:
                    learningRate = 1
                learningRateButton = Button(490,365,300,50,grey,blue,True,(0,0,0),text = "Learning Rate:" + str(round(learningRate,5)))
            increase32.create(screen)
            increase32.hovering(pos)
            if increase32.click(pos,mouseUp):
                learningRate += 0.001
                if learningRate > 1:
                    learningRate = 1
                learningRateButton = Button(490,365,300,50,grey,blue,True,(0,0,0),text = "Learning Rate:" + str(round(learningRate,5)))
    
            decrease31.create(screen)
            decrease31.hovering(pos)
            if decrease31.click(pos,mouseUp):
                learningRate -= 0.0001
                if learningRate < 0.0001:
                    learningRate = 0.0001
                learningRateButton = Button(490,365,300,50,grey,blue,True,(0,0,0),text = "Learning Rate:" + str(round(learningRate,5)))
    
            decrease32.create(screen)
            decrease32.hovering(pos)
            if decrease32.click(pos,mouseUp):
                learningRate -= 0.001
                if learningRate < 0.0001:
                    learningRate = 0.0001
                learningRateButton = Button(490,365,300,50,grey,blue,True,(0,0,0),text = "Learning Rate:" + str(round(learningRate,5)))
    
    
            maxMemoryButton.create(screen)
    
            increase41.create(screen)
            increase41.hovering(pos)
            if increase41.click(pos,mouseUp):
                maxMemory += 1000
                maxMemoryButton = Button(490,420,300,50,grey,blue,True,(0,0,0),text = "Max Memory:" + str(round(maxMemory,5)))
    
            increase42.create(screen)
            increase42.hovering(pos)
            if increase42.click(pos,mouseUp):
                maxMemory += 10000
                maxMemoryButton = Button(490,420,300,50,grey,blue,True,(0,0,0),text = "Max Memory:" + str(round(maxMemory,5)))
    
            decrease41.create(screen)
            decrease41.hovering(pos)
            if decrease41.click(pos,mouseUp):
                maxMemory -= 1000
                if maxMemory < 1000:
                    maxMemory = 1000
                maxMemoryButton = Button(490,420,300,50,grey,blue,True,(0,0,0),text = "Max Memory:" + str(round(maxMemory,5)))
    
            decrease42.create(screen)
            decrease42.hovering(pos)
            if decrease42.click(pos,mouseUp):
                maxMemory -= 10000
                if maxMemory < 1000:
                    maxMemory = 1000
                maxMemoryButton = Button(490,420,300,50,grey,blue,True,(0,0,0),text = "Max Memory:" + str(round(maxMemory,5)))
    
    
            targetUpdateButton.create(screen)
    
            increase51.create(screen)
            increase51.hovering(pos)
            if increase51.click(pos,mouseUp):
                targetUpdate += 1
                targetUpdateButton = Button(490,475,300,50,grey,blue,True,(0,0,0),text = "Target Update:" + str(round(targetUpdate,5)))
    
            increase52.create(screen)
            increase52.hovering(pos)
            if increase52.click(pos,mouseUp):
                targetUpdate += 10
                targetUpdateButton = Button(490,475,300,50,grey,blue,True,(0,0,0),text = "Target Update:" + str(round(targetUpdate,5)))
    
            decrease51.create(screen)
            decrease51.hovering(pos)
            if decrease51.click(pos,mouseUp):
                targetUpdate -= 1
                if targetUpdate < 1:
                    targetUpdate = 1
                targetUpdateButton = Button(490,475,300,50,grey,blue,True,(0,0,0),text = "Target Update:" + str(round(targetUpdate,5)))
    
            decrease52.create(screen)
            decrease52.hovering(pos)
            if decrease52.click(pos,mouseUp):
                targetUpdate -= 10
                if targetUpdate < 1:
                    targetUpdate = 1
                targetUpdateButton = Button(490,475,300,50,grey,blue,True,(0,0,0),text = "Target Update:" + str(round(targetUpdate,5)))
    
    
            discountRateButton.create(screen)
    
            increase61.create(screen)
            increase61.hovering(pos)
            if increase61.click(pos,mouseUp):
                discountRate += 0.0001
                if discountRate > 0.9999:
                    discountRate = 0.9999
                discountRateButton = Button(490,530,300,50,grey,blue,True,(0,0,0),text = "Discount Rate:" + str(round(discountRate,5)))
    
            increase62.create(screen)
            increase62.hovering(pos)
            if increase62.click(pos,mouseUp):
                discountRate += 0.01
                if discountRate > 0.9999:
                    discountRate = 0.9999
                discountRateButton = Button(490,530,300,50,grey,blue,True,(0,0,0),text = "Discount Rate:" + str(round(discountRate,5)))
    
            decrease61.create(screen)
            decrease61.hovering(pos)
            if decrease61.click(pos,mouseUp):
                discountRate -= 0.0001
                if discountRate < 0.0001:
                    discountRate = 0.0001
                discountRateButton = Button(490,530,300,50,grey,blue,True,(0,0,0),text = "Discount Rate:" + str(round(discountRate,5)))
    
            decrease62.create(screen)
            decrease62.hovering(pos)
            if decrease62.click(pos,mouseUp):
                discountRate -= 0.01
                if discountRate < 0.0001:
                    discountRate = 0.0001
                discountRateButton = Button(490,530,300,50,grey,blue,True,(0,0,0),text = "Discount Rate:" + str(round(discountRate,5)))
    
    
            exploreDecayButton.create(screen)
    
            increase71.create(screen)
            increase71.hovering(pos)
            if increase71.click(pos,mouseUp):
                exploreDecay += 0.00001
                if exploreDecay > 0.9999:
                    exploreDecay = 0.9999
                exploreDecayButton = Button(490,585,300,50,grey,blue,True,(0,0,0),text = "Exp. Decay:" + str(round(exploreDecay,5)))
    
            increase72.create(screen)
            increase72.hovering(pos)
            if increase72.click(pos,mouseUp):
                exploreDecay += 0.001
                if exploreDecay > 0.9999:
                    exploreDecay = 0.9999
                exploreDecayButton = Button(490,585,300,50,grey,blue,True,(0,0,0),text = "Explore Decay:" + str(round(exploreDecay,5)))
    
            decrease71.create(screen)
            decrease71.hovering(pos)
            if decrease71.click(pos,mouseUp):
                exploreDecay -= 0.00001
                if exploreDecay < 0.00001:
                    exploreDecay = 0.00001
                exploreDecayButton = Button(490,585,300,50,grey,blue,True,(0,0,0),text = "Explore Decay:" + str(round(exploreDecay,5)))
    
            decrease72.create(screen)
            decrease72.hovering(pos)
            if decrease72.click(pos,mouseUp):
                exploreDecay -= 0.001
                if exploreDecay < 0.00001:
                    exploreDecay = 0.00001
                exploreDecayButton = Button(490,585,300,50,grey,blue,True,(0,0,0),text = "Explore Decay:" + str(round(exploreDecay,5)))
    
    
            batchSizeButton.create(screen)
    
            increase81.create(screen)
            increase81.hovering(pos)
            if increase81.click(pos,mouseUp):
                batchSize += 1
                batchSizeButton = Button(490,640,300,50,grey,blue,True,(0,0,0),text = "Batch Size:" + str(round(batchSize,5)))
    
      
            increase82.create(screen)
            increase82.hovering(pos)
            if increase82.click(pos,mouseUp):
                batchSize += 50
                batchSizeButton = Button(490,640,300,50,grey,blue,True,(0,0,0),text = "Batch Size:" + str(round(batchSize,5)))
    
            decrease81.create(screen)
            decrease81.hovering(pos)
            if decrease81.click(pos,mouseUp):
                batchSize -= 1
                if batchSize < 1:
                    batchSize = 1
                batchSizeButton = Button(490,640,300,50,grey,blue,True,(0,0,0),text = "Batch Size:" + str(round(batchSize,5)))
    
            decrease82.create(screen)
            decrease82.hovering(pos)
            if decrease82.click(pos,mouseUp):
                batchSize -= 50
                if batchSize < 1:
                    batchSize = 1
                batchSizeButton = Button(490,640,300,50,grey,blue,True,(0,0,0),text = "Batch Size:" + str(round(batchSize,5)))
    
            rowsButton.create(screen)
            
    
            columnsButton.create(screen)
            
    
            increaseRowButton.create(screen)
            increaseRowButton.hovering(pos)
            decreaseRowButton.create(screen)
            decreaseRowButton.hovering(pos)
    
            increaseColumnButton.create(screen)
            increaseColumnButton.hovering(pos)
            decreaseColumnButton.create(screen)
            decreaseColumnButton.hovering(pos)
    
            inputDisplay.create(screen)
            outputDisplay.create(screen)
    
            l1Display.create(screen)
            l2Display.create(screen)
            l3Display.create(screen)
            l4Display.create(screen)
            l5Display.create(screen)
            l6Display.create(screen)
    
            l1Increase.create(screen)
            l1Increase.hovering(pos)
            if l1Increase.click(pos,mouseUp):
                l1 += 1
                l1Display = Button(1000,310,200,50,grey,blue,True,(0,0,0),text = str(l1))
                
            l2Increase.create(screen)
            l2Increase.hovering(pos)
            if l2Increase.click(pos,mouseUp):
                l2 += 1
                l2Display = Button(1000,365,200,50,grey,blue,True,(0,0,0),text = str(l2))
            l3Increase.create(screen)
            l3Increase.hovering(pos)
            if l3Increase.click(pos,mouseUp):
                l3 += 1
                l3Display = Button(1000,420,200,50,grey,blue,True,(0,0,0),text = str(l3))
                
            l4Increase.create(screen)
            l4Increase.hovering(pos)
            if l4Increase.click(pos,mouseUp):
                l4 += 1
                l4Display = Button(1000,475,200,50,grey,blue,True,(0,0,0),text = str(l4))
            l5Increase.create(screen)
            l5Increase.hovering(pos)
            if l5Increase.click(pos,mouseUp):
                l5 += 1
                l5Display = Button(1000,530,200,50,grey,blue,True,(0,0,0),text = str(l5))
            l6Increase.create(screen)
            l6Increase.hovering(pos)
            if l6Increase.click(pos,mouseUp):
                l6 += 1
                l6Display = Button(1000,585,200,50,grey,blue,True,(0,0,0),text = str(l6))
    
            l1Decrease.create(screen)
            l1Decrease.hovering(pos)
            if l1Decrease.click(pos,mouseUp):
                l1 -= 1
                if l1 < 1:
                    l1 = 1
                l1Display = Button(1000,310,200,50,grey,blue,True,(0,0,0),text = str(l1))
    
            l2Decrease.create(screen)
            l2Decrease.hovering(pos)
            if l2Decrease.click(pos,mouseUp):
                l2 -= 1
                if l2 < 0:
                    l2 = 0
                l2Display = Button(1000,365,200,50,grey,blue,True,(0,0,0),text = str(l2))
    
            l3Decrease.create(screen)
            l3Decrease.hovering(pos)
            if l3Decrease.click(pos,mouseUp):
                l3 -= 1
                if l3 < 0:
                    l3 = 0
                l3Display = Button(1000,420,200,50,grey,blue,True,(0,0,0),text = str(l3))
    
            l4Decrease.create(screen)
            l4Decrease.hovering(pos)
            if l4Decrease.click(pos,mouseUp):
                l4 -= 1
                if l4 < 0:
                    l4 = 0
                l4Display = Button(1000,475,200,50,grey,blue,True,(0,0,0),text = str(l4))
    
            l5Decrease.create(screen)
            l5Decrease.hovering(pos)
            if l5Decrease.click(pos,mouseUp):
                l5 -= 1
                if l5 < 0:
                    l5 = 0
                l5Display = Button(1000,530,200,50,grey,blue,True,(0,0,0),text = str(l5))
    
            l6Decrease.create(screen)
            l6Decrease.hovering(pos)
            if l6Decrease.click(pos,mouseUp):
                l6 -= 1
                if l6 < 0:
                    l6 = 0
                l6Display = Button(1000,585,200,50,grey,blue,True,(0,0,0),text = str(l6))
    
            
            if increaseRowButton.click(pos,mouseUp):
                rows += 1
             
                rowsButton = Button(80,365,200,50,grey,blue,True,(0,0,0),text = "Rows:" + str(rows))
    
            if decreaseRowButton.click(pos,mouseUp):
                rows -= 1
                if rows < 4:
                    rows = 4
                rowsButton = Button(80,365,200,50,grey,blue,True,(0,0,0),text = "Rows:" + str(rows))
    
            if increaseColumnButton.click(pos,mouseUp):
                columns += 1
                columnsButton = Button(80,530,200,50,grey,blue,True,(0,0,0),text = "Columns:" + str(columns))
    
    
            if decreaseColumnButton.click(pos,mouseUp):
                columns -= 1
                if columns < 4:
                    columns = 4
    
                columnsButton = Button(80,530,200,50,grey,blue,True,(0,0,0),text = "Columns:" + str(columns))
    
    
            if backButton.click(pos,mouseUp):
                position = "gameSelect"
                global createdNetwork
                createdNetwork = False
    
            if resetButton.click(pos,mouseUp):
                maxEpisodes = dmaxEpisodes
                maxSteps = dmaxSteps
                learningRate = dlearningRate
                maxMemory = dmaxMemory
                targetUpdate = dtargetUpdate #how often target network copies the policy network
                discountRate = ddiscountRate
                exploreDecay = dexploreDecay
                batchSize = dbatchSize
                maxEpisodesButton = Button(490,255,300,50,grey,blue,True,(0,0,0),text = "Max Episodes:" + str(maxEpisodes))
                maxStepsButton = Button(490,310,300,50,grey,blue,True,(0,0,0),text = "Max Steps:" + str(maxSteps))
                learningRateButton = Button(490,365,300,50,grey,blue,True,(0,0,0),text = "Learning Rate:" + str(learningRate))
                maxMemoryButton = Button(490,420,300,50,grey,blue,True,(0,0,0),text = "Max Memory:" + str(maxMemory))
                targetUpdateButton = Button(490,475,300,50,grey,blue,True,(0,0,0),text = "Target Update:" + str(targetUpdate))
                discountRateButton = Button(490,530,300,50,grey,blue,True,(0,0,0),text = "Discount Rate:" + str(discountRate))
                exploreDecayButton = Button(490,585,300,50,grey,blue,True,(0,0,0),text = "Explore Decay:" + str(exploreDecay))
                batchSizeButton = Button(490,640,300,50,grey,blue,True,(0,0,0),text = "Batch Size:" + str(batchSize))
                rows = 6
                columns = 7
    
                rowsButton = Button(80,365,200,50,grey,blue,True,(0,0,0),text = "Rows:" + str(rows))
                columnsButton = Button(80,530,200,50,grey,blue,True,(0,0,0),text = "Columns:" + str(columns))
    
                l1 = dl1
                l2 = dl2
                l3 = dl3
                l4 = dl4
                l5 = dl5
                l6 = dl6
    
                l1Display = Button(1000,310,200,50,grey,blue,True,(0,0,0),text = str(l1))
                l2Display = Button(1000,365,200,50,grey,blue,True,(0,0,0),text = str(l2))
                l3Display = Button(1000,420,200,50,grey,blue,True,(0,0,0),text = str(l3))
                l4Display = Button(1000,475,200,50,grey,blue,True,(0,0,0),text = str(l4))
                l5Display = Button(1000,530,200,50,grey,blue,True,(0,0,0),text = str(l5))
                l6Display = Button(1000,585,200,50,grey,blue,True,(0,0,0),text = str(l6))
    
            if advanceButton.click(pos,mouseUp):
                position = "connect4"
                global training
                training = False
                ALAPing = False
    
        elif position == "connect4":
            
            backButton.create(screen)
            backButton.hovering(pos)
            
            trainButtonBackground.create(screen)
            trainButton.create(screen)
            
            trainALAPButton.create(screen)
            
            previewButtonAIvAI.create(screen)
            previewButtonAIvAI.hovering(pos)
            
            previewButtonHvAI.create(screen)
            previewButtonHvAI.hovering(pos)
            
            previewButtonHvH.create(screen)
            previewButtonHvH.hovering(pos)
            
            
            
            if previewButtonAIvAI.click(pos,mouseUp):
                pygame.quit()
                loadAIvAI = True
                reload = True
                training = True
                 
                trainingThread = threading.Thread(target=trainGame1v1,
                    args=["connect4",hiddenLayers,2,maxSteps,
                    learningRate,maxMemory,targetUpdate,discountRate,exploreDecay,
                    batchSize,rows,columns,True,False])

                trainingThread.start()
                
                return rows,columns,position,maxEpisodes,maxSteps,learningRate,maxMemory,targetUpdate,discountRate,exploreDecay,batchSize

            
            if previewButtonHvH.click(pos,mouseUp):
                pygame.quit()
                loadHvH = True
                reload = True
                return rows,columns,position,maxEpisodes,maxSteps,learningRate,maxMemory,targetUpdate,discountRate,exploreDecay,batchSize
                #import Connect4
                #pygame.quit()
                #playGame = threading.Thread(target=Connect4.Game,
                #args=[True,1,rows,columns]).start() 
                #pass in using lists
    
                #playGame.join()
                #pygame.init()
                #pygame.mixer.init() #initialises pygame
                #pygame.font.init() 
                
                #connect4.game(True,rows,columns)
                
            if not training:
                trainButton.hovering(pos)
                trainALAPButton.hovering(pos)
                
            
            if backButton.click(pos,mouseUp):
                position = "connect4Setup"
                setup  = True
                global stopGame
                stopGame = True
       
            if setup:
                setup = False
                hiddenLayers = []
                hiddenLayers.append(l1)
                if l2 > 0:
                    hiddenLayers.append(l2)
                if l3 > 0:
                    hiddenLayers.append(l3)
                if l4 > 0:
                    hiddenLayers.append(l4)
                if l5 > 0:
                    hiddenLayers.append(l5)
                if l6 > 0:
                    hiddenLayers.append(l6)


            if training and not ALAPing:
                trainButton = Button(390,250,trainButtonProgress,70,green,green,True,(0,0,0))
            else:
                trainButton = Button(390,250,500,70,grey,blue,True,(0,0,0),text = "Train AI")
    
            if trainButton.click(pos,mouseUp):
                print("Training Starting...")
                training = True
                trainButtonProgress = 1
                 
                trainingThread = threading.Thread(target=trainGame1v1,
                    args=["connect4",hiddenLayers,maxEpisodes,maxSteps,
                    learningRate,maxMemory,targetUpdate,discountRate,exploreDecay,
                    batchSize,rows,columns,False,False])
    
                trainingThread.start()
        
            elif trainALAPButton.click(pos,mouseUp) and not training and not ALAPing:
                training = True
                ALAPing = True
                trainALAPButton = Button(390,330,500,70,(255,0,0),blue,True,(0,0,0),text = "Stop Training")
                trainingThread = threading.Thread(target=trainGame1v1,
                    args=["connect4",hiddenLayers,999999999,maxSteps,
                    learningRate,maxMemory,targetUpdate,discountRate,exploreDecay,
                    batchSize,rows,columns,False,True])

                trainingThread.start()

            elif trainALAPButton.click(pos,mouseUp) and training and ALAPing:
                ALAPing = False
                stopGame = True
                training = False
                loadAIvAI = False
                trainALAPButton = Button(390,330,500,70,grey,blue,True,(0,0,0),text = "Train AI until stop")
    
                
                #start thread
    
            #make this a procedure that runs in a new thread
            
    return None,None,None,None,None,None,None,None,None,None,None
        

rows,columns,position,maxEpisodes,maxSteps,learningRate,maxMemory,targetUpdate,discountRate,exploreDecay,batchSize = main(False) 
while reload:
    
    if loadHvH:

        playing = Connect4.Game(True,1,rows,columns)
        print("hert")

        while playing.getHvh():
            time.sleep(2)

    
    while loadAIvAI:
        time.sleep(2)

        


        
        #Connect4

    reload = False
    loadHvH = False
    print("here")
    rows,columns,position,maxEpisodes,maxSteps,learningRate,maxMemory,targetUpdate,discountRate,exploreDecay,batchSize = main([rows,columns,position,maxEpisodes,maxSteps,learningRate,maxMemory,targetUpdate,discountRate,exploreDecay,batchSize]) 
    

    
    
    
    
    
