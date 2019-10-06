import pygame
#pygame is the main library used to create the game
import os
#used to specify the file location of graphics for the game
import math
#used to access pygame's vector library
import random
#adds randomness. This is only used with sound so the game is consistent
import time
#used to time things
import socket
#used for networking, to access the server and play multiplayer
import _thread
#used for networking, so the game can run while communicating with the server on a different thread.
import hashlib
#used to hash passwords
import string
#contains ASCII character set

vec = pygame.math.Vector2 #allows the use of the vector library

white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
black = (0,0,0)
grey = (128,128,128) #Define many colours used throughout rather than needing to use the rgb values

#assets
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder,"images") #specifiy the images file, where graphics are stored.

pygame.init()
pygame.mixer.init() #initialises pygame and sound

jump_sound = pygame.mixer.Sound("Jump.wav")  #different sounds effects in the game
pew_sound = pygame.mixer.Sound("pew.wav")
cackle_sound = pygame.mixer.Sound("cackle.wav")
meow_sound = pygame.mixer.Sound("meow.wav")
howl_sound = pygame.mixer.Sound("howl.wav")
howl_sound.set_volume(0.05)

volume = 0
pygame.mixer.music.set_volume(volume) #sets the volumn

fps = 30 #the game's frames per second

width = 1024
height = 576

ACC = 3     #constants used for the game's physics 
gravity = 0.7
FRICTION = 1

replay_mode = False
wr_mode = False
downloading = False
sending = False

FONT = pygame.font.Font(None, 32) #fonts used in the game

username = None #user's username for multiplayer

lobby1 = []
lobby1r = []
lobby1ready="0" 

lobby1done = False

lobby1alpha = [120,120,120,120] #for multiplayer stores the opaqueness for each player

connected = False #if connected to the server is True
game_info = [[-100,-100,"s"],[-100,-100,"s"],[-100,-100,"s"],[-100,-100,"s"]] #coordinates for each player in multiplayer
spawnpoint = None
yourplayer = None #used to send control coordinates sent to the server

records = [["--","--","--","--","--","--","--"],["--","--","--","--","--","--","--"]] #records for singleplayer
#these are requested by the server when the user goes onto the leaderboards

yoursalt = None #salting to send password securely

standings = []
rankchange = [] #display information to users in multiplayer
scores = []

ip = "10.35.52.44" #default ip, but can be changed



def send_to_server(data): #sends data to the server
    client.send((data + "`").encode()) #adds the ` to show it is the end of the string and encodes the data

def udp_send_to_server(data): #sends data to the server using udp, which is much faster but less accurate than tcp
    udp_client.send((data + "`").encode())
    
def seperate_data(data): #this function is used to seperate data recieved by the server by using end bits
    datas = [] #seperates each piece of data into seperate elements of a list
    
    done = False
    i = 0
    while not done:
        try:            
            if data[i] == "`": #the ` key represents the end of a bit
                datas.append(data[:i])
                data = data[i + 1:]
                i = 0
                
            else:
                i += 1
                    
        except:
            return datas


"""
The below procedure is used to listen for data from the server. As the client must always be listening for data from
the server once connected to the server, this must be run in a seperate thread. This allows this procedure and the
game to run concurrently. As this is run in a seperate thread and must stay on constanly, to allow communication
between here and the rest of the code, global variables has to be used.

The procedure works by taking the data recieved by the server, using the seperate_data function to seperate it, then
detects what the data was sent to do. To distinguish this, ALL data comes with an 8 character prefix, such as STANDING
This allows the client to handle the data correctly. I also kept the prefixes in all caps to make them more readable.
"""

def receive(client,addr):
    global connected
    global position
    global user
    global passw
    global username
    global lobby1
    global lobby1r
    global lobby1ready
    global lobby1done
    global setup
    global yourplayer
    global records
    global downloading
    global sending
    global scores
    global yoursalt
    global standings
    global rankchange
    global spawnpoint
    global lobby1alpha
    global datas
    global enemies
    
    try: #this is kept in a try except so the program disconnects from the server rather than giving an error.
        
        
        while True: #used to make code run indefinately
            
            datas = client.recv(1024) #recieve and decode data from the server
            datas = datas.decode()
            
            datas_list = seperate_data(datas)
            
            for datas in datas_list: #runs through the seperated data
                
                if datas != "" and datas[:8] != "REPLAY1-" and datas[:8] != "DC?-----": 
                    print("Data:",datas) 

                #if statements are used above to stop the printing of some data. The data that is filtered out is
                #is either not needed such as "", or is too excessive to print to console.

                if datas[:8] == "STANDING":
                    standings.append(datas[8:]) #get standings in multiplayer

                elif datas[:8] == "DONE----": #user can leave the lobby, and display results
                    rankchange.append(datas[8:])
                    
                

                
                elif datas[:8] == "YOURSALT": #salting for password
                    yoursalt = datas[8:]

                elif datas[:8] == "ALPHA---": #recieves a player's new alpha channel value
                    lobby1alpha[int(datas[8:])] = 120
                    



                elif datas[:8] == "LASTALIV":   #checks this person is still connected and is the last person alive
                    client.send(("FINISH1-F`").encode()) #tells the server you are the only player still connected
                    #the server will then award this user first place in the game
                    

                elif datas[:8] == "SCORES--":
                    scores.append(datas[8:]) #adds the new scores

                elif datas[:8] == "WIPESCOR": #blanks the scores list so new scores can be added
                    scores = []
                        
                
                elif datas[:8] == "LOGIN---":
                    if datas[8:] == "YES":
                        position = "multiplayer2" #moves them to the next screen
                        username = user.data #creates a variable for the username if they are successful
                    else:
                        position = "multiplayer_failure"
                        user.data = "" #reset text boxes
                        user.text = "Username: "
                        user.reset()
                        passw.data = ""
                        passw.text = "Password: "
                        passw.reset()

                elif datas[:8] == "WREPLAY-": #tells the server client is about to send a world record
                    print("Sending new world record for level",datas[8:9])
                    sending = True
                    new_wr = show_replay("replay" + str(datas[8:9]) + ".txt") #gets the data from the text file
                    for i in range(len(new_wr)):
                        if i % 10 == 0: #without this % 10, data was transmitted inaccurately due to the large amounts
                            #of data being sent. This slows it down in a little bit.
                            time.sleep(0.03)
                        client.send(("WEPLAY1" + "-" + new_wr[i] + "`").encode())

                    client.send(("WEPLAY" + str(datas[8:9]) + "F" + "`").encode()) #tells the server the record is done
                    sending = False



                elif datas[:8] == "REQUESTU": #receives a username of a time
                    index = int(datas[8:9]) - 1
                    username = datas[9:]
                    records[0][index] = username

                elif datas[:8] == "REQUESTT": #receives a time
                    index = int(datas[8:9]) - 1
                    record_time = datas[9:]
                    records[1][index] = record_time

                elif datas[:8] == "REPLAY1-":
                    if "replay1" in locals():
                        add = datas[8:]
                        replay1.append(add[:-1])
                    else:
                        replay1 = []
                        add = datas[8:]
                        replay1.append(add[:-1]) #allows the user to recieve a replay
                        

                elif datas[:7] == "REPLAYF":
                    write_replay(replay1,"wr_replay"+str(datas[7:8])+".txt")
                    downloading = False
                    replay1 = [] #tells the client the server has finished sending the record

                    
                        
                elif datas[:8] == "LOBBY1M-":
                    lobby1.append(datas[8:])
                    print("Lobby 1 users:",lobby1)
                    
                elif datas[:8] == "LOBBY1MR":
                    lobby1r.append(datas[8:])
                    print("Lobby 1 ratings:",lobby1r) #gets the usernames and record to display in the lobby
                    
                elif datas[:8] == "READY1--": #ready up count for the lobby has increased
                    lobby1ready = datas[8:]

                elif datas[:8] == "CHECKREA": #confirms the ready up has been registered
                    lobby1done = True

                    
                elif datas[:8] == "WIPE1---": #clears the lobby
                    lobby1 = []
                    lobby1r = []
                    
                elif datas[:8] == "START1--": #starts the level
                    lobby1ready = "0"
                    if game_type == "level1m":
                        position = "level1m" #take the user into the game

                        
                    elif game_type == "wizardwars":
                        spawnpoint = datas[8:]
                        print("your spawnpoint is",spawnpoint) #this game point requires each player
                        position = "wizardwars" #to have a unique spawnpoint

                        
                    lobby1done = False #resets this for next time the user is in a lobby
                    setup = True #tells client to set up the level.
                    
                elif datas[:8] == "YOURNUM-": #server gives each client a number to control 
                    yourplayer = datas[8:9] #updating each player's coordinates
                    print(yourplayer)
     

                elif datas[:8] == "POS1K---": #server tells the client that an enemy has been killed
                    
                    count = 0
                    enemy = [e1,e2,e3,e4,e5,e6,e7,e8,e9,e10]
                    enemynames = ["e1 ","e2 ","e3 ","e4 ","e5 ","e6 ","e7 ","e8 ","e9 ","e10"]
                    for i in enemy:
                        if enemynames[count] == datas[8:11]:
                            i.alive = False #kills that enemy
                            print("client has killed",i.ids)
                            i.kill() #removes it from the list
                        count += 1
            
    except Exception as e:
        print(e)
        connected = False #shows the connection has dropped


def receive_udp(udp_client,addr):
    global game_info
    global enemies
    print("udp started")
    while True:
        data = udp_client.recv(1024) #gets udp data
        data = data.decode()
        data_list = seperate_data(data)
        for data in data_list:

            if data[:8] == "POS11---":
                game_info = []
                for i in range(4):
                    temp = []
                    temp.append(int(data[i * 10 + 8 : i * 10 + 13 ])) #players x coordinate
                    temp.append(int(data[i * 10 + 13 : i * 10 + 17 ])) #players y coordinate
                    temp.append(data[i * 10 + 17 : i * 10 + 18 ]) #players direction
                    game_info.append(temp)

            elif data != "":
                print(data) #don't output data if there is no data

            try:

                if data[:8] == "SHOOT---": #when another player shoots, the image must be remade on this screen
                    if data[17:18] == "l": #direction of fire
                        direction = "left"
                        start_x = - int(data[8:13]) + play.pos.x + play.totaldistance - 80 #start placement of the
                        #projectile. the + or - 80 is used to stop the player killing themself when shooting
                        #this is done by making the projectile appear infront of the player, rather than inside them
                    else:
                        direction = "right"
                        start_x = - int(data[8:13]) + play.pos.x + play.totaldistance + 80
                    newprojectile = projectile(start_x,int(data[13:17]),10,direction,"lightening","sideways")
                    #creates the projectile
            except Exception as e:
                print("shoot error",e)

def connect_to_server(): #allows the user to connect to the game server
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates the socket
        
        udp_client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        my_ip = socket.gethostbyname(socket.gethostname())
        global ip
        ip = new_ip.text[10:] #get ip address from text box
        port = 7777
        udp_port = 8888
        client.connect((ip,port)) #connects to the server with the ip and port
        udp_client.connect((ip,udp_port))
        addr = (ip,port) #saves the connection details
        upd_addr = (ip,udp_port)
        print("Connected to server")
        _thread.start_new_thread(receive,(client,addr)) #start tcp and udp threads
        _thread.start_new_thread(receive_udp,(udp_client,addr))
        return udp_client,client,addr,True

    except Exception as e: #connection failed
        print("Not connected to server",e)
        connected = False
        return None,None,None,False
    

def get_time(level):
    f=open('times.txt')
    lines=f.readlines()
    f.close()
    time = lines[level - 1]
    return round(float(time[:-1]),2) #gets the time to 2 decimal places

def write_time(time,level): 
    f=open('times.txt','r+') #opens text document
    lines = f.readlines()
    lines[level - 1] = str(time) + "\n"
    f.seek(0)
    f.truncate() #clears that line
    f.writelines(lines)    #adds the new time
    f.close()    
          
def save(data): #saves the players level to a text document
    f=open("progress.txt",'r+')
    f.truncate(0) #removes current contents
    f.write(str(data))
    f.close()

def write_replay(recording,file): #writes the replay to the file
    f=open(file,'w')
    f.seek(0)
    f.truncate()     
    for item in recording:
      f.write(str(item)+"\n")
    f.close()

    
def show_replay(file): #gets the replay and puts it in an array.
    f=open(file)
    lines=f.readlines()
    return lines


def record_or_play_replay(replay,play,movement,ghost):
    if replay != False and not ghost:
        play.pos.y = replay[1]
        play.move_screen_in_replay_mode(replay[0]) #this will move the screen the given amount
        play.photo = replay[2]
        play.photo = play.photo[:-1] #these just remove the new line
        play.state = replay[3]
        play.state = play.state[:-1]
        play.fired = replay[4]
        play.fired = play.fired[:-1]
        if play.fired == "True": #fire the wand
            pew_sound.play()
            if play.photo == "r" or play.photo == "R":
                play.direct = "right"
            elif play.photo == "l" or play.photo == "L":
                play.direct = "left" #gets the direction so the wand fires in the right direction.
                
            hits = pygame.sprite.spritecollide(play,platforms, False)
            if hits: #gives immunity to projectile if player is standing next to a platform
                play.projectiles.append(friendly_projectile(width/2 - 8,play.pos.y-20,play.direct,2))
            else:
                play.projectiles.append(friendly_projectile(width/2 - 8,play.pos.y-20,play.direct,0))

        elif play.photo != "s":
            if play.photo == "r" or play.photo == "R":
                play.direct = "right"
            elif play.photo == "l" or play.photo == "L":
                play.direct = "left"
                            
        play.replay_set_image() #this will change the player's image
        play.rect.midbottom = play.pos #moves player's hitbox
        
    else:
        recording.append(movement) #records for the replay
        recording.append(play.pos.y)
        recording.append(play.photo)
        recording.append(play.state)
        recording.append(play.fired)
        if ghost and not ghost_player.done:
            ghost_player.pos.y = replay[1] - 32 #as this the coordinate is taken from the bottom,but this is the top
            ghost_player.pos.x -= (replay[0]- movement) #change in x minus how much the player currently playing moved
            ghost_player.photo = replay[2]
            ghost_player.photo = ghost_player.photo[:-1]
            ghost_player.state = replay[3]
            ghost_player.state = ghost_player.state[:-1]
            ghost_player.display_ghost()
            
            
class ghost():
    def __init__(self):
        self.basic_fr1 = pygame.image.load(os.path.join(img_folder,"avt1_fr1.gif")).convert()
        self.basic_rt1 = pygame.image.load(os.path.join(img_folder,"avt1_rt1.png")).convert()
        self.basic_rt2 = pygame.image.load(os.path.join(img_folder,"avt1_rt2.png")).convert()
        self.basic_lf1 = pygame.image.load(os.path.join(img_folder,"avt1_lf1.png")).convert()
        self.basic_lf2 = pygame.image.load(os.path.join(img_folder,"avt1_lf2.png")).convert()
        self.basic_bk2 = pygame.image.load(os.path.join(img_folder,"avt1_bk2.gif")).convert()#store images as variables so they dont need to be loaded every time
        self.basic_bk1 = pygame.image.load(os.path.join(img_folder,"avt1_bk1.gif")).convert()
        self.wiz_fr1 = pygame.image.load(os.path.join(img_folder,"smr1_fr1.gif")).convert()
        self.wiz_rt1 = pygame.image.load(os.path.join(img_folder,"smr1_rt1.png")).convert()
        self.wiz_rt2 = pygame.image.load(os.path.join(img_folder,"smr1_rt2.png")).convert()
        self.wiz_lf1 = pygame.image.load(os.path.join(img_folder,"smr1_lf1.png")).convert()
        self.wiz_lf2 = pygame.image.load(os.path.join(img_folder,"smr1_lf2.png")).convert()        
        self.image = self.basic_fr1            #the image 
        self.image.set_colorkey(white)
        self.pos = vec(width / 2, height / 2)
        self.state = "basic"
        self.photo = "s"
        self.done = False

    def display_ghost(self): #blits the ghost the user races against onto the screen
        if self.photo == "s": #uses the correct photo and state for the player, as stored by the replay
            if self.state == "basic":
                self.image = self.basic_fr1
            else:
                self.image = self.wiz_fr1     

        if self.photo == "r":
            if self.state == "basic":
                self.image = self.basic_rt1
            else:
                self.image = self.wiz_rt1

        if self.photo == "R":
            if self.state == "basic":
                self.image = self.basic_rt2
            else:
                self.image = self.wiz_rt2

        if self.photo == "l":
            if self.state == "basic":
                self.image = self.basic_lf1
            else:
                self.image = self.wiz_lf1

        if self.photo == "L":
            if self.state == "basic":
                self.image = self.basic_lf2
            else:
                self.image = self.wiz_lf2
                
        if self.photo == "b":
            self.image = self.basic_bk2

        if self.photo == "B":
            self.image = self.basic_bk1
                
        self.image.set_colorkey(white)
        self.image.set_alpha(128) #opacity so the user can which player is which
        screen.blit(self.image, (self.pos.x - 16, self.pos.y))

    
class platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h,image,keycolor = black):
        pygame.sprite.Sprite.__init__(self)
        self.image = image #sets the platform's image
        if keycolor == white:
            self.image.set_colorkey(white) #removes background colour
        else:
            self.image.set_colorkey(black)
            
        self.image = pygame.transform.scale(self.image, (w, h)) #changes to the desired size        
        self.rect = self.image.get_rect() #gets hitbox
        self.rect.x = x
        self.rect.y = y #platform coordinates
        
        self.timer = 0
        self.movedirect = "right"
        self.distmoved = 0
        
    def sidemove(self,movement,speed,group): #maximum move distance, speed, what group the platform is in

        if self.movedirect == "right":
            self.rect.x += speed #moves the platform right
            self.distmoved += speed
            if self.distmoved >= movement: #finds if the platform need to start moving the other way
                self.movedirect = "left" 
            if not play.replay:
                hit = pygame.sprite.spritecollide(play, group, False) #checks if the player hits this platform
                if hit:
                    play.move_everything_but_player(-speed) #moves the player
                    play.totaldistance -= speed
        else:
            self.rect.x -= speed #same as above but in the other direction
            self.distmoved -= speed
            if self.distmoved <= 0:
                self.movedirect = "right"
            if not play.replay:
                hit = pygame.sprite.spritecollide(play, group, False)
                if hit:
                    play.move_everything_but_player(speed)
                    play.totaldistance += speed
            

    def upmove(self,movement,speed,group):
        maxtime = int(movement/speed) #time moving in one direction
        if self.timer > int(maxtime/2):
            self.rect.y -= speed*2 #moves upwards

        if self.timer > maxtime: #resets the timer
            self.timer = 0
            
        self.rect.y += speed #moves downwards
        self.timer += 1 

class ladder(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load(os.path.join(img_folder,"ladder.png")).convert() #prepares image
        self.image = pygame.transform.scale(self.image, (64, 64))   
        self.image.set_colorkey(white)
        
        self.rect = self.image.get_rect() #defines hitbox
        self.rect.x = x #ladder coordinates
        self.rect.y = y


        

class enemy(pygame.sprite.Sprite): #inherits from pygame sprite class
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()#gets hitbox
        self.vel = vec(0,0)
        self.acc = vec(0,0) #motion
        self.alive = True

        
        self.timer = 0
        self.jumptimer = 1 #allows enemies to do things periodically
        
        self.movedirect = "right"
        self.distmoved = 0
        self.movedirect2 = "down"
        self.distmoved2 = 0        
        self.respawning = False
        
        self.random_numbers = [312,-116,97,-96,89,-245,167,-23,-300,-120,120,-289]        
        self.random_numbers2 = [-50,300,13,150,-150,-108,-275,56]
        self.random_numbers3 = [-205,201,86,215,-119,-305,201,104,-43,229,-31,28,-159,-96]
        #these allow game to feel random, but actually be the same
        
        
        self.target_change = 0
        self.target = 0
        self.currenttarget = 0
        self.killable = True
        self.obey_gravity = True
        

    def follow(self,cackle = True,random_number_set = 1,number_swap = 90): #enemy follows the player changing the distance to the player
        if cackle:                              
            x = random.randint(0,300)           #number swap gives the amount of time the position changes after.
            if x == 1:
                cackle_sound.play() #plays the cackle sound as this is used for witches

        if random_number_set == 1:
            random_number_set = self.random_numbers #selects what random numbers to use
        elif random_number_set == 2:
            random_number_set = self.random_numbers2
        else:
            random_number_set = self.random_numbers3
                
        if self.target_change == 0: #changes the target location after the set time
            self.currenttarget = play.pos.x + 300 + random_number_set[self.target]
            
        if self.target_change > number_swap: #times when the target should be changed
            self.target += 1
            if self.target >= len(random_number_set):
                self.target = 0 #starts from the beggining of the list of numbers
                
            self.currenttarget = play.pos.x + 300 + random_number_set[self.target]
            self.target_change = 1
            
        if abs(self.pos.x-self.currenttarget) > 30: #the further from the target, the faster it moves
            
            if self.pos.x < self.currenttarget:
                self.pos.x += 10
            else:
                self.pos.x -= 10

        elif abs(self.pos.x-self.currenttarget) > 15:
            if self.pos.x < self.currenttarget:
                self.pos.x += 4
            else:

                self.pos.x -= 4
                
        elif abs(self.pos.x-self.currenttarget) > 5:
            if self.pos.x < self.currenttarget:
                self.pos.x += 2
            else:

                self.pos.x -= 2
                
        self.target_change += 1

                



    def moveh(self,speed,distance,speed_variation = None): #this method allows enemeies to walk backwards and forwards.
        if self.alive:
            if speed_variation != None:            
                speed = self.variate_speed(speed_variation,speed)
            if self.movedirect == "right":  #This is in the enemy class so all enemies can use the class, using inheritance 
                self.pos.x += speed
                self.distmoved += speed #moves the enemy
                if self.distmoved >= distance:
                    self.movedirect = "left" #changes the direction the enemy is moving in
                    self.image = pygame.transform.flip(self.image, True, False)
            else:
                self.pos.x -= speed
                self.distmoved -= speed
                if self.distmoved <= 0:
                    self.movedirect = "right"
                    self.image = pygame.transform.flip(self.image, True, False)

    def variate_speed(self,speed_variation,speed): #speed variation changes how much the variaion is.
        
        if not hasattr(self, 'timer2'): #checks if the attribute has already been defined
            self.timer1 = 0
            self.timer2 = 0

        self.timer2 += 1    #times when the speed should be changed
        if self.timer2 >= 100:
            self.timer1 += 1
            self.timer2 = 0
        if self.timer1 > len(self.random_numbers) - 1:
            self.timer1 = 0
        return speed + self.random_numbers[self.timer1] * speed_variation #changes the speed
            
            



    def fly_up_down(self,speed,distance): 
        if self.movedirect2 == "up":
            self.pos.y += speed #changes the enemies y coordinate
            self.distmoved2 += speed
            if self.distmoved2 >= distance:
                self.movedirect2 = "down" #changes the direciton
        else: #same for other direction
            self.pos.y -= speed
            self.distmoved2 -= speed
            if self.distmoved2 <= 0:
                self.movedirect2 = "up"   

        
    def jump(self,jumpheight,maxtime,sound = None):
        if self.alive:
            if self.jumptimer == maxtime: 
                self.vel.y = jumpheight
                self.jumptimer = 0 #resets the timer
                
                if sound == "cat" and abs(self.pos.x - play.pos.x) < 720 and self.alive:
                    meow_sound.play() #plays sound
                
            self.jumptimer += 1#times when the jump should happen

    def update(self):
        if self.alive: #only does calculations if alive
            check_if_on_platform(self)
            if self.obey_gravity:
                self.acc.y = gravity
            self.vel.y += self.acc.y
            self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.rect.midbottom = (self.pos.x,self.pos.y) #the physics for enemy movement
        
    def show_hitbox(self): #allows hitboxes to be visible for testing
        screen.fill(blue, self.rect)



     
class bug(enemy): #class for a flying enemy. 
    def __init__(self,spawnx,spawny,img = None):
        if img == None:
            self.image = enemysprites.get_image(9,51, 38, 36)
            self.image.set_colorkey(black)
        if img == "bat":
            self.image = pygame.image.load(os.path.join(img_folder,"bat.png")).convert()
            self.image.set_colorkey(black)            
        super(bug,self).__init__() #inherits from enemy class
        self.pos = vec(spawnx,spawny)
        self.rect.center = (self.pos.x,self.pos.y)
        self.obey_gravity = False

class forest_enemy(enemy): #class for a respawning enemy. The only one currently being used is the forest enemy
    def __init__(self,spawnx,spawny,img = None):
        
        self.image = enemysprites2.get_image(13,297,45,52) #preapres image
        self.image.set_colorkey((0,128,0))

        if img == "jungle": #alternative image
            self.image = enemysprites.get_image(56,6, 25, 30)
            self.image.set_colorkey(black)
            self.image = pygame.transform.scale(self.image, (50, 60))
            
        super(forest_enemy,self).__init__() #inherits enemy
        self.pos = vec(spawnx,spawny)
        self.rect.center = (self.pos.x,self.pos.y)
        
        self.position = 0 #what position the enemy is in of the list
        self.respawning = True

        self.cooldown = 0


    def respawn(self,arr):
        if self.cooldown > 0: #stop the enemy skipping positions
            self.cooldown -= 1
        #example array,  arr = [-310,-100, -120,-100, 220,-50, 210,250]
        if not self.alive and self.cooldown == 0:
            self.cooldown = 5 
            self.alive = True
            
            self.pos.x += arr[self.position] #this is a procedure which allows monsters
            self.pos.y += arr[self.position+1] #to loop through a set of locations

            self.position += 2
            if self.position == len(arr): #resets index
                self.position = 0
                

class mage(enemy): #name of this enemy type
    def __init__(self,spawnx,spawny,ids = None,newimage = None,obey_gravity = True):
        if newimage == "angel":
            self.image = enemysprites2.get_image(91,190,67,117) #image 1
            self.image.set_colorkey((0,128,0))
        elif newimage == "witch":
            self.image = pygame.image.load(os.path.join(img_folder,"witch_run.gif")).convert()
            self.image.set_colorkey(white) #image 2
        else:
            self.image = pygame.image.load(os.path.join(img_folder,"mage.png")).convert()
            self.image.set_colorkey(white) #image 3
            self.image = pygame.transform.scale(self.image, (48, 48))

        self.rightface = self.image #images for facing both directions
        self.leftface = pygame.transform.flip(self.image, True, False)
        super(mage,self).__init__() #inherits from enemy class
        
        self.pos = vec(spawnx,spawny) #coordinates and hitbox
        self.rect.center = (self.pos.x,self.pos.y)

        
        self.obey_gravity = obey_gravity
        self.cooldowns = 0
        self.direct = "right"
        self.projectiles2 = []
        self.ids = ids

        
    def mageupdate(self): #makes the mage face the player
        if self.pos.x < play.pos.x:
            self.image = self.rightface #gives the image facing the right way
            self.direct = "right"
        else:

            self.image = self.leftface
            self.direct = "left"
            
    def shoot(self,speed,fire_rate,imgs = None,path = "sideways"): #bigger fire rate, means firing slower
        if self.alive:
            if self.cooldowns == 0: #times when they fire
                self.projectiles2.append(projectile(self.pos.x,self.pos.y - 30,speed,self.direct, img = imgs,paths = path))
            elif self.cooldowns >= fire_rate:
                self.cooldowns = -1 #resets the cooldown, causing the mage to fire
            self.cooldowns += 1 #times the firing
        

        
class turtle(enemy): #name of this enemy type
    def __init__(self,spawnx,spawny,ids = None,img = None,killable = True):
        if img == None:
            self.image = enemysprites.get_image(15,198, 42, 22) #prepares necessary image
            self.image = pygame.transform.scale(self.image, (63, 33))
            self.image.set_colorkey(black)
        elif img == "cat":
            self.image = catsprites.get_image(4,104, 22, 18)
            self.image.set_colorkey(black)            
            self.image = pygame.transform.scale(self.image, (48, 39))
            self.image = pygame.transform.flip(self.image, True, False)
        elif img == "lava":
            self.image = pygame.image.load(os.path.join(img_folder,"lava.png")).convert()
            self.image = pygame.transform.scale(self.image, (150, 50))
            self.image.set_colorkey(white)

                    
        super(turtle,self).__init__() #inherits from enemy class
        self.pos = vec(spawnx,spawny)
        self.rect.center = (self.pos.x,self.pos.y)
        self.obey_gravity = True
        self.ids = ids
        self.killable = killable

        if img == "lava": #makes lava unkillable and not obey gravity
            self.obey_gravity = False #used for lava tiles on level 6

class dragon(enemy): #boss in level 7 (final level)
    def __init__(self):
        self.image = dragon_sprites.get_image(6451,1351,140,140) #default dragon state
        self.image.set_colorkey(black)
        super(dragon,self).__init__() #inherits
        self.obey_gravity = False
        self.killable = False #doesn't follow normal dying rules, so this is set to false
        self.projectiles2 = [] #projectiles fired by dragon

        self.direction = "right" #direction the dragon is flying in
        self.state = "fly" #what the dragon is doing
        
        self.pos = vec(300,250) #default position
        self.rect.center = (self.pos.x,self.pos.y)
        self.rect = self.image.get_rect(center = self.pos)
        self.fly1 = dragon_sprites.get_image(6430,1311,160,170)
        self.fly2 = dragon_sprites.get_image(6685,1311,160,170)
        self.fly3 = dragon_sprites.get_image(6940,1311,160,170)
        self.fly4 = dragon_sprites.get_image(7195,1311,160,170)
        self.fly5 = dragon_sprites.get_image(7450,1311,160,170) #images for the dragon
        self.fly6 = dragon_sprites.get_image(7705,1311,160,170)
        self.fly7 = dragon_sprites.get_image(7960,1311,160,170)
        self.fly8 = dragon_sprites.get_image(8215,1311,160,170)
        self.fly9 = dragon_sprites.get_image(12326,1350,200,170)
        self.fly10 = dragon_sprites.get_image(12581,1350,200,170)
        
        self.lives = 10 #uses lives instead of dying methods

        
        self.rect.inflate(-500,-1000) #changes hitbox to be more accurate
        

        self.timer = 0 #times what the dragon should be doing
        self.swoop = False
        self.animation_timer = 0  #allows dragon to be animated      
        self.total_distance = 0
        self.firemode = 0 #allows different fire patterns
        
        self.fired = False

        self.title = 1
        
        self.explode_timer = 0 #used for the exploding fireball
        
        self.explode_placement_x = 0
        self.explode_placement_y = 0


    def choose_state(self):
        if e1.alive:
            if self.explode_timer != 0:
                self.explode_timer -= 1
                if self.explode_timer == 1: #this used for one of the dragon's final abilities, where a fireball explodes.
                    self.explode_placement_x = self.projectiles2[self.explode_position].posx
                    self.projectiles2[self.explode_position].kill()
                    all_sprites.remove(self.projectiles2[self.explode_position]) #removes itself after exploding
                    
                    self.fire(0,10,0,"fire",determined = True)
                    self.fire(2.59,9.66,15,"fire",determined = True)
                    self.fire(5,8.66,30,"fire",determined = True)
                    self.fire(7.07,7.07,45,"fire",determined = True) #bottom right quandrant
                    self.fire(8.66,5,60,"fire",determined = True)
                    self.fire(9.66,2.59,75,"fire",determined = True)
                    self.fire(10,0,90,"fire",determined = True)

                    self.fire(0,-10,180,"fire",determined = True)
                    self.fire(2.59,-9.66,165,"fire",determined = True)
                    self.fire(5,-8.66,150,"fire",determined = True)
                    self.fire(7.07,-7.07,135,"fire",determined = True) #top right quandrant
                    self.fire(8.66,-5,120,"fire",determined = True)
                    self.fire(9.66,-2.59,105,"fire",determined = True)

                    self.fire(-2.59,9.66,345,"fire",determined = True) #bottom left quandrant
                    self.fire(-5,8.66,330,"fire",determined = True)
                    self.fire(-7.07,7.07,315,"fire",determined = True)
                    self.fire(-8.66,5,300,"fire",determined = True)
                    self.fire(-9.66,2.59,285,"fire",determined = True)
                    self.fire(-10,0,270,"fire",determined = True)

                    self.fire(-2.59,-9.66,195,"fire",determined = True) #top left quandrant
                    self.fire(-5,-8.66,210,"fire",determined = True)
                    self.fire(-7.07,-7.07,225,"fire",determined = True)
                    self.fire(-8.66,-5,240,"fire",determined = True)
                    self.fire(-9.66,-2.59,255,"fire",determined = True)
                    
            if self.state == "fly":
                self.fly()

            elif self.state == "turn":
                self.turn()

            self.timer += 1  #times when the dragon should swoop.

            if self.swoop:
                if self.timer < 40:         #causes the dragon to swoop down
                    self.pos.y += int((40 - self.timer)/2)
                elif self.timer < 80:
                    self.pos.y -= int(((self.timer - 40))/2)  #spends half of the time going up and half going down.
        else:
            self.pos.y += 5


    def fire(self,x,y,angle,img,determined = False): #fires the projectile based on diretion
        if not determined:
            if self.direction == "right": #seperate directions are used to spawn the projectile from the head of the dragon
                self.projectiles2.append(projectile(self.pos.x + 80,self.pos.y - 50,0,0,img,None,custom = [x,y,angle]))
            else:
                self.projectiles2.append(projectile(self.pos.x - 20,self.pos.y - 50,0,0,img,None,custom = [x,y,angle]))

            if img == "fire2":
                self.explode_position = len(self.projectiles2) - 1 #finds the position of the exploding fireball in the list
                                                                    #so the fireball can be removed when it explodes
        else:
            self.projectiles2.append(projectile(self.explode_placement_x,self.explode_placement_y,0,0,img,None,custom = [x,y,angle]))

            
    def next_stage(self): #makes the dragon follow the player
        prev = self.direction
        if self.pos.x > play.pos.x + 250:
            self.direction = "left"
        elif self.pos.x < play.pos.x - 250:
            self.direction = "right"
        if self.direction != prev:   #finds when the dragon needs to turn
            self.state = "turn"

    def fly(self):            
        if self.animation_timer < 3:
            self.image = self.fly1
        elif self.animation_timer < 7:
            self.image = self.fly2
        elif self.animation_timer< 11:
            self.image = self.fly3
        elif self.animation_timer < 15:
            self.image = self.fly4 #fire here as this frame lights up the dragon's mouth
            
            if not self.fired:
                
                self.fired = True
                self.firemode += 1 #firemode allows different shots at different times. It cycles through 10 types
                if self.firemode > 10:
                    self.firemode = 0
                    
                if self.total_distance < 1500: #what is fired is based on distance
                    if self.firemode == 1 or self.firemode == 4 or self.firemode == 5 or self.firemode == 7 or self.firemode == 9:
                            self.fire(5,5,45,"fire")
                            self.fire(-3,3,315,"fire")
                            if self.total_distance > 700: #more based on distance
                                self.fire(0,7,0,"fire")
                            if self.total_distance > 1000:
                                self.fire(7,7,45,"fire")
                    if self.firemode == 0 or self.firemode == 2 or self.firemode == 3 or self.firemode == 6 or self.firemode == 8:
                            self.fire(2,8,14,"fire")
                            self.fire(-2,8,346,"fire")
                            if self.total_distance > 700:
                                self.fire(0,7,0,"fire")
                            if self.total_distance > 1000:

                                self.fire(-10,3,287,"fire")

                    if self.firemode == 10:  #firemode determines what is fired
                            self.fire(12,12,45,"fire")
                            self.fire(-12,12,315,"fire")
                            self.fire(0,5,0,"fire")
                            if self.total_distance > 700:
                                self.fire(3,7,23,"fire")
                            if self.total_distance > 1000:
                                self.fire(-3,7,337,"fire")

                elif self.total_distance < 3000: #what the dragon fires changes based on distance travelled
                    if self.firemode == 1 or self.firemode == 4 or self.firemode == 5 or self.firemode == 7 or self.firemode == 9:
                            self.fire(5,3,30,"fire1")
                            self.fire(-5,3,330,"fire1")
                            if self.total_distance > 2200:
                                self.fire(0,7,0,"fire1") #these are all just the different fireballs being released
                            if self.total_distance > 2500:
                                self.fire(7,7,45,"fire1")
                                self.fire(-7,7,315,"fire1")
                    if self.firemode == 0 or self.firemode == 2 or self.firemode == 3 or self.firemode == 6 or self.firemode == 8:
                            self.fire(7,10,10,"fire1")
                            self.fire(-7,10,350,"fire1")
                            if self.total_distance > 2200:
                                self.fire(0,7,0,"fire1")
                            if self.total_distance > 2500:
                                self.fire(10,3,73,"fire1")
                                self.fire(-10,3,287,"fire1")

                    if self.firemode == 10:
                            self.fire(13,13,45,"fire1")
                            self.fire(0,6,0,"fire1")
                            if self.total_distance > 2200:
                                self.fire(3,7,23,"fire1")
                            if self.total_distance > 2500:
                                self.fire(4,16,14,"fire1")

                elif self.total_distance < 4500:
                    if self.firemode == 1 or self.firemode == 4 or self.firemode == 5 or self.firemode == 7 or self.firemode == 9:
                            self.fire(5,3,30,"fire1")
                            self.fire(-5,3,330,"fire1")
                            self.fire(-7,10,350,"fire")
                            if self.total_distance > 3700:
                                self.fire(0,7,0,"fire1")
                            if self.total_distance > 4000:
                                self.fire(7,7,45,"fire1")
                                self.fire(-7,7,315,"fire1")
                    if self.firemode == 0 or self.firemode == 2 or self.firemode == 3 or self.firemode == 6 or self.firemode == 8:
                            self.fire(7,10,10,"fire1")
                            self.fire(-7,10,350,"fire1")
                            self.fire(5,3,30,"fire")
                            if self.total_distance > 3700:
                                self.fire(0,7,0,"fire1")
                            if self.total_distance > 4000:
                                self.fire(10,3,73,"fire1")
                                self.fire(-10,3,287,"fire1")

                    if self.firemode == 10:
                            self.fire(13,13,45,"fire1")
                            self.fire(-13,13,315,"fire1")
                            if self.total_distance > 3700:
                                self.fire(3,7,23,"fire1")
                            if self.total_distance > 4000:
                                self.fire(10,3,73,"fire1")
                                self.fire(-10,3,287,"fire1")

                elif self.lives > 7: #after a set distance, what the dragon fires is based on lives left
                    if self.firemode == 1 or self.firemode == 4 or self.firemode == 5 or self.firemode == 7 or self.firemode == 9:
                            self.fire(7,10,10,"fire")
                            self.fire(-7,10,350,"fire")
                            self.fire(0,7,0,"fire1")
                            self.fire(7,7,45,"fire1")
                    if self.firemode == 0 or self.firemode == 2 or self.firemode == 3 or self.firemode == 6 or self.firemode == 8:
                            self.fire(7,10,10,"fire1")
                            self.fire(-5,3,330,"fire")
                            self.fire(0,7,0,"fire1")
                            self.fire(-4,16,346,"fire1")

                    if self.firemode == 10: #fires in all directions
                        if self.lives < 8:
                            img = "fire1"
                        else:
                            img = "fire"
                            
                        self.fire(0,10,0,img)
                        self.fire(2.59,9.66,15,img)
                        self.fire(5,8.66,30,img)
                        self.fire(7.07,7.07,45,img) #right
                        self.fire(8.66,5,60,img)
                        self.fire(9.66,2.59,75,img)
                        self.fire(10,0,90,img)


                        self.fire(-2.59,9.66,345,img) #left
                        self.fire(-5,8.66,330,img)
                        self.fire(-7.07,7.07,315,img)
                        self.fire(-8.66,5,300,img)
                        self.fire(-9.66,2.59,285,img)
                        self.fire(-10,0,270,img)

                elif self.lives > 4:
                    if self.firemode == 1 or self.firemode == 4 or self.firemode == 5 or self.firemode == 7 or self.firemode == 9:
                            self.fire(10,6,30,"fire1")
                            self.fire(-10,6,330,"fire1")
                            if self.lives < 8:
                                self.fire(0,9,0,"fire1")
                            if self.lives < 6:
                                self.fire(9,9,45,"fire1")
                    if self.firemode == 0 or self.firemode == 2 or self.firemode == 3 or self.firemode == 6 or self.firemode == 8:
                            self.fire(7,10,10,"fire1")
                            self.fire(-7,10,350,"fire1")
                            if self.lives < 8:
                                self.fire(0,7,0,"fire1")
                            if self.lives < 6:
                                self.fire(-4,16,346,"fire1")

                    if self.firemode == 10: #exploding fireball
                        self.fire(0,4,0,"fire2")
                        self.explode_timer = 45
                        self.explode_placement_x = self.pos.x
                        self.explode_placement_y = self.pos.y + 180 #this is the position that the fireball will explode at.              

                else:
                    if self.firemode == 1 or self.firemode == 2 or self.firemode == 4 or self.firemode == 5 or self.firemode == 7 or self.firemode == 9:
                            self.fire(7,10,10,"fire")
                            self.fire(-7,10,350,"fire")
                            if self.lives < 7:
                                self.fire(0,9,0,"fire1")
                            if self.lives < 3:
                                self.fire(9,9,45,"fire1")
                    if self.firemode == 0 or self.firemode == 3 or self.firemode == 6 or self.firemode == 8:
                        if self.lives < 2:
                            img = "fire1"
                        else:
                            img = "fire"
                            
                        self.fire(0,10,0,img)
                        self.fire(2.59,9.66,15,img)
                        self.fire(5,8.66,30,img)
                        self.fire(7.07,7.07,45,img) #right
                        self.fire(8.66,5,60,img)
                        self.fire(9.66,2.59,75,img)
                        self.fire(10,0,90,img)


                        self.fire(-2.59,9.66,345,img) #left
                        self.fire(-5,8.66,330,img)
                        self.fire(-7.07,7.07,315,img)
                        self.fire(-8.66,5,300,img)
                        self.fire(-9.66,2.59,285,img)
                        self.fire(-10,0,270,img)

                    if self.firemode == 10: #exploding fireball
                        self.fire(0,4,0,"fire2")
                        self.explode_timer = 45
                        self.explode_placement_x = self.pos.x
                        self.explode_placement_y = self.pos.y + 180 #this is the position that the fireball will explode at.              
                        
          
        elif self.animation_timer < 18: #animates the dragon, continued from before the dragon fired
            self.fired = False
            self.image = self.fly5
        elif self.animation_timer < 22:
            self.image = self.fly6
        elif self.animation_timer < 26:
            self.image = self.fly7
        elif self.animation_timer < 30:
            self.image = self.fly8
        else:
            self.animation_timer = 0
            self.next_stage()

        if self.direction == "right": #moves the dragon
            if self.total_distance > 10000:
                self.pos.x += 16
                self.total_distance += 16
            else:
                self.pos.x += 12
                self.total_distance += 12
        else:
            if self.total_distance > 10000:
                self.pos.x -= 16
                self.total_distance -= 16
            else:
                self.pos.x -= 12
                self.total_distance -= 12
            self.image = pygame.transform.flip(self.image, True, False)
            
        self.animation_timer += 1 #increments the frame timer
        self.image.set_colorkey(black)
        
    def turn(self):
        if self.direction == "right":
            moving = 1
        else:
            moving = -1 #finds which direction the dragon is moving

        if self.animation_timer < 4:
            self.image = self.fly9   #frames for when the dragon turns around
            self.pos.x += 8 * moving   #movement while the dragon turns
            self.total_distance += 8 * moving
        elif self.animation_timer < 8:
            self.image = self.fly10
            self.pos.x += 6 * moving
            self.total_distance += 6 * moving

        else:
            self.animation_timer = 0 #resets the animation timer
            
            if self.timer > 150: #swoops down or stops stops swooping after this timer expires
                self.swoop = not self.swoop
                self.timer = 0 #resets the timer
                
            self.state = "fly"  #sets the state back to fly now the turn has finished

        if self.direction == "left":  #flips the image if the dragon is facing left
            self.image = pygame.transform.flip(self.image, True, False)
            
        self.animation_timer += 1
        self.image.set_colorkey(black) #removes background colour
            
class projectile(enemy):        
    def __init__(self,posx,posy,speed,direct,img,paths,custom = False): #custom takes a list. x pixels per frame, 
        if img == None:         #y pixels per frame and the angle of the projectile
            self.image = pygame.image.load(os.path.join(img_folder,"newfire.png")).convert()
            self.image.set_colorkey(black)
        if img == "lightening":
            self.image = pygame.image.load(os.path.join(img_folder,"magicbolt.gif")).convert()
            self.image.set_colorkey((61,61,61))   #preparing given image
            self.image = pygame.transform.rotate(self.image,-90)
            self.image = pygame.transform.scale(self.image, (64, 24))
        elif img == "meteor":
            self.image = pygame.image.load(os.path.join(img_folder,"firecircle.png")).convert()
            self.image.set_colorkey(black)
            self.image = pygame.transform.scale(self.image, (48,32))
        elif img == "fire":
            self.image = pygame.image.load(os.path.join(img_folder,"fire1_ 01.png")).convert()
            self.image.set_colorkey(black)
            self.fire1 = pygame.image.load(os.path.join(img_folder,"fire1_ 01.png")).convert()
            self.fire2 = pygame.image.load(os.path.join(img_folder,"fire1_ 02.png")).convert()
            self.fire3 = pygame.image.load(os.path.join(img_folder,"fire1_ 03.png")).convert()
            self.fire4 = pygame.image.load(os.path.join(img_folder,"fire1_ 04.png")).convert()
            self.fire5 = pygame.image.load(os.path.join(img_folder,"fire1_ 05.png")).convert()
            self.fire6 = pygame.image.load(os.path.join(img_folder,"fire1_ 06.png")).convert()
            self.fire7 = pygame.image.load(os.path.join(img_folder,"fire1_ 07.png")).convert()
            self.fire8 = pygame.image.load(os.path.join(img_folder,"fire1_ 08.png")).convert()
            self.fire9 = pygame.image.load(os.path.join(img_folder,"fire1_ 09.png")).convert() #differenet fireball images
            self.fire10 = pygame.image.load(os.path.join(img_folder,"fire1_ 10.png")).convert()
            self.fire11 = pygame.image.load(os.path.join(img_folder,"fire1_ 11.png")).convert()
            self.fire12 = pygame.image.load(os.path.join(img_folder,"fire1_ 12.png")).convert()
            self.fire13 = pygame.image.load(os.path.join(img_folder,"fire1_ 13.png")).convert()

            
        elif img == "fire1":
            self.image = pygame.image.load(os.path.join(img_folder,"fire2_ 01.png")).convert()
            self.image = pygame.transform.scale(self.image, (48, 48))
            self.image.set_colorkey(black)
            self.fire1 = pygame.image.load(os.path.join(img_folder,"fire2_ 01.png")).convert()
            self.fire2 = pygame.image.load(os.path.join(img_folder,"fire2_ 02.png")).convert()
            self.fire3 = pygame.image.load(os.path.join(img_folder,"fire2_ 03.png")).convert()
            self.fire4 = pygame.image.load(os.path.join(img_folder,"fire2_ 04.png")).convert()
            self.fire5 = pygame.image.load(os.path.join(img_folder,"fire2_ 05.png")).convert()
            self.fire6 = pygame.image.load(os.path.join(img_folder,"fire2_ 06.png")).convert()
            self.fire7 = pygame.image.load(os.path.join(img_folder,"fire2_ 07.png")).convert()
            self.fire8 = pygame.image.load(os.path.join(img_folder,"fire2_ 08.png")).convert()
            self.fire9 = pygame.image.load(os.path.join(img_folder,"fire2_ 09.png")).convert()
            self.fire10 = pygame.image.load(os.path.join(img_folder,"fire2_ 10.png")).convert()
            self.fire11 = pygame.image.load(os.path.join(img_folder,"fire2_ 11.png")).convert()
            self.fire12 = pygame.image.load(os.path.join(img_folder,"fire2_ 12.png")).convert()
            self.fire13 = pygame.image.load(os.path.join(img_folder,"fire2_ 13.png")).convert()
        elif img == "fire2":
            self.image = pygame.image.load(os.path.join(img_folder,"fire3_ 01.png")).convert()
            self.image.set_colorkey(black)
            self.fire1 = pygame.image.load(os.path.join(img_folder,"fire3_ 01.png")).convert()
            self.fire2 = pygame.image.load(os.path.join(img_folder,"fire3_ 02.png")).convert()
            self.fire3 = pygame.image.load(os.path.join(img_folder,"fire3_ 03.png")).convert()
            self.fire4 = pygame.image.load(os.path.join(img_folder,"fire3_ 04.png")).convert()
            self.fire5 = pygame.image.load(os.path.join(img_folder,"fire3_ 05.png")).convert()
            self.fire6 = pygame.image.load(os.path.join(img_folder,"fire3_ 06.png")).convert()
            self.fire7 = pygame.image.load(os.path.join(img_folder,"fire3_ 07.png")).convert()
            self.fire8 = pygame.image.load(os.path.join(img_folder,"fire3_ 08.png")).convert()
            self.fire9 = pygame.image.load(os.path.join(img_folder,"fire3_ 09.png")).convert()
            self.fire10 = pygame.image.load(os.path.join(img_folder,"fire3_ 10.png")).convert()
            self.fire11 = pygame.image.load(os.path.join(img_folder,"fire3_ 11.png")).convert()
            self.fire12 = pygame.image.load(os.path.join(img_folder,"fire3_ 12.png")).convert()
            self.fire13 = pygame.image.load(os.path.join(img_folder,"fire3_ 13.png")).convert()
            
        self.path = paths
        self.rightface = self.image
        self.leftface = pygame.transform.flip(self.image, True, False)
        self.posx = posx
        self.posy = posy
        self.pos = vec(posx,posy)
        
        if self.path == "downwards": #set path and rotate image 
            self.image = pygame.transform.rotate(self.image,90)
            
        super(projectile,self).__init__() #inherit from enemy
        
        if img == "fire1":
            self.rect = self.image.get_rect(center=self.pos)
            self.rect.inflate_ip(-6,0) #adjust hitboxes
        elif img == "fire":
            self.rect = self.image.get_rect(center=self.pos)
            self.rect.inflate_ip(0,0)
        else:
            self.rect = self.image.get_rect(center=self.pos)

        self.rect.center = (self.posx,self.posy)
        self.obey_gravity = False
        self.killable = False        
        self.projectile_speed = speed
        projectiles.add(self)
        all_sprites.add(self)
        self.direction = direct
        
        self.distance = 0
        
        self.timer = 0
        
        self.custom = custom
        self.animation = 0
        self.img = img

    def update(self):
        if not self.custom:
            
            self.distance += self.projectile_speed #counts how far the projectile has travelled
            
            if self.path == "sideways" or self.path == "zigzag":
                if self.direction == "right":
                    self.posx += self.projectile_speed #moves the projectile 
                    self.image = self.leftface #makes the projectile face the right way
                else:
                    self.posx -= self.projectile_speed

                if self.path == "zigzag": #zigzag path
                    if self.timer < 30:
                        self.posy -= self.projectile_speed*0.25 #moves the projectile up and down
                    else:
                        self.posy += self.projectile_speed*0.25
                        if self.timer > 60:
                            self.timer = 0
                            
                    self.timer += 1
                


            if self.path == "downwards": 
                self.posy += self.projectile_speed #makes the projectile move downwards

            self.rect.center = self.posx,self.posy

            if self.distance >= 800: #kills the projectile after a distance
                all_sprites.remove(self)
                projectiles.remove(self)
                self.kill()
        else:
            self.posx += self.custom[0] #moves the projectile the given amount
            self.posy += self.custom[1]
            if self.img == "fire" or self.img == "fire1" or self.img == "fire2":
                if self.animation < 2:
                    self.image = self.fire1
                elif self.animation < 4:
                    self.image = self.fire2
                elif self.animation < 6:
                    self.image = self.fire3
                elif self.animation < 8:
                    self.image = self.fire4
                elif self.animation < 10:
                    self.image = self.fire5
                elif self.animation < 12:
                    self.image = self.fire6 #different frames for the fireball
                elif self.animation < 14:
                    self.image = self.fire7
                elif self.animation < 16:
                    self.image = self.fire8
                elif self.animation < 18:
                    self.image = self.fire9
                elif self.animation < 20:
                    self.image = self.fire10
                elif self.animation < 22:
                    self.image = self.fire11
                elif self.animation < 24:
                    self.image = self.fire12
                elif self.animation < 25: #gets an extra frame when the animation timer resets
                    self.image = self.fire13
                else:
                    self.animation = 0
                    self.timer += 25
                
            self.image.set_colorkey(black)
            
            self.image = pygame.transform.rotate(self.image,self.custom[2])  #rotates the image
            
            self.animation += 1

            self.rect.center = self.posx,self.posy

            if self.timer >= 300: #removes projectile after an amount of time
                all_sprites.remove(self)
                self.kill()     
        

class wolf(enemy):
    def __init__(self,spawnx,spawny,ids = None):

        self.image = wolves_img.get_image(322,258, 79, 38) #gets image
        self.image.set_colorkey(black)            
        self.image = pygame.transform.scale(self.image, (58, 28))
        self.image = pygame.transform.flip(self.image, True, False) 
        
                 
        super(wolf,self).__init__() #runs the enemy initialise
        self.pos = vec(spawnx,spawny)
        self.rect.center = (self.pos.x,self.pos.y)

        self.animation = True
        self.animation_timer = 5
        self.howl_timer = 100
        self.obey_gravity = True
        self.ids = ids
        
        self.howl_image = wolves_img.get_image(517, 249, 58, 38) #prepares the howl image
        self.howl_image.set_colorkey(black)
        self.howl_image = pygame.transform.scale(self.howl_image, (58, 28))

        self.frame1 = wolves_img.get_image(322, 258, 58, 28) #frame 1
        self.frame1.set_colorkey(black)            
        self.frame1 = pygame.transform.scale(self.frame1, (58, 28))        

        self.frame2 = wolves_img.get_image(386, 291, 58, 28) #frame 2
        self.frame2.set_colorkey(black)            
        self.frame2 = pygame.transform.scale(self.frame2, (58, 28))
                        
    def moveh(self,speed,distance): #this method will overrides the enemy moving method,adding animation to the wolf.
        if self.alive:
            if self.howl_timer <= 0: #activates the howl
                self.howl_timer -= 1
                if self.howl_timer <= -30:
                    self.howl_timer = 100
                self.image = self.howl_image 
                if self.pos.x > 0 and self.pos.x < 720:
                    howl_sound.play() #plays the howl sound
            else:

                if self.movedirect == "right":  
                    self.pos.x += speed
                    self.distmoved += speed
                    if self.distmoved >= distance:
                        self.movedirect = "left"
                else:
                    self.pos.x -= speed
                    self.distmoved -= speed
                    if self.distmoved <= 0:
                        self.movedirect = "right" #completes movement, changes directionn after 
                                                  #maximum distance has been reached
                        
                self.howl_timer -= 1  #reduces the time till the next howl
                if self.animation_timer > 0:
                    self.animation_timer -= 1
                else:
                    self.animation_timer = 5
                    self.animation = not self.animation #swaps between the 2 animation frames every 5 frames

                    if self.animation:
                        self.image = self.frame1 #change the frame

                    else:
                        self.image  = self.frame2

                    if self.movedirect == "right": #makes the wolf face the direction he is walking
                        self.image = pygame.transform.flip(self.image, True, False)
                

class skeleton(enemy): 
    def __init__(self,spawnx,spawny):
        self.image = sprites.get_image(0,0, 64, 64) #sets up image
        self.image.set_colorkey(black)
        self.image = pygame.transform.scale(self.image, (64, 64))
        
        super(skeleton,self).__init__() #inherits from enemy
        self.pos = vec(spawnx,spawny)
        self.rect.center = (self.pos.x,self.pos.y)


class wizardpowerup(pygame.sprite.Sprite):
    def __init__(self,spawnx,spawny):
        pygame.sprite.Sprite.__init__(self) #inherit from sprite class
        
        self.image = pygame.image.load(os.path.join(img_folder,"staff05.png")).convert()
        self.image.set_colorkey(black)
        self.image = pygame.transform.scale(self.image, (64, 64)) #getting image 
        
        self.rect = self.image.get_rect()     #get hitbox   
        self.rect.center = (spawnx,spawny) #spawn coordinates


def fall_on_platform(self,group,speed):
    hit = pygame.sprite.spritecollide(self, group, False)
    if hit:
        self.pos.y += speed #pushed the entity down at the same speed as the platform

        

            
def check_if_on_platform(self): #this makes the character stand on the platform when needed
        if self.vel.y + 0.5 * self.acc.y > 0: #checks if the player is moving downwards
            hit = pygame.sprite.spritecollide(self, platforms, False)#checks for platform collision 
            if hit and self.pos.y > hit[0].rect.top and self.vel.y != 1: 
                self.pos.y = hit[0].rect.top
                self.vel.y = 0

                
                global position
                if position == "level3":
                    fall_on_platform(self,moving_platforms3,2) #platforms which move vertically 
                    fall_on_platform(self,moving_platforms4,3)
                    fall_on_platform(self,moving_platforms5,3)
                    fall_on_platform(self,moving_platforms8,3)
                    fall_on_platform(self,moving_platforms10,3)
                    fall_on_platform(self,moving_platforms11,4)

        hit = pygame.sprite.spritecollide(self, finish_line, False)
        if hit and play.show_end_screen != "done": #that is for multiplayer to not end the game
            play.show_end_screen = True #once they are finished
                
class friendly_projectile(pygame.sprite.Sprite):    
    def __init__(self,posx,posy,direct,immunity):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direct #sets the direction of motion based on where the player was facing
        
        self.image = pygame.image.load(os.path.join(img_folder,"wizardtrail.png")).convert()
        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (64, 19)) #prepares the image
        self.image.set_colorkey(black)
        
        self.rect = self.image.get_rect() #gets the projectile's hitbox
        self.posx = posx
        self.posy = posy #projectile coordinates
        
        self.projectile_speed = 10
        self.rect.center = (self.posx,self.posy)
        friend_projectiles.add(self)
        all_sprites.add(self)
        self.immunity = immunity
        
        self.hit_dragon = False

    def check_dragon(self): 
        if self.hit_dragon:
            self.hit_dragon = False
            return True
        return False

    def update(self):
        if self.direction == "right":
            self.posx += self.projectile_speed
        else:
            self.posx -= self.projectile_speed #moves the projectile based on its direction

        self.rect.center = self.posx,self.posy #updates the position
        hits = pygame.sprite.spritecollide(self,enemies, False)
        
        if hits or self.posx > 1280 or self.posx < 0: #removes the projectile if off the screen or has collided
            all_sprites.remove(self) #removes the projectile if it has hit something
            friend_projectiles.remove(self)
            self.kill()
            if position != "level7" and hits:
                    all_sprites.remove(hits[0])
                    enemies.remove(hits[0])
                    hits[0].kill() #remove the enemy that has been hit
                    
            elif hits:
                self.hit_dragon = True #changes a variable showing the level7 dragon has been hit so the lives are reduced

        hits = pygame.sprite.spritecollide(self,platforms, False)
        if hits and self.immunity == 0: #can't kill if immune
            all_sprites.remove(self)
            friend_projectiles.remove(self)
            self.kill()
            
        if self.immunity > 0:#reduces time left in immunity
            self.immunity -= 1





class player(pygame.sprite.Sprite): 
    def __init__(self,start_location_y = height/2,start_location_offset_x = 0):   
        pygame.sprite.Sprite.__init__(self)
        #player images
        self.basic_fr1 = pygame.image.load(os.path.join(img_folder,"avt1_fr1.gif")).convert()
        self.basic_rt1 = pygame.image.load(os.path.join(img_folder,"avt1_rt1.png")).convert()
        self.basic_rt2 = pygame.image.load(os.path.join(img_folder,"avt1_rt2.png")).convert()
        self.basic_lf1 = pygame.image.load(os.path.join(img_folder,"avt1_lf1.png")).convert()
        self.basic_lf2 = pygame.image.load(os.path.join(img_folder,"avt1_lf2.png")).convert()
        self.basic_bk2 = pygame.image.load(os.path.join(img_folder,"avt1_bk2.gif")).convert()

        self.basic_bk1 = pygame.image.load(os.path.join(img_folder,"avt1_bk1.gif")).convert()



        
        self.wiz_fr1 = pygame.image.load(os.path.join(img_folder,"smr1_fr1.gif")).convert()
        self.wiz_rt1 = pygame.image.load(os.path.join(img_folder,"smr1_rt1.png")).convert()
        self.wiz_rt2 = pygame.image.load(os.path.join(img_folder,"smr1_rt2.png")).convert()
        self.wiz_lf1 = pygame.image.load(os.path.join(img_folder,"smr1_lf1.png")).convert()
        self.wiz_lf2 = pygame.image.load(os.path.join(img_folder,"smr1_lf2.png")).convert()

        
        self.image = self.basic_fr1         #the current image 
        self.image.set_colorkey(white)      #removes the background colour, giving transparency
        self.rect = self.image.get_rect()                #creates the hitbox for the player

        
                
        self.totaldistance = width/2
        self.wand_number = 1

        self.rect.center = (width / 2,start_location_y) #the player's hitbox will be the same as their position
        self.pos = vec(width / 2,height / 2)
        self.vel = vec(0, 0)  #vectors for motion and position
        self.acc = vec(0, 0)
        
        self.animationtimer = 0
        self.max_idle_time = 7
        self.idle_time = self.max_idle_time
        
        self.state = "basic"

        self.projectiles = []  #list of all of the projeciles
        self.cooldown_timer = 0 #timer until the player can fire the wand
        
        self.immunity = 0

        self.direct = "right"
        self.cheat_mode = False
        self.show_end_screen = False
        self.photo = "s"
        self.dying = []
        self.climbing = False
        self.replay = False
        self.fired = False
        self.kill = False
        if start_location_offset_x != 0: #used for wizard wars. Allows players to spawn in different places
            self.start_location_y = start_location_y
            self.start_location_offset_x = start_location_offset_x
            
    def spawn_wand(self):  #determines where a new wand should spawn 
        if self.totaldistance < self.wand_number * -4500:
            self.wand_number += 1
            return self.wand_number * 4500 + self.totaldistance #spawns every 4500 pixels
        return None


    def replay_set_image(self): #changes the player's picture to what is given in the document
        #uses the correct state and photo to reacreate replay.
        if self.photo == "s":
            if self.state == "basic":
                self.image = self.basic_fr1
            else:
                self.image = self.wiz_fr1     

        if self.photo == "r":
            if self.state == "basic":
                self.image = self.basic_rt1
            else:
                self.image = self.wiz_rt1

        if self.photo == "R":
            if self.state == "basic":
                self.image = self.basic_rt2
            else:
                self.image = self.wiz_rt2

        if self.photo == "l":
            if self.state == "basic":
                self.image = self.basic_lf1
            else:
                self.image = self.wiz_lf1

        if self.photo == "L":
            if self.state == "basic":
                self.image = self.basic_lf2
            else:
                self.image = self.wiz_lf2
                
        if self.photo == "b":
            self.image = self.basic_bk2

        if self.photo == "B":
            self.image = self.basic_bk1
                
        self.image.set_colorkey(white)

    def move_screen_in_replay_mode(self,change):
        for i in platforms:         #this procedure moves everything by that amount, keeping the 
            i.rect.x += change       #player in the center of the screen
        for i in enemies:
            i.pos.x += change
        try:
            for i in projectiles:  #try is used as there may not be a projectiles or ladders group,
                i.posx += change    #depending on what level the user is playing
        except:pass
        try:
            for i in ladders: 
                i.rect.x += change
        except:pass
            

        for i in powerups:
            i.rect.x += change
        for i in self.projectiles:
            i.posx += change

        self.totaldistance += change




    def move_everything_but_player(self,change,auto_allow = False):
        allow = False
        if not auto_allow:
            if change < 0:
                direct = "right" #what direction the player is moving in
            else:
                direct = "left"

            
            if not self.climbing:
                self.rect.y -= 13 #moves the player up to stop them colliding with the floor

            if direct == "right":
                self.rect.x += 5 #checks right of the player
                hits = pygame.sprite.spritecollide(self,platforms, False)
                if not hits:
                    allow = True

                self.rect.x -= 5

            else:
                self.rect.x -= 5 #checks left of the playing
                hits = pygame.sprite.spritecollide(self,platforms, False)
                if not hits:
                    allow = True

                self.rect.x += 5

            if not self.climbing:
                self.rect.y += 13

        if allow or auto_allow:
            self.totaldistance += change #This is the distnace moved by the player

            
            for i in platforms:         #this procedure moves everything by that amount, keeping the 
                i.rect.x += change       #player in the center of the screen

                
            for i in enemies:
                i.pos.x += change
            try:
                for i in projectiles:  #try is used as there may not be a projectiles or ladders group,
                    i.posx += change    #depending on what level the user is playing
            except:pass
            try:
                for i in ladders: 
                    i.rect.x += change
            except:pass
                

            for i in powerups:
                i.rect.x += change
            for i in self.projectiles:
                i.posx += change

    def jump(self,platforms):
        # jump only if standing on a platform

        self.rect.y += 5
        hits = pygame.sprite.spritecollide(self,platforms, False)
        self.rect.y -= 5
        
        if hits or self.cheat_mode:
            jump_sound.play()
            
            self.vel.y = -20 #causes the player to actually jump


    def check_jump(self,platforms):
        self.rect.y -= 20 #moves the player upwards to check what is above them
        hits = pygame.sprite.spritecollide(self,platforms, False)
        if hits:
            if self.acc.y < 0:
                self.acc.y = 0 #velocity and acceleration are stopped, and gravity will soon move the player down
            if self.vel.y < 0:
                self.vel.y = 0
            self.pos.y += 1 #moves the player down slightly, this made the motion seem more realistic
        self.rect.y += 20 #returns the player to where they originally were
        
    def update(self):        

        for i in self.dying:
            i.pos.y += 8 #moves enemy downwards if the enemy has been killed

            if i.pos.y > 720: #once enemy is off the screen, remove the enemy
                self.dying.remove(i)
                i.kill()

            
        if not self.replay:



            if "ladders" in globals(): #checks if the group ladders exists. Some levels do not have ladders.
                player_rect = self.rect
                self.rect = pygame.Rect(self.pos.x, self.pos.y - 16, 1, 1)
                #realligning hitboxes so the player's center must be on the ladder, not just colliding
                onladder = pygame.sprite.spritecollide(self, ladders, False) #checks if the player is on a ladder
                if not onladder:
                    self.climbing = False #if they are not on a ladder, the player cannot be climbing
                self.rect = player_rect
            else:
                self.climbing = False

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP: #keybinds for upwards
                        if "ladders" in globals():
                            if onladder: #onladder just means if the player is on a ladder
                                self.climbing = True #if the player presses the up or down on the ladder, they 
                            else:                       #will grip onto the ladder
                                self.jump(platforms)
                        else:
                            self.jump(platforms) #if they are not on a ladder, they will jump as normal
                        
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:#keybinds for down
                        if "ladders" in globals():
                            if onladder:
                                self.climbing = True



            if self.climbing:
                keys = pygame.key.get_pressed()  #checking pressed keys
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.animationtimer += 1 #changes the climbing animation
                    self.rect.y -=3 
                    above_platform = pygame.sprite.spritecollide(self,platforms, False) #checks if the player can climb.
                    if not above_platform:                                          #if they have a platform  
                        self.pos.y -= 3                                             #above them, they cannot climb up
                    self.rect.y += 3

                if keys[pygame.K_DOWN] or keys[pygame.K_s]: #same but for the s key
                    self.animationtimer += 1 #changes the climbing animation
                    self.rect.y +=3 #moves the player down
                    above_platform = pygame.sprite.spritecollide(self,platforms, False) 
                    if not above_platform:                                              
                        self.pos.y += 3

            else:
                self.animationtimer+=1
                
                        
            if self.cooldown_timer > 0:
                self.cooldown_timer -= 1
            
            if not self.climbing: #gravity does not apply if the player is climbing
                self.acc = vec(0, gravity)

                
            
            keys = pygame.key.get_pressed() 
            if keys[pygame.K_SPACE] and self.state == "wizard" and self.cooldown_timer == 0:
                self.fired = True
                pew_sound.play() 
                self.cooldown_timer += 30 #increases the time until the player can shoot again
                hits = pygame.sprite.spritecollide(self,platforms, False)
                if hits:
                    self.projectiles.append(friendly_projectile(width/2,self.pos.y-20,self.direct,2))
                else:
                    self.projectiles.append(friendly_projectile(width/2,self.pos.y-20,self.direct,0))
                    
                if position == "wizardwars": #tells the server the user has fired 
                    if self.direct == "left":
                        udp_send_to_server("SHOOT---"+str(round(play.totaldistance)).zfill(5)+str(round(play.pos.y)-16).zfill(4)+"l")
                    else:
                        udp_send_to_server("SHOOT---"+str(round(play.totaldistance)).zfill(5)+str(round(play.pos.y)-16).zfill(4)+"r")
                        
            else:
                self.fired = False

            if keys[pygame.K_a] or keys[pygame.K_LEFT]: #keybinds
                self.vel.x = ACC #gives the player velocity when they move
                if not self.cheat_mode:
                    self.move_everything_but_player(5)
                else:
                    self.move_everything_but_player(15)
                self.direct = "left"

                if self.animationtimer < 5: #when the frame has been displayed for less than 5 frames
                    self.photo = "l"
                    if self.state == "basic":
                        self.image = self.basic_lf1 #changes image to necessary image
                    elif self.state == "wizard":
                        self.image = self.wiz_lf1
                else:
                    self.photo = "L"        #other frame
                    if self.state == "basic":
                        self.image = self.basic_lf2 #also changes image to necessary image
                    elif self.state == "wizard":
                        self.image = self.wiz_lf2
                self.idle_time = self.max_idle_time
                
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: #same but for the right direction
                self.direct = "right"
                self.vel.x = -ACC
                if not self.cheat_mode:
                    self.move_everything_but_player(-5) #move the player
                else:
                    self.move_everything_but_player(-15)

                if self.animationtimer < 5:
                    self.photo = "r"
                    if self.state == "basic":
                        self.image = self.basic_rt1
                    elif self.state == "wizard":
                        self.image = self.wiz_rt1   #change the frame
                else:
                    self.photo = "R"
                    if self.state == "basic":
                        self.image = self.basic_rt2
                    elif self.state == "wizard":
                        self.image = self.wiz_rt2
                self.idle_time = self.max_idle_time
            else:
                if not self.climbing:
                    self.animationtimer = 0 #resets the animation timer

                
            if self.vel.x > 0:
                self.vel.x -= FRICTION #applies opposition to motion
            elif self.vel.x < 0:
                self.vel.x += FRICTION
                
            self.move_everything_but_player(self.vel.x)
            
            if not self.climbing:
                self.check_jump(platforms)
                if self.vel.y + self.acc.y < 20: 
                    self.vel += self.acc
                self.pos.y += self.vel.y + 0.5 * self.acc.y        
                self.vel.y += 1 #this makes jumping seem much more realistic
            self.rect.midbottom = self.pos

            
            if self.animationtimer == 10: #resets the animation timer
                self.animationtimer = 0
                
            if self.idle_time == 0: #changes the image to the idle image
                self.photo = "s"    
                if self.state == "basic":
                    self.image = self.basic_fr1
                else:
                    self.image = self.wiz_fr1                 
            else:
                self.idle_time -= 1 #decreases the time until the image becomes idle


            if "ladders" in globals():
                if self.climbing:
                    if self.animationtimer < 4: #changes the frame based on the timer
                        self.photo = "b"
                        self.image = self.basic_bk2
                    else:
                        self.photo = "B"
                        self.image = self.basic_bk1
                
            self.image.set_colorkey(white)


            #these are the positions to send to the server for multiplayer

            check_if_on_platform(self)            

            if self.immunity > 0:
                self.immunity-=1

    def check_enemy_collisions(self):  #enemy collision, through jumping
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            return False #kills the player when the press the enter key
        
        if self.cheat_mode:
            return True
        
        hit = pygame.sprite.spritecollide(self, enemies, False)
        if hit:
            if (self.vel.y > 0 or self.pos.y < hit[0].pos.y - 16) and hit[0].killable and not self.climbing or self.replay: 
                self.immunity = 10              #checks the player is moving downwards,and that the                  
                self.vel.y = -15
                
                if position == "level1m":                       
                    enemy = [e1,e2,e3,e4,e5,e6,e7,e8,e9,e10] #all enemies in the level
                    for i in enemy:
                        if hit[0] == i:
                            send_to_server("UPDATEK1"+i.ids)#tell the server enemy has been killed                            
                            self.immunity = 5 #gives the player a short immunity when jumping on an enemy
                            #until the server tells the client to kill the enemy
                    
                if not hit[0].respawning and position != "level7":
                    self.dying.append(hit[0])
                if position != "level7":
                    hit[0].alive = False
    

                
            elif self.state != "basic" and position != "level7" and position != "wizardwars":
                self.state = "basic" #if players gets hit, they lose wizard, but stay alive
                self.immunity = 30 #also given some immunity after being hit
            elif self.immunity == 0:
                return False #shows the player has died
        try:
            hit = pygame.sprite.spritecollide(self, projectiles, False)
            if hit:
                if self.state != "basic" and position != "wizardwars":
                    self.state = "basic"
                    self.immunity = 30
                elif self.immunity == 0:
                    return False
        except:pass
        return True #player has not died

    def check_powerup(self):
        hit = pygame.sprite.spritecollide(self, powerups, True)
        if hit:
            self.state = "wizard" #upgrades the player to the wizard form

def timer():
    end = time.time() #current time
    timer = button(grey,35,20,100,50,("Time: "))
    font = pygame.font.SysFont('comicsans', 40)   #adds text
    text = font.render(str(round(end - start,2)), 1, (0,0,0)) #finds the time between start and current
    timer.draw(screen) 
    pygame.draw.rect(screen,grey, (135,20,100,50),0)
    screen.blit(text, (150,30))
    return end #returns the time, this may be useful for recording the best time

def is_player_alive(ingame):
    alive = play.check_enemy_collisions() #checks if the player has been killed or killed an enemy
    if play.pos.y > dispy or not alive:
        return "singleplayer" #back on the map
    else:
        return ingame #stay in game

def level1m(play):
    global rankchange
    killed = "00"
    position = "level1m"


    #update


    e1.moveh(3,140)
    e2.moveh(4,130)
    e3.moveh(4,120)
    e4.moveh(5,120)
    e5.moveh(5,120) 
    e6.mageupdate() #speed,fire rate, fire rate is reversed
    e6.shoot(10,30)
    e6.mageupdate()
    e7.shoot(13,30)
    e7.mageupdate()
    e8.shoot(15,30)
    e8.mageupdate()
    e9.shoot(17,30)
    e9.mageupdate()
    e10.shoot(18,25,imgs = "lightening")
    e10.mageupdate()
    e10.moveh(7,150)
    e10.jump(-9,40)
    all_sprites.update()

    alive = play.check_enemy_collisions()
    if play.pos.y > dispy or not alive:
        play.pos.y = 100
        play.move_everything_but_player(-play.totaldistance+width/2,auto_allow = True)
        play.totaldistance = width/2
        alive = True

    screen.blit(backdropm,(0,0))

    end = timer()
    
    global standings
    try:#can fail if while the for loop is running, the list changes
        standb = button(grey,1000,20,250,50,("Standings:"))
        standb.draw(screen)
        for i in range(len(standings)):
            standb = button(grey,1000,70 + 50 * i,250,50,(str(standings[i])))
            standb.draw(screen)
    except:pass
    
    udp_send_to_server(("UPDATE1")+str(yourplayer)+
    str(str(round(play.totaldistance+16)).zfill(5))+str(str(round(play.pos.y)-32).zfill(4))+play.photo)


    #killed is what the player has killed
    #direction is what way they are facing

    platforms.draw(screen)
    projectiles.draw(screen)
    enemies.draw(screen)

    if game_info[0][2] == "s": #choses the necessary image to display
        yourimage = player1image
                                 #directions are reversed as the other person moving forward
    elif game_info[0][2] == "l": #causes you to move backwards
        yourimage = player1imager
    elif game_info[0][2] == "L":
        yourimage = player1imageR
    elif game_info[0][2] == "r":
        yourimage = player1imagel
    elif game_info[0][2] == "R":
        yourimage = player1imageL

    if yourplayer != "0":
        screen.blit(yourimage,(play.totaldistance-game_info[0][0]+play.pos.x,game_info[0][1])) #blits the player's image using the class stored on the computer to reduce latency
    else:
        screen.blit(yourimage,(play.pos.x-16,play.pos.y - 32)) #blits the player using the coordinates from their machine
        #to prevent latency

    if game_info[1][2] == "s": #next player
        yourimage = player2image
    elif game_info[1][2] == "l":
        yourimage = player2imager
    elif game_info[1][2] == "L":
        yourimage = player2imageR
    elif game_info[1][2] == "r":
        yourimage = player2imagel
    elif game_info[1][2] == "R":
        yourimage = player2imageL

    if yourplayer != "1":
        screen.blit(yourimage,(play.totaldistance-game_info[1][0]+play.pos.x,game_info[1][1])) #blits the player's image using the class stored on the computer to reduce latency
    else:
        screen.blit(yourimage,(play.pos.x-16,play.pos.y - 32))
               
    if game_info[2][2] == "s": #next player
        yourimage = player3image
    elif game_info[2][2] == "l":
        yourimage = player3imager
    elif game_info[2][2] == "L":
        yourimage = player3imageR
    elif game_info[2][2] == "r":
        yourimage = player3imagel
    elif game_info[2][2] == "R":
        yourimage = player3imageL

    if yourplayer != "2":
        screen.blit(yourimage,(play.totaldistance-game_info[2][0]+play.pos.x,game_info[2][1])) #blits the player's image using the class stored on the computer to reduce latency
    else:
        screen.blit(yourimage,(play.pos.x-16,play.pos.y - 32))
            
    if game_info[3][2] == "s": #next player
        yourimage = player4image
    elif game_info[3][2] == "l":
        yourimage = player4imager
    elif game_info[3][2] == "L":
        yourimage = player4imageR
    elif game_info[3][2] == "r":
        yourimage = player4imagel
    elif game_info[3][2] == "R":
        yourimage = player4imageL

    if yourplayer != "3":
        screen.blit(yourimage,(play.totaldistance-game_info[3][0]+play.pos.x,game_info[3][1])) #blits the player's image using the class stored on the computer to reduce latency
    else:
        screen.blit(yourimage,(play.pos.x-16,play.pos.y - 32)) 



    if play.show_end_screen != "done" and play.show_end_screen:

        send_to_server("FINISH1-")
        play.show_end_screen = "done"

    if rankchange != []: #only shows if the game is finished
        time.sleep(1) # gives time for the results to be processed and recived before displaying them
        standb = button(grey,390,220,500,80,("Results:"))
        standb.draw(screen)
        for i in range(len(rankchange)): #display results
            standb = button(grey,390,300 + 80 * i,500,80,(str(i + 1)+". "+str(rankchange[i])))
            standb.draw(screen)

        pygame.display.flip()
        time.sleep(5)
        global lobby1
        global lobby1r
        global lobby1ready #reset variables
        
        lobby1 = []
        lobby1r = []
        lobby1ready = "0"
        position = "home"
            
        rankchange = []
        standings = [] #reset these
    
    pygame.display.flip()

    return play,position


def wizardwars(play):
    global lobby1alpha
    global rankchange
    killed = "00"
    position = "wizardwars"

    all_sprites.update()




    alive = play.check_enemy_collisions()
    if play.pos.y > dispy or not alive:
        
        play.immunity = 120 #stops the player dying immediately after spawning
        
        if play.pos.y > 4500:
            play.move_everything_but_player(play.start_location_offset_x)
            
        else:
            
            send_to_server("FINISH1-")
            print("distance",play.totaldistance)
            print("start location",play.start_location_offset_x)
            play.move_everything_but_player(-play.totaldistance + play.start_location_offset_x,True)
            

            
        play.pos.y = play.start_location_y
        play.totaldistance = play.start_location_offset_x
        print("new distance",play.totaldistance)
        play.state = "wizard"
        alive = True
        
    screen.blit(backdropm,(0,0))

    end = time.time()
    timer = button(grey,35,20,100,50,("Time: "))
    font = pygame.font.SysFont('comicsans', 40)   #adds text
    text = font.render(str(round(end - start,2)), 1, (0,0,0))
    timer.draw(screen)
    pygame.draw.rect(screen,grey, (135,20,100,50),0)
    screen.blit(text, (150,30))

    try: #this can fail if the scores are wiped while its being drawn
        standb = button(grey,245,20,245,50,("Scores:"))
        standb.draw(screen)
        for i in range(len(scores)):
            if i < 3: 
                standb = button(grey,500 + 255 * i,20,245,50,scores[i])
                standb.draw(screen)
            else:#last box doesnt fit so it goes on the line below
                standb = button(grey,1010,80,245,50,scores[i])
                standb.draw(screen)
    except:pass
            
    udp_send_to_server(("UPDATE1")+str(yourplayer)+str(str(round(play.totaldistance+16)).zfill(5))+str(str(round(play.pos.y)-32).zfill(4))+play.photo+killed)

    #killed is what the player has killed
    #direction is what way they are facing

    platforms.draw(screen)
    projectiles.draw(screen)
    enemies.draw(screen)

    if game_info[0][2] == "s":
        yourimage = player1image
                                 #directions are reversed as the other person moving forward
    elif game_info[0][2] == "l": #causes you to move backwards
        yourimage = player1imager
    elif game_info[0][2] == "L":
        yourimage = player1imageR
    elif game_info[0][2] == "r":
        yourimage = player1imagel
    elif game_info[0][2] == "R":
        yourimage = player1imageL

    if lobby1alpha[0] > 0: #gives the image the opaqueness
        yourimage.set_alpha(128)
        lobby1alpha[0] -= 1

    if yourplayer != "0":
        screen.blit(yourimage,(play.totaldistance-game_info[0][0]+play.pos.x,game_info[0][1])) #blits the player's image using the class stored on the computer to reduce latency
    else:
        screen.blit(yourimage,(play.pos.x-16,play.pos.y - 32))

    yourimage.set_alpha(None)


    if game_info[1][2] == "s": #next player
        yourimage = player2image
    elif game_info[1][2] == "l":
        yourimage = player2imager
    elif game_info[1][2] == "L":
        yourimage = player2imageR
    elif game_info[1][2] == "r":
        yourimage = player2imagel
    elif game_info[1][2] == "R":
        yourimage = player2imageL

    if lobby1alpha[1] > 0:
        yourimage.set_alpha(128)
        lobby1alpha[1] -= 1


    if yourplayer != "1":
        screen.blit(yourimage,(play.totaldistance-game_info[1][0]+play.pos.x,game_info[1][1])) #blits the player's image using the class stored on the computer to reduce latency
    else:
        screen.blit(yourimage,(play.pos.x-16,play.pos.y - 32))
    yourimage.set_alpha(None)   
            
    if game_info[2][2] == "s": #next player
        yourimage = player3image
    elif game_info[2][2] == "l":
        yourimage = player3imager
    elif game_info[2][2] == "L":
        yourimage = player3imageR
    elif game_info[2][2] == "r":
        yourimage = player3imagel
    elif game_info[2][2] == "R":
        yourimage = player3imageL

    if lobby1alpha[2] > 0:
        yourimage.set_alpha(128)
        lobby1alpha[2] -= 1


    if yourplayer != "2":
        screen.blit(yourimage,(play.totaldistance-game_info[2][0]+play.pos.x,game_info[2][1])) #blits the player's image using the class stored on the computer to reduce latency
    else:
        screen.blit(yourimage,(play.pos.x-16,play.pos.y - 32))

    yourimage.set_alpha(None)
            
    if game_info[3][2] == "s": #next player
        yourimage = player4image
    elif game_info[3][2] == "l":
        yourimage = player4imager
    elif game_info[3][2] == "L":
        yourimage = player4imageR
    elif game_info[3][2] == "r":
        yourimage = player4imagel
    elif game_info[3][2] == "R":
        yourimage = player4imageL

    if lobby1alpha[3] > 0:
        yourimage.set_alpha(128)
        lobby1alpha[3] -= 1



    if yourplayer != "3":
        screen.blit(yourimage,(play.totaldistance-game_info[3][0]+play.pos.x,game_info[3][1])) #blits the player's image using the class stored on the computer to reduce latency
    else:
        screen.blit(yourimage,(play.pos.x-16,play.pos.y - 32))  
    yourimage.set_alpha(None)

    if rankchange != []:
        time.sleep(1)
        standb = button(grey,390,220,500,80,("Results:"))
        standb.draw(screen)
        for i in range(len(rankchange)):
            standb = button(grey,390,300 + 80 * i,500,80,(str(i + 1)+". "+str(rankchange[i])))
            standb.draw(screen)

        pygame.display.flip()
        time.sleep(5)
        global lobby1
        global lobby1r
        global lobby1ready #reset variables
        
        lobby1 = []
        lobby1r = []
        lobby1ready = "0"
        position = "home"
            
        rankchange = []
        standings = [] #reset these

    
    pygame.display.flip()

    return play,position     

def level1(replay = False,ghost = False):
    oldpos = p1.rect.x


    e1.moveh(3,150)
    e2.moveh(5,200)
    e3.moveh(6,150)
    e4.moveh(6,150)
    e5.moveh(7,150)

    all_sprites.update()
    
    play.check_powerup()
    
    position = is_player_alive("level1") #decides if the player's position, such as the map or in game

    screen.blit(backdrop1,(0,0))

    end = timer()
    
    movement = p1.rect.x - oldpos
    record_or_play_replay(replay,play,movement,ghost)
    
    all_sprites.draw(screen)
    enemies.draw(screen)
    
    

    
    if play.show_end_screen:
        endd = button(grey,dispx/2-150,dispy/2,300,50,("Level Complete!!!"))
        endd.draw(screen) #tells the user they have won
        pygame.display.flip()        #refreshes the screen
        time.sleep(5)  #pauses on the end screen
        position = "singleplayer"
        
        global playerlvl
        if playerlvl == 1: 
            playerlvl += 1
            save(playerlvl) #saves the player's new level


        best_time = get_time(1)
        if end - start < best_time:
            write_time(round(end-start,2),1) # saves the time

            write_replay(recording,"replay1.txt") #saves the replay                
    
    pygame.display.flip()
    return position



def level2(replay = False,ghost = False):
    oldpos = p1.rect.x
    
    e1.respawn([200,-100,200,-100,200,-100, -600,300])
    e1.moveh(5,150)
    e2.moveh(6,200,speed_variation = 0.01)
    e2.respawn([200,0,200,0,200,0,200,0,-800,0])
    
    e3.moveh(6,300,speed_variation = 0.01)
    e4.moveh(5,300,speed_variation = 0.01)
    e5.moveh(7,300,speed_variation = 0.015)
    e6.moveh(6,300,speed_variation = 0.018)
    
    all_sprites.update() #updates the sprites
    p2.sidemove(250,4,moving_platforms1)
    
    play.check_powerup()
    

    position = is_player_alive("level2") #decides if the player's position, such as the map or in game
    screen.blit(backdrop2,(0,0)) #adds the background to the level
    end = timer() #displays the timer
    
    movement = p1.rect.x - oldpos
    record_or_play_replay(replay,play,movement,ghost)
    
    all_sprites.draw(screen) #draws sprites to the screen
    enemies.draw(screen)
    players.draw(screen) #they are in order to make the player appear at the fron, then the enemy.
    
    if play.show_end_screen:
        endd = button(grey,dispx/2-150,dispy/2,300,50,("Level Complete!!!"))
        endd.draw(screen)
        pygame.display.flip()        
        time.sleep(5)
        position = "singleplayer"
        global playerlvl
        if playerlvl == 2:
            playerlvl += 1
            save(playerlvl)

        best_time = get_time(2)
        if end - start < best_time: #checks if this is the best time
            write_time(round(end-start,2),2) # saves the time

            write_replay(recording,"replay2.txt") #saves the replay    
    
    pygame.display.flip()

    return position


def level3(replay = False,ghost = False): ################################ level 3 #################
    oldpos = p1.rect.x
    #events


    #update

    e1.moveh(3,150)
    e1.jump(-10,90) #-20 is player jump
    e2.moveh(5,150)
    e3.moveh(3,150)
    e3.jump(-10,70)
    e4.moveh(3,150) #move enemies
    e4.jump(-10,40)
    e5.moveh(7,150)
    e6.moveh(8,125)
    e7.moveh(8,150)
    e8.moveh(8,200)
    e9.moveh(7,200)
    
    
    p12.upmove(400,2,moving_platforms3)
    p13.upmove(600,3,moving_platforms4)
    p14.upmove(400,3,moving_platforms5)
    p22.upmove(400,3,moving_platforms8)
    p24.upmove(400,3,moving_platforms10) #move platforms
    p25.upmove(400,4,moving_platforms11)
    all_sprites.update()
    p9.sidemove(200,2,moving_platforms1)
    p10.sidemove(200,5,moving_platforms2)
    p16.sidemove(200,5,moving_platforms6)
    p21.sidemove(200,5,moving_platforms7)
    p23.sidemove(500,6,moving_platforms9)
    
    play.check_powerup()
    alive = play.check_enemy_collisions()

    
    if play.pos.y > (dispy + 100) or not alive:
        position = "singleplayer"
    else:
        position = "level3"

    screen.blit(backdrop3,(0,0))

    end = time.time()
    timer = button(grey,35,20,100,50,("Time: "))
    font = pygame.font.SysFont('comicsans', 40)   #adds text
    text = font.render(str(round(end - start,2)), 1, (0,0,0))
    timer.draw(screen)
    pygame.draw.rect(screen,grey, (135,20,100,50),0)
    screen.blit(text, (150,30))
    movement = p1.rect.x - oldpos
    record_or_play_replay(replay,play,movement,ghost)
    all_sprites.draw(screen)
    enemies.draw(screen)
    if play.show_end_screen:
        endd = button(grey,dispx/2-150,dispy/2,300,50,("Level Complete!!!"))
        endd.draw(screen)
        pygame.display.flip()
        time.sleep(5)
        position = "singleplayer"
        global playerlvl
        if playerlvl == 3:
            playerlvl += 1
            save(playerlvl)
        best_time = get_time(3)
        if end - start < best_time:
            write_time(round(end-start,2),3) # saves the time

            write_replay(recording,"replay3.txt") #saves the replay 
    
    pygame.display.flip()

    return position





def level4(replay = False,ghost = False):
    oldpos = p1.rect.x

    e1.moveh(3,150)
    e1.jump(-10,90) #-20 is player jump
    e2.moveh(5,150)
    e2.jump(-10,100)
    e3.moveh(3,150)
    e3.jump(-10,70)
    e4.moveh(7,150)
    e4.jump(-6,70)
    e5.moveh(12,200)
    e5.jump(-6,70)
    e6.mageupdate()
    e6.shoot(10,60)
    e7.mageupdate()
    e7.shoot(10,60)
    e8.mageupdate()
    e8.shoot(10,60)
    e9.mageupdate()
    e9.shoot(10,60)
    e11.mageupdate()
    e11.shoot(15,35)
    e12.mageupdate()
    e12.shoot(15,60)

    all_sprites.update()
    
    play.check_powerup()
    alive = play.check_enemy_collisions()

    
    if play.pos.y > dispy or alive == False:
        position = "singleplayer"
    else:
        position = "level4"

    screen.blit(backdrop5,(0,0))
    end = time.time()
    timer = button(grey,35,20,120,50,("Time: "))
    font = pygame.font.SysFont('comicsans', 40)   #adds text
    text = font.render(str(round(end - start,2)), 1, (0,0,0))
    timer.draw(screen)
    pygame.draw.rect(screen,grey, (135,20,100,50),0)
    screen.blit(text, (150,30))
    movement = p1.rect.x - oldpos
    record_or_play_replay(replay,play,movement,ghost)
    platforms.draw(screen)
    all_sprites.draw(screen)
    enemies.draw(screen)
    
    if play.show_end_screen:
        endd = button(grey,dispx/2-150,dispy/2,300,50,("Level Complete!!!"))
        endd.draw(screen)
        pygame.display.flip()        
        time.sleep(5)
        position = "singleplayer"
        global playerlvl
        if playerlvl == 4:
            playerlvl += 1
            save(playerlvl)

        best_time = get_time(4)
        if end - start < best_time:
            write_time(round(end-start,2),4) # saves the time

            write_replay(recording,"replay4.txt") #saves the replay     
    pygame.display.flip()

    return position

def level5(replay = False,ghost = False):
    oldpos = p1.rect.x

    e1.follow()
    e1.mageupdate()
    e1.shoot(10,50, path = "downwards")
    e2.moveh(5,150)
    e2.jump(-10,100,sound = "cat")
    e3.moveh(7,150)
    e3.jump(-10,100,sound = "cat")
    e4.moveh(12,300)
    e4.fly_up_down(6,150)
    e5.mageupdate()
    e5.shoot(12,40,path = "zigzag")
    e6.mageupdate()
    e6.shoot(15,20,path = "downwards")
    e7.mageupdate()
    e7.shoot(15,20,path = "downwards")

    e8.mageupdate()
    e8.shoot(15,24,path = "downwards")
    e9.mageupdate()
    e9.shoot(15,22,path = "downwards")
    e10.mageupdate()
    e10.shoot(15,22,path = "downwards")

    e11.mageupdate()
    e11.shoot(18,40,path = "zigzag")

    e12.moveh(12,100)
    e13.moveh(13,100)
    e14.moveh(14,100)
    e15.moveh(15,100)
    e16.moveh(16,100)
    e17.moveh(17,100)
    e18.moveh(18,100)
    e19.moveh(19,100)
    
    e12.jump(-2,100,sound = "cat")
    e13.jump(-2,110,sound = "cat")
    e14.jump(-2,120,sound = "cat")
    e15.jump(-2,130,sound = "cat")
    e16.jump(-2,105,sound = "cat")
    e17.jump(-2,115,sound = "cat")
    e18.jump(-2,125,sound = "cat")
    e19.jump(-2,135,sound = "cat")
    
    e20.mageupdate()
    e20.shoot(14,40,path = "zigzag")
    e21.mageupdate()
    e21.shoot(14,40,path = "zigzag")

    platforms.update()
    play.update()
    projectiles.update()
    enemies.update()
    friend_projectiles.update()
    
    play.check_powerup()
    alive = play.check_enemy_collisions()


    if play.pos.y > dispy or alive == False:
        position = "singleplayer"
    else:
        position = "level5"

    screen.blit(backdrop6,(0,0))
    end = time.time()
    timer = button(grey,35,20,120,50,("Time: "))
    font = pygame.font.SysFont('comicsans', 40)   #adds text
    text = font.render(str(round(end - start,2)), 1, (0,0,0))
    timer.draw(screen)
    pygame.draw.rect(screen,grey, (135,20,100,50),0)
    screen.blit(text, (150,30))
    platforms.draw(screen)
    movement = p1.rect.x - oldpos
    record_or_play_replay(replay,play,movement,ghost)
    all_sprites.draw(screen)
    enemies.draw(screen)

    
    if play.show_end_screen:
        endd = button(grey,dispx/2-150,dispy/2,300,50,("Level Complete!!!"))
        endd.draw(screen)
        pygame.display.flip()        
        time.sleep(5)
        position = "singleplayer"
        global playerlvl
        if playerlvl == 5:
            playerlvl += 1
            save(playerlvl)

        best_time = get_time(5)
        if end - start < best_time:
            write_time(round(end-start,2),5) # saves the time

            write_replay(recording,"replay5.txt") #saves the replay 
    
    pygame.display.flip()

    return position

def level6(replay = False,ghost = False):
    oldpos = p1.rect.x

    #increased fire speed makes them fire slower
    e2.follow(cackle = False,number_swap = 70)
    e2.shoot(12,40,imgs = "meteor",path = "downwards")
    e3.follow(cackle = False,number_swap = 60,random_number_set = 2)
    e3.shoot(14,50,imgs = "meteor",path = "downwards")
    e4.follow(cackle = False,number_swap = 50,random_number_set = 3)
    e4.shoot(18,75,imgs = "meteor",path = "downwards")
    
    e5.shoot(14,45)
    e5.mageupdate()
    e5.moveh(4,150)

    e6.shoot(16,40)
    e6.mageupdate()
    e6.moveh(5,150)

    e7.shoot(18,35,imgs = "lightening") #this mage shoots, moves side to side and jumps
    e7.mageupdate()
    e7.moveh(7,230)
    e7.jump(-9,40)


    platforms.update()
    play.update() #updates in that order
    projectiles.update()
    enemies.update()
    friend_projectiles.update()
    p2.sidemove(400,6,moving_platforms1)
    p3.sidemove(400,8,moving_platforms2)
    p4.sidemove(400,7,moving_platforms3)
    
    play.check_powerup()
    alive = play.check_enemy_collisions()


    if play.pos.y > dispy or alive == False:
        position = "singleplayer"
    else:
        position = "level6"

    screen.blit(backdrop7,(0,0))
    end = time.time()
    timer = button(grey,35,20,120,50,("Time: "))
    font = pygame.font.SysFont('comicsans', 40)   #adds text
    text = font.render(str(round(end - start,2)), 1, (0,0,0))
    timer.draw(screen)
    pygame.draw.rect(screen,grey, (135,20,100,50),0)
    screen.blit(text, (150,30))
    platforms.draw(screen)
    movement = p1.rect.x - oldpos
    record_or_play_replay(replay,play,movement,ghost)
    all_sprites.draw(screen)
    enemies.draw(screen)

    
    if play.show_end_screen:
        endd = button(grey,dispx/2-150,dispy/2,300,50,("Level Complete!!!"))
        endd.draw(screen)
        pygame.display.flip()        
        time.sleep(5)
        position = "singleplayer"
        global playerlvl
        if playerlvl == 6:
            playerlvl += 1
            save(playerlvl)

        best_time = get_time(6)
        if end - start < best_time:
            write_time(round(end-start,2),6) # saves the time

            write_replay(recording,"replay6.txt") #saves the replay 
    
    pygame.display.flip()

    return position


def level7(replay = False,ghost = False):
    oldpos = reference.rect.x

    e1.choose_state()
    e2.shoot(15,5,imgs = "meteor",path = "downwards") #fireball trail
    e2.pos.x += 4 #moves right

    spawn = play.spawn_wand() #checks if another wand should be added

    if spawn != None:
        p2 = wizardpowerup(spawn,388)
        powerups.add(p2)
        all_sprites.add(p2)


    platforms.update()
    play.update()
    projectiles.update()
    enemies.update()
    friend_projectiles.update()
    
    for i in play.projectiles:  #check if a projectile hit the dragon
        hit_dragon = i.check_dragon()
        if hit_dragon:
            e1.lives -= 1

    play.check_powerup()
    alive = play.check_enemy_collisions()

    if play.pos.y > dispy or alive == False:
        position = "singleplayer"
    else:
        position = "level7"


    #draw
    end = time.time()
    timer = button(grey,35,20,120,50,("Time: "))
    font = pygame.font.SysFont('comicsans', 40)   #adds text
    text = font.render(str(round((end - start),2)), 1, (0,0,0))
    timer.draw(screen)
    pygame.draw.rect(screen,grey, (135,20,100,50),0)
    screen.blit(text, (150,30))
    
    lives = button(grey,1050,20,120,50,("Lives: ")) #creates the lives display
    text = font.render(str(e1.lives), 1, (0,0,0))
    lives.draw(screen)
    pygame.draw.rect(screen,grey, (1150,20,100,50),0)
    screen.blit(text, (1165,30))

    if e1.total_distance > 1000 and e1.title == 1:
        e1.title = 2
    elif e1.total_distance > 4500 and e1.title == 2:
        e1.title = 3
    elif not e1.alive:
        e1.title = 4
    
    if e1.title == 1:
        title = button(grey,290,20,700,50,("Welcome to final battle, but you will never win..."))
        title.draw(screen)
        
    elif e1.title == 2:

        title = button(grey,290,20,700,50,("Reach the wand to kill the dragon"))
        title.draw(screen)
    elif e1.title == 3:
        title = button(grey,290,20,700,50,("Finish him!!!"))
        title.draw(screen)

    elif e1.title == 4:
        title = button(grey,290,20,700,50,("Congratualations, You have made it"))
        title.draw(screen)
        
    platforms.draw(screen)
    movement = reference.rect.x - oldpos
    
    record_or_play_replay(replay,play,movement,ghost)
    
    #for i in e1.projectiles2: #shows the hitbox, use only for testing
    #i.show_hitbox()
    
    all_sprites.draw(screen)
    enemies.draw(screen)
    

    if e1.lives < 1: #dragon is dead
        if e1.alive:
            e1.alive = False
            tile = castle_sprite.get_image(96,768, 32, 32)
            p1 = platform(play.pos.x, 200, 64, 64,star) 
            finish_line.add(p1)
            platforms.add(p1)
            all_sprites.add(p1) #finish line
            
            p1 = platform(play.pos.x - 300, 350, 32, 32,tile,keycolor = white)
            platforms.add(p1) #adds platforms to reach star
            all_sprites.add(p1)
            p1 = platform(play.pos.x - 250, 250, 32, 32,tile,keycolor = white)
            platforms.add(p1)
            all_sprites.add(p1)
            p1 = platform(play.pos.x - 200, 150, 32, 32,tile,keycolor = white)
            platforms.add(p1)
            all_sprites.add(p1)
            p1 = platform(play.pos.x - 168, 150, 32, 32,tile,keycolor = white)
            platforms.add(p1)
            all_sprites.add(p1)
            p1 = platform(play.pos.x - 136, 150, 32, 32,tile,keycolor = white)
            platforms.add(p1)
            all_sprites.add(p1)
            p1 = platform(play.pos.x - 104, 150, 32, 32,tile,keycolor = white)
            platforms.add(p1)
            all_sprites.add(p1)
            p1 = platform(play.pos.x - 72, 150, 32, 32,tile,keycolor = white)
            platforms.add(p1)
            all_sprites.add(p1)
            p1 = platform(play.pos.x - 40, 150, 32, 32,tile,keycolor = white)
            platforms.add(p1)
            all_sprites.add(p1)
            
    if play.show_end_screen:
        endd = button(grey,dispx/2-250,dispy/2,500,50,("- You are a True Master -"))
        endd.draw(screen)
        endd2 = button(grey,dispx/2-250,dispy/2 + 50,500,50,("Thank you for playing"))
        endd2.draw(screen)
        endd3 = button(grey,dispx/2-250,dispy/2 + 100,500,50,("Made by Tyler Clark"))
        endd3.draw(screen)
        pygame.display.flip()
        pygame.mixer.music.stop()
        pygame.mixer.music.load("final_star.mp3") #load ending music
        pygame.mixer.music.play(-1)
        time.sleep(14)
        position = "singleplayer"
        global playerlvl
        if playerlvl == 7:
            playerlvl += 1
            save(playerlvl)
        best_time = get_time(7)
        if end - start < best_time:
            write_time(round((end-start),2),7) # saves the time

            write_replay(recording,"replay7.txt") #saves the replay 
    
    pygame.display.flip()

    return position

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
        
    def draw(self,screen,outline=None):  #method to draw the button
        if outline:   #decides if the button has an outline.
            pygame.draw.rect(screen, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0) #draws the button outline.
            #the outline is a black box which is slighly bigger than the button. This appears as an outline
            
        pygame.draw.rect(screen,self.current_colour, (self.x,self.y,self.width,self.height),0)
        #draws the button
        
        if self.text != "":   #only adds text if there is text to add
            font = pygame.font.SysFont('comicsans', 40)   #defines the font used.
            text = font.render(self.text, 1, (0,0,0))      #renders the text
            screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2))) 
            #puts the text in the center of the button.
            
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

class inputbox():
    def __init__(self, x, y, w, h,show, text=""):
        self.rect = pygame.Rect(x, y, w, h) #create the box
        self.color = blue #colour
        self.text = text #the text typed in
        self.data = ""   #what is shown on the bo
        self.txt_surface = FONT.render(text, True, green) #write text
        self.active = False   #is the input box  currently selected
        self.show = show  #if the text typed in should be shown

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # if the user clicked on the input_box rect
            if self.rect.collidepoint(event.pos):
                # toggle the active variable. This also changes the colour
                self.active = not self.active
            else:
                self.active = False
            #change the current color of the input box
            self.color = green if self.active else blue
        if event.type == pygame.KEYDOWN:  #when the user presses a key
            if self.active:
                if event.key == pygame.K_BACKSPACE: #removes a character
                    if len(self.text) > 10:
                        self.text = self.text[:-1]
                        self.data = self.data[:-1]
                else:
                    
                    if event.unicode in string.printable[:-6]: #checks character is valid

                        if self.show:
                            self.text += event.unicode  #adds a character
                        else:
                            self.text += "•"    #displays dots if a password
                        self.data += event.unicode #adds to the actual text they have typed
                # re-render the text
                self.txt_surface = FONT.render(self.text, True, green)
                
    def reset(self):
        self.txt_surface = FONT.render(self.text, True, green)
        
    def update(self):
        # resize the box if the text is too long
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rectangle.
        pygame.draw.rect(screen, self.color, self.rect, 2)


class spritesheet():
    def __init__(self,filename):
        self.spritesheet = pygame.image.load(os.path.join(img_folder,filename)).convert()
        #the spritesheet being used
        
    def get_image(self, x, y, width, height):
        # this cuts the image out of the spritesheet
        image = pygame.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image.set_colorkey(white)
        return image        


info = pygame.display.Info()
monitorx = 1280
monitory = 720
dispx, dispy = 1280,720
if dispx > monitorx: # scales screen down if too long
    dispy /= dispx / monitorx
    dispx = monitorx
if dispy > monitory: # scales screen down if too tall
    dispx /= dispy / monitory
    dispy = monitory
    
dispx = int(dispx) # So the resolution does not contain decimals
dispy = int(dispy)

screen = pygame.display.set_mode((dispx,dispy),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((800,600))

pygame.display.set_caption("Game")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
#sprites are objects

player1 = player()

position = "home"

f = open("progress.txt", "r") #gets what level the player is from the text document
playerlvl = int(f.readline())
f.close()

#home code:
singleplayer = button(grey,427,330,427,50,"Single Player")
multiplayer = button(grey,427,410,427,50,"Multiplayer")
quit_ = button(grey,427,490,427,50,"Quit")
connect = button(grey,917,30,317,50,"Connect to Server")
usertab = button(grey,917,100,317,50,"Current User: None")
logout = button(grey,50,30,317,50,"Logout")

volume_up = button(grey,370,660,100,50,">")
volume_change = button(grey,160,660,200,50,"Volume: " + str(volume)) # allows user to change the volume
volume_down = button(grey,50,660,100,50,"<")


background = pygame.image.load(os.path.join(img_folder,"background.png")).convert()
background = pygame.transform.scale(background, (1280, 720))
backgroundx = 0
title = pygame.image.load(os.path.join(img_folder,"title.png")).convert()
title.set_colorkey(black)
title = pygame.transform.scale(title, (960, 98))

#mode toggle button
mode = "normal" #can be normal or record. record shows best times and can play against and watch replays
mode_button = button(grey,1000,20,250,50,"Mode = Normal")
backtomenu = button(grey,35,20,100,50,"Back")

replay_button = button(grey,490,250,300,50,"Watch Replay")
wr_replay = button(grey,490,300,300,50,"Watch World Record")

controls = button(grey,30,250,250,50,"Show Controls") #toggle controls button

show_controls = False

controls2 = button(grey,30,325,250,50,"Move:") #show when controls toggle is on
controls3 = button(grey,30,375,250,50,"WASD or Arrows")
controls4 = button(grey,30,450,250,50,"Fire with wizard:")
controls5 = button(grey,30,500,250,50,"SPACE")
controls6 = button(grey,30,575,250,50,"Exit level:")
controls7 = button(grey,30,625,250,50,"ENTER")
controls8 = button(grey,420,625,400,50,"Press SPACE to start level")

#multiplayer code:
user = inputbox(int(dispx/2-250),int(dispy/2),1000,30,True,text = "Username: ")
passw = inputbox(int(dispx/2-250),int(dispy/2)+100,1000,30,False,text = "Password: ")
input_boxes = [user,passw]
submit = button(grey,int(dispx/2),int(dispy/2)+40,200,50,"Submit")


new_ip = inputbox(int(970),int(680),1500,30,True,text = ("ServerIP: " + ip)) #create ip input box

failure = button(grey,427,330,470,50,"Invalid details, please try again")


mlevel1 = button(grey,340,370,270,50,"Level 1")
wizardwarsm = button(grey,660,370,270,50,"Wizard Wars")
leaderboard_button = button(grey,505,510,270,50,"Leaderboards")
readyup = button(grey,780,410,270,50,"Ready Up")




#leaderboard buttons
#records = [[usernamelvl1,usernamelvl2...],[timelvl1,timelvl2...]]

download_in_progress = button(grey,340,250,600,50,"Download in Progress, Please Wait")
sending_in_progress = button(grey,340,250,600,50,"Sending in Progress, Please Wait")

download_help = button(grey,600,20,600,50,"(Press on the level to download replay)")

heading1 = button(grey,80,300,280,50,"Level")
heading2 = button(grey,360,300,280,50,"Username")
heading3 = button(grey,640,300,280,50,"Time")
heading4 = button(grey,920,300,280,50,"Your Time")

username1 = button(grey,360,350,280,50,str(records[0][0])) #defines buttons for leaderboards
username2 = button(grey,360,400,280,50,str(records[0][1]))
username3 = button(grey,360,450,280,50,str(records[0][2]))
username4 = button(grey,360,500,280,50,str(records[0][3]))
username5 = button(grey,360,550,280,50,str(records[0][4]))
username6 = button(grey,360,600,280,50,str(records[0][5]))
username7 = button(grey,360,650,280,50,str(records[0][6]))

time1 = button(grey,640,350,280,50,str(records[1][0]))
time2 = button(grey,640,400,280,50,str(records[1][1]))
time3 = button(grey,640,450,280,50,str(records[1][2]))
time4 = button(grey,640,500,280,50,str(records[1][3]))
time5 = button(grey,640,550,280,50,str(records[1][4]))
time6 = button(grey,640,600,280,50,str(records[1][5]))
time7 = button(grey,640,650,280,50,str(records[1][6]))

level1_button = button(grey,80,350,280,50,"Level 1")
level2_button = button(grey,80,400,280,50,"Level 2")
level3_button = button(grey,80,450,280,50,"Level 3")
level4_button = button(grey,80,500,280,50,"Level 4")
level5_button = button(grey,80,550,280,50,"Level 5")
level6_button = button(grey,80,600,280,50,"Level 6")
level7_button = button(grey,80,650,280,50,"Level 7")

your_record1 = button(grey,920,350,280,50,str(get_time(1))) #define buttons for the user's own times.
your_record2 = button(grey,920,400,280,50,str(get_time(2)))
your_record3 = button(grey,920,450,280,50,str(get_time(3)))
your_record4 = button(grey,920,500,280,50,str(get_time(4)))
your_record5 = button(grey,920,550,280,50,str(get_time(5)))
your_record6 = button(grey,920,600,280,50,str(get_time(6)))
your_record7 = button(grey,920,650,280,50,str(get_time(7)))


backdropm = pygame.image.load(os.path.join(img_folder,"background0.png")).convert()
backdropm = pygame.transform.scale(backdropm, (dispx, dispy))

player1image = (pygame.image.load(os.path.join(img_folder,"gsd1_fr1.gif")).convert())  #normal stance
player1image.set_colorkey(white)
player2image = (pygame.image.load(os.path.join(img_folder,"npc9_fr1.gif")).convert())
player2image.set_colorkey(white)
player3image = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player3image.set_colorkey(white)
player4image = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player4image.set_colorkey(white)

player1imager = (pygame.image.load(os.path.join(img_folder,"gsd1_lf1.gif")).convert()) #right 1
player1imager.set_colorkey(white)
player2imager = (pygame.image.load(os.path.join(img_folder,"npc9_lf1.gif")).convert())
player2imager.set_colorkey(white)
player3imager = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player3imager.set_colorkey(white)
player4imager = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player4imager.set_colorkey(white)

player1imageR = (pygame.image.load(os.path.join(img_folder,"gsd1_lf2.gif")).convert()) #right 2
player1imageR.set_colorkey(white)
player2imageR = (pygame.image.load(os.path.join(img_folder,"npc9_lf2.gif")).convert())
player2imageR.set_colorkey(white)
player3imageR = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player3imageR.set_colorkey(white)
player4imageR = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player4imageR.set_colorkey(white)

player1imagel = (pygame.image.load(os.path.join(img_folder,"gsd1_rt1.gif")).convert()) #left 1
player1imagel.set_colorkey(white)
player2imagel = (pygame.image.load(os.path.join(img_folder,"npc9_rt1.gif")).convert())
player2imagel.set_colorkey(white)
player3imagel = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player3imagel.set_colorkey(white)
player4imagel = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player4imagel.set_colorkey(white)

player1imageL = (pygame.image.load(os.path.join(img_folder,"gsd1_rt2.gif")).convert()) #left 2
player1imageL.set_colorkey(white)
player2imageL = (pygame.image.load(os.path.join(img_folder,"npc9_rt2.gif")).convert())
player2imageL.set_colorkey(white)
player3imageL = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player3imageL.set_colorkey(white)
player4imageL = (pygame.image.load(os.path.join(img_folder,"mage.png")).convert())
player4imageL.set_colorkey(white)
#singleplayer map code:

backtomenu = button(grey,35,20,100,50,"Back")

map_ = pygame.image.load(os.path.join(img_folder,"grass.png")).convert()
map_ = pygame.transform.scale(map_, (1580, 720))
base = pygame.image.load(os.path.join(img_folder,"startbase.png")).convert()
base = pygame.transform.scale(base, (192, 161))
pad = pygame.image.load(os.path.join(img_folder,"pad.png")).convert()
pad = pygame.transform.scale(pad, (85, 45))
pad.set_colorkey(white)

donepad = pygame.image.load(os.path.join(img_folder,"padfinished.png")).convert()
donepad = pygame.transform.scale(donepad, (85, 45))
donepad.set_colorkey(white)

castle4 = pygame.image.load(os.path.join(img_folder,"castle4.png")).convert()
castle4 = pygame.transform.scale(castle4, (192, 161))
castle4.set_colorkey(black)
castle7 = pygame.image.load(os.path.join(img_folder,"castle7.png")).convert()
castle7 = pygame.transform.scale(castle7, (192, 161))
castle7.set_colorkey(black)
path = pygame.image.load(os.path.join(img_folder,"path.png")).convert()
path = pygame.transform.scale(path, (20, 20))
front1 = pygame.image.load(os.path.join(img_folder,"avt1_fr1.gif")).convert()
front1.set_colorkey(white)

castle8 = pygame.image.load(os.path.join(img_folder,"castle.png")).convert()
castle8 = pygame.transform.scale(castle8, (192, 161))
castle8.set_colorkey(black)

#game graphics

sprites = spritesheet("BODY_skeleton.png")
spriteplatform = spritesheet("floatplatforms.png")
spriteplatform2 = spritesheet("platformspritesheet.png")
enemysprites = spritesheet("rpgcritters2.png")
enemysprites2 = spritesheet("9RPGenemies.PNG")
spriteplatform3 = spritesheet("spritesheet3.png")
catsprites = spritesheet("cat.png")
level2sprites = spritesheet("level1grass.png")
wolves_img = spritesheet("wolfsheet1.png")
volcano_sprites = spritesheet("volcano_spritesheet.png")
castle_sprite = spritesheet("castle_tile.png")
dragon_sprites = spritesheet("wyvern_fire.png")

level2platforms = spritesheet("newlevel2.png")

winterplatform = pygame.image.load(os.path.join(img_folder,"winterplatform.png")).convert()

grassplatform = pygame.image.load(os.path.join(img_folder,"grassplatform.png")).convert()
desertplatform2 = pygame.image.load(os.path.join(img_folder,"desertplatform2.png")).convert()

sandtile = pygame.image.load(os.path.join(img_folder,"sandtile.png")).convert()

icecube = pygame.image.load(os.path.join(img_folder,"ice.png")).convert()

pipe = pygame.image.load(os.path.join(img_folder,"pipe.png")).convert()
pipe = pygame.transform.scale(pipe, (55, 64))
pipe.set_colorkey(white)

star = pygame.image.load(os.path.join(img_folder,"star.png")).convert()
star = pygame.transform.scale(star, (64, 64))
star.set_colorkey(black)

backdrop1 = pygame.image.load(os.path.join(img_folder,"backdrop11.jpeg")).convert()
backdrop1 = pygame.transform.scale(backdrop1, (dispx, dispy))

backdrop2 = pygame.image.load(os.path.join(img_folder,"newlevel2backdrop.png")).convert()
backdrop2 = pygame.transform.scale(backdrop2, (dispx, dispy))

backdrop3 = pygame.image.load(os.path.join(img_folder,"level1backdrop.png")).convert()
backdrop3 = pygame.transform.scale(backdrop3, (dispx, dispy))

backdrop5 = pygame.image.load(os.path.join(img_folder,"level2backdrop.png")).convert()
backdrop5 = pygame.transform.scale(backdrop5, (dispx, dispy))

backdrop6 = pygame.image.load(os.path.join(img_folder,"backdrop3.png")).convert()
backdrop6 = pygame.transform.scale(backdrop6, (dispx, dispy))

backdrop7 = pygame.image.load(os.path.join(img_folder,"bg_volcano.png")).convert()
backdrop7 = pygame.transform.scale(backdrop7, (dispx, dispy))

sound_playing = False

mapx = 180
mapy = 190
move = 0
playerpos = 0
no_move = 0  #stops the player from accidentally moving on the map

def mapmove(direct,mapx,mapy,move): #moves the player the given distance in the given direction
    if direct=="right":
        return mapx+5,mapy
    elif direct=="left":
        return mapx-5,mapy
    elif direct=="up":
        return mapx,mapy-5
    elif direct=="down":
        return mapx,mapy+5



def scrollbackground(background,x,width,height): #makes the background move
    rel_x = x % background.get_rect().width
    screen.blit(background, (rel_x - background.get_rect().width, 0))
    if rel_x < width:
            screen.blit(background, (rel_x, 0))
    x -= 1
    return x

running = True
replay_sound_playing = False

pygame.mixer.music.load("Rise of spirit.mp3") #plays the background music
pygame.mixer.music.play(-1) #makes the music automatically repeat


while running:
    
    clock.tick(fps) #makes game run at a set frames per second
    #these are all the positions where the standard music is used
    if position=="home" or position=="singleplayer" or position == "multiplayer" or position == "multiplayer2" or position == "multiplayer_failure" or position=="lobby" or position == "leaderboard":
        if not sound_playing:
        
            pygame.mixer.music.stop()
            pygame.mixer.music.load("Rise of spirit.mp3")
            pygame.mixer.music.play(-1)
            sound_playing = True
            replay_sound_playing = False #shows the replay sound isnt running since the map screen music is

    else:

        if not replay_sound_playing and replay_mode:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("replay_music.mp3") #makes the replay music play during replays
            pygame.mixer.music.play(-1)
            replay_sound_playing = True

            sound_playing = False

    if position=="home" or position=="singleplayer" or position == "multiplayer" or position == "multiplayer2" or position == "multiplayer_failure" or position=="lobby" or position == "leaderboard":
        for event in pygame.event.get(): # checks for all events
            if position == "home":
                quit_.hover()
                singleplayer.hover()
                multiplayer.hover()
                connect.hover()
                logout.hover()
                
                volume_change.hover()
                volume_up.hover() #makes volume buttons hoverable
                volume_down.hover()
                
                if not connected:
                    new_ip.handle_event(event)

                if volume_up.press() and volume < 10: #increase volume
                    volume += 1
                    pygame.mixer.music.set_volume(volume/10) #set new volume
                    volume_change = button(grey,160,660,200,50,"Volume: " + str(int(volume))) #change label

                elif volume_down.press() and volume > 0: #decrease volume
                    volume -= 1
                    pygame.mixer.music.set_volume(volume/10) 
                    volume_change = button(grey,160,660,200,50,"Volume: " + str(int(volume)))
                    
                    


                if username == None:
                    usertab.hover()
                    if logout.press() and connected:
                        username = None
                        position = "multiplayer" #allows user to try and log in
                else:
                    if logout.press(): #logs the user out
                        username = None
                        send_to_server("LOGOUT--")
                        user.data = ""
                        user.text = "Username: "
                        user.reset() #reset the text boxes
                        passw.data = ""
                        passw.text = "Password: "
                        passw.reset()
                        
                if connected: #changes colour of button and text in the button
                    connect.colour = green
                    connect.text = "Connected"
                else:
                    connect.colour = red
                    connect.text = "Connect to server"
                    username = None
                    
                if quit_.press():
                    running = False #exits the game loop
                    
                elif singleplayer.press():
                    position = "singleplayer" #changes the player's position
                    
                elif multiplayer.press() and connected:
                    if username == None:
                        position = "multiplayer"
                    else:
                        position = "multiplayer2"
                        send_to_server("RATING--") #gets the new rating
                        game_info = [[-100,-100,"s"],[-100,-100,"s"],[-100,-100,"s"],[-100,-100,"s"]]
                        #resets player positions
                        
                elif usertab.press():
                    if username == None and connected: #moves player to multiplayer
                        position = "multiplayer"
                        
                elif connect.press() and not connected:
                    print("Connecting") #attempts to connect to server
                    udp_client,client,addr,connected = connect_to_server()

            elif position == "multiplayer_failure": #creates a screen with just a button allowing them to go back
                failure.hover()
                if failure.press(): #takes the username back to the log in page
                    position="multiplayer"

            elif position == "leaderboard":
                
                backtomenu.hover()
                
                level1_button.hover()
                level2_button.hover()
                level3_button.hover() #allows hover function on buttons which allow world records to be downloaded
                level4_button.hover()
                level5_button.hover()
                level6_button.hover()
                level7_button.hover()
                if backtomenu.press():
                    position = "multiplayer2"

                elif level1_button.press() and not downloading and not sending:
                    send_to_server("REPLAYr1") #requests to download a record
                    downloading = True
                    
                elif level2_button.press() and not downloading and not sending:
                    send_to_server("REPLAYr2")
                    downloading = True

                elif level3_button.press() and not downloading and not sending:
                    send_to_server("REPLAYr3")
                    downloading = True

                elif level4_button.press() and not downloading and not sending:
                    send_to_server("REPLAYr4")
                    downloading = True

                elif level5_button.press() and not downloading and not sending:
                    send_to_server("REPLAYr5")
                    downloading = True

                elif level6_button.press() and not downloading and not sending:
                    send_to_server("REPLAYr6")
                    downloading = True

                elif level7_button.press() and not downloading and not sending:
                    send_to_server("REPLAYr7")
                    downloading = True
                    
            elif position == "multiplayer2":
                backtomenu.hover()
                mlevel1.hover() #differenet levels
                wizardwarsm.hover()
                leaderboard_button.hover() #leaderboards
                
                if backtomenu.press():
                    position="home" #back to main menu

                elif leaderboard_button.press():
                    your_record1 = button(grey,920,350,280,50,str(get_time(1)))
                    your_record2 = button(grey,920,400,280,50,str(get_time(2))) #updates the buttons for any new records set while playing this session
                    your_record3 = button(grey,920,450,280,50,str(get_time(3)))
                    your_record4 = button(grey,920,500,280,50,str(get_time(4)))
                    your_record5 = button(grey,920,550,280,50,str(get_time(5)))
                    your_record6 = button(grey,920,600,280,50,str(get_time(6)))
                    your_record7 = button(grey,920,650,280,50,str(get_time(7)))
                    for i in range(7):
                        send_to_server("MYRECORD" + str(i + 1) + str(get_time(i + 1))) #sends the time, and which level it is for


                    send_to_server("REQUEST-") #requests the leaderboards
                    position = "leaderboard"

                elif mlevel1.press():
                    position = "lobby" #changes position to the lobby
                    game_type = "level1m"
                    print((str(username)+" has connected to the lobby"))
                    send_to_server("JOINL1--") #tells the server they have joined the lobby

                elif wizardwarsm.press(): #moves player to wizard wars lobby
                    position="lobby"
                    game_type = "wizardwars"
                    print((str(username)+" has connected to the lobby"))
                    send_to_server((str(username)+" has connected to the lobby"))
                    send_to_server("JOINL2--")
                        
            elif position == "lobby": #leave the lobby
                backtomenu.hover()
                readyup.hover()
                if backtomenu.press():
                    if lobby1done:
                        send_to_server("UNREADY1") #remove ready-up
                        lobby1done = False
                    send_to_server("LEAVE1--")  #tells server they have left the lobby
                    lobby1 = [] #reset these lists
                    lobby1r = []
                    lobby1ready="0"
                    position = "multiplayer2"
                    
                elif readyup.press():
                    if not lobby1done: #checks they haven't already done it
                        send_to_server("READY1--")

                    
            elif position == "multiplayer":
                backtomenu.hover()
                submit.hover()
                if backtomenu.press():
                    position="home"
                if submit.press():

                    if len(passw.data) > 6 and "`" not in user.data and "`" not in passw.data: #checks the length of the password
                        #checks the user has not entered the end
                        send_to_server(str("USERNAME" + user.data)) #sends username
                        time.sleep(0.2) #stops to wait to recieve the salt
                        m = hashlib.sha256()
                        try:
                            m.update((passw.data+yoursalt).encode()) #hash the password and salt
                            cipher = m.digest()
                            send_to_server(str("PASSWORD" + str(cipher))) #sends the hash
                        except Exception as e:
                            print(e)
                            position = "multiplayer_failure"
                    else:
                        position = "multiplayer_failure"
                    
                for box in input_boxes: #handles changes to the input boxes such as typing
                    box.handle_event(event)


            elif position == "singleplayer":
                if replay_mode: #swaps these back to default values
                    replay_mode = False
                    
                if wr_mode:
                    wr_mode = False
                if no_move > 0: #timer which stops players accidentally moving
                    no_move -= 1
                    
                backtomenu.hover()
                if backtomenu.press():
                    position = "home" #takes user back to home page
                    
                if playerlvl > playerpos:
                    mode_button.hover()
                    if mode_button.press():
                        if mode == "normal": #toggles between normal and speedrun mode
                            mode = "speedrun"
                        else:
                            mode = "normal"
                        mode_button = button(grey,1000,20,250,50,"Mode = "+mode)
                        
                replay_button.hover()
                if replay_button.press(): #allows user to watch replay
                    position = "level" + str(playerpos)
                    replay_mode = True
                    setup = True
                    mode = "normal" #user can't be in both replay and speedrun mode
                    mode_button = button(grey,1000,20,250,50,"Mode = "+mode)

                wr_replay.hover()
                if wr_replay.press(): #watch world record
                    position = "level" + str(playerpos)
                    replay_mode = True
                    setup = True
                    mode = "normal"
                    wr_mode = True

                    
                controls.hover()
                if controls.press():
                    show_controls = not show_controls #toggles the controls
                    if show_controls:
                         controls = button(grey,30,250,250,50,"Hide Controls") #changes text on the button
                    else:
                         controls = button(grey,30,250,250,50,"Show Controls")

                #this section below handles the user moving around the map
                #the user can only move in set places to follow the paths
                    
                pressed = pygame.key.get_pressed() #gets the keys pressed
                if playerpos == 0:
                    if (pressed[pygame.K_d] or pressed[pygame.K_RIGHT]) and move == 0 and no_move == 0:  
                        move = 28 #distance to move
                        map_direction = "right" #direction to move
                        playerpos = 1 #new playerpos after moving
                elif playerpos == 1:
                    if (pressed[pygame.K_a] or pressed[pygame.K_LEFT]) and move == 0 and no_move == 0:
                        move = 28
                        map_direction = "left"
                        playerpos = 0
                    if (pressed[pygame.K_s] or pressed[pygame.K_DOWN]) and move == 0 and playerlvl > 1 and no_move == 0:
                        move = 30
                        map_direction = "down"
                        playerpos = 2
                        
                    if pressed[pygame.K_SPACE] and move == 0:
                        position = "level1" #changes the position to the given level
                        setup = True #indicates the game needs to be set up.
                        
                        sound_playing = False
                        pygame.mixer.music.stop() #stops the current music
                        pygame.mixer.music.load("A_wintertale.mp3") 
                        pygame.mixer.music.play(-1) #plays and loops the new music
                elif playerpos == 2:
                    if (pressed[pygame.K_w] or pressed[pygame.K_UP]) and move == 0 and no_move == 0:
                        move = 30
                        map_direction = "up" #moves the player
                        playerpos = 1
                    if (pressed[pygame.K_s] or pressed[pygame.K_DOWN]) and move == 0 and playerlvl > 2 and no_move == 0:
                        move = 30
                        map_direction = "down"
                        playerpos = 3
                    if pressed[pygame.K_SPACE] and move == 0:
                        position = "level2"
                        setup = True
                        sound_playing = False
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("jungle_music.mp3")
                        pygame.mixer.music.play(-1)
                elif playerpos == 3:
                    if (pressed[pygame.K_w] or pressed[pygame.K_UP]) and move == 0 and no_move == 0:
                        move = 30
                        map_direction = "up"
                        playerpos = 2
                    if (pressed[pygame.K_d] or pressed[pygame.K_RIGHT]) and move == 0 and playerlvl > 3 and no_move == 0:
                        move = 104
                        map_direction = "right"
                        playerpos = 4
                    if pressed[pygame.K_SPACE] and move == 0:
                        position = "level3"
                        setup = True
                        sound_playing = False
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("Snowland.mp3")
                        pygame.mixer.music.play(-1)               
                elif playerpos == 4:
                    if (pressed[pygame.K_w] or pressed[pygame.K_UP]) and move == 0 and playerlvl > 4 and no_move == 0:
                        move = 30
                        map_direction = "up"
                        playerpos = 5
                    if (pressed[pygame.K_a] or pressed[pygame.K_LEFT]) and move == 0 and no_move == 0:
                        move = 104
                        map_direction = "left"
                        playerpos = 3
                    if pressed[pygame.K_SPACE] and move == 0:
                        position = "level4"
                        setup = True
                        sound_playing = False
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("Desert_Mystic.mp3")
                        pygame.mixer.music.play(-1)
                elif playerpos == 5:
                    if (pressed[pygame.K_w] or pressed[pygame.K_UP]) and move == 0 and playerlvl > 5 and no_move == 0:
                        move = 30
                        map_direction = "up"
                        playerpos = 6
                    if (pressed[pygame.K_s] or pressed[pygame.K_DOWN]) and move == 0 and no_move == 0:
                        move = 30
                        map_direction = "down"
                        playerpos = 4


                    if pressed[pygame.K_SPACE] and move == 0:
                        position = "level5"
                        setup = True
                        sound_playing = False
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("crypt.wav") #add new music
                        pygame.mixer.music.play(-1)                        
                elif playerpos == 6:
                    if (pressed[pygame.K_s] or pressed[pygame.K_DOWN]) and move == 0 and no_move == 0:
                        move = 30
                        map_direction = "down"
                        playerpos = 5
                    if (pressed[pygame.K_d] or pressed[pygame.K_RIGHT]) and move == 0 and playerlvl > 6 and no_move == 0:
                        move = 40
                        map_direction = "right"
                        playerpos = 7

                    if pressed[pygame.K_SPACE] and move == 0:
                        position = "level6"
                        setup = True
                        sound_playing = False
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("lava_land.mp3") #add new music
                        pygame.mixer.music.play(-1)   
                elif playerpos == 7:
                    if (pressed[pygame.K_a] or pressed[pygame.K_LEFT]) and move == 0 and no_move == 0:
                        move = 40
                        map_direction = "left"
                        playerpos = 6
                    if pressed[pygame.K_SPACE] and move == 0:
                        position = "level7"
                        setup = True
                        sound_playing = False
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("queen_of_the_night.mp3") #add new music
                        pygame.mixer.music.play(-1)
                        
    if position == "multiplayer":
        for box in input_boxes:
            box.update()        

    screen.fill(black)
    if position == "home" or position == "multiplayer" or position == "multiplayer_failure" or position == "multiplayer2" or position=="lobby" or position == "leaderboard":
        backgroundx = scrollbackground(background,backgroundx,dispx,dispy)#makes the background move in screens that need it

        
    if position == "home":
        new_ip.update()
        if username == None:
            usertab.text = "Current User: None" #shows username if they are logged in, otherwise just display None
        else:
            usertab.text = "Current User: " + str(username)
            
        singleplayer.draw(screen,(0,0,0))
        multiplayer.draw(screen,(0,0,0)) #draw buttons on home page
        quit_.draw(screen,(0,0,0))
        connect.draw(screen,(0,0,0))
        screen.blit(title, (160,180))
        usertab.draw(screen,(0,0,0))
        volume_change.draw(screen,(0,0,0))
        volume_up.draw(screen,(0,0,0))
        volume_down.draw(screen,(0,0,0))

        new_ip.draw(screen)
        if username != None: #button text changes depending on if the user is logged in
            logout.text = "Logout"
        else:
            logout.text = "Logged Out"
        logout.draw(screen,(0,0,0))
        
    elif position == "multiplayer_failure":
        failure.draw(screen,(0,0,0))
        screen.blit(title, (160,180)) #tells user they were unable to log in
        
    elif position == "lobby":
        screen.blit(title, (160,180))
        
        backtomenu.draw(screen,(0,0,0))
        
        pygame.draw.rect(screen, black, (180-2,280-2,530+4,300+4),0) #draw box outline
        pygame.draw.rect(screen,grey, (180,280,530,300),0) #draw grey box
        
        try:#this try except stops crash if this runs before server sends data
            screen.blit((pygame.font.Font(None, 48)).render(("Users in Lobby:    Ready ups:"+str(lobby1ready)), True, (0,0,0)), (200, 300))  #sub title 
            for i in range(len(lobby1)): #shows all the users in the lobby
                screen.blit((pygame.font.Font(None, 42)).render(lobby1[i], True, (0,0,0)), (200, 340+i*40))  #displays users below one another
                screen.blit((pygame.font.Font(None, 42)).render(lobby1r[i], True, (0,0,0)), (400, 340+i*40))  #displays users below one another
            readyup.draw(screen,(0,0,0))#draws the ready-up button
        except Exception as e:
            print("error displaying lobby",e)



        
    elif position == "multiplayer2":
        mlevel1.draw(screen,(0,0,0)) #draw buttons
        leaderboard_button.draw(screen,(0,0,0))
        wizardwarsm.draw(screen,(0,0,0))
        backtomenu.draw(screen,(0,0,0))
        screen.blit(title, (160,180))
        
    elif position == "multiplayer":       
        screen.blit(title, (160,180))
        backtomenu.draw(screen,(0,0,0))
        submit.draw(screen,(0,0,0))
        for box in input_boxes:
            box.draw(screen)

        

    if position != "singleplayer" and position != "home":
        no_move = 4 #during testing, users found it to be annoying that they would move on the map as they
                    #were still holding a move key from in game. This delays that action, therefore preventing it
        
    if position == "level1m":
        if setup:
            #entities
            pygame.mixer.music.stop()
            pygame.mixer.music.load("level1m.ogg") 
            pygame.mixer.music.play(-1)
            play = player()
            start = time.time()
            e1 = turtle(1030,100,ids = "e1 ") #ids is used to tell the server when an enemy has been killed
            e2 = turtle(1390,100,ids = "e2 ")
            e3 = turtle(2450,505,ids = "e3 ")
            e4 = turtle(2510,100,ids = "e4 ")
            e5 = turtle(2710,100,ids = "e5 ")
            e6 = mage(2970,100,ids = "e6 ")
            e7 = mage(4320,350,ids = "e7 ")
            e8 = mage(4080,460,ids = "e8 ")
            e9 = mage(4330,570,ids = "e9 ")
            e10 = mage(5250,500,ids = "e10",newimage = "angel")
            #setup
            setup = False
            #platforms
            platforms = pygame.sprite.Group()
            powerups = pygame.sprite.Group()
            finish_line = pygame.sprite.Group()   #creates all groups needed for the level
            enemies = pygame.sprite.Group()
            projectiles = pygame.sprite.Group()

            all_sprites = pygame.sprite.Group()
            enemies.add(e1)
            enemies.add(e2)
            enemies.add(e3)
            enemies.add(e4)
            enemies.add(e5)
            enemies.add(e6)
            enemies.add(e7)
            enemies.add(e8)
            enemies.add(e9)
            enemies.add(e10) 
            for i in enemies:       
                all_sprites.add(i)
            for i in powerups:
                all_sprites.add(i)   #adds all enemies and powerups to the all_sprites group
                
            p1 = platform(330, 426, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p1)

            p2 = platform(650, 386, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p2)

            p3 = platform(1020, 386, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p3)

            p4 = platform(1220, 436, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p4)            

            p5 = platform(1380, 326, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p5)

            p6 = platform(1690, 526, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p6)

            p7 = platform(2020, 625, 350, 85,spriteplatform2.get_image(83,876,601,146)) #these are the first groud tiles
            platforms.add(p7) #slight pixel overlap 25

            p8 = platform(2340, 625, 350, 85,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p8)

            p9 = platform(2440, 525, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p9)

            p10 = platform(2150, 425, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p10)

            p11 = platform(2000, 325, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p11)

            p12 = platform(2240, 275, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p12)

            p13 = platform(2500, 275, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p13)

            p14 = platform(2700, 375, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p14)

            p15 = platform(2900, 275, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p15)

            p16 = platform(3100, 375, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p16)

            p17 = platform(3300, 475, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p17)

            p18 = platform(3500, 575, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p18)

            p19 = platform(3700, 625, 350, 85,spriteplatform2.get_image(83,876,601,146)) #more grouns tiles
            platforms.add(p19)

            p20 = platform(4025, 625, 350, 84,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p20)


            p21 = platform(4200, 575, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p21)

            p22 = platform(4000, 450, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p22)

            p23 = platform(4200, 325, 150, 36,spriteplatform2.get_image(83,876,601,146)) #these 3 are where the mages sit
            platforms.add(p23)

            p24 = platform(4400, 305, 150, 36,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p24)

            p25 = platform(4625, 625, 350, 84,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p25)

            p26 = platform(4950, 625, 350, 84,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p26)

            p27 = platform(5275, 625, 350, 84,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p27)

            p28 = platform(5725, 650, 32, 32,star) 
            platforms.add(p28)
            finish_line.add(p28)
            
            for i in platforms:       
                all_sprites.add(i)  #adds all platforms to the group
              
            all_sprites.add(play) #adds the player to the group
        play,position = level1m(play)   #starts the game by calling the function  


    if position == "wizardwars":
        if setup:
            #entities
            pygame.mixer.music.stop()
            pygame.mixer.music.load("level1m.ogg") 
            pygame.mixer.music.play(-1)
            platforms = pygame.sprite.Group()
            powerups = pygame.sprite.Group()
            finish_line = pygame.sprite.Group()   #creates all groups needed for the level
            enemies = pygame.sprite.Group()
            projectiles = pygame.sprite.Group()
            friend_projectiles = pygame.sprite.Group()
            if spawnpoint == "0":
                play = player(start_location_y = 100,start_location_offset_x = -510)
            elif spawnpoint == "1":
                play = player(start_location_y = 100,start_location_offset_x = 300)
            elif spawnpoint == "2":
                play = player(start_location_y = 450,start_location_offset_x = -645)
            elif spawnpoint == "3":
                play = player(start_location_y = 450,start_location_offset_x = 400)
            play.state = "wizard"
            start = time.time() #starts timer
            setup = False
            play.pos.y = 5000 #have to kill the player to move them


            all_sprites = pygame.sprite.Group()
            for i in powerups:
                all_sprites.add(i)   #adds all enemies and powerups to the all_sprites group   ..... #spriteplatform takes x,y,width,height


            p1 = platform(80, 525, 69, 34,spriteplatform.get_image(175,416,69,34))#top row
            platforms.add(p1) #small platform low left

            p1 = platform(1125, 525, 69, 34,spriteplatform.get_image(175,416,69,34))#top row
            platforms.add(p1) #small platform low right

            p1 = platform(605, 450, 69, 34,spriteplatform.get_image(175,416,69,34))#top row
            platforms.add(p1) #small platform middle

            p1 = platform(-355, 400, 69, 34,spriteplatform.get_image(175,416,69,34))#top row
            platforms.add(p1) #small platform high left

            p1 = platform(1585, 400, 69, 34,spriteplatform.get_image(175,416,69,34))#top row
            platforms.add(p1) #small platform high right

            p1 = platform(-425, 310, 69, 34,spriteplatform.get_image(175,416,69,34))#top row
            platforms.add(p1) #small platform high left outer

            p1 = platform(1645, 310, 69, 34,spriteplatform.get_image(175,416,69,34))#top row
            platforms.add(p1) #small platform high right outer
                
            p1 = platform(-215, 250, 250, 61,spriteplatform2.get_image(83,876,601,146))#top row
            platforms.add(p1)

            p1 = platform(355, 200, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p1)

            p1 = platform(675, 200, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p1)

            p1 = platform(1245, 250, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p1)

            p1 = platform(-265, 450, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p1)#far left outside

            p1 = platform(1295, 450, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p1)#far right outside 

            p1 = platform(915, 310, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p1) #top sides

            p1 = platform(115, 310, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p1) #top sides

            p1 = platform(35, 650, 250, 61,spriteplatform2.get_image(83,876,601,146))#bottom row
            platforms.add(p1)

            p1 = platform(995, 650, 250, 61,spriteplatform2.get_image(83,876,601,146))
            platforms.add(p1)

            p1 = platform(515, 500, 250, 61,spriteplatform2.get_image(83,876,601,146))#middle
            platforms.add(p1)

            p1 = platform(295, 380, 250, 61,spriteplatform2.get_image(83,876,601,146))#high
            platforms.add(p1)

            p1 = platform(735, 380, 250, 61,spriteplatform2.get_image(83,876,601,146))#high
            platforms.add(p1)

            p1 = platform(295, 580, 250, 61,spriteplatform2.get_image(83,876,601,146))#2nd low
            platforms.add(p1)

            p1 = platform(735, 580, 250, 61,spriteplatform2.get_image(83,876,601,146))#2nd low
            platforms.add(p1)   
            
            for i in platforms:       
                all_sprites.add(i)  #adds all platforms to the group
              
            all_sprites.add(play) #adds the player to the group

            
        play,position = wizardwars(play)


    if replay_mode:
        pygame.event.get()

    if position == "level1":
        if setup: #sets up the level
            play = player()
            setup = False
            all_sprites = pygame.sprite.Group()
            all_sprites.add(play)
            
            recording = []

            start = time.time()
            
            e1 = wolf(1900,0)
            
            e2 = wolf(2375,0) #create different enemy objects
            e3 = wolf(3050,0)
            e4 = wolf(4100,0)
            e5 = wolf(4100,0)
            
            p1 = wizardpowerup(3376,54)

            platforms = pygame.sprite.Group()
            
            powerups = pygame.sprite.Group()
            powerups.add(p1)

            friend_projectiles = pygame.sprite.Group()
            projectiles = pygame.sprite.Group() #remake these group
            ladders = pygame.sprite.Group()
            
            finish_line = pygame.sprite.Group()
            
            enemies = pygame.sprite.Group()

            enemies.add(e1)            
            enemies.add(e2)
            enemies.add(e3) #add the different enemies
            enemies.add(e4)
            enemies.add(e5)
            
            for i in enemies:       
                all_sprites.add(i)
                
            for i in powerups:
                all_sprites.add(i)
                
            for i in range(17): #floor tiles
                p1 = platform(330 + i * 280, 630, 300, 100,winterplatform,keycolor = white) #x,y,width,height
                platforms.add(p1) 

            p1 = platform(600, 566, 64, 64,icecube,keycolor = white)
            platforms.add(p1) 
            p1 = platform(664, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)  #first two platforms

            #step backwards to first big platform
            p1 = platform(792, 566, 64, 64,icecube,keycolor = white)
            platforms.add(p1)            

            p1 = platform(900, 502, 64, 64,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(1050, 438, 64, 64,icecube,keycolor = white) #two floating platforms
            platforms.add(p1)

            p1 = platform(1200, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(1200, 374, 128, 128,icecube,keycolor = white) #two big platforms
            platforms.add(p1)
            p1 = platform(1328, 438, 64, 64,icecube,keycolor = white) #step up to the two big platforms
            platforms.add(p1)

            p1 = platform(1328, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1) #ice floor platforms
            p1 = platform(1456, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            
            p1 = platform(1584, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)

            p1 = platform(1648, 438, 64, 64,icecube,keycolor = white)
            platforms.add(p1) #small step up platform
            p1 = platform(1712, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            
            p1 = platform(1712, 374, 128, 128,icecube,keycolor = white)
            platforms.add(p1) #raised ice platforms
            p1 = platform(1840, 374, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(1968, 374, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2096, 374, 128, 128,icecube,keycolor = white)
            platforms.add(p1)

            #really high platforms
            p1 = platform(1840, 246, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(1968, 246, 128, 128,icecube,keycolor = white)
            platforms.add(p1)

            #steps up and down from very high platform
            p1 = platform(1776, 310, 64, 64,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2096, 310, 64, 64,icecube,keycolor = white)
            platforms.add(p1)            

            #step down to lower ice platform
            p1 = platform(2224, 438, 64, 64,icecube,keycolor = white)
            platforms.add(p1)            
            

            p1 = platform(1840, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1) #lower ice platforms
            p1 = platform(1968, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2096, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2224, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2352, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2480, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)

            #staircase
            p1 = platform(2608, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2736, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2736, 374, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2864, 502, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2864, 374, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2864, 246, 128, 128,icecube,keycolor = white)
            platforms.add(p1)
            for j in range(4):
                for i in range(4): #use a for loop to create the 4 platforms, on 4 different columns
                    p1 = platform(2992 + j * 128, 502 - i*128, 128, 128,icecube,keycolor = white)
                    platforms.add(p1)                

            p1 = platform(2672, 438, 64, 64,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2800, 310, 64, 64,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(2928, 182, 64, 64,icecube,keycolor = white)
            platforms.add(p1)

            p1 = platform(3360, 86, 32, 32,icecube,keycolor = white)
            platforms.add(p1)            

            p1 = platform(3504, 246, 128, 128,icecube,keycolor = white)
            platforms.add(p1) #first platform after drop
            for i in range(2):
                p1 = platform(3504 + i * 128, 374, 128, 128,icecube,keycolor = white)
                platforms.add(p1) #ice platforms layer 2 after drop           
            for i in range(3):
                p1 = platform(3504 + i * 128, 502, 128, 128,icecube,keycolor = white)
                platforms.add(p1) #ice floor platforms after drop

            #steps
            p1 = platform(3504, 182, 64, 64,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(3632, 310, 64, 64,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(3760, 438, 64, 64,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(3888, 566, 64, 64,icecube,keycolor = white)
            platforms.add(p1)

            #final jumps

            p1 = platform(4820, 242, 48, 48,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(4680, 350, 48, 48,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(4540, 458, 48, 48,icecube,keycolor = white)
            platforms.add(p1)
            p1 = platform(4400, 566, 48, 48,icecube,keycolor = white)#566
            platforms.add(p1)

            for i in range(3):
                p1 = platform(4900, 502 - i*128, 128, 128,icecube,keycolor = white)
                platforms.add(p1)                

            p1 = platform(5246, 650, 32, 32,star)
            platforms.add(p1)
            finish_line.add(p1)
            
            for i in platforms:       
                all_sprites.add(i)
            
            
            if replay_mode or mode == "speedrun":
                if wr_mode: #does necessary option based on what the user has selected they want to do
                    moves = show_replay("wr_replay1.txt")
                else:
                    moves = show_replay("replay1.txt")#here
                frame = 0
                change_to_singleplayer = False
                if mode == "speedrun":
                    ghost_player = ghost()
                else:
                    play.replay = True
                    
        if replay_mode:
            try:
                moves[frame+5]#moves to next frame
            except:
                change_to_singleplayer = True

            position = level1(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]])
            frame += 5 
            if change_to_singleplayer:
                replay_mode = False
                position = "singleplayer"
        else:
            if mode == "speedrun":
                try:
                    moves[frame+5]
                except:
                    ghost_player.done = True
                    frame = 0
                position = level1(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]],ghost = True)
                frame += 5
                
            else:
                position = level1()

            
            
    if position == "level2": 
        if setup:

            play = player()
            start = time.time()
            recording = []
            e1 = forest_enemy(2400,450)
            e2 = forest_enemy(3300,450,img = "jungle")
            
            e3 = bug(5300,222)
            e4 = bug(6000,222)
            e5 = bug(6000,372)
            e6 = bug(6000,522)
            setup = False
            #defining all the needed groups
            players = pygame.sprite.Group()
            players.add(play)
            platforms = pygame.sprite.Group()
            ladders = pygame.sprite.Group()
            powerups = pygame.sprite.Group()

            moving_platforms1 = pygame.sprite.Group()

            friend_projectiles = pygame.sprite.Group()
            projectiles = pygame.sprite.Group() #remake these group
            ladders = pygame.sprite.Group()
            finish_line = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()

            enemies.add(e1)
            enemies.add(e2)
            enemies.add(e3)
            enemies.add(e4)
            enemies.add(e5)
            enemies.add(e6)

            for i in enemies:       
                all_sprites.add(i)
            for i in powerups:
                all_sprites.add(i)

            level2ground = level2platforms.get_image(1,33,92,92) #defines all of the platforms used in this level
            level2ground.set_colorkey(black)
            level2thin = level2platforms.get_image(97,33,31,92)
            level2thin.set_colorkey(black)
            level2reg = level2platforms.get_image(129,33,95,32)
            level2reg.set_colorkey(black)

                                                     
            for i in range(30): #ground tiles
                p1 = platform(330 + i * 200, 630, 200, 200,level2ground,keycolor = white) #x,y,width,height
                platforms.add(p1) 
            
            p1 = platform(830, 530, 100, 300,level2thin,keycolor = white)
            platforms.add(p1)

            p1 = platform(1030, 470, 100, 300,level2thin,keycolor = white)
            platforms.add(p1)#first two thin platforms

            p1 = platform(1170, 525, 100, 300,level2thin,keycolor = white) 
            platforms.add(p1)#step back up

            p1 = platform(1280, 420, 150, 50,level2reg,keycolor = white) #wide platforms
            platforms.add(p1)

            p1 = platform(1530, 380, 150, 50,level2reg,keycolor = white)
            platforms.add(p1)


            p2 = platform(1780, 380, 150, 50,level2reg,keycolor = white)
            platforms.add(p2) #moving platform
            moving_platforms1.add(p2)

            p1 = platform(2250, 400, 100, 300,level2thin,keycolor = white)
            platforms.add(p1)

            for i in range(4): #this are the platforms going diagonally upwards
                p1 = platform(2400 + 200 * i, 450 - 100 * i, 150, 50,level2reg,keycolor = white)
                platforms.add(p1)                

            p1 = platform(2600, 550, 150, 50,level2reg,keycolor = white)
            platforms.add(p1)

            p1 = platform(3150, 400, 100, 300,level2thin,keycolor = white)
            platforms.add(p1)
            p1 = platform(3250, 400, 100, 300,level2thin,keycolor = white)
            platforms.add(p1)

            for i in range(8):#first platform run
                p1 = platform(3300 + 150 * i, 350, 150, 50,level2reg,keycolor = white)
                platforms.add(p1)

            #ladders to get back up
            for i in range(6): #first ladders
                l1 = ladder(4500,566 - 64 * i)
                ladders.add(l1)

            
            for i in range(4): #first ladders
                l1 = ladder(4222,286 - 64 * i)
                ladders.add(l1)

            for i in range(4): #platorms right of the first ladder
                p1 = platform(4286 + 150 * i, 158, 150, 50,level2reg,keycolor = white)
                platforms.add(p1)

            for i in range(6): #second ladders going downwards
                l1 = ladder(4886,414 - 64 * i)
                ladders.add(l1)
                
            p1 = platform(4950, 158, 150, 50,level2reg,keycolor = white)
            platforms.add(p1)

            p1 = platform(4950, -142, 100, 300,level2thin,keycolor = white)
            platforms.add(p1)
            
            for i in range(4): #platforms to the right of the downwards ladder
                p1 = platform(4950 + 150 * i, 414, 150, 50,level2reg,keycolor = white)
                platforms.add(p1)

            for i in range(6): #ladders going back up
                l1 = ladder(5486,350 - 64 * i)
                ladders.add(l1)

            for i in range(2):#column platforms
                p1 = platform(5550, 470 - i * 300, 100, 300,level2thin,keycolor = white)
                platforms.add(p1)                

            for i in range(10):#last ladders
                l1 = ladder(6050,566 - 64 * i)
                ladders.add(l1)

            for i in range(3):
                p1 = platform(6114 + 150 * i, 158, 150, 50,level2reg,keycolor = white)
                platforms.add(p1)

            p1 = platform(6720, 650, 32, 32,star)
            platforms.add(p1)
            finish_line.add(p1)

            for i in ladders:       
                all_sprites.add(i)
            
            for i in platforms:       
                all_sprites.add(i)
              
            all_sprites.add(play)
            
            if replay_mode or mode == "speedrun":
                moves = show_replay("replay2.txt")#here
                frame = 0
                change_to_singleplayer = False
                if mode == "speedrun":
                    ghost_player = ghost()
                else:
                    play.replay = True
                    
        if replay_mode:
            try:
                moves[frame+5]
            except:
                change_to_singleplayer = True
                
            position = level2(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]])
            frame += 5
            if change_to_singleplayer:
                replay_mode = False
                position = "singleplayer"
        else:
            if mode == "speedrun":
                try:
                    moves[frame+5]
                except:
                    ghost_player.done = True
                    frame = 0
                position = level2(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]],ghost = True)
                frame += 5#these
            else:
                position = level2()

        
        
    if position == "level3":
        if setup:
            #entities
            play = player()
            recording = []
            start = time.time()
            e1 = skeleton(2945,0)
            e2 = turtle(3845,0)
            e3 = skeleton(4600,0)
            e4 = skeleton(4900,0)
            e5 = turtle(5500,0)
            e6 = turtle(6000,0) #add enemies
            e7 = turtle(6000,0)
            e8 = bug(6300,height+80)
            e9 = bug(7680,height-100)
            p1 = wizardpowerup(4100,height+68)
            setup = False
            platforms = pygame.sprite.Group()
            powerups = pygame.sprite.Group()
            powerups.add(p1)

            friend_projectiles = pygame.sprite.Group()
            projectiles = pygame.sprite.Group() #remake these group
            ladders = pygame.sprite.Group()
                        
            moving_platforms1 = pygame.sprite.Group()
            moving_platforms2 = pygame.sprite.Group()
            moving_platforms3 = pygame.sprite.Group()
            moving_platforms4 = pygame.sprite.Group() #moving platform groups
            moving_platforms5 = pygame.sprite.Group()
            moving_platforms6 = pygame.sprite.Group()
            moving_platforms7 = pygame.sprite.Group()
            moving_platforms8 = pygame.sprite.Group()
            moving_platforms9 = pygame.sprite.Group()
            moving_platforms10 = pygame.sprite.Group()
            moving_platforms11 = pygame.sprite.Group()
            finish_line = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()
            enemies.add(e1)
            enemies.add(e2)
            enemies.add(e3)
            enemies.add(e4) #add enemies
            enemies.add(e5)
            enemies.add(e6)
            enemies.add(e7)
            enemies.add(e8)
            enemies.add(e9)
            for i in enemies:       
                all_sprites.add(i)
            for i in powerups:
                all_sprites.add(i) #add to all_sprites group
                
            p1 = platform(330, 476, 250, 86,spriteplatform.get_image(226,512, 122, 42)) #first large platform
            platforms.add(p1)
            p1 = platform(550, 356, 50, 24,spriteplatform.get_image(175,416,69,34))
            platforms.add(p1)
            p1 = platform(650, 256, 50, 24,spriteplatform.get_image(175,416,69,34)) 
            platforms.add(p1)
            p1 = platform(790, 356, 50, 24,spriteplatform.get_image(175,416,69,34))
            platforms.add(p1)
            p1 = platform(910, 296, 69, 34,spriteplatform.get_image(175,416,69,34)) #4 smaller platforms
            platforms.add(p1)
            p1 = platform(1070, 326, 100, 34,spriteplatform.get_image(226,512, 122, 42))
            platforms.add(p1)
            p1 = platform(1210, 426, 80, 28,spriteplatform.get_image(226,512, 122, 42))
            platforms.add(p1)
            p1 = platform(1340, 476, 250, 86,spriteplatform.get_image(226,512, 122, 42))#3 other size platforms before
            platforms.add(p1)                                                           #moving platforms
                
            p9 = platform(1640, 426, 50, 20,spriteplatform.get_image(226,512, 122, 42))
                        
            p10 = platform(1840, 356, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            p1 = platform(2140, 356, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            platforms.add(p1)
            p12 = platform(2290, 356, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            p13 = platform(2420, 256, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            p14 = platform(2620, 196, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            p1 = platform(2770, 196, 350, 50,spriteplatform.get_image(226,512, 122, 42))
            platforms.add(p1)
            p16 = platform(3220, 276, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            p1 = platform(3600, 676, 800, 55,grassplatform)
            platforms.add(p1)
            p1 = platform(4400, 676, 800, 55,grassplatform)
            platforms.add(p1)
            p1 = platform(5200, 676, 800, 55,grassplatform)
            platforms.add(p1)
            p1 = platform(6000, 676, 800, 55,grassplatform)
            platforms.add(p1)
            p21 = platform(6900, 576, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            p22 = platform(7100, 476, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            p23 = platform(7280, 476, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            p24 = platform(7830, 436, 50, 20,spriteplatform.get_image(226,512, 122, 42))
            p25 = platform(7950, 386, 50, 20,spriteplatform.get_image(226,512, 122, 42))

            platforms.add(p9)
            moving_platforms1.add(p9)
            
            platforms.add(p10)
            moving_platforms2.add(p10)
                        
            moving_platforms3.add(p12)
            platforms.add(p12)

            moving_platforms4.add(p13)
            platforms.add(p13)

            moving_platforms5.add(p14)
            platforms.add(p14)
            
            moving_platforms6.add(p16)
            platforms.add(p16)

            moving_platforms7.add(p21)
            platforms.add(p21)

            moving_platforms8.add(p22)
            platforms.add(p22)

            moving_platforms9.add(p23)
            platforms.add(p23)

            moving_platforms10.add(p24)
            platforms.add(p24)

            moving_platforms11.add(p25)
            platforms.add(p25)

            p1 = platform(8100, 620, 32, 32,star) 
            finish_line.add(p1)
            platforms.add(p1)
            all_sprites.add(p1) #finish line
            
            for i in platforms:       
                all_sprites.add(i)
              
            all_sprites.add(play)
            
            if replay_mode or mode == "speedrun":
                moves = show_replay("replay3.txt")
                frame = 0
                change_to_singleplayer = False
                if mode == "speedrun":
                    ghost_player = ghost()
                else:
                    play.replay = True
                    
        if replay_mode:
            try:
                moves[frame+5]
            except:
                change_to_singleplayer = True
                
            position = level3(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]])
            frame += 5 #there
            if change_to_singleplayer:
                replay_mode = False
                position = "singleplayer"
        else:
            if mode == "speedrun":
                try:
                    moves[frame+5]
                except:
                    ghost_player.done = True
                    frame = 0
                position = level3(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]],ghost = True)
                frame += 5
            else:
                position = level3()

    elif position == "level4":
        if setup:
            start = time.time()
            #entities
            play = player()
            recording = []
            e1 = turtle(1000,dispy-100)
            e2 = turtle(1250,dispy-100)
            e3 = turtle(1590,0)
            e4 = turtle(1900,0)
            e5 = turtle(2810,0)
            e6 = mage(3550,0)
            e12 = turtle(4000,0)
            e7 = mage(5025,dispy-156)
            e8 = mage(5025,dispy-356)
            e9 = mage(5025,dispy-556)
            e11 = mage(5750,650)
            e12 = mage(1670,620)
            setup = False
            platforms = pygame.sprite.Group()
            hardplatforms = pygame.sprite.Group()
            powerups = pygame.sprite.Group()
            

            friend_projectiles = pygame.sprite.Group()
            projectiles = pygame.sprite.Group() #remake these group
            ladders = pygame.sprite.Group()
            
            finish_line = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()
            all_sprites.add(play)
            enemies.add(e1)
            enemies.add(e2)
            enemies.add(e3) #add enemies to group
            enemies.add(e4)
            enemies.add(e5)
            enemies.add(e6)
            enemies.add(e7)
            enemies.add(e8)
            enemies.add(e9)
            enemies.add(e11)
            enemies.add(e12)
            for i in enemies:       
                all_sprites.add(i)
            for i in powerups:
                all_sprites.add(i)
                
            #all the platforms and stuff goes here
            p1 = platform(330, dispy-87, 600, 88,desertplatform2)
            platforms.add(p1)
            p2 = platform(930, dispy-87, 600, 88,desertplatform2)
            platforms.add(p2)
            p3 = platform(1530, dispy-87, 600, 88,desertplatform2)
            platforms.add(p3)
            p4 = platform(1530, 585, 48, 48,sandtile)
            platforms.add(p4)
            p5 = platform(1578, 585, 48, 48,sandtile) #bottom row
            platforms.add(p5)
            
            p5 = platform(1578, 537, 48, 48,sandtile) # middle row
            platforms.add(p5)
            
            p6 = platform(1578, 489, 48, 48,sandtile) #top row
            platforms.add(p6)
            p7 = platform(1626, 489, 48, 48,sandtile)
            platforms.add(p7)
            p8 = platform(1674, 489, 48, 48,sandtile)
            platforms.add(p8)
            p9 = platform(2130, dispy-87, 600, 88,desertplatform2)
            platforms.add(p9)
            p10 = platform(2730, dispy-87, 600, 88,desertplatform2)
            platforms.add(p10)
            p11 = platform(2400, dispy-135, 48, 48,sandtile)
            platforms.add(p11)
            p12 = platform(3330, dispy-87, 600, 88,desertplatform2)
            platforms.add(p12)
            p13 = platform(3930, dispy-87, 600, 88,desertplatform2)
            platforms.add(p13)
            p14 = platform(4530, dispy-87, 600, 88,desertplatform2)
            platforms.add(p14)
            p15 = platform(5130, dispy-87, 600, 88,desertplatform2)
            platforms.add(p15)

            p16 = platform(5000, dispy-155, 48, 48,sandtile)
            platforms.add(p16)
            p17 = platform(5000, dispy-355, 48, 48,sandtile)
            platforms.add(p17)
            p18 = platform(5000, dispy-555, 48, 48,sandtile)  #stand for mages
            platforms.add(p18)

            p19 = platform(4500, dispy-135, 48, 48,sandtile)
            platforms.add(p19)
            p20 = platform(4600, dispy-235, 48, 48,sandtile)
            platforms.add(p20)
            p21 = platform(4700, dispy-355, 48, 48,sandtile)
            platforms.add(p21)

            p22 = platform(4800, dispy-355, 48, 48,sandtile)
            platforms.add(p22)
            p23 = platform(4900, dispy-435, 48, 48,sandtile)
            platforms.add(p23)

            p24 = platform(5000, dispy-255, 48, 48,sandtile) #ones between mage stands
            platforms.add(p24)
            p25 = platform(5000, dispy-455, 48, 48,sandtile)
            platforms.add(p25)
            p26 = platform(5000, dispy-655, 48, 48,sandtile)
            platforms.add(p26)
            p50 = platform(5000, dispy-303, 48, 48,sandtile)
            platforms.add(p50)
            p51 = platform(5000, dispy-503, 48, 48,sandtile)
            platforms.add(p51)
            p52 = platform(5000, dispy-703, 48, 48,sandtile)
            platforms.add(p52)

            p27 = platform(4800, dispy-555, 48, 48,sandtile)
            platforms.add(p27)
            p28 = platform(4900, dispy-655, 48, 48,sandtile)
            platforms.add(p28)
            

            for i in range(14):
                p1 = platform(5150, -127 + i * 48, 48, 48,sandtile) #long column
                platforms.add(p1)

            p1 = platform(5832, 515, 48, 48,sandtile) #step up
            platforms.add(p1)
            
            for i in range(13):
                p1 = platform(5784 - i * 48, 419, 48, 48,sandtile) #long row 
                platforms.add(p1)


            # in between platforms
            p1 = platform(5734, 371, 48, 48,sandtile)
            platforms.add(p1)            
            p1 = platform(5590, 371, 48, 48,sandtile)
            platforms.add(p1)
            p1 = platform(5542, 371, 48, 48,sandtile)
            platforms.add(p1)
            p1 = platform(5350, 371, 48, 48,sandtile)
            platforms.add(p1)
            p1 = platform(5398, 371, 48, 48,sandtile)
            platforms.add(p1)
            p1 = platform(5208, 371, 48, 48,sandtile)
            platforms.add(p1)
            
            for i in range(13):
                p1 = platform(5832 - i * 48, 275, 48, 48,sandtile) #long row 2
                platforms.add(p1)

            #jumps at top
            p1 = platform(5400, 179, 48, 48,sandtile)
            platforms.add(p1)

            p1 = platform(5544, 131, 48, 48,sandtile) 
            platforms.add(p1)

            p1 = platform(5640, 131, 48, 48,sandtile) 
            platforms.add(p1)

            p1 = platform(5832, 131, 48, 48,sandtile) 
            platforms.add(p1)


            for i in range(12):
                p1 = platform(5880, 65 + i * 48, 48, 48,sandtile) #long column
                platforms.add(p1)
                
            p42 = platform(5116, dispy-555, 32, 32,sandtile)  #stairs down
            platforms.add(p42)
            p43 = platform(5050, dispy-455, 32, 32,sandtile)
            platforms.add(p43)
            p44 = platform(5116, dispy-355, 32, 32,sandtile)
            platforms.add(p44)
            p45 = platform(5050, dispy-255, 32, 32,sandtile)
            platforms.add(p45)

            p46 = platform(5730, dispy-87, 600, 88,desertplatform2)
            platforms.add(p46)
            p47 = platform(6330, dispy-87, 600, 88,desertplatform2)
            platforms.add(p47)

            p48 = platform(7000, dispy-87, 32, 32,star) #at 7000
            finish_line.add(p48)
            platforms.add(p48)
            all_sprites.add(p48)
            
              
            all_sprites.add(play)
            
            if replay_mode or mode == "speedrun":
                moves = show_replay("replay4.txt")#here
                frame = 0
                change_to_singleplayer = False
                if mode == "speedrun":
                    ghost_player = ghost()
                else:
                    play.replay = True
                    
        if replay_mode:
            try:
                moves[frame+5]
            except:
                change_to_singleplayer = True
                
            position = level4(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]])
            frame += 5 #there
            if change_to_singleplayer:
                replay_mode = False
                position = "singleplayer"
        else:
            if mode == "speedrun":
                try:
                    moves[frame+5]
                except:
                    ghost_player.done = True
                    frame = 0
                position = level4(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]],ghost = True)
                frame += 5#these
            else:
                position = level4()

                
    elif position == "level5":
        if setup:
            start = time.time()
            #entities
            play = player()
            recording = []
            
            e1 = mage(330,0,newimage = "witch")
            
            e2 = turtle(730,400,img = "cat")
            e3 = turtle(1430,400,img = "cat")
            e4 = bug(1130,350,img = "bat")
            e5 = mage(2300,650)
            e6 = mage(2600,0,newimage = "witch")
            e7 = mage(2800,0,newimage = "witch")
            
            e8 = mage(3200,0,newimage = "witch") # above the tunnel witches
            e9 = mage(3500,0,newimage = "witch")
            e10 = mage(3800,0,newimage = "witch")
            e11 = mage(3400,300,newimage = "witch")

            e12 = turtle(4245,630,img = "cat")
            e13 = turtle(4245,630,img = "cat")
            e14 = turtle(4245,630,img = "cat")
            e15 = turtle(4245,630,img = "cat")
            e16 = turtle(4245,630,img = "cat")
            e17 = turtle(4245,630,img = "cat")
            e18 = turtle(4245,630,img = "cat")
            e19 = turtle(4245,630,img = "cat")

            e20 = mage(4700,650,newimage = "witch")
            e21 = mage(4800,650,newimage = "witch")

            setup = False
            #platforms
            platforms = pygame.sprite.Group()
            hardplatforms = pygame.sprite.Group()
            powerups = pygame.sprite.Group()

            friend_projectiles = pygame.sprite.Group()
            projectiles = pygame.sprite.Group() #remake these group
            ladders = pygame.sprite.Group()
            
            finish_line = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()
            all_sprites.add(play)
            enemies.add(e1)
            enemies.add(e2)
            enemies.add(e3)
            enemies.add(e4)
            enemies.add(e5)
            enemies.add(e6)
            enemies.add(e7)
            enemies.add(e8)
            enemies.add(e9)
            enemies.add(e10)
            enemies.add(e11)
            enemies.add(e12)
            enemies.add(e13)
            enemies.add(e14)
            enemies.add(e15)
            enemies.add(e16)
            enemies.add(e17)
            enemies.add(e18)
            enemies.add(e19)
            enemies.add(e20)
            enemies.add(e21)
            for i in enemies:       
                all_sprites.add(i)
            for i in powerups:
                all_sprites.add(i)
                
            #all the platforms and stuff goes here
            floor_platform = spriteplatform3.get_image(96,33, 93, 46)
            sky_platform = spriteplatform3.get_image(96,0, 95, 31)
            for i in range(10):
                p1 = platform(330 + 540 * i, 620, 600, 298,floor_platform,keycolor = white) #floor platforms
                platforms.add(p1)
            for i in range(31):
                p2 = platform(200*i, 100, 200, 65,sky_platform,keycolor = white) #sky platforms
                platforms.add(p2)

            p1 = platform(950, 550, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)
          
            p1 = platform(1150, 500, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(2050, 555, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(2200, 490, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(2350, 555, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1) #platforms surrounding mages ^^

            for i in range(5): 
                p1 = platform(3000 + 200 * i, 555, 200, 65,sky_platform,keycolor = white) #row of platforms
                platforms.add(p1)

                p1 = platform(3000 + 200 * i, 405, 200, 65,sky_platform,keycolor = white)
                platforms.add(p1)

            p1 = platform(4000, 555, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(4050, 485, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1) #step from 1st to second row

            p1 = platform(3950, 255, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(3750, 255, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1) # 2 platforms on the third row

            p1 = platform(4150, 255, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(3500, 295, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)

            for i in range(5): 
                p1 = platform(4400, 555 + i * -65, 200, 65,sky_platform,keycolor = white)
                platforms.add(p1)

            p1 = platform(4600, 480, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(4800, 480, 200, 65,sky_platform,keycolor = white)
            platforms.add(p1)            

            p1 = platform(5900, 680, 32, 32,star) 
            finish_line.add(p1)
            platforms.add(p1)
            all_sprites.add(p1) #finish line
              
            all_sprites.add(play)
            
            if replay_mode or mode == "speedrun":
                moves = show_replay("replay5.txt")
                frame = 0
                change_to_singleplayer = False
                if mode == "speedrun":
                    ghost_player = ghost()
                else:
                    play.replay = True
                    
        if replay_mode:
            try:
                moves[frame+5]
            except:
                change_to_singleplayer = True
                
            position = level5(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]])
            frame += 5 
            if change_to_singleplayer:
                replay_mode = False
                position = "singleplayer"
        else:
            if mode == "speedrun":
                try:
                    moves[frame+5]
                except:
                    ghost_player.done = True
                    frame = 0
                position = level5(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]],ghost = True)
                frame += 5#these
            else:
                position = level5()     


    elif position == "level6":
        if setup:
            start = time.time()
            #entities
            play = player()
            recording = []
            #e1 is used for the lava
            
            e2 = mage(200,-100,obey_gravity = False)
            e3 = mage(400,-100,obey_gravity = False)
            e4 = mage(600,-100,obey_gravity = False)            
            e5 = mage(5850,300)
            e6 = mage(7350,300)            
            e7 = mage(9480,350,newimage = "angel")
            setup = False
            moving_platforms1 = pygame.sprite.Group()
            moving_platforms2 = pygame.sprite.Group()
            moving_platforms3 = pygame.sprite.Group()
            platforms = pygame.sprite.Group()
            hardplatforms = pygame.sprite.Group()
            powerups = pygame.sprite.Group()

            friend_projectiles = pygame.sprite.Group()
            projectiles = pygame.sprite.Group() #remake these group
            ladders = pygame.sprite.Group()            
            finish_line = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()
            all_sprites.add(play)
            enemies.add(e2)
            enemies.add(e3)
            enemies.add(e4)
            enemies.add(e5)
            enemies.add(e6)
            enemies.add(e7)
            for i in range(85): #lava tiles at the bottom. 
                e1 = turtle(-500 + 150 * i,720,killable = False,img = "lava")#starts at - incase player moves backwards
                enemies.add(e1)

            for i in enemies:       
                all_sprites.add(i)
            for i in powerups:
                all_sprites.add(i)
                
            wide_platform = volcano_sprites.get_image(86,880, 596, 140)
            

            p1 = platform(250, 400, 300, 100,wide_platform,keycolor = white)#initial platforms
            platforms.add(p1)

            p1 = platform(700, 450, 300, 100,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(1120, 360, 300, 100,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(1560, 390, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(1860, 340, 300, 100,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(2230, 380, 300, 100,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(2600, 420, 300, 100,wide_platform,keycolor = white)
            platforms.add(p1)

            p2 = platform(3000, 420, 300, 100,wide_platform,keycolor = white)
            platforms.add(p2)
            moving_platforms1.add(p2) #first moving platform

            p1 = platform(3750, 420, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(4000, 420, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p3 = platform(4240, 420, 150, 50,wide_platform,keycolor = white)
            platforms.add(p3)
            moving_platforms2.add(p3) #second moving platform

            p1 = platform(4850, 420, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(5150, 430, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(5450, 500, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(5750, 500, 450, 150,wide_platform,keycolor = white) #where the first enemy stands
            platforms.add(p1)

            p1 = platform(6350, 470, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(6650, 440, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(6850, 410, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(7050, 410, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(7250, 410, 450, 150,wide_platform,keycolor = white) #second enemy
            platforms.add(p1)

            p4 = platform(7800, 450, 150, 50,wide_platform,keycolor = white)
            platforms.add(p4)
            moving_platforms3.add(p4) #third moving platform
            
            p1 = platform(8400, 410, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(8600, 380, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(8800, 350, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(9000, 380, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(9200, 410, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(9400, 410, 450, 150,wide_platform,keycolor = white) #third enemy
            platforms.add(p1)

            p1 = platform(10000, 380, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(10200, 350, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(10400, 320, 150, 50,wide_platform,keycolor = white)
            platforms.add(p1)

            p1 = platform(10700, 500, 32, 32,star) 
            finish_line.add(p1)
            platforms.add(p1)
            all_sprites.add(p1) #finish line
              
            all_sprites.add(play)
            
            if replay_mode or mode == "speedrun":
                moves = show_replay("replay6.txt")
                frame = 0
                change_to_singleplayer = False
                if mode == "speedrun":
                    ghost_player = ghost()
                else:
                    play.replay = True
                    
        if replay_mode:
            try:
                moves[frame+5]
            except:
                change_to_singleplayer = True
                
            position = level6(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]])
            frame += 5 
            if change_to_singleplayer:
                replay_mode = False
                position = "singleplayer"
        else:
            if mode == "speedrun":
                try:
                    moves[frame+5]
                except:
                    ghost_player.done = True
                    frame = 0
                position = level6(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]],ghost = True)
                frame += 5
            else:
                position = level6()


    elif position == "level7":
        if setup:
            start = time.time()
            recording = []
            play = player()
            e1 = dragon()
            e2 = mage(100,-100,obey_gravity = False)
            
            p0 = wizardpowerup(4500,388)
            
            reference = wizardpowerup(0,2000)
            powerups = pygame.sprite.Group()
            setup = False
            platforms = pygame.sprite.Group()
            hardplatforms = pygame.sprite.Group()

            friend_projectiles = pygame.sprite.Group()
            projectiles = pygame.sprite.Group() #remake these group
            ladders = pygame.sprite.Group()
            
            finish_line = pygame.sprite.Group()
            enemies = pygame.sprite.Group()
            all_sprites = pygame.sprite.Group()
            
            powerups.add(p0)
            powerups.add(reference)
            
            all_sprites.add(play)
            enemies.add(e1)
            enemies.add(e2)

            for i in enemies:       
                all_sprites.add(i)
            for i in powerups:
                all_sprites.add(i)
                
            tile = castle_sprite.get_image(96,768, 32, 32)
                
            place = 0
            for i in range(1000): #generates platforms
                if i % 10 != 0:  
                    if place == 0:
                        p1 = platform(32 * i, 562, 32, 32,tile,keycolor = white) #adds middle platforms
                        platforms.add(p1)
                    else: #for each x coorinate, there is either a middle platform or both a top and bottom platform
                        place -= 1
                        p1 = platform(32 * i, 452, 32, 32,tile,keycolor = white) #high platforms
                        platforms.add(p1)
                        p1 = platform(32 * i, 672, 32, 32,tile,keycolor = white) #low platforms
                        platforms.add(p1)
                else:
                    place = 4
                    p1 = platform(32 * i, 452, 32, 32,tile,keycolor = white) #high platforms
                    platforms.add(p1)
                    p1 = platform(32 * i, 672, 32, 32,tile,keycolor = white) #low platforms
                    platforms.add(p1)

            """
            Each platform is made in groups of 5 tiles. As this algorithm is always placing
            platforms on the middle row or both top and bottom, and should do half of the time doing both of these
            tasks.
            First, a bottom and top tiles are added. It then adds 4 more while place counts down from 4.
            Once this is done, it then adds the middle platform. The remaining 5 iterations before the if statment
            resets this process adds in the middle platforms.
            """
              
            all_sprites.add(play)
            
            if replay_mode or mode == "speedrun":
                moves = show_replay("replay7.txt")#here
                frame = 0
                change_to_singleplayer = False
                if mode == "speedrun":
                    ghost_player = ghost()
                else:
                    play.replay = True
                    
        if replay_mode:
            try:
                moves[frame+5]
            except:
                change_to_singleplayer = True
                
            position = level7(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]])
            frame += 5
            if change_to_singleplayer:
                replay_mode = False
                position = "singleplayer"
        else:
            if mode == "speedrun":
                try:
                    moves[frame+5]
                except:
                    ghost_player.done = True
                    frame = 0
                position = level7(replay = [float(moves[frame]),float(moves[frame + 1]),moves[frame + 2],moves[frame + 3],moves[frame + 4]],ghost = True)
                frame += 5#these
            else:
                position = level7()

    elif position == "leaderboard":
        screen.blit(title, (160,180))
        
        username1 = button(grey,360,350,280,50,str(records[0][0]))
        username2 = button(grey,360,400,280,50,str(records[0][1]))
        username3 = button(grey,360,450,280,50,str(records[0][2])) #redefines the buttons so they are updated
        username4 = button(grey,360,500,280,50,str(records[0][3])) #everytime the user goes onto the 
        username5 = button(grey,360,550,280,50,str(records[0][4])) #leaderboards
        username6 = button(grey,360,600,280,50,str(records[0][5]))
        username7 = button(grey,360,650,280,50,str(records[0][6]))

        time1 = button(grey,640,350,280,50,str(records[1][0]))
        time2 = button(grey,640,400,280,50,str(records[1][1]))
        time3 = button(grey,640,450,280,50,str(records[1][2]))
        time4 = button(grey,640,500,280,50,str(records[1][3]))
        time5 = button(grey,640,550,280,50,str(records[1][4]))
        time6 = button(grey,640,600,280,50,str(records[1][5]))
        time7 = button(grey,640,650,280,50,str(records[1][6]))


        if downloading: #shows the user that they are downloading a replay
            download_in_progress.draw(screen,(0,0,0))

        if sending:#shows user that they are sending a replay
            sending_in_progress.draw(screen,(0,0,0))
            

        download_help.draw(screen,(0,0,0))

        heading4.draw(screen,(0,0,0)) #draw buttons previously defined
        heading1.draw(screen,(0,0,0))
        heading2.draw(screen,(0,0,0))
        heading3.draw(screen,(0,0,0))


        your_record1.draw(screen,(0,0,0))
        your_record2.draw(screen,(0,0,0))
        your_record3.draw(screen,(0,0,0))
        your_record4.draw(screen,(0,0,0))
        your_record5.draw(screen,(0,0,0))
        your_record6.draw(screen,(0,0,0))
        your_record7.draw(screen,(0,0,0))
        
        level1_button.draw(screen,(0,0,0))
        level2_button.draw(screen,(0,0,0))
        level3_button.draw(screen,(0,0,0))
        level4_button.draw(screen,(0,0,0))
        level5_button.draw(screen,(0,0,0))
        level6_button.draw(screen,(0,0,0))
        level7_button.draw(screen,(0,0,0))
        username1.draw(screen,(0,0,0))
        username2.draw(screen,(0,0,0))
        username3.draw(screen,(0,0,0))
        username4.draw(screen,(0,0,0))
        username5.draw(screen,(0,0,0))
        username6.draw(screen,(0,0,0))
        username7.draw(screen,(0,0,0))
        time1.draw(screen,(0,0,0))
        time2.draw(screen,(0,0,0))
        time3.draw(screen,(0,0,0))
        time4.draw(screen,(0,0,0))
        time5.draw(screen,(0,0,0))
        time6.draw(screen,(0,0,0))
        time7.draw(screen,(0,0,0))
        backtomenu.draw(screen,(0,0,0))

        
    elif position == "singleplayer":
        screen.blit(map_,(0,0))
        
        for i in range(6): #add the pathways between required levels
            screen.blit(path,(190 + i*20,210))
        if playerlvl > 1:
            for i in range(6):
                screen.blit(path,(323,i*20+238))
        if playerlvl > 2:
            for i in range(6):
                screen.blit(path,(323,i*20+388))
        if playerlvl > 3:
            for i in range(24):
                screen.blit(path,(360+i*20,512))

        if playerlvl > 4:
            for i in range(7):
                screen.blit(path,(843,i*-20+500))
        if playerlvl > 5:
            for i in range(7):
                screen.blit(path,(843,i*-20+358))
        if playerlvl > 6:
            for i in range(9):
                screen.blit(path,(873+i*20,213))

                
        backtomenu.draw(screen,(0,0,0))
        
        screen.blit(base,(50,80))
        screen.blit(pad,(290,200))
        screen.blit(pad,(290,350))
        screen.blit(pad,(290,500))
        screen.blit(pad,(810,200))
        screen.blit(pad,(810,350))
        screen.blit(pad,(810,500))
        screen.blit(castle7,(1000,100))

        if playerlvl == 8:
            mode_button.draw(screen,(0,0,0))

        if playerpos != 0: #cannot get a time for that position as it isn't a level
            mytime = get_time(playerpos) #gets the player's best time for that level

            if mytime == 99999: #checks if there is no best time
                mytime = "No Time"
                replay_mode = False
                mode = "normal" #stops the user from using speedrun mode
                mode_button = button(grey,1000,20,250,50,"Mode = Normal")
            else:
                replay_button.draw(screen,(0,0,0))
            show_time = button(grey,390,20,500,50,"Best Time: "+str(mytime))
            show_time.draw(screen,(0,0,0)) #shows the time

        controls.draw(screen,(0,0,0))
        if show_controls: #draw controls
            controls2.draw(screen,(0,0,0))
            controls3.draw(screen,(0,0,0))
            controls4.draw(screen,(0,0,0))
            controls5.draw(screen,(0,0,0))
            controls6.draw(screen,(0,0,0))
            controls7.draw(screen,(0,0,0))
            controls8.draw(screen,(0,0,0))

        if playerpos != 0: #give option to show world record
            test = show_replay("wr_replay" + str(playerpos) + ".txt") #checks to see if user has this world record saved
            try:
                test2 = test[0]
                wr_replay.draw(screen,(0,0,0))
            except:pass
        

        if move == 0:
            screen.blit(front1,(mapx,mapy)) #draws the player on the screen
        else:
            mapx, mapy = mapmove(map_direction,mapx,mapy,move) #moves the player
            screen.blit(front1,(mapx,mapy)) #draws the player on the screen
            move -= 1 #reduces the number of moves
            
    if position=="home" or position=="singleplayer" or position == "multiplayer" or position == "multiplayer_failure" or position == "multiplayer2" or position=="lobby" or position == "leaderboard":
        pygame.display.flip() # do this after drawing everything

pygame.quit() #quits the game
