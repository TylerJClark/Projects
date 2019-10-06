import socket
#allows communication with clients
import _thread
#allows communication with clients concurrently
import sqlite3
#gives access to the database
import time as t
#allows using time
import os
#allows changing file directories

#C:\Users\TYLER\OneDrive\real_coursework\server\main_server.py
os.chdir("C:/Users/TYLER/OneDrive/real_coursework/server") #server filepath

class user(): #each client gets an instance of this class
    def __init__(self):
        self.username = ""
        self.logged = False
        self.lobby = None
        self.game_type = None
        self.lobby_pos = None
        self.rating = 0
        self.assigned = False
        self.assigned_number = None
        self.leave = False
        self.client_addr = None
        
def send(data,lists): #sends data to the server via tcp
    data = data + "`"
    for i in lists:
        i.send(data.encode())

def udp_send(data,addresses): #sends data to server via udp
    data = data + "`"
    for address in addresses:
        udp_server.sendto(data.encode(), address)

def seperate_data(data): #seperates different strings of data from users
    datas = [] #list of strings from the user
    done = False
    i = 0 #a counter
    while not done: #runs through the recieved string
        try:
            if data[i] == "`": #if a tile key is found, a new item is added to the list. 
                datas.append(data[:i])
                data = data[i + 1:]
                i = 0
                
            else:
                i += 1
                
        except:
            return datas #returns the list

def show_replay(file):#opens a file a returns the lines
    f=open(file)
    lines=f.readlines()
    return lines



def rank_algorithm(position,ranks): #takes current player's placement, and list of ratings in order
    change = 0
    for i in range(len(ranks)):#compares each player to each other player
        if position < i: #player did better than this player
            change += rank_change(ranks[position],ranks[i],True)
        elif position > i: #player did worse than other player
            change -= rank_change(ranks[position],ranks[i],False)
            
    return change
        
def rank_change(player,otherplayer,won): #decides the change in rating
    diff = (player - otherplayer)
    #this list is the rating changes based on difference in ratings
    values = [(1000,1),(300,3),(200,7),(100,10),(75,14),(50,17),(25,21),(0,24),(-25,28),(-50,31),(-75,35),(-100,38),(-200,42),(-300,45),(-1000,50)]
    for i in range(len(values)):
        if won:
            if diff > values[i][0]: #current player beat this player
                return values[i][1]
        else:
            if diff < values[len(values) - 1 - i][0]:
                return values[i][1]   #current player lost to this player


class lobby():
    def __init__(self,mode):
        self.mode = mode #what game mode is this

        self.clients = [[]] #addresses of client. needed to know where to send data
        self.udp_addr = [[]]
        
        self.client_names = [[]]
        self.client_ratings = [[]] #these are used to display to the user, and to amend ratings.
        
        self.ready_ups = [0]#readyups for each lobby
        
        self.ingame = [False]#says whether the lobby is in game. This can stop players joining lobbies that are
        #already in game.
        
        
        self.update_info = [[[0,9000,"s"],[0,9000,"s"],[0,9000,"s"],[0,9000,"s"]]]#each list should give x,y,direct
        
        
        self.placements = [[]]
        self.assignments = [[0,1,2,3]]#assigns each player a number
        self.disconnections = [[]] #keeps track of any players who leave the game
        self.udp_timeout = [[]]
        
        if mode == "wizard_wars":#in wizard wars, each lobby needs a set of lives
            self.player_lives = [[]]
            

    def find_availible_lobby(self,client,client_name,client_rating,addr): 
        for i in range(len(self.ingame)):
            if not self.ingame[i] and len(self.clients[i]) < 4: #finds a lobby that isnt in game and isnt full.

                self.clients[i].append(client) #adds this client's details to the lobby
                self.client_names[i].append(client_name)
                self.client_ratings[i].append(client_rating)
                    
                send("WIPE1---",self.clients[i])
                for j in self.client_names[i]:
                    send(("LOBBY1M-"+str(j)),self.clients[i]) #resends the lobby data to users in the lobby
                for j in self.client_ratings[i]:
                    send(("LOBBY1MR"+str(j)),self.clients[i])
                    
                client.send(("READY1--"+str(self.ready_ups[i]) + "`").encode()) #tells the user how many people have readied up
                                
                yourinstance.lobby_pos = len(self.clients[i]) - 1
                return i

        print("new lobby created")
        print("clients",self.clients)
        self.clients.append([client]) #if there are no availible lobbies, a new one is created
        self.client_names.append([client_name])
        self.client_ratings.append([client_rating])
        self.udp_addr.append([])
        self.placements.append([])
        self.assignments.append([0,1,2,3])
        self.disconnections.append([])
        self.udp_timeout.append([])
        
        yourinstance.lobby_pos = 0
        self.ready_ups.append(0)
        self.ingame.append(False)
        self.update_info.append([[0,9000,"s"],[0,9000,"s"],[0,9000,"s"],[0,9000,"s"]])
        send(("LOBBY1M-"+str(client_name)),self.clients[-1])
        send(("LOBBY1MR"+str(client_rating)),self.clients[-1])
        print(self.udp_addr)
        return len(self.clients) - 1

    #this function returns the lobby the user is in. The second number is the game type


def clients(client,addr,yourinstance):
    global lobby1
    global lobby2
    global allclients
    global all_client_usernames
    x = True
    timer = 0
    udp_timer = 1000
    while x:
        timer += 1
        if timer > 1000000: #used for sending data periodically
            timer = 0
            
        if yourinstance.game_type != None and not yourinstance.leave:
            if yourinstance.game_type.ingame[yourinstance.lobby]:
                
                
                try:

                    try:
                        udp_server.settimeout(4)#sets maximum time for response of 4 seconds
                        attempt = True
                        try:
                            data,client_addr = udp_server.recvfrom(1024) #receieve udp data
                        except:
                            if udp_server.timeout: #if client doesn't respond within 4 seconds
                                try:
                                    if yourinstance.game_type.udp_timeout[yourinstance.lobby][yourinstance.assigned_number] == 0:
                                        attempt = False #doesn't allow user to get a new assigned number when they shouldn't
                                        x = False #removes this thread from server
                                        print(yourinstance.username,"has timed out")
                                except Exception as e:
                                    print("error checking udp timeout",e)
                        if attempt:
                            try:
                                enter = True
                                for i in range(len(yourinstance.game_type.udp_addr[yourinstance.lobby])):
                                    if client_addr[0] == yourinstance.game_type.udp_addr[yourinstance.lobby][i][0]: #checks if the ips are the same
                                        enter = False
                                        if yourinstance.game_type.udp_addr[yourinstance.lobby][i][1] != client_addr[1]:
                                            yourinstance.game_type.udp_addr[yourinstance.lobby][i] = (client_addr[0],client_addr[1]) #gets the new port number
                                            yourinstance.client_addr = client_addr
                                

                                if not yourinstance.assigned and enter and len(yourinstance.game_type.udp_addr[yourinstance.lobby]) < len(yourinstance.game_type.client_names[yourinstance.lobby]):
    
                                    print("attempting to add to udp server",yourinstance.username)
                                    yourinstance.game_type.udp_addr[yourinstance.lobby].append(client_addr) #adds client address
                                    yourinstance.game_type.udp_timeout[yourinstance.lobby].append(100)
                                    yourinstance.client_addr = client_addr
                                    yourinstance.assigned_number = yourinstance.game_type.assignments[yourinstance.lobby][0] #finds the next availible number

                                    yourinstance.game_type.assignments[yourinstance.lobby].remove(yourinstance.assigned_number) #removes that number
                                    print("giving assignemnt",yourinstance.assigned_number,"to",yourinstance.username) #outputs who gets what number

                                    client.send(("YOURNUM-"+str(yourinstance.assigned_number)+"`").encode()) #sends the user what number they are
                                    print("added to udp server:",yourinstance.game_type.udp_addr) #outputs the address
                                    yourinstance.assigned = True
                                    if yourinstance.game_type.mode == "wizard_wars":
                                        print("added to player_lives") #add username, ratings and lives to the list
                                        yourinstance.game_type.player_lives[yourinstance.lobby].append([yourinstance.username,yourinstance.rating,10])
                                        send("WIPESCOR",yourinstance.game_type.clients[yourinstance.lobby])#blanks the scores list
                                        for i in yourinstance.game_type.player_lives[yourinstance.lobby]:
                                            send("SCORES--"+str(i[0])+"  "+str(i[1])+"  "+str(i[2]),yourinstance.game_type.clients[yourinstance.lobby])
                                            #add the new scores
                                            
                            except Exception as e:
                                print("adding udp client error:",e)
                            
                    except Exception as e:
                        print("udp error:",e)
                        yourinstance.leave = True
                        data = ""
                        

                        
                    try:
                        data_list = seperate_data(data.decode()) #separates the data, after being converted to a string
                    except:
                        data_list = []
                    for data in data_list: #runs through different data items

                        if data[:7] == "UPDATE1":
                            if data[7:8] == "0":#data[7:8] shows what player sent the data
                                yourinstance.game_type.udp_timeout[yourinstance.lobby][0] = 100
                                yourinstance.game_type.update_info[yourinstance.lobby][0][0] = data[8:13] #x
                                yourinstance.game_type.update_info[yourinstance.lobby][0][1] = data[13:17] #y
                                yourinstance.game_type.update_info[yourinstance.lobby][0][2] = data[17:18] #direction
                            elif data[7:8] == "1":
                                yourinstance.game_type.udp_timeout[yourinstance.lobby][1] = 100
                                yourinstance.game_type.update_info[yourinstance.lobby][1][0] = data[8:13]
                                yourinstance.game_type.update_info[yourinstance.lobby][1][1] = data[13:17]
                                yourinstance.game_type.update_info[yourinstance.lobby][1][2] = data[17:18]
                            elif data[7:8] == "2":
                                yourinstance.game_type.udp_timeout[yourinstance.lobby][2] = 100
                                yourinstance.game_type.update_info[yourinstance.lobby][2][0] = data[8:13]
                                yourinstance.game_type.update_info[yourinstance.lobby][2][1] = data[13:17]
                                yourinstance.game_type.update_info[yourinstance.lobby][2][2] = data[17:18]
                            elif data[7:8] == "3":
                                yourinstance.game_type.udp_timeout[yourinstance.lobby][3] = 100
                                yourinstance.game_type.update_info[yourinstance.lobby][3][0] = data[8:13]
                                yourinstance.game_type.update_info[yourinstance.lobby][3][1] = data[13:17]
                                yourinstance.game_type.update_info[yourinstance.lobby][3][2] = data[17:18]

                            positions = ("POS11---"+str(yourinstance.game_type.update_info[yourinstance.lobby][0][0]).zfill(5)
                                        +str(yourinstance.game_type.update_info[yourinstance.lobby][0][1]).zfill(4)
                                        +yourinstance.game_type.update_info[yourinstance.lobby][0][2]
                                        +str(yourinstance.game_type.update_info[yourinstance.lobby][1][0]).zfill(5)
                                        +str(yourinstance.game_type.update_info[yourinstance.lobby][1][1]).zfill(4)
                                        +yourinstance.game_type.update_info[yourinstance.lobby][1][2]
                                        +str(yourinstance.game_type.update_info[yourinstance.lobby][2][0]).zfill(5)
                                        +str(yourinstance.game_type.update_info[yourinstance.lobby][2][1]).zfill(4)
                                        +yourinstance.game_type.update_info[yourinstance.lobby][2][2]
                                        +str(yourinstance.game_type.update_info[yourinstance.lobby][3][0]).zfill(5)
                                        +str(yourinstance.game_type.update_info[yourinstance.lobby][3][1]).zfill(4)
                                        +yourinstance.game_type.update_info[yourinstance.lobby][3][2])

                            #sends the positions and images of all the different players
                            
                            udp_send(positions,yourinstance.game_type.udp_addr[yourinstance.lobby])
                            
                        elif data[:8] == "SHOOT---": #tells clients where to spawn projectiles
                            udp_send(data+"`",yourinstance.game_type.udp_addr[yourinstance.lobby])
                         
                except Exception as e:
                    print(e)
                


        if timer % 50 == 0 and x: #periodically checks if the user has disconnected
            try: 
                client.send(("`").encode())
            except:
                x = False #removes this thread from server
                try:
                    print(yourinstance.username,"has disconnected")
                except:
                    print("unlogged in user has disconnected")#stops error if user has not logged in yet
                #client has left the game
            
        try:
            try:
                data = client.recv(1024) #receive tcp data
                data = data.decode()
                print("data received:",data)
            except:
                data = ""

            data_list = seperate_data(data) #seperates data using the end bits
            
            for data in data_list:                
                if data[:8] == "USERNAME":
                    yourinstance.username = data[8:] #username
                    conn = sqlite3.connect('game.db')
                    cursor = conn.execute('SELECT username,password,salt from accounts') #gets the records
                    
                    try:
                        for row in cursor: #loops through the records
                            if row[0] == yourinstance.username: #finds the username

                                client.send(str("YOURSALT"+str(row[2])+"`").encode())#sends that user's salt
                    except Exception as e:
                        print(e)

                    conn.close()
                                
                elif data[:8] == "PASSWORD":
                    yourinstance.password = data[8:]
                    
                    
                elif data[:8] == "LOGOUT--": #user has logged out so clears data based on that user
                    all_client_usernames.remove(yourinstance.username)
                    yourinstance.username = ""
                    yourinstance.password = ""
                    yourinstance.logged = False
                    
                elif data[:8] == "REQUEST-":
                    conn = sqlite3.connect('game.db') #connects to database
                    cur = conn.execute('SELECT level,time,username from records') #gets the relevant records
                    
                    for row in cur:
                        client.send(str("REQUESTU"+str(row[0])+str(row[2])+"`").encode())
                        client.send(str("REQUESTT"+str(row[0])+str(row[1])+"`").encode()) #sends the data to client
                    conn.close()

                elif data[:8] == "MYRECORD":
                    level = str(data[8:9])
                    time = float(data[9:])
                    conn = sqlite3.connect('game.db') #connects to database
                    cur = conn.execute('SELECT level,time from records')
                    for row in cur: #row[0] = level,row[1] = time,row[2] = username
                        if str(row[0]) == level and time < float(row[1]): # this means the record has been beaten. Otherwise it has not.
                            print("New world record recieved")
                            conn.execute("DELETE FROM records WHERE level=?", (level))
                            conn.commit()
                            #used to remove rows from the records table                            
                            cur.execute("INSERT INTO records (level, time, username) values (?, ?, ?)",
                                        (level, time, yourinstance.username));
                            conn.commit()
                            #adds a record into the records table

                            client.send(("WREPLAY-" + str(level) + "`").encode())
                    conn.close()

                elif data[:8] == "WEPLAY1-": #weplay1- receives a record from the client
                    if "wreplay1" in locals(): #if list already exists, just add to it
                        add = data[8:]
                        wreplay1.append(add[:-1])
                    else: #else the list must first be created. 
                        wreplay1 = []
                        add = data[8:]
                        wreplay1.append(add[:-1])


                elif data[:7] == "WEPLAYF":#shows that a replay has finished being downloaded
                    print("Record finished downloading for level"+str(data[7:8]))
                    write_replay(wreplay1,"record_replay"+str(data[7:8])+".txt")
                    wreplay1 = []


                elif data[:7] == "REPLAYr": #REPLAYX- sends a replay to the client
                    print("sending replay")
                    replay1 = show_replay("record_replay"+str(data[7:8])+".txt")
                    for i in range(len(replay1)):
                        if i % 10 == 0:
                            t.sleep(0.03) #slows down transmission to prevent errors
                        client.send(("REPLAY1-" + replay1[i] + "`").encode())

                    client.send(("REPLAYF"+str(data[7:8])+ "`").encode())
                        

                    
                elif data[:8] == "WIPE1---": #removes client from a lobby
                    yourinstance.game_type.clients[yourinstance.lobby].remove(client)
                    yourinstance.game_type.client_names[yourinstance.lobby].remove(yourinstance.username)
                    yourinstance.game_type.client_ratings[yourinstance.lobby].remove(yourinstance.rating)
                    
                elif data[:8] == "JOINL1--": # join lobby1
                    yourinstance.lobby = lobby1.find_availible_lobby(client,yourinstance.username,yourinstance.rating,yourinstance.addr)
                    yourinstance.game_type = lobby1
                    print(yourinstance.username,"has joined lobby 1")
                    
                elif data[:8] == "JOINL2--": # join lobby1
                    yourinstance.lobby = lobby2.find_availible_lobby(client,yourinstance.username,yourinstance.rating,yourinstance.addr)
                    yourinstance.game_type = lobby2
                    print(yourinstance.username,"has joined lobby 2")
                    
                elif data[:8] == "READY1--": #wizard wars requires two people to start
                    if yourinstance.game_type.mode != "wizard_wars" or len(yourinstance.game_type.clients[yourinstance.lobby]) > 1:
                        client.send(("CHECKREA`").encode())
                        yourinstance.game_type.ready_ups[yourinstance.lobby] += 1
                        send("READY1--"+str(yourinstance.game_type.ready_ups[yourinstance.lobby]),yourinstance.game_type.clients[yourinstance.lobby])
                        print("READY",yourinstance.lobby)
                        yourinstance.assigned = False
                        yourinstance.leave = False

                        #starts game if ready-ups is eqaul to the amount of players in the lobby
                        if yourinstance.game_type.ready_ups[yourinstance.lobby] == len(yourinstance.game_type.client_names[yourinstance.lobby]) and yourinstance.game_type.ready_ups[yourinstance.lobby] > 0:
                                yourinstance.game_type.ready_ups[yourinstance.lobby] = 0
                                #resets the number of ready-ups for the lobby

                                if yourinstance.game_type.mode == "wizard_wars":
                                    for i in range(len(yourinstance.game_type.client_names[yourinstance.lobby])):
                                        yourinstance.game_type.clients[yourinstance.lobby][i].send(("START1--"+str(i)+"`").encode())
                                else:     
                                    send("START1--",yourinstance.game_type.clients[yourinstance.lobby])
                                yourinstance.game_type.ingame[yourinstance.lobby] = True #shows this lobby is ingame
                                yourinstance.game_type.ready_ups[yourinstance.lobby] = 0
                                print("lobby number",yourinstance.lobby,"has started")

                        
                         
                if data[:8] == "LEAVE1--": #leave lobby1
                    print(yourinstance.username,"has left the lobby")
                    try:
                        yourinstance.game_type.clients[yourinstance.lobby].remove(client)
                    except:pass
                    try: #removes player from lists
                        yourinstance.game_type.client_names[yourinstance.lobby].remove(yourinstance.username)
                        yourinstance.game_type.client_ratings[yourinstance.lobby].remove(yourinstance.rating)
                    except:pass
                    for i in yourinstance.game_type.clients[yourinstance.lobby]:
                        send("WIPE1---",yourinstance.game_type.clients[yourinstance.lobby])
                    for i in range(len(yourinstance.game_type.client_names[yourinstance.lobby])):
                        send(("LOBBY1M-"+str(yourinstance.game_type.client_names[yourinstance.lobby][i])),yourinstance.game_type.clients[yourinstance.lobby])
                        send(("LOBBY1MR"+str(yourinstance.game_type.client_ratings[yourinstance.lobby][i])),yourinstance.game_type.clients[yourinstance.lobby])
                        #sends updated names and ratings
                             
                if data[:8] == "UNREADY1": #leave lobby1
                    yourinstance.game_type.ready_ups[yourinstance.lobby] -= 1
                    send("READY1--"+str(yourinstance.game_type.ready_ups[yourinstance.lobby]),yourinstance.game_type.clients[yourinstance.lobby])

                elif data[:8] == "RATING--": #this updates the user's rating for playing another game
                    conn = sqlite3.connect('game.db')
                    cursor = conn.execute('SELECT username,rating from accounts') #gets the records
                    
                    try:
                        for row in cursor: #loops through the record
                            if row[0] == yourinstance.username: #finds username
                                yourinstance.rating = row[1] #sets new rating 
                                break
                    except Exception as e:
                        print(e)
                    conn.close()                    
                    
                    
                elif data[:8] == "FINISH1-": #when the user tells the server they have finished
                    if yourinstance.game_type.mode == "wizard_wars":
                        if len(data) == 8: #stops this running if the person sending is the last one alive
                            for i in range(len(yourinstance.game_type.player_lives[yourinstance.lobby])):
                                if yourinstance.game_type.player_lives[yourinstance.lobby][i][0] == yourinstance.username:
                                    if yourinstance.game_type.player_lives[yourinstance.lobby][i][2] == 1: #checks if the player has died 10 times
                                        yourinstance.game_type.placements[yourinstance.lobby].insert(0,(yourinstance.username,yourinstance.rating))
                                        print(yourinstance.username,"has been added to placements")
                                        if len(yourinstance.game_type.placements[yourinstance.lobby]) == len(yourinstance.game_type.client_names[yourinstance.lobby]) - 1:
                                            for j in range(len(yourinstance.game_type.client_names[yourinstance.lobby])):
                                                
                                                if (yourinstance.game_type.client_names[yourinstance.lobby][j],yourinstance.game_type.client_ratings[yourinstance.lobby][j]) not in yourinstance.game_type.placements[yourinstance.lobby]:
                                                    yourinstance.game_type.placements[yourinstance.lobby].insert(0,(yourinstance.game_type.client_names[yourinstance.lobby][j],yourinstance.game_type.client_ratings[yourinstance.lobby][j]))
                                                    print("added final member")
                                                #this occurs if there is only one player left.
                                                #as the outcome is already decided, the game ends
                                    
                                    if yourinstance.game_type.player_lives[yourinstance.lobby][i][2] > 0: #keeps lives at 0
                                            yourinstance.game_type.player_lives[yourinstance.lobby][i][2] -= 1#reduces lives
                                            
                                    send("ALPHA---"+str(yourinstance.assigned_number),yourinstance.game_type.clients[yourinstance.lobby])
                                    #alpha is used to make invulnerable players appear opaque
                            send("WIPESCOR",yourinstance.game_type.clients[yourinstance.lobby])#blanks the scores list
                            for i in yourinstance.game_type.player_lives[yourinstance.lobby]:
                                send("SCORES--"+str(i[0])+"  "+str(i[1])+"  "+str(i[2]),yourinstance.game_type.clients[yourinstance.lobby])
                                #add the new scores

                        else:
                            yourinstance.game_type.placements[yourinstance.lobby].insert(0,(yourinstance.username,yourinstance.rating))
                            #adds the user into the placements list in the correct order

                    else:
                        print(yourinstance.username,"has finished")
                        yourinstance.game_type.placements[yourinstance.lobby].append((yourinstance.username,yourinstance.rating))
                        send(("STANDING"+str(yourinstance.username)+"  "+str(yourinstance.rating)),yourinstance.game_type.clients[yourinstance.lobby])
                        #sends user the player who just finshed so they can be displayed to clients

                    if len(yourinstance.game_type.placements[yourinstance.lobby]) == len(yourinstance.game_type.client_names[yourinstance.lobby]): #if game is fully finished
                        
                        changes = [] #stores the changes in rating
                        
                        ratings = [] #stores the player's ratings

                        for i in yourinstance.game_type.disconnections[yourinstance.lobby][::-1]:
                            yourinstance.game_type.placements[yourinstance.lobby].append(i) #add disconnected players in last
                            #order is backwards, so the first player to leave comes last
                            
                        print("intial",yourinstance.game_type.placements[yourinstance.lobby])
                        
                        for i in yourinstance.game_type.placements[yourinstance.lobby]:
                            ratings.append(int(i[1])) #adds the player's ratings
                            
                        print("ratings",ratings)
                        for i in range(len(yourinstance.game_type.placements[yourinstance.lobby])): #looks through the placements of the game
                            changes.append(rank_algorithm(i,ratings)) #adds the changes to the list

                            if changes[i] >= 0: #shows + sign
                                send("DONE----"+str(yourinstance.game_type.placements[yourinstance.lobby][i][0]) + "      " + str(yourinstance.game_type.placements[yourinstance.lobby][i][1]) + "      +" + str(changes[i]),yourinstance.game_type.clients[yourinstance.lobby])
                            else: #shows - sign
                                send("DONE----"+str(yourinstance.game_type.placements[yourinstance.lobby][i][0]) + "      " + str(yourinstance.game_type.placements[yourinstance.lobby][i][1]) + "       " + str(changes[i]),yourinstance.game_type.clients[yourinstance.lobby])

                        conn = sqlite3.connect('game.db')
                        for i in range(len(yourinstance.game_type.placements[yourinstance.lobby])):

                            new_rating = int(yourinstance.game_type.placements[yourinstance.lobby][i][1]) + changes[i] #apply changes
                            cursor = conn.cursor()
                            cursor.execute("UPDATE accounts SET rating = ? WHERE username = ?",(new_rating,yourinstance.game_type.placements[yourinstance.lobby][i][0],))
                            conn.commit() #apply changes to the database
                            print("rank updated")
                        conn.close()

                        print("changes",changes) #outputs changes
                        

                        
                        yourinstance.game_type.clients[yourinstance.lobby] = [] #resets this lobby for future use
                        yourinstance.game_type.client_names[yourinstance.lobby] = []
                        yourinstance.game_type.client_ratings[yourinstance.lobby] = []
                        yourinstance.game_type.ingame[yourinstance.lobby] = False 
                        yourinstance.game_type.udp_addr[yourinstance.lobby] = []
                        yourinstance.game_type.ready_ups[yourinstance.lobby] = 0
                        yourinstance.game_type.update_info[yourinstance.lobby] = [[0,9000,"s"],[0,9000,"s"],[0,9000,"s"],[0,9000,"s"]]

                        yourinstance.game_type.placements[yourinstance.lobby] = []
                        yourinstance.game_type.udp_timeout[yourinstance.lobby] = []
                        yourinstance.game_type.assignments[yourinstance.lobby] = [0,1,2,3]
                        yourinstance.game_type.disconnections[yourinstance.lobby] = []
                        if yourinstance.game_type.mode == "wizard_wars":
                            yourinstance.game_type.player_lives[yourinstance.lobby] = []
                     
                if data[:8] == "UPDATEK1": #receives data that an enemy has been killed
                    print("killed",data[8:11])
                    send(("POS1K---"+str(data[8:11])),yourinstance.game_type.clients[yourinstance.lobby])
                    #sends this to the clients
                
                if not yourinstance.logged and data[:8] == "PASSWORD": #allowsn users to log in
                    conn = sqlite3.connect('game.db')
                    cursor = conn.execute('SELECT username,password,rating,salt from accounts') #gets the records
                    
                    try:
                        for row in cursor: #loops through the record
                            if row[0] == yourinstance.username and row[1] == yourinstance.password and yourinstance.username not in all_client_usernames: #checks details
                                print("User has now logged in")
                                client.send(str("LOGIN---YES`").encode())  #allows the user to log in
                                all_client_usernames.append(yourinstance.username)
                                yourinstance.logged = True
                                yourinstance.rating = row[2]
                                break
                        if not yourinstance.logged:
                            print("Invalid login")
                            client.send(str("LOGIN---NO`").encode()) #denies the user access
                    except Exception as e:
                        print(e)
                    conn.close()
                        
        
        except Exception as e:
            print("error",e)
            x = False
            

    if yourinstance.game_type != None: #checks if the player is on a game
        if yourinstance.game_type.ingame[yourinstance.lobby]:
            print("added user",yourinstance.username,"to disconnects")
            yourinstance.game_type.disconnections[yourinstance.lobby].append((yourinstance.username,yourinstance.rating))
            #adds them to the list of disconnected players
                
            
    allclients.remove(client)
    try:
        if yourinstance.logged:#user may not be logged in
            all_client_usernames.remove(yourinstance.username)
    except:
        print("error removing client from namelist")
        
    if yourinstance.lobby != None: #removes user from any relevant lists
            try:
                yourinstance.game_type.clients[yourinstance.lobby].remove(client)
                print("removed from clients")
                yourinstance.game_type.client_names[yourinstance.lobby].remove(yourinstance.username)
                print("removed from names")
                yourinstance.game_type.client_ratings[yourinstance.lobby].remove(yourinstance.rating)
                print("removed from rating")
                print("udp addr",yourinstance.game_type.udp_addr,yourinstance.client_addr,yourinstance.client_addr[0])
                yourinstance.game_type.udp_addr[yourinstance.lobby].remove(yourinstance.game_type.udp_addr[yourinstance.lobby][yourinstance.assigned_number])
                print("udp addr",yourinstance.game_type.udp_addr)
                print("removed from addr")
                
                if len(yourinstance.game_type.clients) == 1:
                    try:
                        yourinstance.game_type.clients[yourinstance.lobby][0].send(("LASTALIV`").encode())
                        #this is to end the game if only one player remains as the outcome is already decided
                    except Exception as e:
                        print("error sending data to last person",e)

                    
            except Exception as e:
                print("error removing player from lists",e)
            try:
                if len(yourinstance.game_type.client_names[yourinstance.lobby]) == 0:
                    print("resetting lobby")
                    yourinstance.game_type.clients[yourinstance.lobby] = [] #resets this lobby for future use
                    yourinstance.game_type.client_names[yourinstance.lobby] = []
                    yourinstance.game_type.client_ratings[yourinstance.lobby] = []
                    yourinstance.game_type.ingame[yourinstance.lobby] = False 
                    yourinstance.game_type.udp_addr[yourinstance.lobby] = []
                    yourinstance.game_type.ready_ups[yourinstance.lobby] = 0
                    yourinstance.game_type.update_info[yourinstance.lobby] = [[0,9000,"s"],[0,9000,"s"],[0,9000,"s"],[0,9000,"s"]]
                    yourinstance.game_type.udp_timeout[yourinstance.lobby] = []
                    yourinstance.game_type.placements[yourinstance.lobby] = []
                    yourinstance.game_type.assignments[yourinstance.lobby] = [0,1,2,3]
                    yourinstance.game_type.disconnections[yourinstance.lobby] = []
                    if yourinstance.game_type.mode == "wizard_wars":
                        yourinstance.game_type.player_lives[yourinstance.lobby] = [] #resets the lobby if everyone leaves                      
                    
            except Exception as e:
                print("error resetting lobby",e)
            
    client.close()


tcp_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #creates the server socket
ip = socket.gethostbyname(socket.gethostname())  #stores the server ip in a variable
port = 7777 #defines port number
address = (ip,port)     #stores the ip and port together in a tuple. This is a required argument by the socket library
tcp_server.bind(address) #binds the address to the server.
tcp_server.listen(5) #makes the server listen for data being sent to it. 
print("ip:",ip,"\nport:",port) #print the ip and port.

udp_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
port = 8888
address = (ip,port)
udp_server.bind(address)

allclients = []
all_client_usernames = []

lobby1 = lobby("racer") #different lobby instance for each game mode
lobby2 = lobby("wizard_wars")
while True:
    client,addr = tcp_server.accept() #connects to a client    
    client.settimeout(0.005)
    if client not in allclients:
        allclients.append(client)
        
        yourinstance = user() #create instance to store variables about this person
        yourinstance.addr = address
        
        client.send(b'hello') #sends client data to check they are connected
        
        _thread.start_new_thread(clients,(client,addr,yourinstance,)) #creates new thread for concurrent processing

tcp_server.close()
udp_server.close()
