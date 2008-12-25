var Vote = function(){
    // All actions are related to a question
    var questionId;
    // The object we operate on actually. It can be a question or an answer.
    var postId;
    var questionAuthorId;
    var currentUserId;
    var answerContainerIdPrefix = 'answer-container-';
    var voteContainerId = 'vote-buttons';
    var imgIdPrefixAccept = 'answer-img-accept-';
    var commentLinkIdPrefix = 'comment-';
    
    var VoteType = {
        acceptAnswer : 0,
        upVote : 1,
        downVote : 2,
        offensive : 3,
        favorite : 4
    };

    var showMessage = function(object, msg) {
        var div = $('<div class="vote-notification"><h3>' + msg + '</h3>(点击消息框关闭)</div>');

        div.click(function(event) {
            $(".vote-notification").fadeOut("fast", function() { $(this).remove(); });
        });

        object.parent().append(div);
        div.fadeIn("fast");
    };
    
    var bindEvents = function(){
        // find all accept button whose id begin with "answer-img-accept-"
        if(questionAuthorId == currentUserId){
            var acceptedButtons = 'div.'+ voteContainerId +' img[id^='+ imgIdPrefixAccept +']';
            $(acceptedButtons).unbind('click').click(function(event){
               Vote.accept($(event.target))
            });
        }
    };
    
    var submit = function(object, voteType, callback) {
        $.ajax({
            type: "POST",
            cache: false,
            dataType: "json",
            url: "/questions/" + questionId + "/vote/",
            data: { "type": voteType, "postId": postId },
            error: handleFail,
            success: function(data){callback(object, data)}});
    };
    
    var handleFail = function(xhr, msg){
        alert("Callback invoke error: " + msg)
    };

    // callback function for Accept Answer action
    var callback_accept = function(object, data){
        if(data.allowed == "0" && data.success == "0"){
            showMessage(object, "用户权限不在操作范围");
        }
        else if(data.allowed == "-1"){
            showMessage(object, "不能设置自己的回答为最佳答案");
        }
        else if(data.status == "1"){
            object.attr("src", "/content/images/vote-accepted.png");
            $("#"+answerContainerIdPrefix+postId).removeClass("accepted-answer");
        }
        else if(data.success == "1"){
            var acceptedButtons = 'div.'+ voteContainerId +' img[id^='+ imgIdPrefixAccept +']';
            $(acceptedButtons).attr("src", "/content/images/vote-accepted.png");
            var answers = ("div[id^="+answerContainerIdPrefix +"]");
            $(answers).removeClass("accepted-answer");
            var commentLinks = ("div[id^="+answerContainerIdPrefix +"] div[id^="+ commentLinkIdPrefix +"]");
            $(commentLinks).removeClass("comment-link-accepted");
            
            object.attr("src", "/content/images/vote-accepted-on.png");
            $("#"+answerContainerIdPrefix+postId).addClass("accepted-answer");
            $("#"+commentLinkIdPrefix+postId).addClass("comment-link-accepted");
        }
        else{
            showMessage(object, data.message);
        }
    };

    return {
        init : function(qId, questionAuthor, userId){
            questionId = qId;
            questionAuthorId = questionAuthor;
            currentUserId = userId;
            bindEvents();
        },
        
        // Accept answer public function
        accept: function(object){
            postId = object.attr("id").substring(imgIdPrefixAccept.length);
            submit(object, VoteType.acceptAnswer, callback_accept);
        }
    }
} ();
