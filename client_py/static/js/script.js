// 加入回车提交支持，shift+回车换行
var input = document.getElementById("chatinput");
input.addEventListener("keydown", function (event) {
    if (event.keyCode === 13 && !event.shiftKey) {
        event.preventDefault();
        document.getElementById("sendbutton").click();
    }
});

// Add your JavaScript here
document.getElementById("sendbutton").addEventListener("click", function () {
    // Get the user's message from the input field
    var message = document.getElementById("chatinput").value;
    var chatlog = document.getElementById("chatlog");
    var query = document.createElement("div");
    var response = document.createElement("div");
    var reference_summary = document.createElement("div");
    var reference = document.createElement("div");
    query.classList.add('query')
    response.classList.add('response')
    reference_summary.onclick = function () {
        toggleCollapse(reference);
    }
    reference_summary.id = 'reference_summary'
    reference.id = 'reference'
    reference.style.height = '0px'
    reference.style.overflow = 'hidden'

    if (message.length < 1) {
        query.innerHTML = "🤔<br>"
        response.innerHTML = "🤖<br>Message cannot be null\n问题不能为空";
        // 给response添加一个动画类
        response.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
        chatlog.appendChild(response);
        response.scrollIntoView({ behavior: 'smooth', block: 'end' });
    } else {
        // Clear the input field
        document.getElementById("chatinput").value = "";

        // 直接向llm请求
        // var xhr = new XMLHttpRequest();
        // xhr.open("POST", "http://127.0.0.1:8000/chat");
        // xhr.setRequestHeader("Content-Type", "application/json");
        // var request = {
        //     "messages": [
        //         {
        //             "content": message,
        //             "role": "user"
        //         }
        //     ],
        //     "model": "default",
        //     "stream": false
        // }

        // 向量检索+llm
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "http://127.0.0.1:8100/search");
        xhr.setRequestHeader("Content-Type", "application/json");
        var request = { "query": message };
        xhr.send(JSON.stringify(request));

        // Display "typing" message while the bot is thinking
        var typingMessage = document.createElement("div");
        // 新增一个小圆点元素，添加typing类
        var dot = document.createElement("div");
        dot.classList.add("typing");
        typingMessage.appendChild(dot);
        chatlog.appendChild(typingMessage);
        typingMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });
        xhr.onload = function () {
            // Append the chatbot's response to the chatlog
            chatlog.removeChild(typingMessage);
            var resp = JSON.parse(xhr.responseText)
            // console.log(resp);
            query.innerHTML = "<br><span>" + message + "</span>🤔<br><br>"
            response.innerHTML = "🤖<span>" + resp['content'] + "</span><br><br>";
            reference_summary.innerHTML = '[出处]...'
            reference.innerHTML = resp['reference'];

            // 给response添加一个动画类
            query.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
            chatlog.appendChild(query);
            query.scrollIntoView({ behavior: 'smooth', block: 'end' });

            response.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
            chatlog.appendChild(response);
            response.scrollIntoView({ behavior: 'smooth', block: 'end' });

            reference_summary.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
            chatlog.appendChild(reference_summary)
            reference_summary.scrollIntoView({ behavior: 'smooth', block: 'end' });

            reference.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
            chatlog.appendChild(reference)
            reference.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }
});

function toggleCollapse(longText) {
    // var longText = document.getElementById("reference"); // 获取要折叠的元素
    if (longText.style.height === "0px") { // 当前是折叠状态
        longText.style.height = "auto"; // 展开
    } else {
        longText.style.height = "0px"; // 折叠
    }
};

document.getElementById("clear_history").addEventListener("click", function () {
    chatlog = document.getElementById("chatlog");
    chatlog.innerHTML = ""
});