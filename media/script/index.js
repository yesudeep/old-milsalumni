/**
 * Index page script.
 * Copyright (C) 2010 happychickoo.
 *
 * MIT License.
 */
jQuery(function(){
    jQuery("li#presentation-sidebar .tabs").tabs("ul.panes > li", {
        event: 'mouseover',
        effect: 'fade',
		fadeOutSpeed: 50,
		rotate: true
    });
});
