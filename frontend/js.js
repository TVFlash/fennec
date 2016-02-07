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
