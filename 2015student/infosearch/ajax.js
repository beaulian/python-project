$(document).ready(function(){
    $("#submit").click(function(){
        var yuan = $("#selectyuan option:selected").text();
        var dong = $("#selectdong option:selected").text();
        var room = $("#room").val();
        $.ajax({
            url: "http://127.0.0.1:5000/roommates",
            type: 'post',
            data: {
                yuan: yuan,
                dong: dong,
                room: room
            },
            dataType: 'json',
            success: function(data){
                var info = data["info"];
                for (i=0; i<info.length; i++)
                    $("#roommates").append(
                    "<p style='float:left;'>室友[" + (i+1) + "]: &nbsp;" + "姓名: " + info[i].name + "&nbsp;&nbsp;&nbsp;" + "床位号: " +info[i].bedID + "</p>" + "<br>");
            }
        })
    });

    $("#submit2").click(function(){

        var classID = $("#classID").val();
        $.ajax({
            url: "http://127.0.0.1:5000/api/stuinfo/scale",
            type: 'post',
            data: {
                classID: classID
            },
            dataType: 'json',
            success: function(data){
                $("#scale").empty();
                $("#scale").append("<p style='float:left;'>" + data.classroom + "</p>" +
                                    "<br>" +
                                    "<p style='float:left;'>班级总人数: " + data.sum + "&nbsp;&nbsp;男生人数: " +
                                     data.boys + "&nbsp;&nbsp;女生人数: " + data.girls + "</p>")
            }
        })
    });
});
