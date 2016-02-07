$('#searchBox').on("keypress", function (e) {            

    if (e.keyCode == 13) { //newline

        // Cancel the default action on keypress event
        e.preventDefault(); 

        alert($('#searchBox').val())
    }
});