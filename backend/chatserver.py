from websocket_server import WebsocketServer
import json
import requests
#Chat Server
#====================================================================================
#MARK: WebSocket
#====================================================================================

#Beginning of Chat websocket implementation
MAX_NUM_STATIONS = 100
chat_station_users = [[] for i in range(MAX_NUM_STATIONS)] #chat_station_users[stationid] = list_of_users
station_index = 0
uservotes = [{} for i in range(MAX_NUM_STATIONS)] #list of kick votes for each user
currMedVote = 0 #number of skips for currently playing media
currMedID = 0 

#Just join chat services
def new_client(client, server):
	print("%d connected" % client['id'])
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
                elif json_obj['stationid'] < 0:
                        raise ValueError;
        except ValueError:
                server.send_message(client, "Malformed JSON or invalid value");
                return;

        print json_obj
        stationid = json_obj['stationid'];

	if json_obj['type'] == 'send':
                #check for commands
                mess = json_obj['message']
                parts = mess.split(' ')
                if mess == '!skip':
                    print 'got a skip'
                    url = 'http://localhost:2000/api/' + str(stationid)
                    r = requests.get(url)
                    print '**' + str(r.content) + '**'

                    #check if currently playing song is same as before, if not reset count to 0
                    #currMedVote += 1
                    #if currMedVote > 5:
                        #tell server to remove currently playing media
                  #  print 'ended skip'
                    pass
                if len(parts) > 1:
                    if parts[0] == '!kick':
                  #      print 'got a kick'
                        user = parts[1]
                        if user not in uservotes[stationid]:
                            uservotes[stationid][user] = [] 
                            uservotes[stationid][user].append(client)
                           # print 'adding a new one'
                        else:
                #            if client not in uservotes[stationid][user]:
                            uservotes[stationid][user].append(client)
                       #     print 'adding to old'
                            if len(uservotes[stationid][user]) * 2 > len(chat_station_users[stationid]):
              #                  print 'should be kicking now'
                                for cl in chat_station_users[stationid]:
                                    print cl['id'], type(cl['id'])
                                    if cl['id'] == int(user):
              #                          print 'found em'
                                        client_leave_chat_station(cl, stationid)

		#Send normal message
                client_send_chat_station(client, stationid, json_obj['message']);
	elif json_obj['type'] == 'join':
		#Join station
		client_join_chat_station(client, stationid)
	elif json_obj['type'] == 'leave':
		#Leave station
		client_leave_chat_station(client, stationid)
	return

def client_send_chat_station(client, stationid, message):
	for station in chat_station_users:
		for c in station:
			if c['id'] != client['id']:
				server.send_message(c, build_json(client, message));
			return;

#Put client into specific station
def client_join_chat_station(client, stationid):
        if client in chat_station_users[stationid]:
                print("%d already in %d" % (client['id'], stationid));
                return
	chat_station_users[stationid].append(client)
        client_send_chat_station(client, stationid, "joined the channel");
		client_send_chat_station(client, stationid, "joined the channel");
        print("%d joined %d" % (client['id'], stationid));
	return

#Remove client from specific station
def client_leave_chat_station(client, stationid):
        for client in chat_station_users[stationid]:
                chat_station_users[stationid].remove(client)
                client_send_chat_station(client, stationid, "left the channel");
                print("%d left %d" % (client['id'], stationid));
#       print("%d not in %d" % (client['id'], stationid));
	return

def build_json(client, message):
        data = {};
        data['client'] = client['id'];
        data['message'] = message;
        return json.dumps(data);

if __name__ == '__main__':
	server = WebsocketServer(5000, "0.0.0.0")
	server.set_fn_new_client(new_client)
	server.set_fn_client_left(client_left)
	server.set_fn_message_received(message_received)
	server.run_forever()

#End of Chat websocket implementation
