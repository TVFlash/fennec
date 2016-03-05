var username;
var ownerName;
var searchQueueYT;
var searchQueueSC;
var stationNum;
var socket;
var playlist = [];

var adjectives = ["angry","quick","fast","cute","adorable","tiny","ferocious","ugly","smart","dumb","long","spooky","moon", "fiery"]


var animals = ["Lion","Tiger","Bear","Snake","Fox","Cat","Dog","Jackalope","Rabbit","Tim", "Chicken"];

$(document).ready(function (){
	username = getCookie('username');
	loadStationList();
	while(username === "")
		username = generateUsername();
	document.cookie = 'username=' + username;
	$("#user").text(username);
	socket = new WebSocket("ws://localhost:5000/");
	socket.onopen = function() {
		console.log("WEBSOCKET OPEN")
	};

	socket.onmessage = function(e) {
		// e.data contains received string.
		addChatMessage($.parseJSON(e.data))
	};

	socket.onclose = function() {
		console.log("#close websocket");
	};

	socket.onerror = function(e) {
		console.log("error" + e)
	};
})

function addChatMessage(data){
	$('#chatArea').prepend("<p>" + data.client + ": " + data.message + "</p>")
}

function generateUsername(){
	return adjectives[Math.floor(Math.random() * adjectives.length)] + animals[Math.floor(Math.random() * animals.length)]
}

function addbox(num){
	if(stationNum == null){
		return;
	}
	if(num < 5){
		$.post("http://localhost:2000/api/" + stationNum + "/add",searchQueueYT[num],function(data){
				addToPlayBar(searchQueueYT[num]);
		})
	} else {
		$.post("http://localhost:2000/api/" + stationNum + "/add",searchQueueSC[num-5],function(data){
				addToPlayBar(searchQueueSC[num-5]);
		})
	}

}

// $('#user').on("click", function(e){

// 	username = generateUsername();
// 	document.cookie = 'username=' + username;
// 	$("#user").text(username);
// });

function sendChatMessage(string) {
	var packet = {};
	packet.type = "send";
	packet.stationid = stationNum;
	packet.message = string;
	packet.owner = username;
	// You can send message to the Web Socket using ws.send.
	var message = JSON.stringify(packet);
	socket.send(message);
}

function joinChat() {
	var packet = {};
	packet.type = "join";
	packet.stationid = parseInt(stationNum);
	// You can send message to the Web Socket using ws.send.
	socket.send(JSON.stringify(packet));
}

function leaveChat() {
	var packet = {};
	packet.type = "leave";
	packet.stationid = stationNum;
	// You can send message to the Web Socket using ws.send.
	socket.send(JSON.stringify(packet));
}

//Lifted from W3Schools
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}

$('#searchBox').on("keypress", function (e) {

    if (e.keyCode == 13) { //newline

        // Cancel the default action on keypress event
        e.preventDefault();
        emptySearchWindow();

        $.get("http://localhost:2000/api/search/youtube",{q:$('#searchBox').val()}, function (data){
        		searchQueueYT = data.items;
        		for(var i = 0; i < 5; i++){
        			data.items[i].source = 0;
        			data.items[i].uniqueId = data.items[i].videoId;
        			createYTSearchPreviewItem(data.items[i],i)
        		}
        	}, "json");
        $.get("http://localhost:2000/api/search/soundcloud",{q:$('#searchBox').val()}, function (data){
        		searchQueueSC = data.items;
        		for(var i = 0; i < 5; i++){
        			data.items[i].source = 1;
        			data.items[i].uniqueId = data.items[i].trackId;
        			createSCSearchPreviewItem(data.items[i],i);
        		}
        	}, "json");
    }
});

function emptySearchWindow(){
	$('#searchWindow').empty();
}

function createYTSearchPreviewItem(datum,num){
	var preview = "<a onclick='addbox(" + num + ")'><div class='previewBox'><img src='" + datum.thumbnail + "' /><h1>" + datum.title + "</h1><p>" + datum.channelTitle + "</p></div></a>";


	$('#searchWindow').append(preview)
}

function createSCSearchPreviewItem(datum, num){
	if(datum.thumbnail == null)
		datum.thumbnail = "soundcloud.png";
	if(datum.description == null || datum.description === "")
		datum.description = "Not Provided"
	var preview = "<a onclick='addbox(" + (num + 5) + ")'><div class='previewBox'><img src='" + datum.thumbnail + "'/><h1>" + datum.title + "</h1><p>" + datum.uploader + "</p></div></a>";
	$('#searchWindow').append(preview);
}

function addToPlayBar(item, num){
	console.log(item);
	var preview = "<div class='playlistBox' onclick='removePlayListItem(\"" + item.uniqueId + "\")'><img src='" + item.thumbnail + "' /><h1>" + item.title + "</h1><p>" + item.channelTitle + "</p></div>";

	$('#leftBar').append(preview);
}

function addToPlayBarFresh(item){
	console.log(item);
	if(item.videoUrl === null){
		item.source = 1;
		item.uniqueId = videoId;
	} else {
		item.source = 0;
		item.uniqueId = trackId;
	}
	var preview = "<div class='playlistBox' onclick='removePlayListItem(\"" + item.uniqueId + "\")'><img src='" + item.thumbnail + "' /><h1>" + item.title + "</h1><p>" + item.channelTitle + "</p></div>";
	playlist.push(item);
	$('#leftBar').append(preview);
}


function removePlayListItem(id){
	console.log("Received remove for #" + id);
	$.get("http://localhost:2000/api/" + stationNum + "/" + id + "/remove", {},function(data){
		console.log(data);
	});
}

function loadStation(data){
	stationNum = data;
	$.get("http://localhost:2000/api/" + data, null, function(datas){
		//receive array of all the media objects
		datas = $.parseJSON(datas);
		setStationColor(datas.color);
		//stationNum = datas.stationid;
		stationView();
		joinChat();
		$('#leftBar').empty();
		var num = 0;
		$.each(datas.queue, function(item){
			addToPlayBarFresh(item);
		})

		console.log(datas);
	});
}

function setStationColor(color){
	console.log(color);
	color = "#" + color;
	$('header').css('background-color', color);
	$('footer').css('background-color', color)
}

function stationView(){
	playlist = [];
	$('#leftBar').show();
	$('#chatBar').show();
	$('#stations').hide();
	$('#content').show();
	$('#stationCreator').hide();
}

function browseView(){
	setStationColor("008ae6");
	loadStationList();
	ownerName = null;
	stationNum = null;
	$('#leftBar').hide();
	$('#chatBar').hide();
	$('#stations').show();
	$('#content').hide();
	$('#stationCreator').hide();
	leaveChat();
}

function loadStationList(){
	console.log("swag")
	$.get("http://localhost:2000/api/stations", {},function(data){
		console.log(data);
	}, "json");
}

function createStationBox(item){
	console.log(item);
	var box = "<div id='stationBox' style='background-color: #" + item.color + "' onmouseup='loadStation(" + item.id + ")'><h2>" + item.name + "</h2></div>";
	$('#stationContainer').append(box)
}

$('#createStation').on("click", function(e) {
	$('#stationCreator').fadeIn();
})

$('#cancelCreate').on("click", function(e) {
	$('#stationCreator').fadeOut();
})

$('#create').on("click", function(e) {
	var stationName = $('#stationName').val();
	var stationColor = $('#stationColor').val();
	stationColor = stationColor.substring(1,8);
	console.log(stationColor);

	if(stationName === "" || stationColor === "")
		return;

	var pack = {
		'name': stationName,
		'color': stationColor.substring(1, 8),
		'owner': username,
		'visible': $("#stationVisible").val()
	};

	console.log(pack);

	$.post("http://localhost:2000/api/create", pack, function(data) {
		console.log(data);
		loadStation(data.stationId)
	}, "json");
})

$('#refreshStations').on("click", function(e){
	loadStationList();
})

$('#logo').on("click", function(e) {
	browseView();
})

$('#chatBarInput').on("keypress", function(e){
	if(e.keyCode == 13 && $('#chatBarInput').val() !== ""){
		sendChatMessage($('#chatBarInput').val());
		$('#chatBarInput').val("");

	}
})