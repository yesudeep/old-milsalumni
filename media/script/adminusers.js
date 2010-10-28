jQuery(function(){
    var accordion = jQuery('ul.accordion');

    // Accordion behavior (click).
    jQuery('> li > h1', accordion).live('click', function(e){
        var item = jQuery(this).parent('li');
        item.siblings('.active').removeClass('active');
        item.toggleClass('active');
    });
    
});
