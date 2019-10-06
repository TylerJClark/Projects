import pygame
import random
import os
import time
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
pygame.display.set_caption("Kill the thugs 2")
clock = pygame.time.Clock()
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
            else:
                self.current_colour = self.colour

        

    def press(self):#checks if the mouse button is pressed.
        if self.clicked(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return True 
        return False



class policeman_():
    def __init__(self,button,x,y,weapon,impact = None):
        self.damage = 100
        self.range = 200
        self.speed = 15
        self.max_cooldown = 120
        self.button = button
        self.coordx = x
        self.coordy = y
        self.cooldown = 0
        self.projectile_image = weapon
        self.targets = 1
        self.max_targets = 1
        self.image = policeman2 #upgrade path [mech arm,thug lyfe][double hit,quad hit]
        self.display = [0,0]
        self.upgrades = [[policemanmechb,policemanthugb,policemanthugqb],[policemandoubleb,policemanquadb,policemanoctb]]
        self.upgradecosts = [[250,10000,50000],[100,400,4000]] 
        self.upgradephotos = [[policemanmech,policemanthug,policemanthugq],[policemandouble,policemanquad,policemanoct]]
        self.stun = 0

        self.aoe = 0
        self.degrades = False
        self.confuse = 0
        self.impact = impact
        self.explode_image = None

    def mech_arm(self):
        self.speed = 20
        self.max_cooldown = 40
        self.image = policemanmech2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [1,None]

    def thug_lyfe(self):
        self.speed = 30
        self.max_cooldown = 4
        self.damage = 500
        self.image = policemanthug2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [2,None]

    def thug_lyfe2(self):
        self.speed = 30
        self.max_cooldown = 4  #187 dps
        self.damage = 7750 #750
        self.image = policemanthugq2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,None]

    def double(self):
        self.image = policemandouble2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,1]
        self.max_targets = 2

    def quad(self):
        self.image = policemanquad2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,2]
        self.max_targets = 4

    def oct(self):
        self.image = policemanoct2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,None]
        self.max_targets = 8
        
class dog_():
    def __init__(self,button,x,y,weapon,impact = None):
        self.damage = 60
        self.range = 300
        self.speed = 20
        self.targets = 1
        self.max_targets = 1
        self.max_cooldown = 40
        self.button = button
        self.coordx = x
        self.coordy = y
        self.cooldown = 0
        self.projectile_image = weapon
        self.image = doge2
        self.display = [0,0]
        self.upgrades = [[dogesniperb,dogesniperDb,dogesniperDDb],[stundogeb,stundogedoubleb,stundogequadb]]
        self.upgradecosts = [[500,1000,30000],[600,1500,15000]] 
        self.upgradephotos = [[dogesniper,dogesniperD,dogesniperDD],[stundoge,stundogedouble,stundogequad]]
        self.stun = 0

        self.aoe = 0
        self.degrades = False
        self.confuse = 0
        self.impact = impact
        self.explode_image = None

    def sniper(self):
        self.damage = 250
        self.range = 1000
        self.speed = 30
        self.image = dogesniper2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [1,None]

    def sniperD(self):
        self.damage = 1000
        self.image = dogesniperD2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [2,None]

    def sniperDD(self):
        self.damage = 10000 #55.555 for nuke
        self.max_cooldown = 60 #167 dps
        self.image = dogesniperDD2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,None]

    def stunsingle(self):
        self.stun = 20
        self.image = stundoge2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,1]
        
    def stundouble(self):
        self.stun = 30
        self.image = stundogedouble2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,2]
        self.max_targets = 2        

    def stunquad(self):
        self.stun = 40
        self.image = stundogequad2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,None]
        self.max_targets = 4    


class mine_():
    def __init__(self,button,x,y,weapon,impact = None):
        self.damage = 150
        self.range = 300
        self.speed = 30
        self.max_cooldown = 180
        self.button = button
        self.coordx = x
        self.coordy = y
        self.cooldown = 0
        self.projectile_image = weapon
        self.targets = 1
        self.max_targets = 1
        self.image = mine2 #####
        self.display = [0,0]
        self.upgrades = [[grenadeb,bombb,nukeb],[confuseb,more_confuseb,degradeb]]
        self.upgradecosts = [[500,2000,150000],[2500,5000,30000]] 
        self.upgradephotos = [[grenade,bomb,nuke],[confuse,more_confuse,degrade]]
        self.stun = 0
        self.aoe = 75
        self.degrades = False
        self.confuse = 0
        self.impact = impact
        self.explode_image = explode
        #[[grenade,bomb,nuke],[confuse,moreconfuse,degrade_moreconfuse]]

    def grenade_(self):
        self.range = 250
        self.damage = 500
        self.aoe = 100
        self.image = grenade2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [1,None]

    def bomb_(self):
        self.range = 350
        self.speed = 35
        self.damage = 1000
        self.aoe = 150
        self.image = bomb2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [2,None]

    def nuke_(self):
        self.range = 450
        self.speed = 40
        self.aoe = 250 #56 dps
        self.damage = 10000
        self.image = nuke2
        self.explode_image = nuke_explode
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,None]

    def confuse_(self):
        self.confuse = 30
        self.aoe = 125
        self.image = confuse2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,1]

    def more_confuse_(self):
        self.confuse = 60
        self.aoe = 150
        self.image = more_confuse2
        #self.image = nuke2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,2]

    def degrade_(self):
        self.aoe = 200
        self.degrades = True
        self.image = degrade2
        self.button = button(grey,self.coordx,self.coordy,75,75,"")
        self.display = [None,None]


class explosion():
    def __init__(self,image,x,y):
        self.image  = image
        self.timer = 15
        self.x = x
        self.y = y
        
        
class projectile_():
    def __init__(self,damage,image,speed,currentx,currenty,targetx,targety,enemy,stun,aoe,explode_image,confuse,degrade):
        self.damage = damage
        self.image = image
        self.speed = speed
        self.currentx = currentx
        self.currenty = currenty
        self.targetx = targetx
        self.targety = targety
        self.distx = self.targetx - self.currentx
        self.disty = self.targety - self.currenty
        self.dist = 99999
        self.enemy = enemy
        self.stun = stun
        self.aoe = aoe
        self.explodex = None
        self.explodey = None
        self.explode_total = None
        self.explode_image = explode_image
        self.confuse = confuse
        self.degrade = degrade
        


class enemy():
    def __init__(self):
        self.coordx = 50
        self.coordy = 300
        self.stun = 0
        self.total_distance = 0
        self.confuse = 0
        self.total_confuse = 3

class thug_(enemy):
    def __init__(self):
        super(thug_,self).__init__()
        self.hp = 100
        self.movespeed = 2
        self.value = 10
        self.image = thug
        self.stun = 0
        self.stun_resist = 1
        self.lower = None
        
class crook_(enemy):
    def __init__(self):
        super(crook_,self).__init__()
        self.hp = 250
        self.movespeed = 1
        self.value = 30
        self.image = crook
        self.stun_resist = 1
        self.lower = thug_()
class hitman_(enemy):
    def __init__(self):
        super(hitman_,self).__init__()
        self.hp = 500
        self.movespeed = 4
        self.value = 50
        self.image = hitman
        self.stun_resist = 1
        self.lower = crook_()
        
class boss_(enemy):
    def __init__(self):
        super(boss_,self).__init__()
        self.hp = 1000
        self.movespeed = 3
        self.value = 100
        self.image = boss
        self.stun_resist = 1
        self.lower = hitman_()
        
class god_(enemy):
    def __init__(self):
        super(god_,self).__init__()
        self.hp = 8000
        self.movespeed = 2
        self.value = 150
        self.image = god
        self.stun_resist = 2
        self.total_confuse = 2
        self.lower = boss_()

class asteroid_(enemy):
    def __init__(self):
        super(asteroid_,self).__init__()
        self.hp = 5000
        self.movespeed = 6
        self.value = 200
        self.image = asteroid
        self.stun_resist = 5
        self.total_confuse = 1
        self.lower = god_()

class star_(enemy):
    def __init__(self):
        super(star_,self).__init__()
        self.hp = 20000
        self.movespeed = 3
        self.value = 300
        self.image = star
        self.stun_resist = 4
        self.total_confuse = 2
        self.lower = asteroid_()

class black_hole_(enemy):
    def __init__(self):
        super(black_hole_,self).__init__()
        self.hp = 500000
        self.movespeed = 2
        self.value = 1000
        self.image = black_hole
        self.stun_resist = 15
        self.total_confuse = 1
        self.lower = None

def generate_enemies(timer,kills,enemies,bosslvl):   

    if kills > 10000:
        if enemies == []:
            bosslvl += 1
            for i in range(bosslvl):
                enemies.append(black_hole_())

    elif kills > 9900:
        if timer % 150 == 0:
            enemies.append(black_hole_())
        if timer % 18 == 0:
            enemies.append(star_())
        if timer % 9 == 0:
            enemies.append(asteroid_())


    elif kills > 9100:
        if timer % 180 == 0:
            enemies.append(black_hole_())
        if timer % 18 == 0:
            enemies.append(star_())
        if timer % 9 == 0:
            enemies.append(asteroid_())

    elif kills > 9000:
        if timer % 115 == 0:
            enemies.append(black_hole_())

    elif kills > 8550:
        if timer % 500 == 0:
            enemies.append(black_hole_())
        if timer % 20 == 0:
            enemies.append(star_())

    elif kills > 8500:
        if timer % 150 == 0:
            enemies.append(black_hole_())

    elif kills > 8050:
        if timer % 15 == 0:
            enemies.append(asteroid_())
        if timer % 700 == 0:
            enemies.append(black_hole_())

    elif kills > 8000:
        if timer % 200 == 0:
            enemies.append(black_hole_())

    elif kills > 7530:
        if timer % 18 == 0:
            enemies.append(star_())
        if timer % 9 == 0:
            enemies.append(asteroid_())

    elif kills > 7500:
        if timer % 300 == 0:
            enemies.append(black_hole_())
            
    elif kills > 7025:
        if timer % 18 == 0:
            enemies.append(star_())
        if timer % 8 == 0:
            enemies.append(asteroid_())

    elif kills > 7000:
        if timer % 500 == 0:
            enemies.append(black_hole_())

    elif kills > 6700:
        if timer % 19 == 0:
            enemies.append(star_())
        if timer % 13 == 0:
            enemies.append(asteroid_())

    elif kills > 6500:
        if timer % 25 == 0:
            enemies.append(star_())
        if timer % 13 == 0:
            enemies.append(god_())

    elif kills > 6100:
        if timer % 19 == 0:
            enemies.append(star_())

    elif kills > 5900:
        if timer % 12 == 0:
            enemies.append(asteroid_())
        
    elif kills > 5000:
        if timer % int((100 - 5.7*math.log(kills - 4900,1.5))) == 0: #8
            enemies.append(god_())
        if timer % 8 == 0:
            enemies.append(thug_())

    elif kills > 4000:
        if timer % int((183 - 4.5*math.log(kills - 3900,1.2))) == 0: #21
            enemies.append(god_())
        if timer % int((180 - 4.5*math.log(kills - 3900,1.2))) == 0:
            enemies.append(boss_())
        if timer % 10 == 0:
            enemies.append(thug_())

    elif kills > 3000:
        if timer % int((175 - 3.2*math.log(kills - 2900,1.15))) == 0: #12
            enemies.append(god_())
        if timer % int((172 - 3.2*math.log(kills - 2900,1.15))) == 0:
            enemies.append(boss_())
        if timer % int(171 - 3.2*math.log(kills - 2900,1.15)) == 0:
            enemies.append(hitman_())  
        if timer % 10 == 0:
            enemies.append(thug_())


    elif kills > 2100:
        if timer % int((142 - 2.2*math.log(kills - 2000,1.15))) == 0:
            enemies.append(god_())
        if timer % int((118 - 2.2*math.log(kills - 2000,1.15))) == 0:
            enemies.append(crook_())
        if timer % int((128 - 2.2*math.log(kills - 2000,1.15))) == 0:
            enemies.append(boss_())
        if timer % int((128 - 2.2*math.log(kills - 2000,1.15))) == 0:
            enemies.append(thug_())
        if timer % int(130 - 2.2*math.log(kills - 2000,1.15)) == 0:
            enemies.append(hitman_())


    elif kills > 2000:
        if timer % 20 == 0:
            enemies.append(thug_())
    
    elif kills > 1800:
        if timer % 40 == 0:
            enemies.append(god_())
        if timer % 8 == 0:
            enemies.append(crook_())
        if timer % 20 == 0:
            enemies.append(boss_())
        if timer % 4 == 0:
            enemies.append(thug_())
        if timer % 10 == 0:
            enemies.append(hitman_())

            
    elif kills > 1500:
        if timer % 6 == 0:
            enemies.append(crook_())
        if timer % 40 == 0:
            enemies.append(god_())

    elif kills > 1200:
        if timer % 4 == 0:
            enemies.append(thug_())
        if timer % 50 == 0:
            enemies.append(god_())
            
    elif kills > 1000:
        if timer % 40 == 0:
            enemies.append(god_())

    elif kills > 950:
        if timer % 6 == 0:
            enemies.append(crook_())
        if timer % 45 == 0:
            enemies.append(god_())

    elif kills > 900:
        if timer % 5 == 0:
            enemies.append(crook_())
        if timer % 13 == 0:
            enemies.append(boss_())
    
    elif kills > 850:
        if timer % 6 == 0:
            enemies.append(crook_())
        if timer % 14 == 0:
            enemies.append(hitman_())

    elif kills > 800:
        if timer % 6 == 0:
            enemies.append(thug_())
        if timer % 60 == 0:
            enemies.append(god_())

    elif kills > 750:
        if timer % 4 == 0:
            enemies.append(thug_())
        if timer % 22 == 0:
            enemies.append(boss_())

    elif kills > 700:
        if timer % 6 == 0:
            enemies.append(thug_())
        if timer % 12 == 0:
            enemies.append(hitman_())
    
    elif kills > 650:
        if timer % 6 == 0:
            enemies.append(thug_())
        if timer % 13 == 0:
            enemies.append(crook_())
            
    elif kills > 600:#####
        if timer % 66 == 0:
            enemies.append(god_())
            
    elif kills > 550:
        if timer % 40 == 0:
            enemies.append(boss_())

    elif kills > 500:
        if timer % 26 == 0:
            enemies.append(hitman_())
            
    elif kills > 480:
        if timer % 8 == 0:
            enemies.append(crook_())
            
    elif kills > 420:
        if timer % 6 == 0:
            enemies.append(thug_())

    elif kills > 400:
        if timer % 150 == 0:
            enemies.append(god_())
        if timer % 50 == 0:
            enemies.append(boss_())
    
    elif kills > 350:
        if timer % 160 == 0:
            enemies.append(god_())
        if timer % 80 == 0:
            enemies.append(boss_())
            
    elif kills > 320:
        if timer % 30 == 0:
            enemies.append(hitman_())
        if timer % 80 == 0:
            enemies.append(boss_())
            
    elif kills > 300:
        if timer % 160 == 0:
            enemies.append(god_())


    elif kills > 250:
        if timer % 50 == 0:
            enemies.append(thug_())
        if timer % 120 == 0:
            enemies.append(hitman_())
        if timer % 60 == 0:
            enemies.append(crook_())
        if timer % 250 == 0:
            enemies.append(boss_())
            
    elif kills > 210:
        if timer % 50 == 0:
            enemies.append(thug_())
        if timer % 120 == 0:
            enemies.append(hitman_())
        if timer % 70 == 0:
            enemies.append(crook_())

    elif kills > 200:
        if timer % 60 == 0:
            enemies.append(boss_())

    elif kills > 160:
        if timer % 60 == 0:
            enemies.append(thug_())
        if timer % 150 == 0:
            enemies.append(hitman_())
        if timer % 80 == 0:
            enemies.append(crook_())

    elif kills > 140:
        if timer % 60 == 0:
            enemies.append(crook_())
        if timer % 150 == 0:
            enemies.append(hitman_())

    elif kills > 120:
        if timer % 70 == 0:
            enemies.append(crook_())
        if timer % 50 == 0:
            enemies.append(thug_())
            
    elif kills > 110:
        if timer % 60 == 0:
            enemies.append(thug_())
        if timer % 150 == 0:
            enemies.append(hitman_())
            
    elif kills > 105:
        if timer % 30 == 0:
            enemies.append(crook_())
            
    elif kills > 100:
        if timer % 80 == 0:
            enemies.append(crook_())
    elif kills > 70:
        if timer % 35 == 0:
            enemies.append(thug_())
    elif kills > 65:
        if timer % 150 == 0:
            enemies.append(hitman_())
        if timer % 70 == 0:
            enemies.append(thug_())
            
    elif kills > 50:
        if timer % 60 == 0:
            enemies.append(thug_())
            
    elif kills > 40:
        if timer % 80 == 0:
            enemies.append(thug_())
        if timer % 100 == 0:
            enemies.append(crook_())
            
    elif kills > 20:
        if timer % 90 == 0:
            enemies.append(thug_())
        if timer % 180 == 0:
            enemies.append(crook_())
            
    elif kills > 18:
        if timer % 20 == 0:
            enemies.append(thug_())
            
    elif kills > 10:
        if timer % 95 == 0:
            enemies.append(thug_())
        if timer % 120 == 0:
            enemies.append(thug_())
            
    elif kills > 5:
        if timer % 90 == 0:
            enemies.append(thug_())
            
    elif timer % 110 == 0 and timer > 120:
        enemies.append(thug_())  #[coordx,cordy,hp]

        
    return enemies,bosslvl

def find_range(x1,x2,y1,y2):
    return abs((((x2-x1)**2 + (y2-y1)**2))**0.5)

ingame = True

policeman = pygame.image.load(os.path.join("policemanjpg.jpg")).convert()
policeman = pygame.transform.scale(policeman, (105, 105))
policeman2 = pygame.transform.scale(policeman, (75, 75))
policemanb = button(grey,780,50,105,105,"")
policeman.set_colorkey((255,255,255))
policeman2.set_colorkey((255,255,255))

policemanmech = pygame.image.load(os.path.join("policemanmech.PNG")).convert()
policemanmech = pygame.transform.scale(policemanmech, (105, 105))
policemanmech2 = pygame.transform.scale(policemanmech, (75, 75))
policemanmechb = button(grey,780,50,105,105,"")
policemanmech.set_colorkey((255,255,255))
policemanmech2.set_colorkey((255,255,255))

policemanthug = pygame.image.load(os.path.join("policemanthug.png")).convert()
policemanthug = pygame.transform.scale(policemanthug, (105, 105))
policemanthug2 = pygame.transform.scale(policemanthug, (75, 75))
policemanthugb = button(grey,780,50,105,105,"")
policemanthug.set_colorkey((255,255,255))
policemanthug2.set_colorkey((255,255,255))

policemanthugq = pygame.image.load(os.path.join("policemanthugq.png")).convert()
policemanthugq = pygame.transform.scale(policemanthugq, (105, 105))
policemanthugq2 = pygame.transform.scale(policemanthugq, (75, 75))
policemanthugqb = button(grey,780,50,105,105,"")
policemanthugq.set_colorkey((255,255,255))
policemanthugq2.set_colorkey((255,255,255))

policemandouble = pygame.image.load(os.path.join("policemandouble.PNG")).convert()
policemandouble = pygame.transform.scale(policemandouble, (105, 105))
policemandouble2 = pygame.transform.scale(policemandouble, (75, 75))
policemandoubleb = button(grey,380,50,105,105,"")
policemandouble.set_colorkey((255,255,255))
policemandouble2.set_colorkey((255,255,255))

policemanquad = pygame.image.load(os.path.join("policemanquad.PNG")).convert()
policemanquad = pygame.transform.scale(policemanquad, (105, 105))
policemanquad2 = pygame.transform.scale(policemanquad, (75, 75))
policemanquadb = button(grey,380,50,105,105,"")
policemanquad.set_colorkey((255,255,255))
policemanquad2.set_colorkey((255,255,255))

policemanoct = pygame.image.load(os.path.join("policemanoct.PNG")).convert()
policemanoct = pygame.transform.scale(policemanoct, (105, 105))
policemanoct2 = pygame.transform.scale(policemanoct, (75, 75))
policemanoctb = button(grey,380,50,105,105,"")
policemanoct.set_colorkey((255,255,255))
policemanoct2.set_colorkey((255,255,255))

doge = pygame.image.load(os.path.join("doggo.png")).convert()
doge2 = pygame.transform.scale(doge, (75, 75))
doge = pygame.transform.scale(doge, (105, 105))
doge.set_colorkey((255,255,255))
doge2.set_colorkey((255,255,255))
dogb = button(grey,930,50,105,105,"")

dogesniper = pygame.image.load(os.path.join("dogesniper.png")).convert()
dogesniper2 = pygame.transform.scale(dogesniper, (75, 75))
dogesniper = pygame.transform.scale(dogesniper, (105, 105))
dogesniperb = button(grey,780,50,105,105,"")
dogesniper.set_colorkey((255,255,255))
dogesniper2.set_colorkey((255,255,255))

dogesniperD = pygame.image.load(os.path.join("dogesniperD.png")).convert()
dogesniperD2 = pygame.transform.scale(dogesniperD, (75, 75))
dogesniperD = pygame.transform.scale(dogesniperD, (105, 105))
dogesniperDb = button(grey,780,50,105,105,"")
dogesniperD.set_colorkey((255,255,255))
dogesniperD2.set_colorkey((255,255,255))

dogesniperDD = pygame.image.load(os.path.join("dogesniperDD.png")).convert()
dogesniperDD2 = pygame.transform.scale(dogesniperDD, (75, 75))
dogesniperDD = pygame.transform.scale(dogesniperDD, (105, 105))
dogesniperDDb = button(grey,780,50,105,105,"")
dogesniperDD.set_colorkey((255,255,255))
dogesniperDD2.set_colorkey((255,255,255))

stundoge = pygame.image.load(os.path.join("stundoge.png")).convert()
stundoge2 = pygame.transform.scale(stundoge, (75, 75))
stundoge = pygame.transform.scale(stundoge, (105, 105))
stundogeb = button(grey,380,50,105,105,"")
stundoge.set_colorkey((255,255,255))
stundoge2.set_colorkey((255,255,255))

stundogedouble = pygame.image.load(os.path.join("stundogedouble.png")).convert()
stundogedouble2 = pygame.transform.scale(stundogedouble, (75, 75))
stundogedouble = pygame.transform.scale(stundogedouble, (105, 105))
stundogedoubleb = button(grey,380,50,105,105,"")
stundogedouble.set_colorkey((255,255,255))
stundogedouble2.set_colorkey((255,255,255))

stundogequad = pygame.image.load(os.path.join("stundogequad.png")).convert()
stundogequad2 = pygame.transform.scale(stundogequad, (75, 75))
stundogequad = pygame.transform.scale(stundogequad, (105, 105))
stundogequadb = button(grey,380,50,105,105,"")
stundogequad.set_colorkey((255,255,255))
stundogequad2.set_colorkey((255,255,255))

mine = pygame.image.load(os.path.join("mine.png")).convert()
mine2 = pygame.transform.scale(mine, (75, 75))
mine = pygame.transform.scale(mine, (105, 105))
mineb = button(grey,380,50,105,105,"")
mine.set_colorkey((255,255,255))
mine2.set_colorkey((255,255,255))

grenade = pygame.image.load(os.path.join("grenade.png")).convert()
grenade2 = pygame.transform.scale(grenade, (75, 75))
grenade = pygame.transform.scale(grenade, (105, 105))
grenadeb = button(grey,780,50,105,105,"")
grenade.set_colorkey((255,255,255))
grenade2.set_colorkey((255,255,255))

bomb = pygame.image.load(os.path.join("bomb.png")).convert()
bomb2 = pygame.transform.scale(bomb, (75, 75))
bomb = pygame.transform.scale(bomb, (105, 105))
bombb = button(grey,780,50,105,105,"")
bomb.set_colorkey((255,255,255))
bomb2.set_colorkey((255,255,255))

nuke = pygame.image.load(os.path.join("nuke.png")).convert()
nuke2 = pygame.transform.scale(nuke, (75, 75))
nuke = pygame.transform.scale(nuke, (105, 105))
nukeb = button(grey,780,50,105,105,"")
nuke.set_colorkey((255,255,255))
nuke2.set_colorkey((255,255,255))

confuse = pygame.image.load(os.path.join("confuse.png")).convert()
confuse2 = pygame.transform.scale(confuse, (75, 75))
confuse = pygame.transform.scale(confuse, (105, 105))
confuseb = button(grey,380,50,105,105,"")
confuse.set_colorkey((255,255,255))
confuse2.set_colorkey((255,255,255))

more_confuse = pygame.image.load(os.path.join("more_confuse.png")).convert()
more_confuse2 = pygame.transform.scale(more_confuse, (75, 75))
more_confuse = pygame.transform.scale(more_confuse, (105, 105))
more_confuseb = button(grey,380,50,105,105,"")
more_confuse.set_colorkey((255,255,255))
more_confuse2.set_colorkey((255,255,255))

degrade = pygame.image.load(os.path.join("degrade.png")).convert()
degrade2 = pygame.transform.scale(degrade, (75, 75))
degrade = pygame.transform.scale(degrade, (105, 105))
degradeb = button(grey,380,50,105,105,"")
degrade.set_colorkey((255,255,255))
degrade2.set_colorkey((255,255,255))


thug = pygame.image.load(os.path.join("thug.jpg")).convert()
thug = pygame.transform.scale(thug, (75, 75))
thug.set_colorkey((255,255,255))
crook = pygame.image.load(os.path.join("crook.jpg")).convert()
crook = pygame.transform.scale(crook, (75, 75))
crook.set_colorkey((255,255,255))
hitman = pygame.image.load(os.path.join("hitman.jpg")).convert()
hitman = pygame.transform.scale(hitman, (75, 75))
hitman.set_colorkey((255,255,255))
boss = pygame.image.load(os.path.join("mafia boss.jpg")).convert()
boss = pygame.transform.scale(boss, (75, 75))
boss.set_colorkey((255,255,255))
god = pygame.image.load(os.path.join("mafia god.jpg")).convert()
god = pygame.transform.scale(god, (75, 75))
god.set_colorkey((255,255,255))
asteroid = pygame.image.load(os.path.join("asteroid.png")).convert()
asteroid = pygame.transform.scale(asteroid, (75, 75))
asteroid.set_colorkey((255,255,255))
star = pygame.image.load(os.path.join("star.png")).convert()
star = pygame.transform.scale(star, (75, 75))
star.set_colorkey((255,255,255))
black_hole = pygame.image.load(os.path.join("black_hole.png")).convert()
black_hole = pygame.transform.scale(black_hole, (75, 75))
black_hole.set_colorkey((255,255,255))



nightstick = pygame.image.load(os.path.join("nightstick.png")).convert()
nightstick = pygame.transform.scale(nightstick, (75, 75))
nightstick.set_colorkey((255,255,255))

bone = pygame.image.load(os.path.join("bone.jpg")).convert()
bone = pygame.transform.scale(bone, (75, 75))
bone.set_colorkey((255,255,255))

white = pygame.image.load(os.path.join("white.png")).convert()
white = pygame.transform.scale(white, (75, 75))
white.set_colorkey((255,255,255))

explode = pygame.image.load(os.path.join("explode.png")).convert()
explode = pygame.transform.scale(explode, (75, 75))
explode.set_colorkey((255,255,255))

nuke_explode = pygame.image.load(os.path.join("nuke_explode.png")).convert()
nuke_explode = pygame.transform.scale(nuke_explode, (125, 125))
nuke_explode.set_colorkey((255,255,255))
        
while ingame:
    #setup
    quitt = button(grey,1160,20,100,100,"Quit")
    replay = button(grey,1160,130,100,100,"Replay")
    dollar = 500
    alive = True
    tiles = []
    regular = None
    policeman_cost = 200
    dog_cost = 500
    mine_cost = 1000
    chosen_tile = None
    policemen = []# = [[damage,range,projectile speed,max cooldown],[button,coords,cooldown],[button,coords,cooldown]]


    dogs = []
    mines = []
    explosions = []
    wave = 1
    enemies = []
    defenders = [policemen,dogs,mines]
    projectiles = []
    timer = 0
    kills = 0
    select = None
    speedup = False
    bosslvl = 0
    chosen_tile = None
    
    for j in range(3):
        for i in range(12):
            if i != 11 or j != 1:
                tiles.append([button(darkgreen,50 + i * 100,200 + 200 * j,75,75,""),[50 + i * 100,200 + 200 * j]])
        
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    speedup = not speedup
        if not speedup:
            clock.tick(fps)
        else:
            clock.tick(1000)
        screen.fill((255,255,255))
        if alive:
            enemies,bosslvl = generate_enemies(timer,kills,enemies,bosslvl)
        timer += 1
        if not alive:

            replay.draw(screen)
            replay.hover()
            if replay.press():
                break


        
        for j in enemies:
            screen.blit(j.image, (j.coordx,j.coordy))
            if alive:
                if j.stun <= 0:
                    if j.confuse > 0:
                        mult = True
                        j.confuse -= 1
                    else:
                        mult = False
                    if not mult:
                        if j.coordx < 1150 and j.coordy < 400:  #299
                            j.coordx += j.movespeed
                            j.total_distance += j.movespeed
                        elif j.coordy < 500:
                            j.coordy += j.movespeed
                            j.total_distance += j.movespeed
                        else:
                            j.coordx -= j.movespeed
                            j.total_distance += j.movespeed

                        if j.coordx < 0 and j.coordy > 400:
                            alive = False

                    if mult:
                        if j.coordy > 400 and j.coordx < 1150: #bottom line
                            j.coordx += j.movespeed
                            j.total_distance -= j.movespeed
                            
                        elif j.coordy > 299 and j.coordx >= 1150: #mid
                            j.coordy -= j.movespeed
                            j.total_distance -= j.movespeed

                        else:
                            j.coordx -= j.movespeed   #top
                            j.total_distance -= j.movespeed
                            
                            

                        if j.coordx < 0 and j.coordy > 400:
                            alive = False


                            
                else:
                    j.stun -= j.stun_resist


        enemies.sort(key=lambda x: x.total_distance, reverse=True)
        for group in defenders:  #(self,damage,image,speed,currentx,currenty,targetx,targety) projectile
            for i in group:
                #range detect
                for j in enemies:
                    if i.cooldown == 0: #check cooldown
                        #find_range(x1,x2,y1,y2)
                        if find_range(i.coordx,j.coordx+37,i.coordy,j.coordy+37) < i.range:
                            #screen.blit(nightstick, (780,50))
                            #projectiles.append([z[0][4],k[1][0],k[1][1],(j[0]+37)-(k[1][0]+37),(j[1]+37)-(k[1][1]+37),[z[0][0],z[0][2]],999999,(j[0]+37),(j[1]+37),[j,i]])
                            projectiles.append(projectile_(i.damage,i.projectile_image,i.speed,i.coordx,i.coordy,j.coordx+37,j.coordy,j,i.stun,i.aoe,i.explode_image,i.confuse,i.degrades))
                            if i.targets == i.max_targets:
                                i.cooldown = i.max_cooldown
                            else:
                                i.targets += 1
                                
                                #k[2] = z[0][3]
                if i.cooldown > 0:
                    i.cooldown -= 1
                    i.targets = 1
                                    
        if alive: #(self,damage,image,speed,currentx,currenty,targetx,targety,enemy) projectile
            for i in projectiles:
                if i.aoe != 0:
                    try:
                        i.explodex = i.enemy.coordx
                        i.explodey = i.enemy.coordy
                        i.explode_total = i.enemy.total_distance
                    except:pass
                i.currentx += (i.distx*i.speed)/(abs(i.distx)+abs(i.disty))
                i.currenty += (i.disty*i.speed)/(abs(i.distx)+abs(i.disty))
                
                dist = find_range(i.currentx,i.targetx,i.currenty,i.targety)
                if dist > i.dist: #hits
                    if i.aoe == 0:
                        if i.stun > 0:
                            i.enemy.stun = i.stun
                        i.enemy.hp -= i.damage
                        if i.enemy.hp <= 0:
                            
                            try:
                                enemies.remove(i.enemy)
                                dollar += i.enemy.value
                                kills += 1
                            except:pass
                        
                    else:
                        if i.explodex == None:
                            i.explodex = i.targetx
                            i.explodey = i.targety
                        #screen.blit(i.explode_image, (i.targetx,i.targety))
                        if i.explode_image == nuke_explode:
                            explosions.append(explosion(i.explode_image,i.explodex,i.explodey - 37))
                        else:
                            explosions.append(explosion(i.explode_image,i.explodex,i.explodey))

                        #print("explosion",i.explode_total)
                        temp = []
                        temp_add = []
                        temp_remove = []
                        
                        for k in enemies:
                            #print("enemy",k.total_distance)
                            #print(abs(i.explode_total - k.total_distance))
                            if abs(i.explode_total - k.total_distance) < i.aoe:
                                        
                                    #enemies.append(asteroid_())
                                k.hp -= i.damage
                                if k.hp <= 0:
                        
                                    try:
                                        temp.append(k)
                                        dollar += k.value
                                        kills += 1
                                    except:pass

                                else:
                                    if k.total_confuse > 0:
                                        k.confuse = i.confuse
                                        k.total_confuse -= 1

                                    if i.degrade:
                                        if k.lower != None:
                                            temp_remove.append(k)
                                            k.lower.coordx = k.coordx
                                            k.lower.coordy = k.coordy
                                            k.lower.stun = k.stun
                                            k.lower.total_distance = k.total_distance
                                            k.lower.confuse = k.confuse
                                            if k.lower.total_confuse > k.total_confuse:
                                                k.lower.total_confuse = k.total_confuse
                                            if k.lower.hp > k.hp:
                                                k.lower.hp = k.hp
                                                
                                            k.lower.value = k.value
                                            temp_add.append(k.lower)
                                            
                                    

                                #if abs(k.total_distance - i.explode_total) < i.aoe:
                                    #break

                        for b in temp:
                            enemies.remove(b)
                        for b in temp_add:
                            enemies.append(b)
                        for b in temp_remove:
                            enemies.remove(b)
                            
                    projectiles.remove(i)
                                    
                            
                else: #still moving
                    i.dist = dist
                    screen.blit(i.image, (i.currentx,i.currenty))

            for i in explosions:
                screen.blit(i.image, (i.x,i.y))
                i.timer -= 1
                if i.timer == 0:
                    explosions.remove(i)
                
                


        if regular == "basic":
            
            policemanb.draw(screen)
            policemanb.hover()
            screen.blit(policeman, (780,50))
            dogb.draw(screen)
            dogb.hover()
            screen.blit(doge, (930,50))
            mineb.draw(screen)
            mineb.hover()
            screen.blit(mine, (380,50))
            
            textsurface = myfont.render("$"+str(policeman_cost), False, (0, 0, 0))
            screen.blit(textsurface,(800,10))
            textsurface = myfont.render("$"+str(dog_cost), False, (0, 0, 0))
            screen.blit(textsurface,(950,10))
            textsurface = myfont.render("$"+str(mine_cost), False, (0, 0, 0))
            screen.blit(textsurface,(400,10))
            
            if policemanb.press() and dollar >= policeman_cost:
                dollar -= policeman_cost
                regular = None
                tiles.remove(chosen_tile)
                #policemen.append([button(grey,chosen_tile[1][0],chosen_tile[1][1],75,75,""),[chosen_tile[1][0],chosen_tile[1][1]],0])
                policemen.append(policeman_(button(grey,chosen_tile[1][0],chosen_tile[1][1],75,75,""),chosen_tile[1][0],chosen_tile[1][1],nightstick))
                select = None
                time.sleep(0.2)
                
            elif dogb.press() and dollar >= dog_cost:
                dollar -= dog_cost
                regular = None
                tiles.remove(chosen_tile)
                #dogs.append([button(grey,chosen_tile[1][0],chosen_tile[1][1],75,75,""),[chosen_tile[1][0],chosen_tile[1][1]],0])
                dogs.append(dog_(button(grey,chosen_tile[1][0],chosen_tile[1][1],75,75,""),chosen_tile[1][0],chosen_tile[1][1],bone))
                select = None
                time.sleep(0.2)

            elif mineb.press() and dollar >= mine_cost:
                dollar -= mine_cost
                regular = None
                tiles.remove(chosen_tile)
                #dogs.append([button(grey,chosen_tile[1][0],chosen_tile[1][1],75,75,""),[chosen_tile[1][0],chosen_tile[1][1]],0])
                mines.append(mine_(button(grey,chosen_tile[1][0],chosen_tile[1][1],75,75,""),chosen_tile[1][0],chosen_tile[1][1],white))
                select = None
                time.sleep(0.2)
                
        elif regular == "police":
            if select.display[0] == 0:
                select.upgrades[0][0].draw(screen)
                select.upgrades[0][0].hover()
                screen.blit(select.upgradephotos[0][0], (780,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[0][0]), False, (0, 0, 0))
                screen.blit(textsurface,(800,10))
                if select.upgrades[0][0].press() and dollar >= select.upgradecosts[0][0]:
                    select.mech_arm()
                    dollar -= select.upgradecosts[0][0]
                    chosen_tile = None
                    time.sleep(0.2)
                    
            elif select.display[0] == 1:
                select.upgrades[0][1].draw(screen)
                select.upgrades[0][1].hover()
                screen.blit(select.upgradephotos[0][1], (780,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[0][1]), False, (0, 0, 0))
                screen.blit(textsurface,(800,10))
                if select.upgrades[0][1].press() and dollar >= select.upgradecosts[0][1]:
                    select.thug_lyfe()
                    dollar -= select.upgradecosts[0][1]
                    chosen_tile = None
                    time.sleep(0.2)

            elif select.display[0] == 2:
                select.upgrades[0][2].draw(screen)
                select.upgrades[0][2].hover()
                screen.blit(select.upgradephotos[0][2], (780,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[0][2]), False, (0, 0, 0))
                screen.blit(textsurface,(800,10))
                if select.upgrades[0][2].press() and dollar >= select.upgradecosts[0][2]:
                    select.thug_lyfe2()
                    dollar -= select.upgradecosts[0][2]
                    chosen_tile = None

            if select.display[1] == 0:
                select.upgrades[1][0].draw(screen)
                select.upgrades[1][0].hover()
                screen.blit(select.upgradephotos[1][0], (380,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[1][0]), False, (0, 0, 0))
                screen.blit(textsurface,(400,10))
                if select.upgrades[1][0].press() and dollar >= select.upgradecosts[1][0]:
                    select.double()
                    dollar -= select.upgradecosts[1][0]
                    chosen_tile = None
                    time.sleep(0.2)
                    
            elif select.display[1] == 1:
                select.upgrades[1][1].draw(screen)
                select.upgrades[1][1].hover()
                screen.blit(select.upgradephotos[1][1], (380,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[1][1]), False, (0, 0, 0))
                screen.blit(textsurface,(400,10))
                if select.upgrades[1][1].press() and dollar >= select.upgradecosts[1][1]:
                    select.quad()
                    dollar -= select.upgradecosts[1][1]
                    chosen_tile = None
                    time.sleep(0.2)


            elif select.display[1] == 2:
                select.upgrades[1][2].draw(screen)
                select.upgrades[1][2].hover()
                screen.blit(select.upgradephotos[1][2], (380,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[1][2]), False, (0, 0, 0))
                screen.blit(textsurface,(400,10))
                if select.upgrades[1][2].press() and dollar >= select.upgradecosts[1][2]:
                    select.oct()
                    dollar -= select.upgradecosts[1][2]
                    chosen_tile = None
                
        elif regular == "doge":
            if select.display[0] == 0:
                select.upgrades[0][0].draw(screen)
                select.upgrades[0][0].hover()
                screen.blit(select.upgradephotos[0][0], (780,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[0][0]), False, (0, 0, 0))
                screen.blit(textsurface,(800,10))
                if select.upgrades[0][0].press() and dollar >= select.upgradecosts[0][0]:
                    select.sniper()
                    dollar -= select.upgradecosts[0][0]
                    chosen_tile = None
                    time.sleep(0.2)
                    
            elif select.display[0] == 1:
                select.upgrades[0][1].draw(screen)
                select.upgrades[0][1].hover()
                screen.blit(select.upgradephotos[0][1], (780,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[0][1]), False, (0, 0, 0))
                screen.blit(textsurface,(800,10))
                if select.upgrades[0][1].press() and dollar >= select.upgradecosts[0][1]:
                    select.sniperD()
                    dollar -= select.upgradecosts[0][1]
                    chosen_tile = None
                    time.sleep(0.2)

            elif select.display[0] == 2:
                select.upgrades[0][2].draw(screen)
                select.upgrades[0][2].hover()
                screen.blit(select.upgradephotos[0][2], (780,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[0][2]), False, (0, 0, 0))
                screen.blit(textsurface,(800,10))
                if select.upgrades[0][2].press() and dollar >= select.upgradecosts[0][2]:
                    select.sniperDD()
                    dollar -= select.upgradecosts[0][2]
                    chosen_tile = None

            if select.display[1] == 0:
                select.upgrades[1][0].draw(screen)
                select.upgrades[1][0].hover()
                screen.blit(select.upgradephotos[1][0], (380,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[1][0]), False, (0, 0, 0))
                screen.blit(textsurface,(400,10))
                if select.upgrades[1][0].press() and dollar >= select.upgradecosts[1][0]:
                    select.stunsingle()
                    dollar -= select.upgradecosts[1][0]
                    chosen_tile = None
                    time.sleep(0.2)
                    
            elif select.display[1] == 1:
                select.upgrades[1][1].draw(screen)
                select.upgrades[1][1].hover()
                screen.blit(select.upgradephotos[1][1], (380,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[1][1]), False, (0, 0, 0))
                screen.blit(textsurface,(400,10))
                if select.upgrades[1][1].press() and dollar >= select.upgradecosts[1][1]:
                    select.stundouble()
                    dollar -= select.upgradecosts[1][1]
                    chosen_tile = None
                    time.sleep(0.2)

            elif select.display[1] == 2:
                select.upgrades[1][2].draw(screen)
                select.upgrades[1][2].hover()
                screen.blit(select.upgradephotos[1][2], (380,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[1][2]), False, (0, 0, 0))
                screen.blit(textsurface,(400,10))
                if select.upgrades[1][2].press() and dollar >= select.upgradecosts[1][2]:
                    select.stunquad()
                    dollar -= select.upgradecosts[1][2]
                    chosen_tile = None


        elif regular == "mines":
            if select.display[0] == 0:
                select.upgrades[0][0].draw(screen)
                select.upgrades[0][0].hover()
                screen.blit(select.upgradephotos[0][0], (780,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[0][0]), False, (0, 0, 0))
                screen.blit(textsurface,(800,10))
                if select.upgrades[0][0].press() and dollar >= select.upgradecosts[0][0]:
                    select.grenade_()
                    dollar -= select.upgradecosts[0][0]
                    chosen_tile = None
                    time.sleep(0.2)
                    
            elif select.display[0] == 1:
                select.upgrades[0][1].draw(screen)
                select.upgrades[0][1].hover()
                screen.blit(select.upgradephotos[0][1], (780,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[0][1]), False, (0, 0, 0))
                screen.blit(textsurface,(800,10))
                if select.upgrades[0][1].press() and dollar >= select.upgradecosts[0][1]:
                    select.bomb_()
                    dollar -= select.upgradecosts[0][1]
                    chosen_tile = None
                    time.sleep(0.2)

            elif select.display[0] == 2:
                select.upgrades[0][2].draw(screen)
                select.upgrades[0][2].hover()
                screen.blit(select.upgradephotos[0][2], (780,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[0][2]), False, (0, 0, 0))
                screen.blit(textsurface,(800,10))
                if select.upgrades[0][2].press() and dollar >= select.upgradecosts[0][2]:
                    select.nuke_()
                    dollar -= select.upgradecosts[0][2]
                    chosen_tile = None

            if select.display[1] == 0:
                select.upgrades[1][0].draw(screen)
                select.upgrades[1][0].hover()
                screen.blit(select.upgradephotos[1][0], (380,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[1][0]), False, (0, 0, 0))
                screen.blit(textsurface,(400,10))
                if select.upgrades[1][0].press() and dollar >= select.upgradecosts[1][0]:
                    select.confuse_()
                    dollar -= select.upgradecosts[1][0]
                    chosen_tile = None
                    time.sleep(0.2)
                    
            elif select.display[1] == 1:
                select.upgrades[1][1].draw(screen)
                select.upgrades[1][1].hover()
                screen.blit(select.upgradephotos[1][1], (380,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[1][1]), False, (0, 0, 0))
                screen.blit(textsurface,(400,10))
                if select.upgrades[1][1].press() and dollar >= select.upgradecosts[1][1]:
                    select.more_confuse_()
                    dollar -= select.upgradecosts[1][1]
                    chosen_tile = None
                    time.sleep(0.2)

            elif select.display[1] == 2:
                select.upgrades[1][2].draw(screen)
                select.upgrades[1][2].hover()
                screen.blit(select.upgradephotos[1][2], (380,50))
                textsurface = myfont.render("$"+str(select.upgradecosts[1][2]), False, (0, 0, 0))
                screen.blit(textsurface,(400,10))
                if select.upgrades[1][2].press() and dollar >= select.upgradecosts[1][2]:
                    select.degrade_()
                    dollar -= select.upgradecosts[1][2]
                    chosen_tile = None
   
        textsurface = myfont.render("Dollar: "+str(dollar), False, (0, 0, 0))
        screen.blit(textsurface,(780,150))
        textsurface = myfont.render("Kills: "+str(kills), False, (0, 0, 0))
        screen.blit(textsurface,(380,150))
        if bosslvl > 0:
            textsurface = myfont.render("Bosses: "+str(bosslvl), False, (0, 0, 0))
            screen.blit(textsurface,(590,150))

        for i in policemen:
            if i == select:
                i.button.draw(screen,show_active = True)
            else:
                i.button.draw(screen)
            i.button.hover()
            screen.blit(i.image, (i.coordx,i.coordy))
            if i.button.press():
                regular = "police"
                select = i
                chosen_tile = None
                    

        for i in dogs:
            if i == select:
                i.button.draw(screen,show_active = True)
            else:
                i.button.draw(screen)
            i.button.hover()
            screen.blit(i.image, (i.coordx,i.coordy))
            if i.button.press():
                regular = "doge"
                select = i
                chosen_tile = None

        for i in mines:
            if i == select:
                i.button.draw(screen,show_active = True)
            else:
                i.button.draw(screen)
            i.button.hover()
            screen.blit(i.image, (i.coordx,i.coordy))
            if i.button.press():
                regular = "mines"
                select = i
                chosen_tile = None
                    
        for i in tiles:
            if i == chosen_tile:
                i[0].draw(screen,show_active = True)
            else:
                i[0].draw(screen)
            i[0].hover()
            if i[0].press():
                regular = "basic"
                chosen_tile = i
                select = None
                
        #pygame.draw.rect(screen,darkgreen,(50 + i * 100,200,75,75))

        quitt.draw(screen)
        quitt.hover()
        if quitt.press():
            ingame = False
            pygame.quit()
            break

        pygame.display.flip()


    
