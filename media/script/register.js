
// script by Josh Fraser (http://www.onlineaspect.com)
function determineTimeZone() {
	var rightNow = new Date();
	var jan1 = new Date(rightNow.getFullYear(), 0, 1, 0, 0, 0, 0);  // jan 1st
	var june1 = new Date(rightNow.getFullYear(), 6, 1, 0, 0, 0, 0); // june 1st
	var temp = jan1.toGMTString();
	var jan2 = new Date(temp.substring(0, temp.lastIndexOf(" ")-1));
	temp = june1.toGMTString();
	var june2 = new Date(temp.substring(0, temp.lastIndexOf(" ")-1));
	var std_time_offset = (jan1 - jan2) / (1000 * 60 * 60);
	var daylight_time_offset = (june1 - june2) / (1000 * 60 * 60);
	var dst;
	if (std_time_offset == daylight_time_offset) {
		dst = "0"; // daylight savings time is NOT observed
	} else {
		// positive is southern, negative is northern hemisphere
		var hemisphere = std_time_offset - daylight_time_offset;
		if (hemisphere >= 0)
			std_time_offset = daylight_time_offset;
		dst = "1"; // daylight savings time is observed
	}
	console.log(convert(std_time_offset)+","+dst);
	/*
	var i;
	// check just to avoid error messages
	if (document.getElementById('timezone')) {
		for (i = 0; i < document.getElementById('timezone').options.length; i++) {
			if (document.getElementById('timezone').options[i].value == convert(std_time_offset)+","+dst) {
				document.getElementById('timezone').selectedIndex = i;
				break;
			}
		}
	}*/
}

function convert(value) {
	var hours = parseInt(value, 10);
   	value -= parseInt(value);
	value *= 60;
	var minutes = parseInt(value, 10);
   	value -= parseInt(value);
	value *= 60;
	var seconds = parseInt(value, 10);
	var display_hours = hours;
	// handle GMT case (00:00)
	if (hours == 0) {
		display_hours = "00";
	} else if (hours > 0) {
		// add a plus sign and perhaps an extra 0
		display_hours = (hours < 10) ? "+0" + hours : "+" + hours;
	} else {
		// add an extra 0 if needed 
		display_hours = (hours > -10) ? "-0" + Math.abs(hours) : hours;
	}
	
	minutes = (minutes < 10) ? "0" + minutes : minutes;
	return display_hours + ":" + minutes;
}

jQuery(function(){
    determineTimeZone();
    AnyTime.picker('birthdate', {format:"%d-%m-%Y"});
});

/*jQuery(function(){
    // Select all textboxes and assign them to an array
    var textboxes = jQuery('form.awesome input.input-text');
    
    // Iterate through all textboxes in the form
    textboxes.each(function(index, input){
        
        var label = jQuery(input).prev();
        
        label.wrapInner("<span></span>")
        label.children("span").animate({opacity: 0.6}, 0);
        
        // check for autocomplete by browser
        if( index == 0 ){
            setInterval(function(){
                textboxes.each(function(index,inputX){
                    if (inputX.value != "") {
                        jQuery(inputX).prev().children("span").animate({opacity: 0},0);
                    }
                });
            }, 100);
        }
    
        // Fade the label back when a field gains focus     
        input.onfocus = function(){
            if (input.value == ""){
                label.children("span").animate({opacity: 0.4}, 5);     
            }
        }
        
        // Check if a field is empty when the user switches out
        input.onblur = function(){
            if (input.value == ""){
                label.children("span").animate({opacity: 0.6}, 5);        
            }
        }
        
        // Fade the label back if a field has text      
        if (input.value != "") {
            label.addClass('hastext');
        }
        
        // Fade the label back when the user starts to type     
        input.onkeypress = function(){
            label.children("span").animate({opacity: 0}, 5);
        };
    });
});*/