var username;

$(document).ready(function (){
	username = getCookie('username')
	while(username === "")
		username = prompt("Enter a username","Guest" + Math.floor(Math.random() * 1000000));
	document.cookie = 'username=' + username;
	$("#user").text(username);
})

$('#user').on("click", function(e){
	var tusername = prompt("Enter a username","Guest" + Math.floor(Math.random() * 1000000));
	if(tusername != "")
		username = tusername;
	else
		username = "Guest" + Math.floor(Math.random() * 1000000);
	document.cookie = 'username=' + username;
	$("#user").text(username);
});


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

        $.get("http://localhost:5000/api/search/youtube",{q:$('#searchBox').val()}, function (data){
        		emptySearchWindow();
        		for(var i = 0; i < 5; i++){
        			createYTSearchPreviewItem(data.items[i])
        		}
        	}, "json");
        $.get("http://localhost:5000/api/search/soundcloud",{q:$('#searchBox').val()}, function (data){
        		for(var i = 0; i < 5; i++){
        			createSCSearchPreviewItem(data.items[i])
        		}
        	}, "json");
    }
});

function emptySearchWindow(){
	$('#searchWindow').empty();
}

function createYTSearchPreviewItem(datum){
	var preview = "<div class='previewBox'><img src='" + datum.thumbnailUrl + "' /><h1>" + datum.title + "</h1><p>" + datum.channelTitle + "</p></div>";
	$('#searchWindow').append(preview)
}

function createSCSearchPreviewItem(datum){
	if(datum.thumbnail == null)
		datum.thumbnail = "soundcloud.png";
	if(datum.description == null || datum.description === "")
		datum.description = "Not Provided"
	var preview = "<div class='previewBox'><img src='" + datum.thumbnail + "'/><h1>" + datum.title + "</h1><p>" + datum.uploader + "</p></div>";
	$('#searchWindow').append(preview);
}

function loadStation(data){
	clearPlaylist();
	$.each(data.queue, function(item){
		addToPlayList(item);
	})
	stationView();
	setStationColor(data.color);
}

function setStationColor(color){
	$('#header').css('background-color', color);
	$('#footer').css('background-color', "0px 3px " + color)
}

function stationView(){
	$('#leftBar').show();
	$('#chatBar').show();
	$('#stations').hide();
	$('#content').show();
	$('#stationCreator').hide();
}

function browseView(){
	loadStationList();
	$('#leftBar').hide();
	$('#chatBar').hide();
	$('#stations').show();
	$('#content').hide();
	$('#stationCreator').hide();
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

	$.post("http://localhost:5000/api/create", {
		title: stationName,
		color: stationColor,
		owner: username,
		visible: $("#stationVisible").val()
	}, function(data) {
		loadStation(data)
	}, "json");
	console.log("Failed to create station");
})

$('#refreshStations').on("click", function(e){
	loadStationList();
})

$('#logo').on("click", function(e) {
	browseView();
})