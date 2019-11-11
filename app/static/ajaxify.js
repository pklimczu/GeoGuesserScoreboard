function send_ajax(url) {
    $.ajax({
        method: "POST",
        url: url,
        data: input_data,
        dataType: 'json',
        success: function() {
            alert("Data zaktualizowana poprawnie");
            setTimeout(window.location.reload(), 1000);
        },
        error: function() {
            alert("Aktualizacja się nie powiodła");
        }
    })    
}