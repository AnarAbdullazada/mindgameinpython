import socketserver
from sqlalchemy import create_engine
import json
import random

engine = create_engine("mysql://root@localhost/mindgame?charset=utf8")
con = engine.connect()

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
            "SelectedCardDndex":None
        },
        "Player2":{
            "Cards":[],
            "SelectedCardDndex":None
        },
        "Player3":{
            "Cards":[],
            "SelectedCardDndex":None
        },
        "Player4":{
            "Cards":[],
            "SelectedCardDndex":None
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

rMate=0
def RoomMates(doorBell):#select player
    global rMate
    rMate=rMate+1
    setup(2)
    return rMate

def setup(PlayerCount):#set starting conditions based on player count.
    game["Table"]["PlayerCount"]=PlayerCount
    if game["Table"]["PlayerCount"]==2:
        game["Table"]["MaxLevel"]=12
        game["Table"]["LiveCount"]=2
        game["Table"]["StarCount"]=1
        for i in range(game["Table"]["PlayerCount"]):
            for k in range(game["Table"]["Level"]):
                game["Players"]["Player"+str(i+1)]["Cards"]=[getDeckCard()]
    
    jgame=json.dumps(game)#refresh database gameState.
    command0="UPDATE kivy SET gameState='"+jgame+"';"
    con.execute(command0)

def getDeckCard():#pops random card from deck.
    randNum=random.randint(0, len(game["Table"]["Cards"])-1)
    selected=game["Table"]["Cards"].pop(randNum)
    return selected

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        selfdata=self.data.decode('utf-8')
        if selfdata=='{"wait":1}':#if player waiting in the room: answer with chosen player for client.
            You=str(RoomMates(selfdata))
            self.request.sendall(You.encode('utf-8'))
        else:#if wants game state: answer with current gameState.
            command1=selfdata
            res=con.execute(command1)
            res=[r for r, in res]
            res=str(res)
            self.request.sendall(res.encode('utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:#listen for tcp packets
        server.serve_forever()
