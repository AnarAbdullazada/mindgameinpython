import random
import json
import socket
import time
import threading

allCards=list(range(1,101))
game={
    "LevelCards":{
        "Level1": [0,0],
        "Level2": [0,1],
        "Level3": [1,0],
        "Level4": [0,0],
        "Level5": [0,1],
        "Level6": [1,0],
        "Level7": [0,0],
        "Level8": [0,1],
        "Level9": [1,0],
        "Level10":[0,0],
        "Level11":[0,0],
        "Level12":[0,0],
    },
    "Players":{
        "Player1":{
            "Cards":[],
            "SelectedCardDndex":None,
            "Hand":False
        },
        "Player2":{
            "Cards":[],
            "SelectedCardDndex":None,
            "Hand":False
        },
        "Player3":{
            "Cards":[],
            "SelectedCardDndex":None,
            "Hand":False
        },
        "Player4":{
            "Cards":[],
            "SelectedCardDndex":None,
            "Hand":False
        },
    },
    "Table":{
        "Cards":allCards,
        "TableCards":[],
        "LiveCount":None,
        "StarCount":None,
        "PlayerCount": None,
        "MaxLevel": 100,
        "WinStatus": None,
        "Level":1
    }
}
me=None

def readFile():#not used
    f = open("game.json", "r")
    return f.read()
    
def ToFlask(Json, Name):#sends local gameState to database.
    Json=json.dumps(Json)
    execSQL("UPDATE kivy SET gameState='"+Json+"';")

def FromFlask(Name):#gets new fresh gameState from database (once not constantly).
    req=execSQL("SELECT gameState FROM kivy;")
    reqtext=req.strip("]['")
    return reqtext

def execSQL(SQL):
    HOST, PORT = "0.tcp.ngrok.io", 18516
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:# Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(bytes(SQL + "\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")
    return received

def getDeckCard():#pops random card from deck
    randNum=random.randint(0, len(game["Table"]["Cards"])-1)
    selected=game["Table"]["Cards"].pop(randNum)
    return selected

def startLevel():#runs at the start of each level.
    while 1:
        global copygame
        global me#my player number.
        copygame=json.dumps(game)
        selectedP=str(me)
        print(selectedP)
        if int(selectedP)>game["Table"]["PlayerCount"] or int(selectedP)<1:#see if my player number is allowed.
            print("Player"+selectedP+" Is Invalid Player")
            continue
        print(game["Players"]["Player"+selectedP])#print what cards i have.
        #implement Star Vote here
        selectedC=int(newInput("Select a card:\n"))#wait for a card to be chosen by user.
        if not (selectedC in game["Players"]["Player"+selectedP]["Cards"]):
            continue
        game["Players"]["Player"+selectedP]["SelectedCardDndex"]=selectedC
        game["Players"]["Player"+selectedP]["Cards"].remove(selectedC)
        print(game["Players"]["Player"+selectedP])
        while 1:
            comm=newInput("Command me (Totable, Cancel):\n")#wait for what you should do with chosen card.
            if comm=="Totable":#putting card on the table
                game["Table"]["TableCards"].append(selectedC)
                game["Players"]["Player"+selectedP]["SelectedCardDndex"]=None
                for elem in game["Players"]:#if players have a cards smaller than card that was put on the table...
                    if game["Players"][elem]["Cards"]!=[]:
                        if min(game["Players"][elem]["Cards"])<selectedC:
                            while min(game["Players"][elem]["Cards"])<selectedC:
                                game["Table"]["Cards"].append(min(game["Players"][elem]["Cards"]))
                                game["Players"][elem]["Cards"].remove(min(game["Players"][elem]["Cards"]))#...remove their small cards and...
                                game["Table"]["WinStatus"]=False#...make them loose
                                if game["Players"][elem]["Cards"]==[]:
                                    break
                                    
                if game["Table"]["WinStatus"]==False:#if you are looseing use lifeCard to be saved.
                    game["Table"]["LiveCount"]-=1
                    if game["Table"]["LiveCount"]==0:#if you dont have lifeCards left the you lost.
                        print("---You lost!----")
                    else:
                        print("---You lost a live!---")
                        game["Table"]["WinStatus"]=None
                break
            if comm=="Cancel":#unchoose chosen card.
                game["Players"]["Player"+selectedP]["Cards"].append(selectedC)
                game["Players"]["Player"+selectedP]["SelectedCardDndex"]=None
                break
            else:#unexpected command was given.
                print("Sorry, didn't catch that:\n")
        if game["Table"]["WinStatus"]==False:#tell other player that you lost by refreshing gameState.
            ToFlask(game, 'Name')
            print("---You lost!----")
            break
        display()#display result of the command being executed on chosen card.
        ToFlask(game, 'Name')#refresh database to let other player know the result of command.
        checker=True
        for elem in game["Players"]:
            if game["Players"][elem]["Cards"]!=[]:
                checker=False
        if checker==True:
            break
    if game["Table"]["WinStatus"]!=False:#if you haven't lost by the end of the round: check if cards are ordered...
        mem=0
        for i in game["Table"]["TableCards"]:
            if i>mem:
                mem=i
            else:
                mem=None
        if (mem!=None):#...if so you pass this round. Load a new level and give rewards for passing.
            print("You pass this round.")
            game["Table"]["Cards"]+=game["Table"]["TableCards"]
            game["Table"]["TableCards"]=[]
            for elem in game["Players"]:
                game["Table"]["Cards"]+=game["Players"][elem]["Cards"]
                game["Players"][elem]["Cards"]=[]
            game["Table"]["LiveCount"]+=game["LevelCards"]["Level"+str(game["Table"]["Level"])][0]
            game["Table"]["StarCount"]+=game["LevelCards"]["Level"+str(game["Table"]["Level"])][1]
            game["Table"]["Level"]+=1
            for i in range(game["Table"]["PlayerCount"]):
                for k in range(game["Table"]["Level"]):
                    game["Players"]["Player"+str(i+1)]["Cards"].append(getDeckCard())
        else:
            print("Error.")

def setup(PlayerCount):#No Longer Needed. Setup is done on server side.
    game["Table"]["PlayerCount"]=PlayerCount
    if game["Table"]["PlayerCount"]==2:
        game["Table"]["MaxLevel"]=12
        game["Table"]["LiveCount"]=2
        game["Table"]["StarCount"]=1
        for i in range(game["Table"]["PlayerCount"]):
            for k in range(game["Table"]["Level"]):
                game["Players"]["Player"+str(i+1)]["Cards"].append(getDeckCard())

    game["LevelCards"]["Level"+str(game["Table"]["Level"])]

def display():#display gameState in readable way.
    for elem in game["Table"]:
        print(elem, "--", game["Table"][elem])
    for i in range(game["Table"]["PlayerCount"]):
        print("Player"+str(i+1), game["Players"]["Player"+str(i+1)]["Cards"])


res=None
autostop=False
copygame=None
def tr1(string):#wait for input while...
    global res
    res=input(string)

def tr2(string):#...constantly refeshing for changes.
    global res
    global autostop
    global game
    global copygame
    while res==None:#when input given by user.
        time.sleep(0.3)
        '''
            Only change local game data if change was made by other players. 
            While wating for input NewInput() also continuesly fetches fresh data from server and checks if any changes were made. 
            So changes made during wating period between inputs were made by other players.
            Copygame is state of game before waiting for input so it will not be changed (in theory) by whatever happens during waiting period.
        '''
        jsonout=FromFlask('Name')
        if copygame!=jsonout:# refresh local gameState to match database gameState.
            game=json.loads(jsonout)
            copygame=jsonout
            display()
            print(string)
    autostop=True#stop Newinput.
    
def newInput(string):#do t1 and t2 at the same time.
    global res
    global autostop
    print("running")
    
    t1 = threading.Thread(target=tr1, args=(string,))
    t2 = threading.Thread(target=tr2, args=(string,))
    t1.start()
    t2.start()
    
    while not autostop:#stop when t2 said so.
        time.sleep(0.3)
    copyres=res
    time.sleep(0.3)
    res=None#reset res for next Time NewInput() runs.
    autostop=False
    return copyres#return input given by user.


me=execSQL('{"wait":1}') # make server setup game by waiting in the room.
print("Player number: ",me)# show my player number.
jsonout=FromFlask('Name')# sync with database gameState.
game=json.loads(jsonout)
copygame=jsonout
while 1:
    if game["Table"]["Level"]<=game["Table"]["MaxLevel"]:
        display()#display what gameSate is like before Level starts.
        ToFlask(game, 'Name')#send local gameState after new Level is loaded to the server.
        startLevel()#start level
        if game["Table"]["WinStatus"]==False:#No lives left so end the game.
            print("---You lost!----")
            break
    else:
        print("You Win!")#passed all Levels so end the game.
        game["Table"]["WinStatus"]=True
        break
