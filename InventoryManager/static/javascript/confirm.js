function show_confirm(action) {
    if (confirm("Jesteś pewien?")){window.location.replace(action);}
}

function show_confirm_custom_text(action, text) {
    if (confirm(text)){window.location.replace(action)}
}