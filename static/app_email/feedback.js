function postFeedback(username, sender, feedback, send_from, post_url, csrf){
    $.ajax({
        type: 'POST',
        url: post_url,
        data: {
            'name': username,
            'sender': sender,
            'feedback': feedback,
            'send_from': send_from,
            csrfmiddlewaretoken: csrf
        },
        success: function (data) {
            title = 'Thông tin';
            type = data['type'];
            message = data['message'];
            ShowAlert(title, message, type, 3000, '');
            let loading = document.getElementById("wavy");
            loading.style.display = "none";
        }
    })
}


function send_feedback_data() {
    let name = document.getElementById("name").value;
    let sender = document.getElementById("sender").value;
    let feedback = document.getElementById("feedback").value;
    let csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    let send_from = document.getElementById("send_from").value;
    let url_request = document.getElementById("url_request").value;
    postFeedback(name, sender, feedback, send_from, url_request, csrf)
}

document.getElementById("button_send").addEventListener("click", () => {
    let loading = document.getElementById("wavy");
    loading.style.display = "block";
    send_feedback_data();
})
