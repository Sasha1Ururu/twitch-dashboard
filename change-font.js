function makeSectionTransparent() {
    console.log("%cInjected script makeSectionTransparent running...", "font-size: 24px");

    document.head.insertAdjacentHTML('afterbegin', `
        <style id="my_text_color">
            *:not([style*="color"]) {
              color: yellow !important;
            }
        </style>
    `);

    window._replace_chat_color = function(color) {
        window.my_text_color.innerHTML = `
            *:not([style*="color"]) {
              color: ${color} !important;
            }
        `;
    };

    window._random_hex_color = function() {
        return '#' + Math.floor(Math.random()*16777215).toString(16);
    };

    setInterval(x => window._replace_chat_color(window._random_hex_color()), 500);

//    setTimeout(function() {
//        window._replace_chat_color('#ab034d');
//    }, 10000);

    console.log('Class "transparent-section" added, <section> is now transparent.');
}

// Run the function
makeSectionTransparent();
