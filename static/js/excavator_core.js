$(document).ready(function(){

    $("#menu li a").click(function(){
        // 000 - AI
        var code = $(this).attr("id");
        var msg = $("#message").val();

        if(code == "clear"){
            $("#result").html("");
        } else {
            ajaxRequest(code, msg) //ajax
        }
    }); // menu listener



    function parseResult(json) {
        // alert(JSON.stringify(json));
        var code = json.code;
        var html = "";
        if(code == "000"){
            html = "<div><ul>";
            $.each(json.resp, function(n, item){
                html += '<li><a href="#">' + item.title+ '</a></li>';
            });
            html += "</ul></div>";

        } else if(code == "001" || code == "999" || code == "901" || code == "902" || code == "904"){
            html = "<p>" + json.resp + "</p>";
        } else if(code == "401") {
            $("#result").html("");
            html = "<p>" + json.resp + "</p>";
        } else if(code == "903") {
            html = "<div><ul>";
            $.each(json.resp, function(n, item){
                html += "<li>" + item.word+ " | " + item.flag + "</li>";
            });
            html += "</ul></div>";
        } else if(code == "905") {
//            alert(JSON.stringify(json.resp));
//            $.each(json.resp, function(n, item){
//                alert(JSON.stringify(item))
//            });
            html = "<div><ul>"
            html += "<li>主: "+json.resp.SUB+"</li>"
            html += "<li>谓: "+json.resp.PRE+"</li>"
            html += "<li>宾: "+json.resp.OBJ+"</li>"
            html += "<li>状: "+json.resp.ADV+"</li>"
            html += "</ul></div>"
        }

        html += "<hr/>"
        $(html).prependTo("#result");

    } //parseResult()


    function ajaxRequest(code, msg) {

        var message = {
            "code": code,
            "msg": msg
        };
        data = JSON.stringify(message);
        $.ajax({
            url: "/enquire",
            type: "POST",
            data: data,
            dataType: "json",
            beforeSend: function(){},
            success: function(data){
                parseResult(data);
            },
            error: function(){
                $("#result").html("Error happened : /")
            }
        });
    } //ajaxRequest()

    function setup400CLick() {
        $("#400").click(function(){
            var code = $(this).attr("id");
            var msg = $("#message").val();
            // send2server(code, msg); //WebSocket
            ajaxRequest(code, msg); //ajax
        });
    }

});// document