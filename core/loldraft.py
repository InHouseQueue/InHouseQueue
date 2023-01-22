import websocket
import json

false = False

def getStr(string, start, end):
	str2 = string.split(start)
	str2 = str2[1].split(end)
	return str2[0]

class WS:

    def __init__(self):
        self.socket = 'wss://draftlol.dawe.gg/'
        self.close = None # default value at start

    def stream(self):
        self.ws = websocket.WebSocketApp(
                    self.socket,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open
                  )

        #print('run forever')
        self.ws.run_forever()
        
    def on_open(self, ws):
        #print('on_open:', ws)

        #data = {"type": "joinroom", "roomId": "XcLps_nS", "password": ""}
        #data = {"type": "createroom"}
        data = {"type": "createroom", "blueName": "In-House Queue Blue", "redName": "In-House Queue Red", "disabledTurns": [], "disabledChamps": [], "timePerPick": "30", "timePerBan": "30"}
        self.ws.send(json.dumps(data))

    def on_close(self, ws):
        print('on_close:', ws)

    def on_message(self, ws, message):
        #print('on_message:', ws, message)
        
        data = json.loads(message)

        if data['type'] == 'update':
            self.close = data['data']['last']

        self.ws.close()
        self.response = ("🔵 https://draftlol.dawe.gg/" + data["roomId"] +"/" +data["bluePassword"], "🔴 https://draftlol.dawe.gg/" + data["roomId"] +"/" +data["redPassword"], "\n**Spectators:** https://draftlol.dawe.gg/" + data["roomId"])

    def get_data_out(self):
        return self.close
   
    def on_error(self, ws, error):
        print('on_error:', ws, error)
        
# --- main ---

websocket.enableTrace(False)  # if you want to see more information  
                             # but code works also without this line

WS().stream()

'''
var = []

async def test():
    async with websockets.connect('wss://www.bitmex.com/realtime') as websocket:
        response = await websocket.recv()
        print(response)

        await websocket.send("ping")
        response = await websocket.recv()
        print(response)
        var.append(response)

        await websocket.send(json.dumps({"op": "subscribe", "args": "test"}))
        response = await websocket.recv()
        print(response)

asyncio.get_event_loop().run_until_complete(test())

print(var)
'''