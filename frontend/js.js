var username;
var ownerName;
var searchQueueYT;
var searchQueueSC;
var stationNum;
var socket;

var adjectives = ["angry","quick","fast","cute","adorable","tiny","ferocious","ugly","smart","dumb","long","spooky","moon"]


var animals = ["Lion","Tiger","Bear","Snake","Fox","Cat","Dog","Jackalope","Rabbit","Tim"];

$(document).ready(function (){
	username = getCookie('username')
	while(username === "")
		username = prompt("Enter a username", generateUsername());
	document.cookie = 'username=' + username;
	$("#user").text(username);
})

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
        	console.log(data)
        		searchQueueYT = data.items;
        		for(var i = 0; i < 5; i++){
        			createYTSearchPreviewItem(data.items[i],i)
        		}
        	}, "json");
        $.get("http://localhost:2000/api/search/soundcloud",{q:$('#searchBox').val()}, function (data){
        		searchQueueSC = data.items;
        		for(var i = 0; i < 5; i++){
        			createSCSearchPreviewItem(data.items[i],i)
        		}
        	}, "json");
    }
});

function emptySearchWindow(){
	$('#searchWindow').empty();
}

function createYTSearchPreviewItem(datum,num){
	var preview = "<a onclick='addbox(" + num + ")'><div class='previewBox'><img src='" + datum.thumbnailUrl + "' /><h1>" + datum.title + "</h1><p>" + datum.channelTitle + "</p></div></a>";


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
	var preview = "<div class='playlistBox' onclick='remove()'><img src='" + item.thumbnailUrl + "' /><h1>" + item.title + "</h1><p>" + item.channelTitle + "</p></div>";
	$('#leftBar').append(preview);
}

function loadStation(data){
	$.get("http://localhost:2000/api/" + data, null, function(data){
		//receive array of all the media objects
		setStationColor(data.hex);
		ownerName = data.owner;
		stationView();
		$('#leftBar').empty();
		var num = 0;
		$.each(data.queue, function(item){
			addToPlayBar(item);
		})

		console.log(data);
	});
}

function setStationColor(color){
	console.log('testing');
	$('header').css('background-color', color);
	$('footer').css('background-color', color)
}

function stationView(){
	$('#leftBar').show();
	$('#chatBar').show();
	$('#stations').hide();
	$('#content').show();
	$('#stationCreator').hide();
	socket = new WebSocket("ws://localhost:5000");
}

function browseView(){
	loadStationList();
	ownerName = null;
	stationNum = null;
	$('#leftBar').hide();
	$('#chatBar').hide();
	$('#stations').show();
	$('#content').hide();
	$('#stationCreator').hide();
	socket.close();
}

function loadStationList(){
	console.log("LOADSTATIONS: DO ME");
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

	if(stationName === "" || stationColor === "")
		return;

	$.post("http://localhost:2000/api/create", {
		title: stationName,
		color: stationColor,
		owner: username,
		visible: $("#stationVisible").val()
	}, function(data) {
		// console.log(data)
		stationNum = data.stationId;
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
		$('#chatArea').prepend("<p>" + $('#chatBarInput').val() + "</p>");
		$('#chatBarInput').val("");


	}
})