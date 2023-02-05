
function like_post(post_id, like_btn_text, csrf) {
        $.ajax({
        type: 'POST',
        url: '/like/',
        data: {
            'post_id': post_id,
            csrfmiddlewaretoken: csrf
        },
        success: function (data) {
            let temp = like_btn_text.split('_');
            temp[1] = 'count'
            let like_count_text = temp.join('_');
            let like_count = data['like_count'];
            let like_count_node = document.getElementById(like_count_text);
            if (like_count === 0) {
                like_count_node.innerHTML = "Hãy là người đầu tiên thích bài viết này!";
            }
            else {
                like_count_node.innerHTML = `Có ${like_count} người thích bài viết này.`;
            }

            // Thay đổi màu nút like
            temp[1] = 'icon'
            let like_icon_text = temp.join('_');
            let like_icon = document.getElementById(like_icon_text);
            like_icon.classList.toggle("text-blue-500");
        }
    })
}

function sendata(like_btn_text) {
    let temp = like_btn_text.split('_')
    let like_btn = document.getElementById(like_btn_text);
    let csrf = like_btn.childNodes[1].value;
    like_post(temp[2], like_btn_text, csrf)
}
