 
 
//  set a disappearing time for flash messages
 setTimeout(function() {
        const msg = document.getElementById('flash-message');
        if (msg) {
            msg.style.display = 'none';
        }
    }, 3000);  // disappears after 3000ms = 3 seconds