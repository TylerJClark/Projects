import pygame
import os
import sprawl
from ButtonLib import Button
import threading
import math
pygame.init()
pygame.mixer.init() #initialises pygame
pygame.font.init()
fps = 60 #the game's frames per second
all_fonts = pygame.font.get_fonts()
myfont = pygame.font.SysFont(all_fonts[7], 30)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)
grey = (128,128,128)
darkgreen = (34,139,34)
screen = pygame.display.set_mode((1280,720),pygame.FULLSCREEN)
pygame.display.set_caption("VectorTD")
clock = pygame.time.Clock()

#3 or 1, 0 or 2

"""
Game should be finished!!!

"""



class button():  #class to quickly make buttons
    def __init__(self,colour, x,y,width,height, text='',active_colour = green):
        self.current_colour = colour
        self.colour = colour #button colour
        self.active_colour = active_colour #colour of the button while the mouse hovers over it.
        self.x = x #x coordinate of top left corner of the button
        self.y = y #y coordinate of top left corner of the button
        self.width = width       #button width
        self.height = height     #button height
        self.text = text         #button text

        #these are the different button options. 
        #these options allow many different buttons to be created from this class
        
    def draw(self,screen,outline=None,show_active = False):  #method to draw the button
        if outline:   #decides if the button has an outline.
            pygame.draw.rect(screen, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0) #draws the button outline.
            #the outline is a black box which is slighly bigger than the button. This appears as an outline
        if show_active:
            self.current_colour = self.active_colour
        pygame.draw.rect(screen,self.current_colour, (self.x,self.y,self.width,self.height),0)
        #draws the button
        
        if self.text != "":   #only adds text if there is text to add
            font = pygame.font.SysFont(all_fonts[7], 25)   #defines the font used.
            text = font.render(self.text, 1, (0,0,0))      #renders the text
            screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2))) 
            #puts the text in the center of the button.

        if show_active:
            self.current_colour = self.colour
        
            
    def clicked(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False  #A method to check if the mouse is over the button.
                      #This is run when th user presses the mouse button.


    def hover(self): #makes the button change colour when the mouse is hovered over it.
            if self.clicked(pygame.mouse.get_pos()):
                self.current_colour = self.active_colour
                return True
            else:
                self.current_colour = self.colour
                return False

        

    def press(self):#checks if the mouse button is pressed.
        if self.clicked(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return True 
        return False


class enemy():
    def __init__(self,x = 0,y = 28,path=None,health = 1,damage = 1,speed = 5):
        self.x = x
        self.y = y
        self.path = path
        self.progress = 0
        self.speed = speed #lower speed is better
        self.health = health
        self.damage = damage
        self.calculateColour()
        self.calculateColourCenter()
        self.active = True
        self.currentSlow = None
        self.currentSlowDuration = None
        self.currentConfuse = 0
        self.currentConfuseWeakness = 1
        self.confuseMax = 3
        self.burn = None
        self.value = math.floor(3 + 2.5*math.log(5*self.health*(1/self.speed)))

    def calculateDamage(self):
        try:
            self.damage = math.floor(math.log(2.8 + 2.8*abs(self.health)))
        except:
            self.damage = 2
            print("hi")

    def applyBurn(self,burn):
        self.burn = burn

    def getValue(self):
        return self.value

    def getHealth(self):
        return self.health

    def changeHealth(self,damage):
        if self.currentConfuse > 0:
            self.health -= damage * self.currentConfuseWeakness
        else:
            self.health -= damage

    def getCoord(self):
        return self.x,self.y

    def getActive(self):
        return self.active

    def changeActive(self):
        self.active = not self.active

    def changeCurrentSlow(self,slow,slowDuration):
        self.currentSlow = slow
        self.currentSlowDuration = slowDuration

    def changeCurrentConfuse(self,confuse,confuseWeakness):
        if self.confuseMax > 0 and self.currentConfuse == 0:
            self.currentConfuse = confuse
            self.currentConfuseWeakness = confuseWeakness
            self.confuseMax -= 1

    def calculateColour(self): #calculates colour to be used
        if self.health <= 5:
            self.colour = (255,0,0)
            
        elif self.health <= 25:
            self.colour = (255,128,0)

        elif self.health <= 125:
            self.colour = (255,255,0)

        elif self.health <= 625:
            self.colour = (0,255,0)

        elif self.health <= 3125:
            self.colour = (0,0,255)

        elif self.health <= 15625:
            self.colour = (75,0,130)

        else:
            self.colour = (238,130,238)

    def calculateColourCenter(self):
        if self.speed >= 25:
            self.center_colour = (255,0,0)
            
        elif self.speed >= 10:
            self.center_colour = (255,128,0)

        elif self.speed >= 5:
            self.center_colour = (255,255,0)

        elif self.speed >= 4:
            self.center_colour = (0,255,0)

        elif self.speed >= 3:
            self.center_colour = (0,0,255)

        elif self.speed >= 2:
            self.center_colour = (75,0,130)

        else:
            self.center_colour = (238,130,238)        
        

    def draw(self):

        pygame.draw.rect(screen, self.colour, [self.x * 10 + 35, self.y * 10 + 155, 10, 10])
        
        pygame.draw.rect(screen, self.center_colour, [self.x * 10 + 38, self.y * 10 + 158, 4, 4])

    def move(self,timer,grid):
        slow = 1
        if self.currentSlow != None:
            slow = self.currentSlow
            self.currentSlowDuration -= 1
            if self.currentSlowDuration <= 0:
                self.currentSlow = None
            
        if self.burn != None:
            if self.burn[1] % 30 == 0:
                self.changeHealth(self.burn[0])
            self.burn[1] -= 1
            if self.burn[1] == 0:
                self.burn = None
        if timer % (math.floor(self.speed * slow)) == 0:
            if self.progress == len(self.path):
                self.calculateDamage()
                return self.damage #kill base

            self.x,self.y = self.path[self.progress]
            if self.currentConfuse == 0:                
                self.progress += 1
            else:
                if self.progress > 0:
                    self.progress -= 1
                    
            if self.currentConfuse > 0:
                self.currentConfuse -= 1
                
            elif self.currentConfuseWeakness == 1.25:
                self.currentConfuseWeakness = 1
                
                

            """else:
                if self.path == None:
                    mysprawler = sprawl.sprawler()

                    self.path = mysprawler.search(grid,(0,28),(104,28)) #0,28 --- 104,28
                self.calculated = True

                return 0"""

            return 0
        return 0
    
class tower():
    def __init__(self,x,y,size,image,ghost_image,direction,cost,towerType):
        self.towerType = towerType
        self.x = x
        self.y = y
        self.size = size
        self.image = image
        self.ghost_image = ghost_image
        self.total_cost_green = 0
        self.total_cost_pink = 0
        self.total_cost_blue = 0
        self.total_cost_orange = 0
        self.ghost = True
        self.direction = direction #direction is 0,1,2,3, with 0 = up, 1 = right, 2 = down, 3 = left
        self.thread1 = None
        self.thread2 = None
        self.thread3 = None
        self.currentUpgrade = None # = [treeside,tier]
        self.firing = False

        self.damage = 0
        
        #direction is already stored
        self.life = 0
        self.reflections = 0
        self.speed = 1
        self.aoe = False
        
        self.slow = False 
        self.slowDuration = False
        self.confuse = 0
        self.confuseWeakness = 1
        
        self.penetrating = False
        self.splitting = 0
        self.fireRate = 9999
        self.toxic = False
        self.radius = False
        
            
        self.calculateUpgradePath()
        #x,y,direction,damage,life,reflections,speed,aoe = False,slow = 0,stun = False,
        #penetrating = False,splitting = False):        
        
        self.button1 = Button(805,70,50,50,(0,200,0),(0,200,0),True,(0,0,0))
        self.button2 = Button(1045,70,50,50,(0,200,0),(0,200,0),True,(0,0,0))
        self.treeSide = None

        if self.towerType == "projector" or self.towerType == "slow_projector":
            self.life = 40
        elif self.towerType == "aoe_projector":
            self.life = 30

            
            

    
    def calculateDistance(self,x,y):
        return ((self.x - x)**2 + (self.y - y)**2)**0.5

    def getFiring(self):
        return self.firing

    def effectTurrets(self,towers,effect):
        for i in towers:
            if i.getFiring():
                if self.calculateDistance((i.getCoord()[0] + 3),i.getCoord()[1] + 3) < self.radius:
                    if effect == "speed":                        
                        i.fireRate = i.fireRate * (20/21)
                        
                    elif effect == "damage":
                        i.damage = i.damage * 1.025

    def removeEffectTurrets(self,towers,effect):
        for i in towers:
            if i.getFiring():
                if self.calculateDistance((i.getCoord()[0] + 3),i.getCoord()[1] + 3) < self.radius:
                    if effect == "speed":
                        i.fireRate = i.fireRate / (20/21)
                    elif effect == "damage":
                        i.damage = i.damage / 1.025       

    def removeEffects(self):
        if self.towerType == "barricade" and self.currentUpgrade != None:
            if self.currentUpgrade[0] == 0:
                global interestMain
                global interestShortage
                interestMain -= self.interestMain
                interestShortage -= self.interestShortage
                
            elif self.currentUpgrade[0] == 1:
                self.removeEffectTurrets(towers,"speed")
                
                if self.currentUpgrade[1] == 3:
                    self.removeEffectTurrets(towers,"speed")
                    self.removeEffectTurrets(towers,"damage")


    def effectNewTower(self,tower):
        if tower.radius != False:
            if self.getFiring():
                if self.calculateDistance((tower.getCoord()[0] + 3),tower.getCoord()[1] + 3) < tower.radius:
                    
                    if tower.currentUpgrade[0] == 1:
                        
                        self.fireRate = self.fireRate * (20/21)
                        
                    if tower.currentUpgrade[1] == 3:
                        self.damage = self.damage * 1.1            

        

                


            


    def getTowerType(self):
        return self.towerType

    def update(self,timer,particles):
        if self.firing:
            particles = self.fire(timer,particles)

        return particles
        

    def fire(self,timer,particles):
        if timer % math.ceil(self.fireRate) == 0:
            particles.append(particle(self.startLocation[0],self.startLocation[1],self.direction,self.damage,
                                      self.life,self.reflections,self.speed,self.aoe,self.slow,self.slowDuration,
                                      self.penetrating,self.splitting,self.confuse,self.confuseWeakness,toxic = self.toxic))
            

        return particles
            
            
        #x,y,direction,particle,life,reflections,speed,aoe = False,slow = 0,stun = False,
        #piercing = False,splitting = False):

    def calculate_start_location(self):
        #print("calc",self.x,self.y)
        if self.direction == 0:
            return (self.x + 2,self.y + 5)
        elif self.direction == 1:
            return (self.x + 5,self.y + 2)
        elif self.direction == 2:
            return (self.x + 2,self.y)
        elif self.direction == 3:
            return (self.x,self.y + 2)

    def calculateCostPath(self):
        self.displayPathCost = [] 
        for i in range(2):
            self.displayPathCost.append([])#trees
            for j in range(3):
                self.displayPathCost[i].append([])#upgrade level
                for k in range(4):
                    if self.upgradePathCost[i][j][k] != 0: #cost
                        self.displayPathCost[i][j].append(self.upgradePathCost[i][j][k])
        
    def calculateUpgradePath(self):#tp

        if self.towerType == "projector":
            self.upgradePath = [["Tough Particles","Harder Particles","Penetrating Particles"],
                                ["Machine Projector","Extra Reflections","Chain Reaction"]]
            self.upgradePathCost = [[[50,50,0,0],[250,250,0,0],[1500,1500,0,0]],[[100,100,0,0],[850,850,0,0],[3500,3500,0,0]]]
            self.initialCost = [75,75,0,0]


            self.total_cost_green = 75
            self.total_cost_blue = 75
            self.towerColour = [(0,255,0),(0,0,255)]
            self.calculateCostPath()

            self.upgradeDescriptions = [[[["Particles travel faster"],["and last 50% longer"]],[["Particle Damage increased by 50%"]],[["Particles move through enemies"]]],
                                       [[["Particles are fired 25% faster"]],[["Particles can be reflected 3 more times"]],[["If a particle kills an enemy, 3 new particles are created"]]]]

            self.upgradeImages = [[tough_projector,hard_projector,penetrating_projector],[machine_projector,reflect_projector,chain_projector]]
            self.upgradeImagesGhost = [[tough_projector_ghost,hard_projector_ghost,penetrating_projector_ghost],[machine_projector_ghost,reflect_projector_ghost,chain_projector_ghost]]
            self.firing = True
            self.damage = 20
            
            #direction is already stored
            self.life = 40
            self.reflections = 5
            self.speed = 4
            self.fireRate = 90

            #x,y,direction,damage,life,reflections,speed,aoe = False,slow = 0,stun = False,
            #piercing = False,splitting = False):
            
            
        elif self.towerType == "reflector":
            self.upgradePath = [["Damage Reflector","Velocity Boost","Super Damage Reflector"],
                                ["Reflective Reflector","Reflection Duplication","Reflection Efficiency"]]
            self.upgradePathCost = [[[175,0,175,0],[250,0,250,0],[2500,0,2500,0]],[[100,0,100,0],[750,0,750,0],[1000,0,1000,0]]]
            self.initialCost = [50,0,50,0]
            self.total_cost_green = 50
            self.total_cost_pink = 50
            self.towerColour = [(0,255,0),(255,192,203)]
            
            self.calculateCostPath()

            

            self.upgradeDescriptions = [[[["Particle damage increased by"],["15% per reflection"]],[["Particles gain speed and have increased lifetime"]],[["Particle damage increased by 50%"]]],
                                       [[["Particle's max reflections"],["is reduced by half"]],[["Another particle is created when one is reflected"]],[["Particles are more 50% efficient to generators (multiplicative)"]]]]

            self.upgradeImages = [[damage_reflector,speed_reflector,super_damage_reflector],[reflective_reflector,duplication_reflector,efficiency_reflector]]
            self.upgradeImagesGhost = [[damage_reflector_ghost,speed_reflector_ghost,super_damage_reflector_ghost],[reflective_reflector_ghost,duplication_reflector_ghost,efficiency_reflector_ghost]]
            
        elif self.towerType == "barricade":
            self.upgradePath = [["Barricade Banking","Higher interest","Shortage recovery"],
                                ["Speed Encouragement","Louder Encouragement","Damage Encouragement"]]
            self.upgradePathCost = [[[0,200,200,0],[0,250,250,0],[0,300,300,0]],[[0,300,300,0],[0,250,250,0],[0,1000,1000,0]]]
            self.initialCost = [0,25,25,0]
            self.total_cost_blue = 25
            self.total_cost_pink = 25

            self.towerColour = [(0,0,255),(255,192,203)]
            self.calculateCostPath()

            self.upgradeDescriptions = [[[["At the end of the wave gain 2%"],["interest on all minerals"],["(Additive)"]],[["At the end of the wave gain 3% interest on all minerals"],["(Additive)"]],[["At the end of the wave gain 10% interest on the mineral"],["you have the least of"],["(Additive)"]]],
                                       [[["Nearby towers have fire rate"],[" increased by 5% "],["(This effect stacks)"]],[["Effect radius increased"]],[["Nearby towers have damage increased by 2.5% (This effect stacks)"]]]]


            self.upgradeImages = [[banking_barricade,interest_barricade,shortage_barricade],[speed_barricade,louder_barricade,damage_barricade]]
            self.upgradeImagesGhost = [[banking_barricade_ghost,interest_barricade_ghost,shortage_barricade_ghost],[speed_barricade_ghost,louder_barricade_ghost,damage_barricade_ghost]]
            self.interestMain = 0
            self.interestShortage = 0
        elif self.towerType == "aoe_projector":
            self.upgradePath = [["Bigger Explosions","Even Bigger Explosions","Toxic Blast"],
                                ["Rapid Fire","Power Particles","Extra Reflections"]]
            self.upgradePathCost = [[[250,0,0,250],[750,0,0,750],[1500,0,0,1500]],[[150,0,0,150],[350,0,0,350],[1000,0,0,1000]]]
            self.initialCost = [150,0,0,150]
            self.total_cost_green = 150
            self.total_cost_orange = 150
            self.towerColour = [(0,255,0),(255, 165, 0)]
            self.calculateCostPath()

            self.upgradeDescriptions = [[[["Area of effect radius increased"]],[["Area of effect radius increased further"]],[["Enemy is poisoned for 10% of particles damage"],["for 5 seconds per second"]]],
                                       [[["Fire rate increased by 25%"]],[["Damage increased by 25%"]],[["Particles can be reflected 50% more times"]]]]

            self.upgradeImages = [[bigger_aoe_projector,even_bigger_aoe_projector,toxic_aoe_projector],[rapid_aoe_projector,power_aoe_projector,reflect_aoe_projector]]
            self.upgradeImagesGhost = [[bigger_aoe_projector_ghost,even_bigger_aoe_projector_ghost,toxic_aoe_projector_ghost],[rapid_aoe_projector_ghost,power_aoe_projector_ghost,reflect_aoe_projector_ghost]]
            self.firing = True
            self.fireRate = 150
            self.damage = 10
            
            #direction is already stored
            self.life = 30
            self.reflections = 5
            self.speed = 5
            self.aoe = 1
            
        elif self.towerType == "slow_projector":
            self.upgradePath = [["Cold Blast","Snowy Blast","Icy Blast"],
                                ["Confuse Enemy","More Confusion","Vulnerable Targets"]]
            self.upgradePathCost = [[[0,100,0,100],[0,250,0,250],[0,350,0,350]],[[0,350,0,350],[0,500,0,500],[0,1500,0,1500]]]
            self.initialCost = [0,100,0,100]
            self.total_cost_blue = 100
            self.total_cost_orange = 100

            self.towerColour = [(0,0,255),(255, 165, 0)]
            self.calculateCostPath()

            self.upgradeDescriptions = [[[["Enemies are slowed by"],["50% for 1 second"]],[["Enemies are slowed by 75% for 1.5 seconds"]],[["Enemies are stunned for 2 seconds"]]],
                                       [[["Enemies move backwards"],["for 0.4 seconds"]],[["Enemies move backwards for 0.8 seconds"]],[["Confused enemies take 25% more damage"]]]]

            self.upgradeImages = [[cold_slow_projector,snowy_slow_projector,icy_slow_projector],[confuse_slow_projector,more_confuse_slow_projector,vulnerable_slow_projector]]
            self.upgradeImagesGhost = [[cold_slow_projector_ghost,snowy_slow_projector_ghost,icy_slow_projector_ghost],[confuse_slow_projector_ghost,more_confuse_slow_projector_ghost,vulnerable_slow_projector_ghost]]
            self.firing = True
            self.damage = 15
            
            #direction is already stored
            self.life = 40
            self.reflections = 5
            self.speed = 4
            self.fireRate = 100
            self.slow = 1.5
            self.slowDuration = 15
            
        elif self.towerType == "generator":
            self.upgradePath = [["Efficient Generation","Masterful Generation","Particle Recycling"],
                                ["Bonus Minerals","Double Bonus Minerals","Triple Bonus Minerals"]]
            self.upgradePathCost = [[[0,0,75,75],[0,0,175,175],[0,0,750,750]],[[0,0,50,50],[0,0,300,300],[0,0,1000,1000]]]
            self.initialCost = [0,0,200,200]
            self.total_cost_pink = 200
            self.total_cost_orange = 200

            self.towerColour = [(255,192,203)  ,(255, 165, 0)]
            self.calculateCostPath()
            

            self.upgradeDescriptions = [[[["Produces 15% more minerals"]],[["Produces 30% more minerals"]],[["Particles are no longer destroyed by the generator, just get weakened"]]],
                                       [[["5% more minerals given"],["as bonus to the next"],["direction(clockwise)"]],[["10% of particles generated are given bonus to each of the"],["next 2 directions"]],[["15% of particles generated are given bonus to each of the "],["next 3 directions"]]]]

            self.upgradeImages = [[efficient_generator,masterful_generator,recycle_generator],[double_generator,triple_generator,quad_generator]]
            self.upgradeImagesGhost = [[efficient_generator_ghost,masterful_generator_ghost,recycle_generator_ghost],[double_generator_ghost,triple_generator_ghost,quad_generator_ghost]]
            

    
    def calculateUpgrade(self):#tj
        global grid
        if self.towerType == "projector":
            if self.currentUpgrade == [0,1]:
                self.speed = 3
                self.life = 72
            elif self.currentUpgrade == [0,2]:
                self.damage = self.damage * 1.5
            elif self.currentUpgrade == [0,3]:
                self.penetrating = True
                
            elif self.currentUpgrade == [1,1]:
                self.fireRate = self.fireRate * 0.75
            elif self.currentUpgrade == [1,2]:
                self.reflections = 8
            elif self.currentUpgrade == [1,3]:
                self.splitting = 3


        if self.towerType == "reflector":
            #effect = R-CONFIG-DAMAGE-VELOCITY-REFLECTIVE-DUPLICATION-EFFICIENCY
            if self.currentUpgrade == [0,1]:
                grid = self.update_grid_reflector(grid,"21fff")
            elif self.currentUpgrade == [0,2]:
                grid = self.update_grid_reflector(grid,"22fff")
            elif self.currentUpgrade == [0,3]:
                grid = self.update_grid_reflector(grid,"32fff")
                
            elif self.currentUpgrade == [1,1]:
                grid = self.update_grid_reflector(grid,"11tff")
            elif self.currentUpgrade == [1,2]:
                grid = self.update_grid_reflector(grid,"11ttf")
            elif self.currentUpgrade == [1,3]:
                grid = self.update_grid_reflector(grid,"11ttt")

        elif self.towerType == "barricade":
            global interestMain
            global interestShortage
            global towers
            global showCircle
            if self.currentUpgrade == [0,1]:
                interestMain += 0.02
                self.interestMain = 0.02
            elif self.currentUpgrade == [0,2]:
                interestMain += 0.03
                self.interestMain = 0.05
            elif self.currentUpgrade == [0,3]:
                interestShortage += 0.1
                self.interestShortage = 0.1

            
            elif self.currentUpgrade == [1,1]:
                self.radius = 10
                self.effectTurrets(towers,"speed") #change the way this works. need to keep amount stored
                
                showCircle = [(self.x) * 10 + 35, (self.y) * 10 + 155,self.radius]
            elif self.currentUpgrade == [1,2]:
                showCircle = [(self.x) * 10 + 35, (self.y) * 10 + 155,self.radius]
                self.removeEffectTurrets(towers,"speed")
                self.radius = 15
                self.effectTurrets(towers,"speed")
            elif self.currentUpgrade == [1,3]:
                self.effectTurrets(towers,"damage")

        elif self.towerType == "aoe_projector":
            if self.currentUpgrade == [0,1]:                
                self.aoe = 2
            elif self.currentUpgrade == [0,2]:
                self.aoe = 3
            elif self.currentUpgrade == [0,3]:
                self.toxic = True

            elif self.currentUpgrade == [1,1]:
                self.fireRate = self.fireRate * 0.75
            elif self.currentUpgrade == [1,2]:
                self.damage = self.damage * 1.25
            elif self.currentUpgrade == [1,3]:
                self.reflections = 8

        elif self.towerType == "slow_projector":
            if self.currentUpgrade == [0,1]:
                self.slow = 2
                self.slowDuration = 30
            elif self.currentUpgrade == [0,2]:
                self.slow = 4
                self.slowDuration = 45
            elif self.currentUpgrade == [0,3]:
                self.slow = 99999999

            elif self.currentUpgrade == [1,1]:
                self.confuse = 12
            elif self.currentUpgrade == [1,2]:
                self.confuse = 24
            elif self.currentUpgrade == [1,3]:
                self.confuseWeakness = 1.25

        elif self.towerType == "generator":
            if self.currentUpgrade == [0,1]:
                grid = self.update_grid(grid,"UU100")#uu+INCREASEmult+bonus+recycle

            elif self.currentUpgrade == [0,2]:
                grid = self.update_grid(grid,"UU200")

            elif self.currentUpgrade == [0,3]:
                grid = self.update_grid(grid,"UU201")

            elif self.currentUpgrade == [1,1]:
                grid = self.update_grid(grid,"UU010")
            elif self.currentUpgrade == [1,2]:
                grid = self.update_grid(grid,"UU020")

            elif self.currentUpgrade == [1,3]:
                grid = self.update_grid(grid,"UU030")


    def show_upgrade(self,screen,pos,mouseUp,orange_mineral,pink_mineral,blue_mineral,green_mineral,towers,re_search,grid):
        sold = False
        global showCircle
        if self.currentUpgrade == None:
            self.button1 = Button(805,70,50,50,(0,200,0),(0,200,0),True,(0,0,0))
            self.button2 = Button(1045,70,50,50,(0,200,0),(0,200,0),True,(0,0,0))
            self.button3 = Button(1220,70,50,50,(0,200,0),(0,200,0),True,(0,0,0))
            pygame.draw.rect(screen, [255,0,0], [865, 0, 5, 120])
            pygame.draw.rect(screen, [255,0,0], [1120, 0, 5, 120])


            #sell button

            char1 = 6 - len(str(self.total_cost_blue)) #this stuff is for selling towers
            char2 = 6 - len(str(self.total_cost_orange))
            if char2 < char1:
                char = char2
            else:
                char = char1

            char3 = 6 - len(str(self.total_cost_green))
            char4 = 6 - len(str(self.total_cost_pink))
            if char3 < char4:
                second_char = char3
            else:
                second_char = char4

            myfont = pygame.font.SysFont(all_fonts[7], 20)
            
                
            textsurface = myfont.render(second_char * "  " + str(math.floor(self.total_cost_green * 0.75)), False, (0, 255, 0))
            screen.blit(textsurface,(1100,70))

            textsurface = myfont.render(char * "  " + str(math.floor(self.total_cost_blue * 0.75)), False, (0, 0, 255))
            screen.blit(textsurface,(1145,70))

            textsurface = myfont.render(second_char * "  " + str(math.floor(self.total_cost_pink * 0.75)), False, (255,192,203))
            screen.blit(textsurface,(1100,95))

            textsurface = myfont.render(char * "  " + str(math.floor(self.total_cost_orange * 0.75)), False, (255, 165, 0))
            screen.blit(textsurface,(1145,95))

            textsurface = myfont.render("Sell", False, (255, 255, 255))
            screen.blit(textsurface,(1165,35))
            
            self.button1.create(screen)
            self.button2.create(screen)
            screen.blit(sellButton,(1220,70))#add sell price

            myfont = pygame.font.SysFont(all_fonts[7], 30)
            #end of sell button
            
            myfont = pygame.font.SysFont(all_fonts[7], 20)
            textsurface = myfont.render(str(self.upgradePath[0][0]), False, (0, 155, 0))
            screen.blit(textsurface,(645,10)) 
            
            textsurface = myfont.render(str(self.upgradePath[1][0]), False, (0, 155, 0))
            screen.blit(textsurface,(885,10))


            for i in range(2):
                char = 6 - len(str(self.displayPathCost[0][0][i]))
                textsurface = myfont.render(str(char * "  " + str(self.displayPathCost[0][0][i])), False, self.towerColour[i])
                screen.blit(textsurface,(670 + i * 50,93)) #cost

                char = 6 - len(str(self.displayPathCost[1][0][i]))
                textsurface = myfont.render(str(char * "  " + str(self.displayPathCost[1][0][i])), False, self.towerColour[i])
                screen.blit(textsurface,(910 + i * 50,93)) #other cost

            
            myfont = pygame.font.SysFont(all_fonts[7], 14)
            
            for i in range(len(self.upgradeDescriptions[0][0])):
                textsurface = myfont.render(str(self.upgradeDescriptions[0][0][i][0]), False, (0, 155, 0))
                screen.blit(textsurface,(645,40 + 20 * i))

            for i in range(len(self.upgradeDescriptions[1][0])):            
                textsurface = myfont.render(str(self.upgradeDescriptions[1][0][i][0]), False, (0, 155, 0))
                screen.blit(textsurface,(885,40 + 20 * i))

            myfont = pygame.font.SysFont(all_fonts[7], 30)

            #images
            self.button1.create(screen)
            self.button2.create(screen)
            
            screen.blit(self.upgradeImages[0][0],(805,70))
            screen.blit(self.upgradeImages[1][0],(1045,70))
            
            if self.towerType == "barricade" and self.treeSide == None:
                self.hoverButton = button(grey,1045,70,50,50,"")
                
                if self.hoverButton.hover():                    
                    showCircle = [(self.x) * 10 + 35, (self.y) * 10 + 155,10]
                else:
                    showCircle = False

            if self.button3.click(pos,mouseUp):
                self.hoverButton = False
                self.removeEffects()
                towers.remove(self) 
                green_mineral += math.floor(self.total_cost_green * 0.75)
                blue_mineral += math.floor(self.total_cost_blue * 0.75)
                pink_mineral += math.floor(self.total_cost_pink * 0.75)
                orange_mineral += math.floor(self.total_cost_orange * 0.75)
                grid = self.remove_grid(grid)
                re_search = True
                sold = True

            if self.button1.click(pos,mouseUp) and green_mineral >= self.upgradePathCost[0][0][0] and blue_mineral >= self.upgradePathCost[0][0][1] and pink_mineral >= self.upgradePathCost[0][0][2] and orange_mineral >= self.upgradePathCost[0][0][3]:
                self.currentUpgrade = [0,1]
                green_mineral -= self.upgradePathCost[0][0][0]
                blue_mineral -= self.upgradePathCost[0][0][1]
                pink_mineral -= self.upgradePathCost[0][0][2]
                orange_mineral -= self.upgradePathCost[0][0][3]

                self.total_cost_green += self.upgradePathCost[0][0][0]
                self.total_cost_blue += self.upgradePathCost[0][0][1]
                self.total_cost_pink += self.upgradePathCost[0][0][2]
                self.total_cost_orange += self.upgradePathCost[0][0][3]
                
                self.image = self.upgradeImages[0][0]
                self.ghost_image = self.upgradeImagesGhost[0][0]
                if self.direction == 0:
                    self.rotate("clockwise",False)
                elif self.direction == 1:
                    self.rotate("clockwise",False)
                    self.rotate("clockwise",False)
                elif self.direction == 2:
                    self.rotate("anticlockwise",False)
                    
                self.upgradeColour = (255,192,203)
                self.calculateUpgrade()
                self.treeSide = 0
                
            elif self.button2.click(pos,mouseUp) and green_mineral >= self.upgradePathCost[1][0][0] and blue_mineral >= self.upgradePathCost[1][0][1] and pink_mineral >= self.upgradePathCost[1][0][2] and orange_mineral >= self.upgradePathCost[1][0][3]:
                if self.towerType == "barricade":
                    showCircle = [(self.x) * 10 + 35, (self.y) * 10 + 155,15]
                self.currentUpgrade = [1,1]
                green_mineral -= self.upgradePathCost[1][0][0]
                blue_mineral -= self.upgradePathCost[1][0][1]
                pink_mineral -= self.upgradePathCost[1][0][2]
                orange_mineral -= self.upgradePathCost[1][0][3]

                self.total_cost_green += self.upgradePathCost[1][0][0]
                self.total_cost_blue += self.upgradePathCost[1][0][1]
                self.total_cost_pink += self.upgradePathCost[1][0][2]
                self.total_cost_orange += self.upgradePathCost[1][0][3]
                
                self.image = self.upgradeImages[1][0]
                self.ghost_image = self.upgradeImagesGhost[1][0]
                if self.direction == 0:
                    self.rotate("clockwise",False)
                elif self.direction == 1:
                    self.rotate("clockwise",False)
                    self.rotate("clockwise",False)
                elif self.direction == 2:
                    self.rotate("anticlockwise",False)
                
                self.upgradeColour = (255,192,203)
                self.calculateUpgrade()
                self.treeSide = 1
                

        elif self.currentUpgrade[1] < 3:
            self.button1 = Button(805,70,50,50,(0,200,0),(0,200,0),True,(0,0,0))
            self.button2 = Button(1220,70,50,50,(0,200,0),(0,200,0),True,(0,0,0))
            pygame.draw.rect(screen, [255,0,0], [1120, 0, 5, 120])
            
            myfont = pygame.font.SysFont(all_fonts[7], 20)
            textsurface = myfont.render(str(self.upgradePath[self.currentUpgrade[0]][self.currentUpgrade[1]]), False, (0, 155, 0))
            screen.blit(textsurface,(635,10))

            if self.towerType == "barricade" and self.treeSide == 1 and self.currentUpgrade[1] == 1:
                self.hoverButton = button(grey,805,70,50,50,"")
                
                if self.hoverButton.hover():                    
                    showCircle = [(self.x) * 10 + 35, (self.y) * 10 + 155,15]
                else:
                    showCircle = [(self.x) * 10 + 35, (self.y) * 10 + 155,10]

            if self.towerType == "barricade" and self.treeSide == 1 and self.currentUpgrade[1] == 2:
                showCircle = [(self.x) * 10 + 35, (self.y) * 10 + 155,15]
                    
            for i in range(2):
                char = 6 - len(str(self.displayPathCost[0][1][i]))
                textsurface = myfont.render(str(char * "  " + str(self.displayPathCost[self.treeSide][self.currentUpgrade[1]][i])), False, self.towerColour[i])
                screen.blit(textsurface,(655 + i * 50,93)) #cost


            myfont = pygame.font.SysFont(all_fonts[7], 14)
            
            for i in range(len(self.upgradeDescriptions[self.currentUpgrade[0]][self.currentUpgrade[1]])):
                textsurface = myfont.render(str(self.upgradeDescriptions[self.currentUpgrade[0]][self.currentUpgrade[1]][i][0]), False, (0, 155, 0))
                screen.blit(textsurface,(635,40 + 20 * i))

            

            char1 = 6 - len(str(self.total_cost_blue)) #this stuff is for selling towers
            char2 = 6 - len(str(self.total_cost_orange))
            if char2 < char1:
                char = char2
            else:
                char = char1

            char3 = 6 - len(str(self.total_cost_green))
            char4 = 6 - len(str(self.total_cost_pink))
            if char3 < char4:
                second_char = char3
            else:
                second_char = char4

            myfont = pygame.font.SysFont(all_fonts[7], 20)
            
                
            textsurface = myfont.render(second_char * "  " + str(math.floor(self.total_cost_green * 0.75)), False, (0, 255, 0))
            screen.blit(textsurface,(1100,70))

            textsurface = myfont.render(char * "  " + str(math.floor(self.total_cost_blue * 0.75)), False, (0, 0, 255))
            screen.blit(textsurface,(1145,70))

            textsurface = myfont.render(second_char * "  " + str(math.floor(self.total_cost_pink * 0.75)), False, (255,192,203))
            screen.blit(textsurface,(1100,95))

            textsurface = myfont.render(char * "  " + str(math.floor(self.total_cost_orange * 0.75)), False, (255, 165, 0))
            screen.blit(textsurface,(1145,95))
            
            self.button1.create(screen)
            self.button2.create(screen)
            
            screen.blit(sellButton,(1220,70))
            screen.blit(self.upgradeImages[self.currentUpgrade[0]][self.currentUpgrade[1]],(805,70))

            myfont = pygame.font.SysFont(all_fonts[7], 30)

            if self.button2.click(pos,mouseUp):
                showCircle = False
                self.removeEffects()
                towers.remove(self) 
                green_mineral += math.floor(self.total_cost_green * 0.75)
                blue_mineral += math.floor(self.total_cost_blue * 0.75)
                pink_mineral += math.floor(self.total_cost_pink * 0.75)
                orange_mineral += math.floor(self.total_cost_orange * 0.75)
                grid = self.remove_grid(grid)
                re_search = True
                sold = True
            
            if self.currentUpgrade[1] == 1:
                if self.button1.click(pos,mouseUp) and green_mineral >= self.upgradePathCost[self.treeSide][1][0] and blue_mineral >= self.upgradePathCost[self.treeSide][1][1] and pink_mineral >= self.upgradePathCost[self.treeSide][1][2] and orange_mineral >= self.upgradePathCost[self.treeSide][1][3]:
                                    
                    green_mineral -= self.upgradePathCost[self.treeSide][1][0]
                    blue_mineral -= self.upgradePathCost[self.treeSide][1][1]
                    pink_mineral -= self.upgradePathCost[self.treeSide][1][2]
                    orange_mineral -= self.upgradePathCost[self.treeSide][1][3]

                    self.total_cost_green += self.upgradePathCost[self.treeSide][1][0]
                    self.total_cost_blue += self.upgradePathCost[self.treeSide][1][1]
                    self.total_cost_pink += self.upgradePathCost[self.treeSide][1][2]
                    self.total_cost_orange += self.upgradePathCost[self.treeSide][1][3]
                    
                    
                    self.image = self.upgradeImages[self.currentUpgrade[0]][self.currentUpgrade[1]]
                    self.ghost_image = self.upgradeImagesGhost[self.currentUpgrade[0]][self.currentUpgrade[1]]
                    if self.direction == 0:
                        self.rotate("clockwise",False)
                    elif self.direction == 1:
                        self.rotate("clockwise",False)
                        self.rotate("clockwise",False)
                    elif self.direction == 2:
                        self.rotate("anticlockwise",False)
                    self.upgradeColour = (255, 165, 0)
                    self.currentUpgrade[1] += 1
                    self.calculateUpgrade()

            elif self.currentUpgrade[1] == 2:
                if self.button1.click(pos,mouseUp) and green_mineral >= self.upgradePathCost[self.treeSide][2][0] and blue_mineral >= self.upgradePathCost[self.treeSide][2][1] and pink_mineral >= self.upgradePathCost[self.treeSide][2][2] and orange_mineral >= self.upgradePathCost[self.treeSide][2][3]:
                    if self.towerType == "barricade" and self.treeSide == 1:
                        showCircle = [(self.x) * 10 + 35, (self.y) * 10 + 155,15]
                    green_mineral -= self.upgradePathCost[self.treeSide][2][0]
                    blue_mineral -= self.upgradePathCost[self.treeSide][2][1]
                    pink_mineral -= self.upgradePathCost[self.treeSide][2][2]
                    orange_mineral -= self.upgradePathCost[self.treeSide][2][3]

                    self.total_cost_green += self.upgradePathCost[self.treeSide][2][0]
                    self.total_cost_blue += self.upgradePathCost[self.treeSide][2][1]
                    self.total_cost_pink += self.upgradePathCost[self.treeSide][2][2]
                    self.total_cost_orange += self.upgradePathCost[self.treeSide][2][3]                    
                    
                    self.image = self.upgradeImages[self.currentUpgrade[0]][self.currentUpgrade[1]]
                    self.ghost_image = self.upgradeImagesGhost[self.currentUpgrade[0]][self.currentUpgrade[1]]
                    if self.direction == 0:
                        self.rotate("clockwise",False)
                    elif self.direction == 1:
                        self.rotate("clockwise",False)
                        self.rotate("clockwise",False)
                    elif self.direction == 2:
                        self.rotate("anticlockwise",False)                    
                    self.currentUpgrade[1] += 1
                    self.calculateUpgrade()
                    

        else:
            char1 = 6 - len(str(self.total_cost_blue)) #this stuff is for selling towers
            char2 = 6 - len(str(self.total_cost_orange))
            if char2 < char1:
                char = char2
            else:
                char = char1

            char3 = 6 - len(str(self.total_cost_green))
            char4 = 6 - len(str(self.total_cost_pink))
            if char3 < char4:
                second_char = char3
            else:
                second_char = char4

            myfont = pygame.font.SysFont(all_fonts[7], 20)
            
                
            textsurface = myfont.render(second_char * "  " + str(math.floor(self.total_cost_green * 0.75)), False, (0, 255, 0))
            screen.blit(textsurface,(1060,70))

            textsurface = myfont.render(char * "  " + str(math.floor(self.total_cost_blue * 0.75)), False, (0, 0, 255))
            screen.blit(textsurface,(1145,70))

            textsurface = myfont.render(second_char * "  " + str(math.floor(self.total_cost_pink * 0.75)), False, (255,192,203))
            screen.blit(textsurface,(1060,95))

            textsurface = myfont.render(char * "  " + str(math.floor(self.total_cost_orange * 0.75)), False, (255, 165, 0))
            screen.blit(textsurface,(1145,95))
            
            self.button2.create(screen)
            screen.blit(sellButton,(1220,70))

            myfont = pygame.font.SysFont(all_fonts[7], 30)

            if self.button2.click(pos,mouseUp):
                showCircle = False
                self.removeEffects()
                towers.remove(self) 
                green_mineral += math.floor(self.total_cost_green * 0.75)
                blue_mineral += math.floor(self.total_cost_blue * 0.75)
                pink_mineral += math.floor(self.total_cost_pink * 0.75)
                orange_mineral += math.floor(self.total_cost_orange * 0.75)
                grid = self.remove_grid(grid)
                re_search = True
                sold = True

            myfont = pygame.font.SysFont(all_fonts[7], 20)
            textsurface = myfont.render("Max Upgrade Achieved", False, (0, 155, 0))
            screen.blit(textsurface,(820,10))
            myfont = pygame.font.SysFont(all_fonts[7], 30)
                

        return orange_mineral,pink_mineral,blue_mineral,green_mineral,towers,re_search,grid,sold


            


                
    def rotate(self,direction,changeDirection = True):
        if direction == "clockwise":
            if changeDirection:
                self.direction += 1
            self.image = pygame.transform.rotate(self.image, 90)
            self.ghost_image = pygame.transform.rotate(self.ghost_image, 90)
        else:
            if changeDirection:
                self.direction -= 1
            self.image = pygame.transform.rotate(self.image, 270)
            self.ghost_image = pygame.transform.rotate(self.ghost_image, 270)

        self.direction = self.direction % 4

    def update_grid_reflector(self,grid,effect):
        for i in range(5):
            if self.direction == 0 or self.direction == 2:
                grid[self.y + i][self.x + i] = "R2" + effect
            else:
                grid[self.y + i][self.x + 4 - i] = "R1" + effect
                
            
            

        return grid
            
            #top left to bottom right 02
            #top right to bottom left


        
        #effect = RR-DAMAGE-VELOCITY-REFLECTIVE-DUPLICATION-EFFICIENCY
        #EFFECT = RR11fff

    def update_grid(self,grid,custom = "BLOCK"):
        
        for i in range(self.size):
            for j in range(self.size):
                grid[self.y + i][self.x + j] = custom
        return grid
        #custom = "UU+increasemult+bonuses+recycle"

    
    def remove_grid(self,grid):
        for i in range(self.size):
            for j in range(self.size):
                grid[self.y + i][self.x + j] = "-----"
        return grid
    
    def draw(self,pos,mouseUp):

        
        #print("draw",self.x,self.y)
        if self.ghost:
            screen.blit(self.ghost_image,((self.x) * 10 + 35, (self.y) * 10 + 155, 10, 10))
        else:
            screen.blit(self.image,((self.x) * 10 + 35, (self.y) * 10 + 155, 10, 10))
            
        
        if self.tower_button.click(pos,mouseUp):
            if self.towerType == "barricade":
                if self.treeSide == 1:
                    global showCircle
                    showCircle = [(self.x) * 10 + 35, (self.y) * 10 + 155,self.radius]
                    
                else:
                    showCircle = False
                    
            else:
                showCircle = False
            return self
        return False
        
    def drawHeld(self,pos): #while placing the tower
        #offset is 35,155 and limit is 1090,690

        if pos[0] >= 35 and pos[0]+self.size*10 <= 1090: #xcoord
            blockx = (pos[0]-35) // 10
            self.x = blockx

        elif pos[0] < 35:
            self.x = 0

        elif pos[0]+self.size*10 > 1090:
            self.x = 150 - self.size * 10

                
        if pos[1] >= 155 and pos[1]+self.size*10 <= 690: #ycoord
            blocky = (pos[1]-155) // 10
            self.y=blocky

            
        elif pos[1] < 155: #allows tower to move to where cursor is, even if cursor isnt on the grid
            self.y = 0

        elif pos[1] > 690 - self.size * 10:
            self.y = 53 - self.size

        screen.blit(self.image,((self.x) * 10 + 35,(self.y) * 10 + 155))
        self.tower_button = Button(self.x * 10 + 35,self.y * 10 + 155,50,50,(0,200,0),(0,200,0),True,(0,0,0))
        self.startLocation = self.calculate_start_location()

        
    def getCoord(self):
        return self.x,self.y

    

    def getCheck(self): #check,path,grid,change_grid
        return self.check

    def getGeneralPath(self): 
        return self.path

    def getGrid(self): 
        return self.grid
    
    def getRe_Search(self):
        return self.re_search

    def getInitialCost(self):
        return self.initialCost

    def getTotalGreenCost(self):
        return self.total_cost_green

    def getTotalOrangeCost(self):
        return self.total_cost_orange

    def getTotalBlueCost(self):
        return self.total_cost_blue

    def getTotalPinkCost(self):
        return self.total_cost_pink

    def checkValidThread(self,towers,grid,originalPath):
        self.checkingValid = True
        self.thread3 = threading.Thread(target=self.checkValid, args=[towers,grid,originalPath]).start()
        

    def getCheckingValid(self):
        return self.checkingValid


    def inPathThread(self,grid,originalPath,index,endIndex,direction):
                
        
        mysprawler = sprawl.sprawler()
        if direction == "forwards":
            newPath = mysprawler.search(grid,originalPath[index-1],originalPath[endIndex],False,1)
        else:
            newPath = mysprawler.search(grid,originalPath[endIndex],originalPath[index-1],False,1,1)

        #print(direction,newPath)
        if newPath != "cancelled":
            check = True
            if newPath == False:
                check=False
                grid=self.remove_grid(grid) #always remove it from grid
                path = originalPath
            else:
                path=originalPath[0:index-1]
                endPath=originalPath[endIndex:]
                if direction == "forwards":
                    for i in newPath:
                        path.append(i)
                else:
                    for i in newPath[::-1]:
                        path.append(i)
                        
                for i in endPath:
                    path.append(i)
                done=False
                
                while not done:
                    change=False
                    for i in range(len(path)-1):
                        tempPath=path[i+1:]
                        if path[i] in tempPath:
                            index=tempPath.index(path[i])
                            index=index+i+1
                            pathStart=path[0:i]
                            pathEnd=path[index:]
                            path=pathStart
                            change=True
                            for j in pathEnd:
                                path.append(j)                       
                            break
                    if not change:
                        done = True
                
            self.checkingValid = False
            self.check = check
            self.path = path
            self.grid = grid
            self.re_search = True
            #print("done searching",self.check)
            return check,path,grid,True

        #print("timed out")
        return None

    def checkValid(self,towers,grid,originalPath):
        inPath=False
        change_grid = True
        check = True
        if not((self.x*10)+35 >= 35 and ((self.x+self.size)*10) +35<= 1084):
            if not((self.y*10)+155 >= 155 and ((self.y*10+self.size))+155 <= 690):
                check=False

        for i in range(self.size):
            if (self.x == 0 and self.y + i == 28):
                check = False

        for i in range(self.size):
            for j in range(self.size):
                 if (self.x + j == 102 and self.y + i > 26 and self.y + i < 30):
                     check = False
                
        for i in towers:
            x,y=i.getCoord()
            size=i.getSize()
            if self.x>=x and self.x<x+size and check:
                if self.y>=y and self.y<y+size:
                    check=False
            if self.x+self.size>x and self.x+self.size<= x+size and check:
                if self.y>=y and self.y<y+size:
                    check=False
            if self.x>=x and self.x< x+size and check:
                if self.y+self.size>y and self.y+self.size<=y+size:
                    check=False
            if self.x+self.size>x and self.x+self.size<= x+size and check:
                if self.y+self.size>y and self.y+self.size<=y+size:
                    check=False
            if self.x<=x and self.x+self.size>=x+size and check:
                if self.y >=y and self.y<y+size:
                    check=False
            if self.x<=x and self.x+self.size>=x+size and check:
                if self.y+self.size >y and self.y+self.size<=y+size:
                    check=False
            if self.y<=y and self.y+self.size>=y+size and check:
                if self.x >=x and self.x<x+size:
                    check=False
            if self.y<=y and self.y+self.size>=y+size and check:
                if self.x+self.size >x and self.x+self.size<=x+size:
                    check=False
            if self.x<x and self.x+self.size>x+size and check:
                if self.y<y and self.y+self.size>y+size:
                    check=False
        if check:
            grid = self.update_grid(grid)
            index=999999
            for i in range(self.size):
                for j in range(self.size):
                    if (self.x + i,self.y + j) in originalPath:
                        inPath = True
                        tempIndex=originalPath.index((self.x + i,self.y + j))
                        if tempIndex==0:
                            tempIndex=1
                        if tempIndex<=index:
                            index=tempIndex
            if index != 999999:
                tempPath=originalPath[index:]
                done=False
                for i in range(len(tempPath)):
                    if grid[tempPath[i][1]][tempPath[i][0]] == "-----" and not done:
                        endIndex=index+i
                        done=True
                    
                        
                        
            if inPath:
                self.thread1 = threading.Thread(target=self.inPathThread, args=[grid,originalPath,index,endIndex,"forwards"])
                #self.thread2 = threading.Thread(target=self.inPathThread, args=[grid,originalPath,index,endIndex,"backwards"])
                
                self.thread1.start()
                #self.thread2.start()
                
            else:
                path = originalPath
                change_grid = False

        else:
            path = originalPath
            change_grid = False

        if not inPath:
            self.checkingValid = False
            self.check = check
            self.path = path
            self.grid = grid
            self.re_search = change_grid
            return check,path,grid,change_grid

    

    def getSize(self):
        return self.size

        
        

class particle():
    def __init__(self,x,y,direction,damage,life,reflections,speed,aoe,slow,slowDuration,
                 penetrating,splitting,confuse,confuseWeakness,static = False,burn = False,toxic = False,
                 efficiency = 1):
        
        self.x = x
        self.y = y
        self.direction = direction
        self.damage = damage
        self.aoe = aoe
        self.life = life
        self.efficiency = efficiency
        
        self.reflections = reflections
        
        self.speed = speed #lower is better
        
        self.slow = slow #slow multiplier
        self.slowDuration = slowDuration
        
        
        self.penetrating = penetrating #does particle survive if it has more damage then enemy has hp
        
        self.splitting = splitting #does the particle split after getting a kill
        self.confuse = confuse
        self.confuseWeakness = confuseWeakness
        self.static = static
        self.burn = burn #this will be a list [burn damage,timer]
        self.toxic = toxic
        self.recycle = 0

        self.calculateColour()
        self.active = True
        
    def getRecycle(self):
        return self.recycle

    def applyCantRecycle(self):
        self.recycle = 5
        

    def checkCoord(self,dx,dy):
        if self.x + dx < 0 or self.x + dx > 104 or self.y + dy < 0 or self.y + dy > 52:
            return False
        return True

    def getBurn(self):
        return self.burn

    def getToxic(self):
        return self.toxic

    def calculateColour(self):
        if self.damage <= 10:
            self.colour = (255,0,0)

        elif self.damage <= 25:
            self.colour = (255,128,0)

        elif self.damage <= 40:
            self.colour = (255,255,0)

        elif self.damage <= 75:
            self.colour = (0,255,0)

        elif self.damage <= 100:
            self.colour = (0,0,255)

        elif self.damage <= 250:
            self.colour = (75,0,130)

        else:
            self.colour = (238,130,238)


    def getCoord(self):
        return self.x,self.y

    def getDirection(self):
        return self.direction

    def getDamage(self):
        return self.damage

    def getAoe(self):
        return self.aoe

    def getLife(self):
        return self.life

    def getReflections(self):
        return self.reflections

    def getSpeed(self):
        return self.speed

    def getSlow(self):
        return self.slow

    def getSlowDuration(self):
        return self.slowDuration

    def getConfuse(self):
        return self.confuse

    def getConfuseWeakness(self):
        return self.confuseWeakness
        
    def getStun(self):
        return self.stun

    def getPenetrating(self):
        return self.penetrating

    def getSplitting(self):
        return self.splitting

    def getActive(self):
        return self.active

    def changeActive(self):
        self.active = not self.active

    def changeDamage(self,amount):
        self.damage -= amount  
            
    def move(self,timer):
        if timer % self.speed == 0:
            if self.recycle > 0:
                self.recycle -= 1
                
            self.life -= 1
            if self.direction == 0:
                self.y += 1
            elif self.direction == 1:
                self.x += 1
            elif self.direction == 2:
                self.y -= 1
            elif self.direction == 3:
                self.x -= 1
                
        elif self.static:
            self.life -= 1

        if self.x < 0 or self.x > 104 or self.y < 0 or self.y > 52 or self.life < 0:
            return False
        return True
            

    def draw(self,screen):
        #not 35,155 so it lines of with image
        if self.direction == 0 or self.direction == 2:
            pygame.draw.circle(screen, self.colour, (self.x * 10 + 40, self.y * 10 + 155), 3)
        else:
            pygame.draw.circle(screen, self.colour, (self.x * 10 + 35, self.y * 10 + 160), 3)
        

            #  1   2    3   4     5   6    7     8    9    10   11   12  13    14   15   16   17   18   19   20   21   22   23   24   25   26   27   28   29   30   31   32   33   34   35   36   37   38   39   40   41    42   43   44   45  46   47   48   49    50
waveTimes = [1750,2000,3200,4000,5000,6000,6000,4000,3000,3500,3000,5000,2000,3000,5000,3000,2500,4000,1750,5000,3500,4500,2000,3000,4000,5000,4000,2500,4000,5500,2500,1300,3000,2300,1600,2800,3200,2900,4300,8000,2600,2800,2200,3000,3200,3400,2500,4000,3500,10000]
def spawnWave(wave,waveTimer,enemies,waveTimes):
    waveTimer += 1
    done = False
    if wave == 1:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 100 == 0 and waveTimer > 250:
                enemies.append(enemy(path=generalPath,health = 1,speed = 8))

    elif wave == 2:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 25,speed = 5))
            if waveTimer % 1300 == 0:
                enemies.append(enemy(path=generalPath,health = 25,speed = 3))

    elif wave == 3:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 140 == 0:
                enemies.append(enemy(path=generalPath,health = 40,speed = 4))
            if waveTimer % 1500 == 0:
                enemies.append(enemy(path=generalPath,health = 65,speed = 6))

    elif wave == 4:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 70,speed = 7))
            
    elif wave == 5:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 70,speed = 4))


    elif wave == 6:

        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 320 == 0:
                enemies.append(enemy(path=generalPath,health = 105,speed = 10))

            if waveTimer % 160 == 0:
                enemies.append(enemy(path=generalPath,health = 15,speed = 5))

            if waveTimer % 5000 == 0:
                enemies.append(enemy(path=generalPath,health = 185,speed = 14))

    elif wave == 7:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 260 == 0:
                enemies.append(enemy(path=generalPath,health = 120,speed = 8))
            if waveTimer % 610 == 0:
                enemies.append(enemy(path=generalPath,health = 60,speed = 2))
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 25,speed = 5))


    elif wave == 8:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 170 == 0:
                enemies.append(enemy(path=generalPath,health = 120,speed = 4))
            if waveTimer % 140 == 0:
                enemies.append(enemy(path=generalPath,health = 25,speed = 2))

    elif wave == 9:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 230 == 0:
                enemies.append(enemy(path=generalPath,health = 130,speed = 6))
            if waveTimer % 300 == 0:
                enemies.append(enemy(path=generalPath,health = 100,speed = 3))

    elif wave == 10:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 90 == 0:
                enemies.append(enemy(path=generalPath,health = 150,speed = 3))
            if waveTimer % 500 == 0:
                enemies.append(enemy(path=generalPath,health = 200,speed = 8))


    elif wave == 11:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 180,speed = 3))
            if waveTimer % 350 == 0:
                enemies.append(enemy(path=generalPath,health = 220,speed = 5))
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 50,speed = 3))

    elif wave == 12:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 250,speed = 5))
            if waveTimer % 4500 == 0:
                enemies.append(enemy(path=generalPath,health = 1400,speed = 12))

    elif wave == 13:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 250,speed = 4))
            if waveTimer % 450 == 0:
                enemies.append(enemy(path=generalPath,health = 400,speed = 9))
            


    elif wave == 14:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 230 == 0:
                enemies.append(enemy(path=generalPath,health = 350,speed = 3))
            if waveTimer % 350 == 0:
                enemies.append(enemy(path=generalPath,health = 525,speed = 8))
            

    elif wave == 15:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 525,speed = 5))
            if waveTimer % 4500 == 0:
                enemies.append(enemy(path=generalPath,health = 5500,speed = 16))

    elif wave == 16:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 500,speed = 4))
            if waveTimer % 500 == 0:
                enemies.append(enemy(path=generalPath,health = 600,speed = 8))

    elif wave == 17:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 400,speed = 2))
            if waveTimer % 400 == 0:
                enemies.append(enemy(path=generalPath,health = 800,speed = 8))
            if waveTimer % 500 == 0:
                enemies.append(enemy(path=generalPath,health = 1500,speed = 12))
                
    elif wave == 18:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 350,speed = 1))
            if waveTimer % 500 == 0:
                enemies.append(enemy(path=generalPath,health = 900,speed = 8))
            if waveTimer % 1800 == 0:
                enemies.append(enemy(path=generalPath,health = 1200,speed = 10))

    elif wave == 19:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 90 == 0:
                enemies.append(enemy(path=generalPath,health = 400,speed = 3))
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 600,speed = 5))
            if waveTimer % 190 == 0:
                enemies.append(enemy(path=generalPath,health = 1200,speed = 6))
                
    elif wave == 20:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 90 == 0:
                enemies.append(enemy(path=generalPath,health = 500,speed = 3))
            if waveTimer % 140 == 0:
                enemies.append(enemy(path=generalPath,health = 700,speed = 5))
                
            if waveTimer % 4500 == 0:
                enemies.append(enemy(path=generalPath,health = 5500,speed = 14))

    elif wave == 21:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 900,speed = 3))
            if waveTimer % 160 == 0:
                enemies.append(enemy(path=generalPath,health = 1200,speed = 5))
                
            if waveTimer % 1000 == 0:
                enemies.append(enemy(path=generalPath,health = 3200,speed = 14))

    elif wave == 22:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 95 == 0:
                enemies.append(enemy(path=generalPath,health = 1100,speed = 2))
            if waveTimer % 140 == 0:
                enemies.append(enemy(path=generalPath,health = 1300,speed = 5))
                
            if waveTimer % 450 == 0:
                enemies.append(enemy(path=generalPath,health = 3500,speed = 9))

    elif wave == 23:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 190 == 0:
                enemies.append(enemy(path=generalPath,health = 1550,speed = 3))
            if waveTimer % 140 == 0:
                enemies.append(enemy(path=generalPath,health = 1650,speed = 4))
            if waveTimer % 1500 == 0:
                enemies.append(enemy(path=generalPath,health = 2200,speed = 7))
                
    elif wave == 24:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 2300,speed = 3))
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 3100,speed = 4))                
            if waveTimer % 250 == 0:
                enemies.append(enemy(path=generalPath,health = 5000,speed = 8))

    elif wave == 25:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 250 == 0:
                enemies.append(enemy(path=generalPath,health = 2600,speed = 4))
            if waveTimer % 230 == 0:
                enemies.append(enemy(path=generalPath,health = 3500,speed = 5))                
            if waveTimer % 280 == 0:
                enemies.append(enemy(path=generalPath,health = 4500,speed = 6))

    elif wave == 26:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 250 == 0:
                enemies.append(enemy(path=generalPath,health = 3000,speed = 6))
            if waveTimer % 230 == 0:
                enemies.append(enemy(path=generalPath,health = 5000,speed = 7))                
            if waveTimer % 280 == 0:
                enemies.append(enemy(path=generalPath,health = 6000,speed = 8))

    elif wave == 27:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 250 == 0:
                enemies.append(enemy(path=generalPath,health = 3000,speed = 5))
            if waveTimer % 330 == 0:
                enemies.append(enemy(path=generalPath,health = 4500,speed = 6))                
            if waveTimer % 190 == 0:
                enemies.append(enemy(path=generalPath,health = 5000,speed = 7))
            if waveTimer % 1400 == 0:
                enemies.append(enemy(path=generalPath,health = 10000,speed = 12))
            if waveTimer % 1450 == 0:
                enemies.append(enemy(path=generalPath,health = 2500,speed = 1))
                
    elif wave == 28:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 7000,speed = 4))
            if waveTimer % 200 == 0:
                enemies.append(enemy(path=generalPath,health = 8000,speed = 5))                
            if waveTimer % 250 == 0:
                enemies.append(enemy(path=generalPath,health = 9000,speed = 6))
            if waveTimer % 300 == 0:
                enemies.append(enemy(path=generalPath,health = 10000,speed = 7))

    elif wave == 29:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 9000,speed = 4))
            if waveTimer % 200 == 0:
                enemies.append(enemy(path=generalPath,health = 10000,speed = 5))                
            if waveTimer % 250 == 0:
                enemies.append(enemy(path=generalPath,health = 11000,speed = 6))
            if waveTimer % 300 == 0:
                enemies.append(enemy(path=generalPath,health = 12000,speed = 7))

    elif wave == 30:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 160 == 0:
                enemies.append(enemy(path=generalPath,health = 20000,speed = 7))
            if waveTimer % 5000 == 0:
                enemies.append(enemy(path=generalPath,health = 250000,speed = 15))                

    elif wave == 31:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 22000,speed = 8))
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 13000,speed = 5))

    elif wave == 32:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 25000,speed = 6))
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 20000,speed = 6))   

    elif wave == 33:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 180 == 0:
                enemies.append(enemy(path=generalPath,health = 31000,speed = 7))
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 35000,speed = 8))

    elif wave == 34:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 230 == 0:
                enemies.append(enemy(path=generalPath,health = 75000,speed = 14))
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 55000,speed = 8))

    elif wave == 35:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 60 == 0:
                enemies.append(enemy(path=generalPath,health = 60000,speed = 6)) 

    elif wave == 36:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 210 == 0:
                enemies.append(enemy(path=generalPath,health = 40000,speed = 4))
            if waveTimer % 180 == 0:
                enemies.append(enemy(path=generalPath,health = 60000,speed = 5))

    elif wave == 37:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 240 == 0:
                enemies.append(enemy(path=generalPath,health = 60000,speed = 5))
            if waveTimer % 190 == 0:
                enemies.append(enemy(path=generalPath,health = 80000,speed = 6))
                
    elif wave == 38:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 240 == 0:
                enemies.append(enemy(path=generalPath,health = 105000,speed = 8))
            if waveTimer % 190 == 0:
                enemies.append(enemy(path=generalPath,health = 125000,speed = 12))
                
    elif wave == 39:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 240 == 0:
                enemies.append(enemy(path=generalPath,health = 115000,speed = 6))
            if waveTimer % 190 == 0:
                enemies.append(enemy(path=generalPath,health = 145000,speed = 10))

    elif wave == 40:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 25000,speed = 2))
            if waveTimer % 450 == 0:
                enemies.append(enemy(path=generalPath,health = 300000,speed = 10))
            if waveTimer % 7800 == 0:
                enemies.append(enemy(path=generalPath,health = 1500000,speed = 25))

    elif wave == 41:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 50000,speed = 2))
            if waveTimer % 450 == 0:
                enemies.append(enemy(path=generalPath,health = 300000,speed = 10))
            if waveTimer % 300 == 0:
                enemies.append(enemy(path=generalPath,health = 250000,speed = 7))

    elif wave == 42:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 60000,speed = 3))
            if waveTimer % 450 == 0:
                enemies.append(enemy(path=generalPath,health = 400000,speed = 9))
            if waveTimer % 300 == 0:
                enemies.append(enemy(path=generalPath,health = 350000,speed = 7))

    elif wave == 43:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 150 == 0:
                enemies.append(enemy(path=generalPath,health = 60000,speed = 2))
            if waveTimer % 450 == 0:
                enemies.append(enemy(path=generalPath,health = 400000,speed = 8))
            if waveTimer % 300 == 0:
                enemies.append(enemy(path=generalPath,health = 350000,speed = 6))


    elif wave == 44:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 65000,speed = 2))
            if waveTimer % 420 == 0:
                enemies.append(enemy(path=generalPath,health = 450000,speed = 8))
            if waveTimer % 280 == 0:
                enemies.append(enemy(path=generalPath,health = 400000,speed = 6))

    elif wave == 45:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 50000,speed = 1))
            if waveTimer % 420 == 0:
                enemies.append(enemy(path=generalPath,health = 100000,speed = 2))
            if waveTimer % 280 == 0:
                enemies.append(enemy(path=generalPath,health = 150000,speed = 3))

    elif wave == 46:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 100000,speed = 3))
            if waveTimer % 420 == 0:
                enemies.append(enemy(path=generalPath,health = 300000,speed = 4))
            if waveTimer % 580 == 0:
                enemies.append(enemy(path=generalPath,health = 500000,speed = 5))

    elif wave == 47:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 130 == 0:
                enemies.append(enemy(path=generalPath,health = 200000,speed = 3))
            if waveTimer % 420 == 0:
                enemies.append(enemy(path=generalPath,health = 400000,speed = 4))
            if waveTimer % 290 == 0:
                enemies.append(enemy(path=generalPath,health = 600000,speed = 5))

    elif wave == 48:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 500000,speed = 5))
            if waveTimer % 420 == 0:
                enemies.append(enemy(path=generalPath,health = 700000,speed = 6))
            if waveTimer % 480 == 0:
                enemies.append(enemy(path=generalPath,health = 900000,speed = 7))

    elif wave == 49:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 500000,speed = 4))
            if waveTimer % 420 == 0:
                enemies.append(enemy(path=generalPath,health = 750000,speed = 5))
            if waveTimer % 480 == 0:
                enemies.append(enemy(path=generalPath,health = 1000000,speed = 6))


    elif wave == 50:
        if waveTimer <= waveTimes[wave - 1]:
            if waveTimer % 120 == 0:
                enemies.append(enemy(path=generalPath,health = 500000,speed = 3))
            if waveTimer % 420 == 0:
                enemies.append(enemy(path=generalPath,health = 750000,speed = 4))
            if waveTimer % 480 == 0:
                enemies.append(enemy(path=generalPath,health = 1000000,speed = 5)) 
            if waveTimer % 9950 == 0:
                enemies.append(enemy(path=generalPath,health = 10000000,speed = 25))

    elif wave > 50:
        if waveTimer == 2500:
            done = True
            
        else:
            if waveTimer % 200 == 0:
                enemies.append(enemy(path=generalPath,health = int(1.28**wave),speed = 2))
                
            if waveTimer % 400 == 0:
                enemies.append(enemy(path=generalPath,health = int(1.3**wave),speed = 5))
                
            if waveTimer % 600 == 0:
                enemies.append(enemy(path=generalPath,health = int(1.31**wave),speed = 8))
                
            if waveTimer % 2450 == 0:
                enemies.append(enemy(path=generalPath,health = int(1.34**wave),speed = 20))    
                
    if len(waveTimes) > wave - 1 and wave < 51 and not done:
        if waveTimer > waveTimes[wave - 1] and enemies == []:
            done = True

    return waveTimer,enemies,done
            
        
def complete_collisions(particles,enemies,green_mineral,pink_mineral,blue_mineral,orange_mineral,totalKills):
    tempEnemies = [] #collisions between particles and enemies
    tempParticles = []
    newParticles = []
    for i in enemies:
        if i.getActive():
            
            for j in particles:
                
                if j.getActive() and i.getActive() and j.getDamage() != 0:
                    
                    if i.getCoord() == j.getCoord():
                        aoe = j.getAoe()
                        if aoe > 0:
                            toxic = j.getToxic()
                            if toxic:
                                effect = [math.floor(j.getDamage()/10),150]
                            else:
                                effect = False
                            newParticles.append(particle(j.getCoord()[0],j.getCoord()[1],j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                            if j.checkCoord(1,0):
                                newParticles.append(particle(j.getCoord()[0] + 1,j.getCoord()[1],j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                            if j.checkCoord(-1,0):
                                newParticles.append(particle(j.getCoord()[0] - 1,j.getCoord()[1],j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                            if j.checkCoord(0,1):
                                newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] + 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                            if j.checkCoord(0,-1):
                                newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] - 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))

                            if aoe > 1:
                                if j.checkCoord(2,0):
                                    newParticles.append(particle(j.getCoord()[0] + 2,j.getCoord()[1],j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(-2,0):
                                    newParticles.append(particle(j.getCoord()[0] - 2,j.getCoord()[1],j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(0,2):
                                    newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] + 2,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(0,-2):#far out                                    
                                    newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] - 2,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))

                                if j.checkCoord(1,1):#inner
                                    newParticles.append(particle(j.getCoord()[0] + 1,j.getCoord()[1] + 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(1,-1):
                                    newParticles.append(particle(j.getCoord()[0] + 1,j.getCoord()[1] - 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(-1,1):
                                    newParticles.append(particle(j.getCoord()[0] - 1,j.getCoord()[1] + 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(-1,-1):
                                    newParticles.append(particle(j.getCoord()[0] - 1,j.getCoord()[1] - 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))

                            if aoe > 2:#further out
                                if j.checkCoord(3,0):
                                    newParticles.append(particle(j.getCoord()[0] + 3,j.getCoord()[1],j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(-3,0):
                                    newParticles.append(particle(j.getCoord()[0] - 3,j.getCoord()[1],j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(0,3):
                                    newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] + 3,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(0,-3):#far out                                    
                                    newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] - 3,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))


                                if j.checkCoord(1,2):
                                    newParticles.append(particle(j.getCoord()[0] + 1,j.getCoord()[1] + 2,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(-1,2):
                                    newParticles.append(particle(j.getCoord()[0] - 1,j.getCoord()[1] + 2,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(1,-2):#far out                                    
                                    newParticles.append(particle(j.getCoord()[0] + 1,j.getCoord()[1] - 2,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(-1,-2):
                                    newParticles.append(particle(j.getCoord()[0] - 1,j.getCoord()[1] - 2,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))


                                if j.checkCoord(-2,-1):
                                    newParticles.append(particle(j.getCoord()[0] - 2,j.getCoord()[1] - 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(2,1):#inner/outer
                                    newParticles.append(particle(j.getCoord()[0] + 2,j.getCoord()[1] + 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(-2,1):
                                    newParticles.append(particle(j.getCoord()[0] - 2,j.getCoord()[1] + 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                if j.checkCoord(2,-1):#inner/outer
                                    newParticles.append(particle(j.getCoord()[0] + 2,j.getCoord()[1] - 1,j.getDirection(),j.getDamage(),25,0,9999999,False,False,False,False,False,False,1,static = True,burn = effect))
                                              


                            #def __init__(self,x,y,direction,damage,life,reflections,speed,aoe,slow,slowDuration,
                            #penetrating,splitting,confuse,confuseWeakness,static = False):

                        if i.getHealth() - j.getDamage() < 0:
                            direction = j.getDirection()
                            if direction == 0:
                                blue_mineral += i.getValue()
                            elif direction == 1:
                                green_mineral += i.getValue()
                            elif direction == 2:
                                pink_mineral += i.getValue()
                            elif direction == 3:
                                green_mineral += i.getValue()
                            totalKills += 1
                                
                            tempEnemies.append(i) # enemy has been killed
                            i.changeActive()
                            
                            if j.getPenetrating():
                                pass

                            elif j.getSplitting() > 0:
                                newParticles.append(particle(j.getCoord()[0],j.getCoord()[1],j.getDirection(),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))
                                newParticles.append(particle(j.getCoord()[0],j.getCoord()[1],((j.getDirection() + 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))
                                newParticles.append(particle(j.getCoord()[0],j.getCoord()[1],((j.getDirection() - 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))
                                tempParticles.append(j) #remove this one
                                j.changeActive()
                            



                                
                                #add 3 new particles here
                            else:
                                tempParticles.append(j)
                                j.changeActive()
                                
                                

                        else:
                            i.changeHealth(j.getDamage())
                            if j.getSlow() != False:
                                i.changeCurrentSlow(j.getSlow(),j.getSlowDuration())

                            if j.getConfuse():
                                i.changeCurrentConfuse(j.getConfuse(),j.getConfuseWeakness())

                            if j.getBurn() != False:
                                i.applyBurn(j.getBurn())

                                
                            elif j.getSplitting() > 0:
                                if j.getDirection() == 2:#2 is up
                                    if j.checkCoord(0,-1):
                                        newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] - 1,j.getDirection(),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                    if j.checkCoord(1,0):
                                        newParticles.append(particle(j.getCoord()[0] + 1,j.getCoord()[1],((j.getDirection() + 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                    if j.checkCoord(-1,0):
                                        newParticles.append(particle(j.getCoord()[0] - 1,j.getCoord()[1],((j.getDirection() - 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                elif j.getDirection() == 1:#right
                                    if j.checkCoord(1,0):
                                        newParticles.append(particle(j.getCoord()[0] + 1,j.getCoord()[1],j.getDirection(),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                    if j.checkCoord(0,1):
                                        newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] + 1,((j.getDirection() + 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                    if j.checkCoord(0,-1):
                                        newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] - 1,((j.getDirection() - 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                elif j.getDirection() == 0: #this is down
                                    if j.checkCoord(0,1):
                                        newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] + 1,j.getDirection(),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                    if j.checkCoord(1,0):
                                        newParticles.append(particle(j.getCoord()[0] + 1,j.getCoord()[1],((j.getDirection() + 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                    if j.checkCoord(-1,0):
                                        newParticles.append(particle(j.getCoord()[0] - 1,j.getCoord()[1],((j.getDirection() - 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))


                                elif j.getDirection() == 3:#left
                                    if j.checkCoord(-1,0):
                                        newParticles.append(particle(j.getCoord()[0] - 1,j.getCoord()[1],j.getDirection(),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                    if j.checkCoord(0,1):
                                        newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] + 1,((j.getDirection() + 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                    if j.checkCoord(0,-1):
                                        newParticles.append(particle(j.getCoord()[0],j.getCoord()[1] - 1,((j.getDirection() - 1) % 4),j.getDamage(),40,8,j.getSpeed(),False,False,False,False,j.getSplitting() - 1,False,1))

                                tempParticles.append(j) #remove this one
                                j.changeActive()

                            elif not j.getPenetrating():
                                tempParticles.append(j)
                                j.changeActive()
                                
                    
                
    for i in tempEnemies:
        enemies.remove(i)
        del i

    for i in tempParticles:
        particles.remove(i)
        del i

    for i in newParticles:
        particles.append(i)

    return particles,enemies,green_mineral,pink_mineral,blue_mineral,orange_mineral,totalKills


def generator_collisions(grid,particles,green_mineral,blue_mineral,pink_mineral,orange_mineral):
    tempParticles = []
    for j in particles:
        x,y = j.getCoord()
        if grid[y][x][0] == "U" and j.getRecycle() == 0:
            direction = j.getDirection()
            if direction == 2:
                pink_mineral += j.efficiency * ((int(grid[y][x][2]) * 0.15 + 1)* j.getDamage())/20
                if int(grid[y][x][3]) == 1:
                   orange_mineral += j.efficiency * j.getDamage()/400
                    
                elif int(grid[y][x][3]) == 2:
                    blue_mineral += j.efficiency * j.getDamage()/250
                    orange_mineral += j.efficiency * j.getDamage()/250
                    
                elif int(grid[y][x][3]) == 3:
                    green_mineral += 3 * j.efficiency * j.getDamage()/400
                    blue_mineral += 3 * j.efficiency * j.getDamage()/400
                    orange_mineral += 3 * j.efficiency * j.getDamage()/400

            elif direction == 1:
                orange_mineral += j.efficiency * ((int(grid[y][x][2]) * 0.15 + 1)* j.getDamage())/20
                
                if int(grid[y][x][3]) == 1:
                   blue_mineral += j.efficiency * j.getDamage()/400
                    
                elif int(grid[y][x][3]) == 2:
                    blue_mineral += j.efficiency * j.getDamage()/200
                    green_mineral += j.efficiency * j.getDamage()/200
                    
                elif int(grid[y][x][3]) == 3:
                    green_mineral += 3 * j.efficiency * j.getDamage()/400
                    blue_mineral += 3 * j.efficiency * j.getDamage()/400
                    pink_mineral += 3 * j.efficiency * j.getDamage()/400

            elif direction == 0:
                blue_mineral += j.efficiency * ((int(grid[y][x][2]) * 0.15 + 1)* j.getDamage())/20
                
                if int(grid[y][x][3]) == 1:
                   green_mineral += j.efficiency * j.getDamage()/400
                    
                elif int(grid[y][x][3]) == 2:
                    pink_mineral += j.efficiency * j.getDamage()/200
                    green_mineral += j.efficiency * j.getDamage()/200
                    
                elif int(grid[y][x][3]) == 3:
                    green_mineral += 3 * j.efficiency * j.getDamage()/400
                    orange_mineral += 3 * j.efficiency * j.getDamage()/400
                    pink_mineral += 3 * j.efficiency * j.getDamage()/400

            elif direction == 3:
                green_mineral += j.efficiency * ((int(grid[y][x][2]) * 0.15 + 1)* j.getDamage())/20
                
                if int(grid[y][x][3]) == 1:
                   pink_mineral += j.efficiency * j.getDamage()/400
                    
                elif int(grid[y][x][3]) == 2:
                    pink_mineral += j.efficiency * j.getDamage()/200
                    orange_mineral += j.efficiency * j.getDamage()/200
                    
                elif int(grid[y][x][3]) == 3:
                    blue_mineral += 3 * j.efficiency * j.getDamage()/400
                    orange_mineral += 3 * j.efficiency * j.getDamage()/400
                    pink_mineral += 3 * j.efficiency * j.getDamage()/400

            if grid[y][x][4] == "0":
                tempParticles.append(j)
            else:
                j.changeDamage(math.floor(j.getDamage())/2)
                j.applyCantRecycle()

    for i in tempParticles:
        particles.remove(i)
        del i
    
                
    return particles,green_mineral,blue_mineral,pink_mineral,orange_mineral 


def reflector_collisions(grid,particles):
    tempParticles = []
    newParticles = []
    for j in particles:
        x,y = j.getCoord()
        if grid[y][x][0] == "R":
            if grid[y][x][4] == "t": #yd
                j.reflections -= 0.5
            else:
                j.reflections -= 1
                
            if j.reflections < 0:
                tempParticles.append(j)

            #effect = R-CONFIG-DAMAGE-VELOCITY-REFLECTIVE-DUPLICATION-EFFICIENCY
            if grid[y][x][2] == "2":
                j.damage = j.damage * 1.15
                j.calculateColour()
            if grid[y][x][2] == "3":
                j.damage = j.damage * 1.5
                j.calculateColour()
            else:
                j.damage = j.damage * 1.05
                j.calculateColour()          

            if grid[y][x][3] == "2":
                j.life += 25
                j.speed = int(j.speed / 1.005)
                if j.speed < 1:
                    j.speed = 1

            if grid[y][x][6] == "t":
                j.efficiency = j.efficiency * 1.5

            oldDirection = j.direction
            oldx = j.x
            oldy = j.y
            if j.direction == 0:
                oldy = 1 + j.y
            elif j.direction == 1:
                oldx = 1 + j.x
            elif j.direction == 2:
                oldy = -1  + j.y
            elif j.direction == 3:
                oldx = -1 + j.x        
            
            if grid[y][x][1] == "1":
                if j.direction == 0 or j.direction == 1:

                    if j.direction == 1:
                        j.x -= 1
                        j.direction += 1
                    else:
                        j.y -= 1
                        j.direction -= 1
                    
                    
                    j.direction = (j.direction + 4) % 4

                else:
                    if j.direction == 3:
                        j.y += 1
                        j.direction += 1 
                    else:
                        j.x += 1
                        j.direction -= 1 
                    
                    j.direction = (j.direction + 4) % 4


                    
            elif grid[y][x][1] == "2":
                if j.direction == 0 or j.direction == 3:

                    if j.direction == 3:
                        j.y -= 1
                        j.direction -= 1
                    else:
                        j.x += 1
                        j.direction += 1
                    
                    
                    j.direction = (j.direction + 4) % 4
                    
                else:

                    if j.direction == 1:
                        j.y += 1
                        j.direction -= 1
                    else:
                        j.x -= 1
                        j.direction += 1
                    
                    j.direction = (j.direction + 4) % 4



            if grid[y][x][5] == "t":
                newParticles.append(particle(oldx,oldy,oldDirection,j.getDamage(),j.life,j.reflections,j.speed,j.aoe,j.slow,j.slowDuration,j.penetrating,j.splitting,j.confuse,j.confuseWeakness,j.static,j.burn,j.toxic,j.efficiency))


    for i in tempParticles:
        particles.remove(i)

    for i in newParticles:
        particles.append(i)
    return particles
            

title = pygame.image.load(os.path.join("vector_title.png")).convert()

arrow_right = pygame.image.load(os.path.join("arrow_right.png")).convert()
arrow_right = pygame.transform.scale(arrow_right, (40, 40))#rotate for other directions
arrow_left = pygame.image.load(os.path.join("arrow_left.png")).convert()
arrow_left = pygame.transform.scale(arrow_left, (40, 40))#rotate for other directions
arrow_up = pygame.image.load(os.path.join("arrow_up.png")).convert()
arrow_up = pygame.transform.scale(arrow_up, (40, 40))#rotate for other directions
arrow_down = pygame.image.load(os.path.join("arrow_down.png")).convert()
arrow_down = pygame.transform.scale(arrow_down, (40, 40))#rotate for other directions

orange_pic = pygame.image.load(os.path.join("orange_crystal.png")).convert()
blue_pic = pygame.image.load(os.path.join("blue_crystal.png")).convert()
green_pic = pygame.image.load(os.path.join("green_crystal.png")).convert()
pink_pic = pygame.image.load(os.path.join("pink_crystal.png")).convert()

orange_pic = pygame.transform.scale(orange_pic, (50, 50))
blue_pic = pygame.transform.scale(blue_pic, (50, 50))
green_pic = pygame.transform.scale(green_pic, (50, 50))
pink_pic = pygame.transform.scale(pink_pic, (50, 50))


orange_pic.set_colorkey((255,255,255))
blue_pic.set_colorkey((255,255,255))
green_pic.set_colorkey((255,255,255))
pink_pic.set_colorkey((255,255,255))

exitb = button(grey,1160,20,100,100,"Back")
quitb = button(grey,400,610,480,100,"Quit")
playb = button(grey,400,370,480,100,"Play")


controls1b = button(grey,100,490,1080,100,"Controls:   Rotate: A or D   -   Unselect tower: W  -  Show Path: S")
controls2b = button(grey,400,490,480,100,"Show Controls")

pausedb = button(grey,450,20,380,80,"--  Paused  --")

continb = button(grey,400,120,480,80,"Continue")
exitmenub = button(grey,400,260,480,80,"Exit to menu")

loadingwaveb = button(grey,403,370,250,100,"Loading next wave...")
checkingb = button(grey,403,370,250,100,"Checking turret...")



shooterButton = Button(1130,130,50,50,(0,200,0),(0,200,0),True,(0,0,0))
reflectorButton = Button(1130,230,50,50,(0,200,0),(0,200,0),True,(0,0,0))
barricadeButton = Button(1130,330,50,50,(0,200,0),(0,200,0),True,(0,0,0))
aoeButton = Button(1130,430,50,50,(0,200,0),(0,200,0),True,(0,0,0))
slowButton = Button(1130,530,50,50,(0,200,0),(0,200,0),True,(0,0,0))
generatorButton = Button(1130,630,50,50,(0,200,0),(0,200,0),True,(0,0,0))


#sell button

sellButton = pygame.image.load("sell.png")
sellButton.set_alpha(None)
sellButton = pygame.transform.scale(sellButton, (50, 50))

#projector
plain_projector = pygame.image.load("plain_project.png")
plain_projector.set_alpha(None)

plain_projector_ghost = pygame.image.load("plain_project_ghost.png")
plain_projector_ghost.set_alpha(None)

machine_projector = pygame.image.load("machine_project.png")
machine_projector.set_alpha(None)

reflect_projector = pygame.image.load("reflect_project.png")
reflect_projector.set_alpha(None)

chain_projector = pygame.image.load("chain_project.png")
chain_projector.set_alpha(None)

tough_projector = pygame.image.load("tough_project.png")
tough_projector.set_alpha(None)

hard_projector = pygame.image.load("hard_project.png")
hard_projector.set_alpha(None)

penetrating_projector = pygame.image.load("penetrating_project.png")
penetrating_projector.set_alpha(None)

machine_projector_ghost = pygame.image.load("machine_project_ghost.png")
machine_projector_ghost.set_alpha(None)

reflect_projector_ghost = pygame.image.load("reflect_project_ghost.png")
reflect_projector_ghost.set_alpha(None)

chain_projector_ghost = pygame.image.load("chain_project_ghost.png")
chain_projector_ghost.set_alpha(None)

tough_projector_ghost = pygame.image.load("tough_project_ghost.png")
tough_projector_ghost.set_alpha(None)

hard_projector_ghost = pygame.image.load("hard_project_ghost.png")
hard_projector_ghost.set_alpha(None)

penetrating_projector_ghost = pygame.image.load("penetrating_project_ghost.png")
penetrating_projector_ghost.set_alpha(None)


#reflector
plain_reflector = pygame.image.load("basic_reflector.png")
plain_reflector.set_alpha(None)

plain_reflector_ghost = pygame.image.load("reflector_basic_ghost.png")
plain_reflector_ghost.set_alpha(None)

damage_reflector = pygame.image.load("damage_reflector.png")
damage_reflector.set_alpha(None)

speed_reflector = pygame.image.load("speed_reflector.png")
speed_reflector.set_alpha(None)

super_damage_reflector = pygame.image.load("super_damage_reflector.png")
super_damage_reflector.set_alpha(None)

reflective_reflector = pygame.image.load("reflective_reflector.png")
reflective_reflector.set_alpha(None)

duplication_reflector = pygame.image.load("duplication_reflector.png")
duplication_reflector.set_alpha(None)

efficiency_reflector = pygame.image.load("efficiency_reflector.png")
efficiency_reflector.set_alpha(None)#

damage_reflector_ghost = pygame.image.load("damage_reflector_ghost.png")
damage_reflector_ghost.set_alpha(None)

speed_reflector_ghost = pygame.image.load("speed_reflector_ghost.png")
speed_reflector_ghost.set_alpha(None)

super_damage_reflector_ghost = pygame.image.load("super_damage_reflector_ghost.png")
super_damage_reflector_ghost.set_alpha(None)

reflective_reflector_ghost = pygame.image.load("reflective_reflector_ghost.png")
reflective_reflector_ghost.set_alpha(None)

duplication_reflector_ghost = pygame.image.load("duplication_reflector_ghost.png")
duplication_reflector_ghost.set_alpha(None)

efficiency_reflector_ghost = pygame.image.load("efficiency_reflector_ghost.png")
efficiency_reflector_ghost.set_alpha(None)



#barricade

plain_barricade = pygame.image.load("basic_barricade.png")
plain_barricade.set_alpha(None)

plain_barricade_ghost = pygame.image.load("barricade_basic_ghost.png")
plain_barricade_ghost.set_alpha(None)

banking_barricade = pygame.image.load("banking_barricade.png")
banking_barricade.set_alpha(None)

interest_barricade = pygame.image.load("interest_barricade.png")
interest_barricade.set_alpha(None)

shortage_barricade = pygame.image.load("shortage_barricade.png")
shortage_barricade.set_alpha(None)

speed_barricade = pygame.image.load("speed_barricade.png")
speed_barricade.set_alpha(None)

louder_barricade = pygame.image.load("louder_barricade.png")
louder_barricade.set_alpha(None)

damage_barricade = pygame.image.load("damage_barricade.png")
damage_barricade.set_alpha(None)#

banking_barricade_ghost = pygame.image.load("banking_barricade_ghost.png")
banking_barricade_ghost.set_alpha(None)

interest_barricade_ghost = pygame.image.load("interest_barricade_ghost.png")
interest_barricade_ghost.set_alpha(None)

shortage_barricade_ghost = pygame.image.load("shortage_barricade_ghost.png")
shortage_barricade_ghost.set_alpha(None)

speed_barricade_ghost = pygame.image.load("speed_barricade_ghost.png")
speed_barricade_ghost.set_alpha(None)

louder_barricade_ghost = pygame.image.load("louder_barricade_ghost.png")
louder_barricade_ghost.set_alpha(None)

damage_barricade_ghost = pygame.image.load("damage_barricade_ghost.png")
damage_barricade_ghost.set_alpha(None)


#aoe projector
aoe_projector = pygame.image.load("aoe_project.png")###############
aoe_projector.set_alpha(None)

aoe_projector_ghost = pygame.image.load("aoe_project_ghost.png")###############
aoe_projector_ghost.set_alpha(None)

bigger_aoe_projector = pygame.image.load("bigger_aoe_project.png")
bigger_aoe_projector.set_alpha(None)

even_bigger_aoe_projector = pygame.image.load("even_bigger_aoe_project.png")
even_bigger_aoe_projector.set_alpha(None)

toxic_aoe_projector = pygame.image.load("toxic_aoe_project.png")
toxic_aoe_projector.set_alpha(None)

rapid_aoe_projector = pygame.image.load("rapid_aoe_project.png")
rapid_aoe_projector.set_alpha(None)

power_aoe_projector = pygame.image.load("power_aoe_project.png")
power_aoe_projector.set_alpha(None)

reflect_aoe_projector = pygame.image.load("reflect_aoe_project.png")
reflect_aoe_projector.set_alpha(None)#

bigger_aoe_projector_ghost = pygame.image.load("bigger_aoe_project_ghost.png")
bigger_aoe_projector_ghost.set_alpha(None)

even_bigger_aoe_projector_ghost = pygame.image.load("even_bigger_aoe_project_ghost.png")
even_bigger_aoe_projector_ghost.set_alpha(None)

toxic_aoe_projector_ghost = pygame.image.load("toxic_aoe_project_ghost.png")
toxic_aoe_projector_ghost.set_alpha(None)

rapid_aoe_projector_ghost = pygame.image.load("rapid_aoe_project_ghost.png")
rapid_aoe_projector_ghost.set_alpha(None)

power_aoe_projector_ghost = pygame.image.load("power_aoe_project_ghost.png")
power_aoe_projector_ghost.set_alpha(None)

reflect_aoe_projector_ghost = pygame.image.load("reflect_aoe_project_ghost.png")
reflect_aoe_projector_ghost.set_alpha(None)

#slow projector
slow_projector = pygame.image.load("slow_project.png")
slow_projector.set_alpha(None)

slow_projector_ghost = pygame.image.load("slow_project_ghost.png")
slow_projector_ghost.set_alpha(None)

cold_slow_projector = pygame.image.load("cold_slow_project.png")
cold_slow_projector.set_alpha(None)

snowy_slow_projector = pygame.image.load("snowy_slow_project.png")
snowy_slow_projector.set_alpha(None)

icy_slow_projector = pygame.image.load("icy_slow_project.png")
icy_slow_projector.set_alpha(None)

confuse_slow_projector = pygame.image.load("confuse_slow_project.png")
confuse_slow_projector.set_alpha(None)

more_confuse_slow_projector = pygame.image.load("more_confuse_slow_project.png")
more_confuse_slow_projector.set_alpha(None)

vulnerable_slow_projector = pygame.image.load("vulnerable_slow_project.png")
vulnerable_slow_projector.set_alpha(None)#

cold_slow_projector_ghost = pygame.image.load("cold_slow_project_ghost.png")
cold_slow_projector_ghost.set_alpha(None)

snowy_slow_projector_ghost = pygame.image.load("snowy_slow_project_ghost.png")
snowy_slow_projector_ghost.set_alpha(None)

icy_slow_projector_ghost = pygame.image.load("icy_slow_project_ghost.png")
icy_slow_projector_ghost.set_alpha(None)

confuse_slow_projector_ghost = pygame.image.load("confuse_slow_project_ghost.png")
confuse_slow_projector_ghost.set_alpha(None)

more_confuse_slow_projector_ghost = pygame.image.load("more_confuse_slow_project_ghost.png")
more_confuse_slow_projector_ghost.set_alpha(None)

vulnerable_slow_projector_ghost = pygame.image.load("vulnerable_slow_project_ghost.png")
vulnerable_slow_projector_ghost.set_alpha(None)

#generator
generator = pygame.image.load("generator.png")
generator.set_alpha(None)

generator_ghost = pygame.image.load("generator_ghost.png")
generator_ghost.set_alpha(None)

efficient_generator = pygame.image.load("efficient_generator.png")
efficient_generator.set_alpha(None)

masterful_generator = pygame.image.load("masterful_generator.png")
masterful_generator.set_alpha(None)

recycle_generator = pygame.image.load("recycle_generator.png")
recycle_generator.set_alpha(None)

double_generator = pygame.image.load("double_generator.png")
double_generator.set_alpha(None)

triple_generator = pygame.image.load("triple_generator.png")
triple_generator.set_alpha(None)

quad_generator = pygame.image.load("quad_generator.png")
quad_generator.set_alpha(None)#

efficient_generator_ghost = pygame.image.load("efficient_generator_ghost.png")
efficient_generator_ghost.set_alpha(None)

masterful_generator_ghost = pygame.image.load("masterful_generator_ghost.png")
masterful_generator_ghost.set_alpha(None)

recycle_generator_ghost = pygame.image.load("recycle_generator_ghost.png")
recycle_generator_ghost.set_alpha(None)

double_generator_ghost = pygame.image.load("double_generator_ghost.png")
double_generator_ghost.set_alpha(None)

triple_generator_ghost = pygame.image.load("triple_generator_ghost.png")
triple_generator_ghost.set_alpha(None)

quad_generator_ghost = pygame.image.load("quad_generator_ghost.png")
quad_generator_ghost.set_alpha(None)

####################

ingame = True
position = "home"


#pink   (255,192,203)      

#orange        (255, 165, 0)
#tower costs
projector_cost = [[75,(0,255,0)],[75,(0,0,255)]]
reflector_cost = [[50,(0,255,0)],[50,(255,192,203) ]]
barricade_cost = [[25,(0,0,255)],[25,(255,192,203) ]]
aoe_projector_cost = [[150,(0,255,0)],[150,(255, 165, 0)]]
slow_projector_cost = [[100,(0,0,255)],[100,(255, 165, 0)]]
generator_cost = [[200,(255,192,203) ],[200,(255, 165, 0)]]
showing = False
no_press = 0
while ingame:
    clock.tick(fps)
    screen.fill((0,0,0))
    pos = pygame.mouse.get_pos()

    if position == "home":

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pass        

        screen.blit(title,(404,150))
        quitb.draw(screen)
        quitb.hover()
        playb.draw(screen)
        playb.hover()
        if showing:
            
            controls1b.hover()
            controls1b.draw(screen)
            if controls1b.press() and no_press == 0:
                showing = False
                no_press = 10
            
        else:            
            controls2b.hover()
            controls2b.draw(screen)
            showing = False
            if controls2b.press() and no_press == 0:
                showing = True
                no_press = 10

        if no_press > 0:
            no_press -= 1

            

            
        if quitb.press():
            ingame = False
            pygame.quit()
            break

        if playb.press():
            position = "setup"

    elif position == "setup":
        showPath = False
        surface1 = pygame.Surface((1280,720))
        surface1.set_colorkey((0,0,0))
        surface1.set_alpha(128)
        showCircle = False
        heldTower = None
        newWaveDisplay = 0
        waveTimer = 0
        lives = 250
        onscreenParticles = 0
        totalKills = 0
        interestMain = 0
        interestShortage = 0
        display = "normal"
        re_search = False
        calculating = False
        calculatingValid = False
        wave = 1
        youdiedb = button(grey,403,370,250,100,"You died on wave"+str(wave))
        orange_mineral = 750
        pink_mineral = 750
        blue_mineral = 750
        green_mineral = 750
        dead = False

        timer = 0
        grid = [] #10x10 squares create grid
        for i in range(53):
            grid.append([])
            for j in range(105): #53,105
                grid[i].append("-----")
        towers = []
        
        enemies = []
        particles = []
        
        position = "game"
        
        #t1 = tower(19,23,5,plain_projector,plain_projector_ghost,3)
        #grid = t1.update_grid(grid)
        #towers.append(t1)
        mysprawler = sprawl.sprawler()
        generalPath = mysprawler.search(grid,(0,28),(104,28),search_depth = 1)
        newPath = generalPath

    elif position == "game":
        timer += 1
        surface1 = pygame.Surface((1280,720))
        surface1.set_colorkey((0,0,0))
        surface1.set_alpha(128)

        if showPath:
            for i in generalPath:
                pygame.draw.rect(surface1, (0,128,128), [i[0] * 10 + 35, i[1] * 10 + 155, 10, 10])


        #top right showing
        if display == "normal":
            myfont = pygame.font.SysFont(all_fonts[7], 24)
            textsurface = myfont.render("Wave: "+str(wave), False, (0, 155, 0))
            screen.blit(textsurface,(645,10)) #wave number

            textsurface = myfont.render("Total kills: "+str(totalKills), False, (0, 155, 0))
            screen.blit(textsurface,(785,10)) #wave number

            textsurface = myfont.render("Lives: "+str(lives), False, (0, 155, 0))
            screen.blit(textsurface,(645,60)) #wave number

            textsurface = myfont.render("Particles: "+str(onscreenParticles)+" / 500", False, (0, 155, 0))
            screen.blit(textsurface,(785,60)) #wave number

            textsurface = myfont.render("Main Interest: "+str(round(interestMain,3)), False, (0, 155, 0))
            screen.blit(textsurface,(1005,10)) #wave number

            textsurface = myfont.render("Shortage Interest: "+str(round(interestShortage,3)), False, (0, 155, 0))
            screen.blit(textsurface,(1005,60)) #wave number
            
            myfont = pygame.font.SysFont(all_fonts[7], 30)

        else:
            orange_mineral,pink_mineral,blue_mineral,green_mineral,towers,re_search,grid,sold = display.show_upgrade(screen,pos,mouseUp,orange_mineral,pink_mineral,blue_mineral,green_mineral,towers,re_search,grid)
            if sold:
                display = "normal"
                
        pygame.draw.rect(screen, [255,0,0], [0, 120, 1280, 5]) #newest red lines
        pygame.draw.rect(screen, [255,0,0], [1120, 120, 5, 600])
        
        pygame.draw.rect(screen, [255,0,0], [615, 0, 5, 120]) #top divider
        
        pygame.draw.rect(screen, [255,0,0], [0, 120, 1120, 5]) #red lines  #[x,y,width,length]
        pygame.draw.rect(screen, [255,0,0], [1120, 120, 5, 600])


        #red line dividers
        for i in range(5):
            pygame.draw.rect(screen, [255,0,0], [1120, 220 + i * 100, 160, 5])
        ########

        pygame.draw.rect(screen, [0,255,0], [0, 380, 35, 80])

        pygame.draw.rect(screen, [0,255,255], [30, 150, 1060, 5]) #long pieces
        pygame.draw.rect(screen, [0,255,255], [30, 685, 1060, 5])

        pygame.draw.rect(screen, [0,255,255], [1085, 150, 5, 540])#end piece
        
        pygame.draw.rect(screen, [0,255,255], [30, 150, 5, 230]) #vertical left
        pygame.draw.rect(screen, [0,255,255], [30, 460, 5, 230])

        #progress bar 30 - 1035
        pygame.draw.rect(screen, [0,80,80], [40, 130, 1035, 14])
        try:
            if waveTimer < waveTimes[wave - 1]:
                pygame.draw.rect(screen, [0,255,0], [40, 133, round(waveTimer / waveTimes[wave - 1] * 1000), 8])
            else:
                pygame.draw.rect(screen, [0,255,0], [40, 133, 1035, 8])
        except:
            pygame.draw.rect(screen, [0,255,0], [40, 133, round(waveTimer / 2500 * 1000), 8])
       

         #arrows
        screen.blit(arrow_left,(80,20))       
        screen.blit(arrow_down,(230,20))
        screen.blit(arrow_up,(380,20))
        screen.blit(arrow_right,(530,20))
        
         #130,330,530,730
        screen.blit(green_pic,(10,30)) #minerals
        screen.blit(blue_pic,(160,30))
        screen.blit(pink_pic,(310,30)) 
        screen.blit(orange_pic,(460,30))

        #120,320,520,720
        myfont = pygame.font.SysFont(all_fonts[7], 25)
        
        textsurface = myfont.render(str(math.floor(green_mineral)), False, (0, 255, 0))
        screen.blit(textsurface,(65,50))
        
        textsurface = myfont.render(str(math.floor(blue_mineral)), False, (0,0,255))
        screen.blit(textsurface,(215,50))
        
        textsurface = myfont.render(str(math.floor(pink_mineral)), False, (255,192,203))
        screen.blit(textsurface,(365,50))
        
        textsurface = myfont.render(str(math.floor(orange_mineral)), False, (255, 165, 0))#665
        screen.blit(textsurface,(515,50)) #amounts of each mineral

        myfont = pygame.font.SysFont(all_fonts[7], 30)


        ############

        #names of towers
        myfont = pygame.font.SysFont(all_fonts[7], 18)
        
        textsurface = myfont.render("Projector", False, (0, 255, 0))
        screen.blit(textsurface,(1130,190)) #amounts of each mineral
        textsurface = myfont.render(str(projector_cost[0][0]), False, projector_cost[0][1])
        screen.blit(textsurface,(1190,130))
        textsurface = myfont.render(str(projector_cost[1][0]), False, projector_cost[1][1])
        screen.blit(textsurface,(1190,160))

        
        textsurface = myfont.render("Reflector", False, (0, 255, 0))
        screen.blit(textsurface,(1130,290))
        textsurface = myfont.render(str(reflector_cost[0][0]), False, reflector_cost[0][1])
        screen.blit(textsurface,(1190,230))
        textsurface = myfont.render(str(reflector_cost[1][0]), False, reflector_cost[1][1])
        screen.blit(textsurface,(1190,260))


        
        textsurface = myfont.render("Barricade", False, (0, 255, 0))
        screen.blit(textsurface,(1130,390))
        textsurface = myfont.render(str(barricade_cost[0][0]), False, barricade_cost[0][1])
        screen.blit(textsurface,(1190,330))
        textsurface = myfont.render(str(barricade_cost[1][0]), False, barricade_cost[1][1])
        screen.blit(textsurface,(1190,360))
        
        
        textsurface = myfont.render("Blast Projector", False, (0, 255, 0))
        screen.blit(textsurface,(1130,490))
        textsurface = myfont.render(str(aoe_projector_cost[0][0]), False, aoe_projector_cost[0][1])
        screen.blit(textsurface,(1190,430))
        textsurface = myfont.render(str(aoe_projector_cost[1][0]), False, aoe_projector_cost[1][1])
        screen.blit(textsurface,(1190,460))

        textsurface = myfont.render("Slow Projector", False, (0, 255, 0))
        screen.blit(textsurface,(1130,590))
        textsurface = myfont.render(str(slow_projector_cost[0][0]), False, slow_projector_cost[0][1])
        screen.blit(textsurface,(1190,530))
        textsurface = myfont.render(str(slow_projector_cost[1][0]), False, slow_projector_cost[1][1])
        screen.blit(textsurface,(1190,560))
        
        textsurface = myfont.render("Generator", False, (0, 255, 0))
        screen.blit(textsurface,(1130,690))
        textsurface = myfont.render(str(generator_cost[0][0]), False, generator_cost[0][1])
        screen.blit(textsurface,(1190,630))
        textsurface = myfont.render(str(generator_cost[1][0]), False, generator_cost[1][1])
        screen.blit(textsurface,(1190,660))
        
        myfont = pygame.font.SysFont(all_fonts[7], 30)
        ##################pygame.draw.rect(screen, [255,0,0], [1120, 220 + i * 100, 160, 5])
        

        pygame.draw.rect(screen, [255,255,0], [1055, 425, 30, 30]) #goal
        #goal coords are 105,26, i think
        for i in towers:
            pressed = i.draw(pos,mouseUp)
            if not calculating and onscreenParticles < 501 and not dead:
                particles = i.update(timer,particles)
                if pressed != False:
                    display = pressed

        if showCircle != False:
            #(self.x) * 10 + 35, (self.y) * 10 + 155
            pygame.draw.circle(surface1, (200,0,0), (showCircle[0] + 25, showCircle[1] + 25), showCircle[2] * 10)
        screen.blit(surface1, (0,0))
            
            



        particles,enemies,green_mineral,pink_mineral,blue_mineral,orange_mineral,totalKills = complete_collisions(particles,enemies,green_mineral,pink_mineral,blue_mineral,orange_mineral,totalKills)
        
        #move and draw enemies
        temp = []
        for i in enemies:
            i.draw()
            if not calculatingValid and not dead:
                lives_lost = i.move(timer,grid)
                if lives_lost > 0:
                    lives -= lives_lost
                    temp.append(i)

        for i in temp:
            enemies.remove(i)
            del i

        particles,enemies,green_mineral,pink_mineral,blue_mineral,orange_mineral,totalKills = complete_collisions(particles,enemies,green_mineral,pink_mineral,blue_mineral,orange_mineral,totalKills) #this has to be run twice to prevent
        #particles passing through enemies


        temp = [] #draw and move particles
        for i in particles:
            i.draw(screen)
            if not calculatingValid and not dead:
                onscreen = i.move(timer)
                if not onscreen:
                    temp.append(i)
                
        for i in temp:
            particles.remove(i)
            del i

        particles,green_mineral,blue_mineral,pink_mineral,orange_mineral = generator_collisions(grid,particles,green_mineral,blue_mineral,pink_mineral,orange_mineral)
        particles = reflector_collisions(grid,particles)

        
        if calculating and not dead:
            if newWaveDisplay > 0:
                newWaveDisplay -= 1
            
            if (mysprawler.finished or not re_search) and newWaveDisplay == 0:
                generalPath = mysprawler.getPath()
                newPath = generalPath
                calculating = False
                #load new wave here
                waveTimer = 0
                enemies = []
                particles = []
                re_search = False
            else:
                waveDisplayb.draw(screen)
                interestDisplayb.draw(screen)
                
                greenDisplayb.draw(screen)
                blueDisplayb.draw(screen)
                pinkDisplayb.draw(screen)
                orangeDisplayb.draw(screen)

        if calculatingValid and not dead:
            not_done_checking = heldTower.getCheckingValid()
            if not not_done_checking:
                
                calculatingValid = False
                #check,generalPath,grid,re_search
                check = heldTower.getCheck()
                newPath = heldTower.getGeneralPath()
                grid = heldTower.getGrid()
                re_search = heldTower.getRe_Search()
                
                if keep:
                    re_search = True
                if check:
                    if heldTower.getTowerType() == "generator":
                        grid = heldTower.update_grid(grid,"UU000")#uu+INCREASEmult+bonus+recycle

                    if heldTower.getTowerType() == "reflector":
                        grid = heldTower.update_grid_reflector(grid,"11fff")
                        #effect = R-CONFIG-DAMAGE-VELOCITY-REFLECTIVE-DUPLICATION-EFFICIENCY
                        #EFFECT = R111fff

                    for i in towers:
                        heldTower.effectNewTower(i)
                        
                    towers.append(heldTower)
                    
                    cost = heldTower.getInitialCost()
                    green_mineral -= cost[0]
                    blue_mineral -= cost[1]
                    pink_mineral -= cost[2]
                    orange_mineral -= cost[3]
                    heldTower=None
                
            else:
                checkingb.draw(screen)                
                

        mouseUp=False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    position = "pause"
                elif event.key == pygame.K_w:
                    heldTower = None
                    display = "normal"
                    showCircle = False

                elif event.key == pygame.K_a and heldTower != None:
                    heldTower.rotate("clockwise")

                elif event.key == pygame.K_d and heldTower != None:
                    heldTower.rotate("anticlockwise")
                    
                elif event.key == pygame.K_s:
                    showPath = not showPath
                    
            if event.type == pygame.MOUSEBUTTONUP:
                mouseUp = True

        if not calculating and not dead:

            waveTimer,enemies,done = spawnWave(wave,waveTimer,enemies,waveTimes) #spawns enemies throughout the wave
            if done:
                #interest stuff
                dgreen = green_mineral
                dblue = blue_mineral
                dpink = pink_mineral
                dorange = orange_mineral
                if green_mineral <= blue_mineral and green_mineral <= pink_mineral and green_mineral <= orange_mineral:
                    green_mineral = green_mineral + interestShortage * green_mineral

                elif blue_mineral <= green_mineral and blue_mineral <= pink_mineral and blue_mineral <= orange_mineral:
                    blue_mineral = blue_mineral + interestShortage * blue_mineral

                elif pink_mineral <= blue_mineral and pink_mineral <= green_mineral and pink_mineral <= orange_mineral:
                    pink_mineral = pink_mineral + interestShortage * pink_mineral

                else:
                    orange_mineral = orange_mineral + interestShortage * orange_mineral

                green_mineral = green_mineral + interestMain * green_mineral
                blue_mineral = blue_mineral + interestMain * blue_mineral
                pink_mineral = pink_mineral + interestMain * pink_mineral
                orange_mineral = orange_mineral + interestMain * orange_mineral
                
                wave += 1
                
                particles = []
                for i in towers:
                    if i.ghost:
                        i.ghost = False
                        
                if re_search:
                    mysprawler.search_with_thread(grid,(0,28),(104,28))
                calculating = True
                newWaveDisplay = 250
                waveDisplayb = button(grey,403,270,250,100,("Wave "+str(wave - 1)+" complete!!!"))
                interestDisplayb = button(grey,403,390,250,100,("Interest Made:"))
                
                greenDisplayb = button(grey,42,520,230,100,("Green: "+str(math.floor(green_mineral - dgreen))))
                blueDisplayb = button(grey,307,520,230,100,("Blue: "+str(math.floor(blue_mineral - dblue))))
                pinkDisplayb = button(grey,582,520,230,100,("Pink: "+str(math.floor(pink_mineral - dpink))))
                orangeDisplayb = button(grey,847,520,230,100,("Orange: "+str(math.floor(orange_mineral - dorange))))

        if lives < 1:
            showCircle = False
            dead = True
            youdiedb = button(grey,353,270,450,100,"Game Over - You died on wave " + str(wave))
            youdiedb.hover()
            youdiedb.draw(screen)
            
            if youdiedb.press():
                position = "home"
                    
        if heldTower != None and not dead:
            if not calculatingValid:
                heldTower.drawHeld(pos)
                if heldTower.firing:
                    newx , newy = heldTower.calculate_start_location()
                    particles.append(particle(newx,newy,heldTower.direction,0,heldTower.life,heldTower.reflections,1,False,False,False,True,False,False,1))
                            #def __init__(self,x,y,direction,damage,life,reflections,speed,aoe,slow,slowDuration,
                            #penetrating,splitting,confuse,confuseWeakness,static = False):
                if mouseUp:
                    keep = False
                    if re_search:
                        keep = True
                    calculatingValid = True
                    heldTower.checkValidThread(towers,grid,newPath)
                

            
        if not calculating and not calculatingValid and not dead:

            shooterButton.create(screen)
            screen.blit(plain_projector,(1130,130))

            reflectorButton.create(screen)
            screen.blit(plain_reflector,(1130,230))

            barricadeButton.create(screen)
            screen.blit(plain_barricade,(1130,330))

            aoeButton.create(screen)
            screen.blit(aoe_projector,(1130,430))

            slowButton.create(screen)####
            screen.blit(slow_projector,(1130,530))

            generatorButton.create(screen)####
            screen.blit(generator,(1130,630))

            if shooterButton.click(pos,mouseUp):
                showCircle = False
                if green_mineral >= projector_cost[0][0] and blue_mineral >= projector_cost[1][0]:
                    heldTower=tower(pos[0],pos[1],5,plain_projector,plain_projector_ghost,3,projector_cost,"projector")
                    display = "normal"

            elif reflectorButton.click(pos,mouseUp):
                showCircle = False
                if green_mineral >= reflector_cost[0][0] and pink_mineral >= reflector_cost[1][0]:
                    heldTower=tower(pos[0],pos[1],5,plain_reflector,plain_reflector_ghost,3,reflector_cost,"reflector")
                    display = "normal"

            elif barricadeButton.click(pos,mouseUp):
                showCircle = False
                if blue_mineral >= barricade_cost[0][0] and pink_mineral >= barricade_cost[1][0]:
                    heldTower=tower(pos[0],pos[1],5,plain_barricade,plain_barricade_ghost,3,barricade_cost,"barricade")
                    display = "normal"

            elif aoeButton.click(pos,mouseUp):
                showCircle = False
                if green_mineral >= aoe_projector_cost[0][0] and orange_mineral >= aoe_projector_cost[1][0]:
                    heldTower=tower(pos[0],pos[1],5,aoe_projector,aoe_projector_ghost,3,aoe_projector_cost,"aoe_projector")
                    display = "normal"

            elif slowButton.click(pos,mouseUp):
                showCircle = False
                if blue_mineral >= slow_projector_cost[0][0] and orange_mineral >= slow_projector_cost[1][0]:
                    heldTower=tower(pos[0],pos[1],5,slow_projector,slow_projector_ghost,3,slow_projector_cost,"slow_projector")
                    display = "normal"

            elif generatorButton.click(pos,mouseUp):
                showCircle = False
                if orange_mineral >= generator_cost[0][0] and pink_mineral >= generator_cost[1][0]:
                    heldTower=tower(pos[0],pos[1],5,generator,generator_ghost,3,generator_cost,"generator")
                    display = "normal"
                
        else:
            screen.blit(plain_projector_ghost,(1130,130))
            screen.blit(plain_reflector_ghost,(1130,230))
            screen.blit(plain_barricade_ghost,(1130,330))
            screen.blit(aoe_projector_ghost,(1130,430))
            screen.blit(slow_projector_ghost,(1130,530))
            screen.blit(generator_ghost,(1130,630))

        onscreenParticles = len(particles)

    elif position == "pause":
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    position = "game"
            
        continb.draw(screen)
        continb.hover()
        exitmenub.draw(screen)
        exitmenub.hover()
        pausedb.draw(screen)
        
        if continb.press():
            position = "game"
            
        if exitmenub.press():
            position = "home"
        
    
    pygame.display.flip()

    
