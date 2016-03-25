var username;
var ownerName;
var currentId;
var searchQueueYT;
var searchQueueSC;
var stationNum;
var socket;
var playlist = [];
var host = "";
var wshost = "ws://moore14.cs.purdue.edu:5000/";
var current;
var time_remaining;
var time_passed;
var moveTime;
var pollStation;
var videos_watched = 0;
var received = 0;

var adjectives = ["Angry","Quick","Fast","Cute","Adorable","Tiny","Ferocious","Ugly","Smart","Dumb","Long","Spooky","Moon", "Fiery", "Chubby", "Esoteric", "Wild", "Calm", "Chill", "Neato", "Rad", "Pickled", "Tubby", "Indecent", "Educated"];


var animals = ["Lion","Tiger","Bear","Snake","Fox","Cat","Dog","Jackalope","Rabbit","Tim", "Chicken", "Cniderian", "Octopus", "Jellyfish", "Roc", "Dragon", "Horse", "Aardvark", "Canary", "Parrot", "Ferret", "Eel", "Okapi", "Vulture"];

$(document).ready(function (){
	username = getCookie('username');
	while(username === "")
		username = generateUsername();

	document.cookie = 'username=' + username;
	$("#user").text(username);
	socket = new WebSocket(wshost);
	socket.onopen = function() {
		if(getQueryVariable("station") === 'null'){
			browseView();
		}
		else if(getQueryVariable("station")){
			loadStation(getQueryVariable("station"));
		} else {
			browseView();
		}
	};

	socket.onmessage = function(e) {
		var tempData = $.parseJSON(e.data);
		if(!received){
			username = resolveUsername(tempData.client);
			$("#user").text(username);
			received = true;
			usernum = tempData.client;
		}
		addChatMessage(tempData)
	};

	socket.onclose = function() {
		console.log("#closed websocket");
	};

	socket.onerror = function(e) {
		console.log("error" + e)
	};
	// if(getQueryVariable("station") === 'null'){
	// 	browseView();
	// }
	// else if(getQueryVariable("station")){
	// 	loadStation(getQueryVariable("station"));
	// } else {
	// 	browseView();
	// }

	document.cookie = 'username=' + username;
	$("#user").text(username);

})



function addChatMessage(data){
	$('#chatArea').prepend("<p>" + resolveUsername(data.client) + ": " + data.message + "</p>")
}

function generateUsername(){
	return adjectives[Math.floor(Math.random() * adjectives.length)] + animals[Math.floor(Math.random() * animals.length)]
}

function resolveUsername(clientNum){
	var offset = Math.floor(clientNum / animals.length);
	var name = clientNum % animals.length;
	return adjectives[name + offset] + " " + animals[name];
}

function addbox(num){
	if(stationNum == null){
		return;
	}
	if(num < 5){
		var pack = {};

		pack.id = searchQueueYT[num].uniqueId;
		pack.thumbnail = searchQueueYT[num].thumbnail;
		pack.uri = searchQueueYT[num].videoUrl;
		pack.addedBy = searchQueueYT[num].channelTitle;
		pack.title = searchQueueYT[num].title;
		pack.length = searchQueueYT[num].duration;

		$.ajax({
			method: "POST",
			url: host + "/api/" + stationNum + "/add",
			data: JSON.stringify(pack),
			contentType: "application/json"
		}).done(function(data){
			addToPlayBar(searchQueueYT[num]);
		})

		// $.post(host + "/api/" + stationNum + "/add",searchQueueYT[num],function(data){
		// 		addToPlayBar(searchQueueYT[num]);
		// })
	} else {
		var pack = {};

		pack.id = searchQueueSC[num].trackId;
		pack.thumbnail = searchQueueSC[num].thumbnail;
		pack.uri = searchQueueSC[num].trackUrl;
		pack.addedBy = searchQueueSC[num].uploader;
		pack.length = searchQueueSC[num].duration / 1000; //Soundcloud uses MS, not S
		pack.title = searchQueueSC[num].title;


		$.ajax({
			method: "POST",
			url: host + "/api/" + stationNum + "/add",
			data: JSON.stringify(pack),
			contentType: "application/json"
		}).done(function(data){
			addToPlayBar(searchQueueSC[num]);
		})

		// $.post(host + "/api/" + stationNum + "/add",searchQueueSC[num-5],function(data){
		// 		addToPlayBar(searchQueueSC[num-5]);
		// })
	}

}

// $('#user').on("click", function(e){

// 	username = generateUsername();
// 	document.cookie = 'username=' + username;
// 	$("#user").text(username);
// });


function updateQueryStringParameter(uri, key, value) {
  var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
  var separator = uri.indexOf('?') !== -1 ? "&" : "?";
  if (uri.match(re)) {
    return uri.replace(re, '$1' + key + "=" + value + '$2');
  }
  else {
    return uri + separator + key + "=" + value;
  }
}

function getQueryVariable(variable)
{
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
       }
       return(false);
}

function sendChatMessage(string) {
	var packet = {};
	packet.type = "send";
	packet.stationid = parseInt(stationNum);
	packet.message = string;
	packet.owner = username;
	// You can send message to the Web Socket using ws.send.
	var message = JSON.stringify(packet);
	console.log(message)
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

        $.get(host + "/api/search/youtube",{q:$('#searchBox').val()}, function (data){
        		searchQueueYT = data.items;
        		for(var i = 0; i < 5; i++){
        			data.items[i].source = 0;
        			data.items[i].uniqueId = data.items[i].videoId;
        			createYTSearchPreviewItem(data.items[i],i)
        		}
        	}, "json");
        setTimeout($.get(host + "/api/search/soundcloud",{q:$('#searchBox').val()}, function (data){
        		searchQueueSC = data.items;
        		for(var i = 0; i < 5; i++){
        			data.items[i].source = 1;
        			data.items[i].uniqueId = data.items[i].trackId;
        			createSCSearchPreviewItem(data.items[i],i);
        		}
        	}, "json"),200);
    }
});

function emptySearchWindow(){
	$('#searchWindow').empty();
}

function createYTSearchPreviewItem(datum,num){
	var preview = "<a onclick='addbox(" + num + ")'><div class='previewBox'><img src='" + datum.thumbnail + "' /><h1>" + datum.title + "</h1><p>" + datum.channelTitle + "</p></div></a>";


	$('#searchWindow').append(preview);
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
	//console.log(item);
	var preview = "<div class='playlistBox' onclick='removePlayListItem(\"" + item.uniqueId + "\")'><img src='" + item.thumbnail + "' /><h1>" + item.title + "</h1><p>" + item.channelTitle + "</p></div>";

	$('#leftBar').append(preview);
}

function addToPlayBarFresh(item){
	if(item.type === "SoundCloud"){
		if(item.thumbnail === null)
			item.thumbnail = "soundcloud.png";
		item.source = 1;
		item.uniqueId = item.id;
	} else {
		item.source = 0;
		item.uniqueId = item.id;
	}
	playlist.push(item);

	var preview = "<div class='playlistBox' onclick='removePlayListItem(\"" + item.uniqueId + "\")'><img src='" + item.thumbnail + "' /><h1>" + item.title + "</h1><p>" + item.addedBy + "</p></div>";
	$('#leftBar').append(preview);
}


function removePlayListItem(id){
	//console.log("Received remove for #" + id);
	$.get(host + "/api/" + stationNum + "/" + id + "/remove", {},function(data){
	//	console.log(data);
	});
}

function loadStation(data){
	stationNum = data;
	$.get(host + "/api/" + data, null, function(datas){
		//console.log(datas)
		//receive array of all the media objects
		setStationColor(datas.color);
		videos_watched = 0;
		time_passed = datas.media_elapsed_time;
		//console.log("time: " + time_passed);

		pollStation = setInterval(function(){
			if(time_remaining > 0)
				refreshMedia();
		},2000);

		window.history.pushState(location.href, "Fennec Station " + data, "?station="+data);

		stationView();
		joinChat();

		refreshMedia();
	}, "json");
}

function refreshMedia(){
	$.get(host + "/api/" + stationNum, null, function(datas){
		$('#leftBar').empty();
		var i = 0;
		var len = datas.queue.length;
		for(var j = 0; j < len; j++){
			var key = j;
			addToPlayBarFresh(datas.queue[key]);
		}
		var data = playlist[0];
		var time = datas.media_elapsed_time
		loadMedia(data, time);

		// if(data.type == "YouTube"){
		// 	time_remaining = data.length + 1;
		// 	if(videos_watched == 0){
		// 		loadYoutubeVideo(data.id,time_passed);
		// 	} else {
		// 		loadYoutubeVideo(data.id,0);
		// 		time_passed = 0;
		// 	}
		// } else if(data.type == "SoundCloud"){
		// 	time_remaining = data.length;
		// 	if(videos_watched == 0){
		// 		loadSoundCloudTrack(data.id,time_passed);
		// 	} else {
		// 		loadSoundCloudTrack(data.id,0);
		// 		time_passed = 0;
		// 	}
		// } else {
		// 	$('#content').empty()
		// 	$('#content').append("there is nothing in the queue")
		// }
	}, "json");
}

//<iframe width="100%" height="450" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/136074708&amp;auto_play=false&amp;hide_related=false&amp;show_comments=true&amp;show_user=true&amp;show_reposts=false&amp;visual=true"></iframe>
function loadMedia(data,time){
	if(data.type == "YouTube"){
		loadYoutubeVideo(data.id,time);
	} else if(data.type == "SoundCloud"){
		loadSoundCloudTrack(data.id,time);
	} else {
		$('#content').empty()
		$('#content').append("there is nothing in the queue")
	}
}

function loadSoundCloudTrack(url, time){
	$('#content').empty();
	$('#content').append('<iframe width="100%" height="600" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/' + url + '&amp;auto_play=true&amp;hide_related=false&amp;show_comments=false&amp;show_user=true&amp;show_reposts=false&amp;visual=true#time=0:50"></iframe>');
}

function loadYoutubeVideo(url, time){
	var currentId = url;
	$('#content').empty();
	$('#content').append('<iframe width="100%" height="100%" src="https://www.youtube.com/embed/' + url + '?autoplay=1&start=' + time + '" frameborder="0" allowfullscreen></iframe>');
}

function setStationColor(color){
	color = "#" + color;
	$('header').css('background-color', color);
	$('footer').css('background-color', color)
}

function stationView(){
	playlist = [];
	$('#leftBar').show();
	$('#chatArea').empty();
	$('#chatBar').show();
	$('#stations').hide();
	$('#content').show();
	$('#stationCreator').hide();
}

function browseView(){
	$('#content').empty();
	clearInterval(pollStation);
	clearInterval(moveTime);
	setStationColor("008ae6");
	window.history.pushState(location.href,"Fennec Browse", updateQueryStringParameter(location.href, "station", null));
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
	$('#stationContainer').empty();
	$.get(host + "/api/stations", {},function(data){
		var i = 0;
		var len = data.length;
		for(var j = 0; j < len; j++){
			var key = j;
			createStationBox(data[key]);

		}
	}, "json");
}

function createStationBox(item){
	var box = "<div class='stationBox' style='background-color: #" + item.color + "' onmouseup='loadStation(" + item.id + ")'>" + item.name + "</div>";
	$('#stationContainer').append(box);
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
	var stationVisible = $('#stationVisible').val();
	stationColor = stationColor.substring(1,8);
//	console.log(stationColor);

	if(stationName === "" || stationColor === "")
		return;


//'visible': $("#stationVisible").val()
	console.log("GET VISIBILITY DONE");
	$.ajax({
		method: "POST",
		url: host + "/api/create",
		data: JSON.stringify({
			'name': stationName,
			'color': stationColor,
			'visibility': stationVisible
		}),
		contentType: "application/json"
	}).done(function(data){
		loadStation(data.stationId);
	})
	// $.post("http://localhost:2000/api/create", pack, function(data) {
	// 	loadStation(data.stationId)
	// }, "json");
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