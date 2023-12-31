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
    var reference_summary = document.createElement("div");
    var reference = document.createElement("div");
    reference_summary.onclick = toggleCollapse
    reference_summary.id = 'reference_summary'
    reference.id = 'reference'
    reference.style.height = '0px'
    reference.style.overflow = 'hidden'

    if (message.length < 1) {
        response.innerHTML = "🤔<br>🤖<br>Message cannot be null\n问题不能为空";
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
        var request = {"query": message};
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
            response.innerHTML = "<br>🤔" + message + "<br>🤖" + resp['content'];
            reference_summary.innerHTML = '[出处]...'
            reference.innerHTML = resp['reference'];
            
            // 给response添加一个动画类
            response.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
            reference_summary.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
            reference.classList.add("animate__animated", "animate__lightSpeedInLeft", "dark");
            chatlog.appendChild(response);
            chatlog.appendChild(reference_summary)
            chatlog.appendChild(reference)
            response.scrollIntoView({ behavior: 'smooth', block: 'end'});
            reference_summary.scrollIntoView({ behavior: 'smooth', block: 'end'});
            reference.scrollIntoView({ behavior: 'smooth', block: 'end'});
        }
    }
});

function toggleCollapse() {
    var longText = document.getElementById("reference"); // 获取要折叠的元素
    console.log('收起')
    if (longText.style.height === "0px") { // 当前是折叠状态
        longText.style.height = "auto"; // 展开
    } else {
        longText.style.height = "0px"; // 折叠
    }
}