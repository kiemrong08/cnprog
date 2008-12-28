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
    var imgClassPrefixFavorite = 'question-img-favorite';
    var imgIdPrefixQuestionVoteup = 'question-img-upvote-';
    var imgIdPrefixQuestionVotedown = 'question-img-downvote-';
    var imgIdPrefixAnswerVoteup = 'answer-img-upvote-';
    var imgIdPrefixAnswerVotedown = 'answer-img-downvote-';
    var divIdFavorite = 'favorite-number';
    var commentLinkIdPrefix = 'comment-';
    var voteNumberClass = "vote-number";
    
    var acceptAnonymousMessage = "用户权限不在操作范围";
    var acceptOwnAnswerMessage = "不能设置自己的回答为最佳答案";
    var favoriteAnonymousMessage = "匿名用户不能收藏问题，请先<a href='/account/signin/?next=/questions/{{QuestionID}}'>注册或者登录</a>";
    var voteAnonymousMessage = "匿名用户不能投票，请先<a href='/account/signin/?next=/questions/{{QuestionID}}'>注册或者登录</a>";
    var upVoteRequiredScoreMessage = "需要+15积分才能投支持票";
    var downVoteRequiredScoreMessage = "需要+100积分才能投反对票";
    var voteOwnDeniedMessage = "不能给自己的帖子投票";
    var voteRequiredMoreVotes = "对不起，您已用完今日所有的投票。查看<a href='/faq'>faq</a>。";
    var voteDenyCancelMessage = "这个投票已经过时，不能撤销您的投票。查看<a href='/faq'>faq</a>。";
    
    var VoteType = {
        acceptAnswer : 0,
        questionUpVote : 1,
        questionDownVote : 2,
        offensive : 3,
        favorite : 4,
        answerUpVote: 5,
        answerDownVote:6
    };

    var getQuestionId = function(){
        return questionId;
    }
    var getFavoriteButton = function(){
        var favoriteButton = 'div.'+ voteContainerId +' img[class='+ imgClassPrefixFavorite +']';
        return $(favoriteButton);
    };
    var getFavoriteNumber = function(){
        var favoriteNumber = '#'+ divIdFavorite ;
        return $(favoriteNumber);
    };
    var getQuestionVoteUpButton = function(){
        var questionVoteUpButton = 'div.'+ voteContainerId +' img[id^='+ imgIdPrefixQuestionVoteup +']';
        return $(questionVoteUpButton);
    };
    var getQuestionVoteDownButton = function(){
        var questionVoteDownButton = 'div.'+ voteContainerId +' img[id^='+ imgIdPrefixQuestionVotedown +']';
        return $(questionVoteDownButton);
    };
    var getAnswerVoteUpButtons = function(){
        var answerVoteUpButton = 'div.'+ voteContainerId +' img[id^='+ imgIdPrefixAnswerVoteup +']';
        return $(answerVoteUpButton);
    };
    var getAnswerVoteDownButtons = function(){
        var answerVoteDownButton = 'div.'+ voteContainerId +' img[id^='+ imgIdPrefixAnswerVotedown +']';
        return $(answerVoteDownButton);
    };
    var getAnswerVoteUpButton = function(id){
        var answerVoteUpButton = 'div.'+ voteContainerId +' img[id='+ imgIdPrefixAnswerVoteup + id + ']';
        return $(answerVoteUpButton);
    };
    var getAnswerVoteDownButton = function(id){
        var answerVoteDownButton = 'div.'+ voteContainerId +' img[id='+ imgIdPrefixAnswerVotedown + id + ']';
        return $(answerVoteDownButton);
    };
   
    var setVoteImage = function(voteType, undo, object){
        var flag = undo ? "" : "-on";
        var arrow = (voteType == VoteType.questionUpVote || voteType == VoteType.answerUpVote) ? "up" : "down";
        object.attr("src", "/content/images/vote-arrow-"+ arrow + flag +".png");
        
        // if undo voting, then undo the pair of arrows.
        if(undo){
            if(voteType == VoteType.questionUpVote || voteType == VoteType.questionDownVote){
                $(getQuestionVoteUpButton()).attr("src", "/content/images/vote-arrow-up.png");
                $(getQuestionVoteDownButton()).attr("src", "/content/images/vote-arrow-down.png");
            }
            else{
                $(getAnswerVoteUpButton(postId)).attr("src", "/content/images/vote-arrow-up.png");
                $(getAnswerVoteDownButton(postId)).attr("src", "/content/images/vote-arrow-down.png");
            }
        }
    };
    
    var setVoteNumber = function(object, number){
        var voteNumber = object.parent('div.'+ voteContainerId).find('div.'+ voteNumberClass);
        $(voteNumber).text(number);
    };
    
    var bindEvents = function(){
        // accept answers
        if(questionAuthorId == currentUserId){
            var acceptedButtons = 'div.'+ voteContainerId +' img[id^='+ imgIdPrefixAccept +']';
            $(acceptedButtons).unbind('click').click(function(event){
               Vote.accept($(event.target))
            });
        }
        // set favorite question
        var favoriteButton = getFavoriteButton();
        favoriteButton.unbind('click').click(function(event){
           Vote.favorite($(event.target))
        });
    
        // question vote up
        var questionVoteUpButton = getQuestionVoteUpButton();
        questionVoteUpButton.unbind('click').click(function(event){
           Vote.vote($(event.target), VoteType.questionUpVote)
        });
    
        var questionVoteDownButton = getQuestionVoteDownButton();
        questionVoteDownButton.unbind('click').click(function(event){
           Vote.vote($(event.target), VoteType.questionDownVote)
        });
    
        var answerVoteUpButton = getAnswerVoteUpButtons();
        answerVoteUpButton.unbind('click').click(function(event){
           Vote.vote($(event.target), VoteType.answerUpVote)
        });
        
        var answerVoteDownButton = getAnswerVoteDownButtons();
        answerVoteDownButton.unbind('click').click(function(event){
           Vote.vote($(event.target), VoteType.answerDownVote)
        });
    };
    
    var submit = function(object, voteType, callback) {
        $.ajax({
            type: "POST",
            cache: false,
            dataType: "json",
            url: "/questions/" + questionId + "/vote/",
            data: { "type": voteType, "postId": postId },
            error: handleFail,
            success: function(data){callback(object, voteType, data)}});
    };
    
    var handleFail = function(xhr, msg){
        alert("Callback invoke error: " + msg)
    };

    // callback function for Accept Answer action
    var callback_accept = function(object, voteType, data){
        if(data.allowed == "0" && data.success == "0"){
            showMessage(object, acceptAnonymousMessage);
        }
        else if(data.allowed == "-1"){
            showMessage(object, acceptOwnAnswerMessage);
        }
        else if(data.status == "1"){
            object.attr("src", "/content/images/vote-accepted.png");
            $("#"+answerContainerIdPrefix+postId).removeClass("accepted-answer");
            $("#"+commentLinkIdPrefix+postId).removeClass("comment-link-accepted");
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

    var callback_favorite = function(object, voteType, data){
        if(data.allowed == "0" && data.success == "0"){
            showMessage(object, favoriteAnonymousMessage.replace("{{QuestionID}}", questionId));
        }
        else if(data.status == "1"){
            object.attr("src", "/content/images/vote-favorite-off.png");
            var fav = getFavoriteNumber();
            fav.removeClass("my-favorite-number");
            if(data.count == 0)
                data.count = '';
            fav.text(data.count);
        }
        else if(data.success == "1"){
            object.attr("src", "/content/images/vote-favorite-on.png");
            var fav = getFavoriteNumber();
            fav.text(data.count);
            fav.addClass("my-favorite-number");
        }
        else{
            showMessage(object, data.message);
        }
    };
        
    var callback_vote = function(object, voteType, data){
        if(data.allowed == "0" && data.success == "0"){
            showMessage(object, voteAnonymousMessage.replace("{{QuestionID}}", questionId));
        }
        else if(data.allowed == "-3"){
            showMessage(object, voteRequiredMoreVotes);
        }
        else if(data.allowed == "-2"){
            if(voteType == VoteType.questionUpVote || voteType == VoteType.answerUpVote){
                showMessage(object, upVoteRequiredScoreMessage);
            }
            else if(voteType == VoteType.questionDownVote || voteType == VoteType.answerDownVote){
                showMessage(object, downVoteRequiredScoreMessage);
            }
        }
        else if(data.allowed == "-1"){
            showMessage(object, voteOwnDeniedMessage);
        }
        else if(data.status == "2"){
            showMessage(object, voteDenyCancelMessage);
        }
        else if(data.status == "1"){
            setVoteImage(voteType, true, object);
            setVoteNumber(object, data.count);
        }     
        else if(data.success == "1"){
            setVoteImage(voteType, false, object);
            setVoteNumber(object, data.count);
            if(data.message.length > 0)
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
        },
        
        favorite: function(object){
            if(!currentUserId || currentUserId.toUpperCase() == "NONE"){
                showMessage(object, favoriteAnonymousMessage.replace("{{QuestionID}}", questionId));
                return false;
            }
            submit(object, VoteType.favorite, callback_favorite);
        },
            
        vote: function(object, voteType){
            if(!currentUserId || currentUserId.toUpperCase() == "NONE"){
                showMessage(object, voteAnonymousMessage.replace("{{QuestionID}}", questionId));
                return false;   
            }
            if(voteType == VoteType.answerUpVote){
                postId = object.attr("id").substring(imgIdPrefixAnswerVoteup.length);
            }
            else if(voteType == VoteType.answerDownVote){
                postId = object.attr("id").substring(imgIdPrefixAnswerVotedown.length);
            }
            
            submit(object, voteType, callback_vote);
        }
    }
} ();


// site comments
function createComments(type) {
    var objectType = type;
    var jDivInit = function(id) {
        return $("#comments-" + objectType + '-' + id);
    };

    var appendLoaderImg = function(id) {
        appendLoader("#comments-" + objectType + '-' + id + " div.comments");
    };

    var canPostComments = function(id, jDiv) {
        var jHidden = jDiv.siblings("#can-post-comments-" + objectType + '-' + id);
        return jHidden.val() == "true";
    };

    var renderForm = function(id, jDiv) {
        var formId = "form-comments-" + objectType + "-" + id;

        // Only add form once to dom..
        if (canPostComments(id, jDiv)) {
            if (jDiv.find("#" + formId).length == 0) {
                var form = '<form id="' + formId + '" class="post-comments"><div>';
                form += '<textarea name="comment" cols="60" rows="5" maxlength="300" onblur="'+ objectType +'Comments.updateTextCounter(this)" ';
                form += 'onfocus="' + objectType + 'Comments.updateTextCounter(this)" onkeyup="'+ objectType +'Comments.updateTextCounter(this)"></textarea>';
                form += '<input type="submit" value="添加评论" /><br><span class="text-counter"></span>';
                form += '<span class="form-error"></span></div></form>';

                jDiv.append(form);

                setupFormValidation("#" + formId,
                    { comment: { required: true, minlength: 10} },
                    function() { postComment(id, formId); });
            }
        }
        else { // Let users know how to post comments.. 
            var divId = "comments-rep-needed-" + objectType + '-' + id;
            if (jDiv.find("#" + divId).length == 0) {
                jDiv.append('<div id="' + divId + '" style="color:red">commenting requires ' + repNeededForComments + ' reputation -- <a href="/faq" class="comment-user">see faq</a></span>');
            }
        }
    };

    var getComments = function(id, jDiv) {
        appendLoaderImg(id);
        $.getJSON("/" + objectType + "s/" + id + "/comments/", function(json) { showComments(id, json); });
    };

    var showComments = function(id, json) {
        var jDiv = jDivInit(id);

        jDiv = jDiv.find("div.comments");   // this div should contain any fetched comments..
        jDiv.find("div[id^='comment-" + objectType + "-'" + "]").remove();  // clean previous calls..

        removeLoader();

        if (json && json.length > 0) {
            for (var i = 0; i < json.length; i++)
                renderComment(jDiv, json[i]);

            jDiv.children().show();
        }
    };

    // {"Id":6,"PostId":38589,"CreationDate":"an hour ago","Text":"hello there!","UserDisplayName":"Jarrod Dixon","UserUrl":"/users/3/jarrod-dixon","DeleteUrl":null}
    var renderComment = function(jDiv, json) {
        var html = '<div id="comment-' + objectType + "-" + json.id + '" style="display:none">' + json.text;
        html += json.user_url ? '&nbsp;&ndash;&nbsp;<a href="' + json.user_url + '"' : '<span';
        html += ' class="comment-user">' + json.user_display_name + (json.user_url ? '</a>' : '</span>');
        html += ' <span class="comment-date">(' + json.add_date + ')</span>';

        if (json.delete_url) {
            var img = "/content/images/close-small.png";
            var imgHover = "/content/images/close-small-hover.png";
            html += '<img onclick="' + objectType + 'Comments.deleteComment($(this), ' + json.object_id + ', \'' + json.delete_url + '\')" src="' + img;
            html += '" onmouseover="$(this).attr(\'src\', \'' + imgHover + '\')" onmouseout="$(this).attr(\'src\', \'' + img
            html += '\')" title="删除此评论" />';
        }

        html += '</div>';

        jDiv.append(html);
    };

    var postComment = function(id, formId) {
        appendLoaderImg(id);

        var formSelector = "#" + formId;
        var textarea = $(formSelector + " textarea");

        $.ajax({
            type: "POST",
            url: "/" + objectType + "s/" + id + "/comments/",
            dataType: "json",
            data: { comment: textarea.val() },
            success: function(json) {
                showComments(id, json);
                textarea.val("");
                commentsFactory[objectType].updateTextCounter(textarea);
                enableSubmitButton(formSelector);
            },
            error: function(res, textStatus, errorThrown) {
                removeLoader();
                showMessage(formSelector, res.responseText);
                enableSubmitButton(formSelector);
            }
        });
    };

    // public methods..
    return {

        init: function() {
            // Setup "show comments" clicks..
            $("a[id^='comments-link-" + objectType + "-" + "']").unbind("click").click(function() { commentsFactory[objectType].show($(this).attr("id").substr(("comments-link-" + objectType + "-").length)); });
        },

        show: function(id) {
            var jDiv = jDivInit(id);
            getComments(id, jDiv);
            renderForm(id, jDiv);
            jDiv.show();
            if (canPostComments(id, jDiv)) jDiv.find("textarea").get(0).focus();
            jDiv.siblings("a").unbind("click").click(function() { commentsFactory[objectType].hide(id); }).text("隐藏评论");
        },

        hide: function(id) {
            var jDiv = jDivInit(id);
            var len = jDiv.children("div.comments").children().length;
            var anchorText = len == 0 ? "添加评论" : "评论 (<b>" + len + "</b>)";

            jDiv.hide();
            jDiv.siblings("a").unbind("click").click(function() { commentsFactory[objectType].show(id); }).html(anchorText);
            jDiv.children("div.comments").children().hide();
        },

        deleteComment: function(jImg, id, deleteUrl) {
            if (confirm("真要删除此评论吗？")) {
                jImg.hide();
                appendLoaderImg(id);
                $.post(deleteUrl, { dataNeeded: "forIIS7" }, function(json) {
                    showComments(id, json);
                }, "json");
            }
        },

        updateTextCounter: function(textarea) {
            var length = textarea.value ? textarea.value.length : 0;
            var color = length > 270 ? "#f00" : length > 200 ? "#f60" : "#999";
            var jSpan = $(textarea).siblings("span.text-counter");
            jSpan.html('还可写' + (300 - length) + ' 字符').css("color", color);
        }
    };
}

var questionComments = createComments('question');
var answerComments = createComments('answer');

$().ready(function() {
    questionComments.init();
    answerComments.init();
});

var commentsFactory = {'question' : questionComments, 'answer' : answerComments};
