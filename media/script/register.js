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