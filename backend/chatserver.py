from websocket_server import WebsocketServer
import json
#Chat Server
#====================================================================================
#MARK: WebSocket
#====================================================================================

#Beginning of Chat websocket implementation
MAX_NUM_STATIONS = 100
chat_station_users = [[] for i in range(MAX_NUM_STATIONS)] #chat_station_users[stationid] = list_of_users
station_index = 0

#Just join chat services
def new_client(client, server):
	print("%d connected" % client['id'])
	server.send_message_to_all("New Client")
        return

#Just leave chat services
def client_left(client, server):
	print("%d disconnected" % client['id'])
        for i in range(MAX_NUM_STATIONS):
                client_leave_chat_station(client, i);
        return

#Redirect to handlers or send message
def message_received(client, server, message):
	print "Received '%s'" % message
        try:
        	json_obj = json.loads(message)
        except ValueError:
                server.send_message(client, "JSON parsing error");
                return
        data = json.dumps(json_obj);
        try:
                #JSON error handling
                print data
                if not '"type"' in data:
                        raise ValueError;
                elif json_obj['type'] == 'send':
                        if not '"message"' in data:
                                raise ValueError("roof");
                if not '"stationid"' in data:
                        raise ValueError;
        except ValueError:
                server.send_message(client, "Malformed JSON");
                return;

        print json_obj

	if json_obj['type'] == 'send':
		#Send normal message
		for c in chat_station_users[json_obj['stationid']]:
			server.send_message(c, json_obj['message'])
	elif json_obj['type'] == 'join':
		#Join station
		client_join_chat_station(client, json_obj['stationid'])
	elif json_obj['type'] == 'leave':
		#Leave station
		client_leave_chat_station(client, json_obj['stationid'])
	return

#Put client into specific station
def client_join_chat_station(client, stationid):
        if client in chat_station_users[stationid]:
                print("%d already in %d" % (client['id'], stationid));
                return
        print("%d joined %d" % (client['id'], stationid));
	chat_station_users[stationid].append(client)
	return

#Remove client from specific station
def client_leave_chat_station(client, stationid):
        if client in chat_station_users[stationid]:
                chat_station_users[stationid].remove(client)
                print("%d left %d" % (client['id'], stationid));
                return
#       print("%d not in %d" % (client['id'], stationid));
	return

if __name__ == '__main__':
	server = WebsocketServer(5000)
	server.set_fn_new_client(new_client)
	server.set_fn_client_left(client_left)
	server.set_fn_message_received(message_received)
	server.run_forever()

#End of Chat websocket implementation
