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
    var response = document.createElement("div");
    if (message.length < 1) {
        response.innerHTML = "🤔<br>🤖<br>Message cannot be null\n问题不能为空";
        // 给response添加一个动画类
        response.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
        chatlog.appendChild(response);
        response.scrollIntoView({ behavior: 'smooth', block: 'end' });
    } else {
        // Clear the input field
        document.getElementById("chatinput").value = "";
        
        // Send the message to the chatbot
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

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "http://127.0.0.1:8100/search");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.setRequestHeader("Access-Control-Allow-Origin", "");
        var request = {"query": message};
        console.log(JSON.stringify(request));
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
            console.log(xhr.responseText)
            var resp = JSON.parse(xhr.responseText)['choices'][0]['message']['content']
            // console.log(resp);
            response.innerHTML = "<br>🤔" + message + "<br>🤖" + resp;
            // 给response添加一个动画类
            response.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
            chatlog.appendChild(response);
            response.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }
});
