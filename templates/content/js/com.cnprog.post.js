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


// site comments

var comments = function() {

    var jDivInit = function(postId) {
        return $("#comments-" + postId);
    };

    var appendLoaderImg = function(postId) {
        appendLoader("#comments-" + postId + " div.comments");
    };

    var canPostComments = function(postId, jDiv) {
        var jHidden = jDiv.siblings("#can-post-comments-" + postId);
        return jHidden.val() == "true";
    };

    var renderForm = function(postId, jDiv) {
        var formId = "form-comments-" + postId;

        // Only add form once to dom..
        if (canPostComments(postId, jDiv)) {
            if (jDiv.find("#" + formId).length == 0) {
                var form = '<form id="' + formId + '" class="post-comments"><div>';
                form += '<textarea name="comment" cols="70" rows="2" maxlength="300" onblur="comments.updateTextCounter(this)" ';
                form += 'onfocus="comments.updateTextCounter(this)" onkeyup="comments.updateTextCounter(this)"></textarea>';
                form += '<input type="submit" value="添加评论" /><br/><span class="text-counter"></span>';
                form += '<span class="form-error"></span></div></form>';

                jDiv.append(form);

                setupFormValidation("#" + formId,
                    { comment: { required: true, minlength: 10} },
                    function() { postComment(postId, formId); });
            }
        }
        else { // Let users know how to post comments.. 
            var divId = "comments-rep-needed-" + postId;
            if (jDiv.find("#" + divId).length == 0) {
                jDiv.append('<div id="' + divId + '" style="color:red">commenting requires ' + repNeededForComments + ' reputation -- <a href="/faq" class="comment-user">see faq</a></span>');
            }
        }
    };

    var getComments = function(postId, jDiv) {
        appendLoaderImg(postId);
        $.getJSON("/questions/" + postId + "/comments/", function(json) { showComments(postId, json); });
    };

    var showComments = function(postId, json) {
        var jDiv = jDivInit(postId);

        jDiv = jDiv.find("div.comments");   // this div should contain any fetched comments..
        jDiv.find("div[id^='comment-']").remove();  // clean previous calls..

        removeLoader();

        if (json && json.length > 0) {
            for (var i = 0; i < json.length; i++)
                renderComment(jDiv, json[i]);

            jDiv.children().show();
        }
    };

    // {"Id":6,"PostId":38589,"CreationDate":"an hour ago","Text":"hello there!","UserDisplayName":"Jarrod Dixon","UserUrl":"/users/3/jarrod-dixon","DeleteUrl":null}
    var renderComment = function(jDiv, json) {
        var html = '<div id="comment-' + json.id + '" style="display:none">' + json.text;
        html += json.UserUrl ? '&nbsp;&ndash;&nbsp;<a href="' + json.user_url + '"' : '<span';
        html += ' class="comment-user">' + json.user_display_name + (json.user_url ? '</a>' : '</span>');
        html += ' <span class="comment-date">(' + json.add_date + ')</span>';

        if (json.DeleteUrl) {
            var img = "/content/images/close-small.png";
            var imgHover = "/content/images/close-small-hover.png";
            html += '<img onclick="comments.deleteComment($(this), ' + json.post_id + ', \'' + json.delete_url + '\')" src="' + img;
            html += '" onmouseover="$(this).attr(\'src\', \'' + imgHover + '\')" onmouseout="$(this).attr(\'src\', \'' + img
            html += '\')" title="删除此评论" />';
        }

        html += '</div>';

        jDiv.append(html);
    };

    var postComment = function(postId, formId) {
        appendLoaderImg(postId);

        var formSelector = "#" + formId;
        var textarea = $(formSelector + " textarea");

        $.ajax({
            type: "POST",
            url: "/questions/" + postId + "/comments/",
            dataType: "json",
            data: { comment: textarea.val(), "fkey": fkey },
            success: function(json) {
                showComments(postId, json);
                textarea.val("");
                comments.updateTextCounter(textarea);
                enableSubmitButton(formSelector);
            },
            error: function(res, textStatus, errorThrown) {
                removeLoader();
                showAjaxError(formSelector, res.responseText);
                enableSubmitButton(formSelector);
            }
        });
    };

    // public methods..
    return {

        init: function() {
            // Setup "show comments" clicks..
            $("a[id^='comments-link-']").unbind("click").click(function() { comments.show($(this).attr("id").substr("comments-link-".length)); });
        },

        show: function(postId) {
            var jDiv = jDivInit(postId);
            getComments(postId, jDiv);
            renderForm(postId, jDiv);
            jDiv.show();
            if (canPostComments(postId, jDiv)) jDiv.find("textarea").get(0).focus();
            jDiv.siblings("a").unbind("click").click(function() { comments.hide(postId); }).text("隐藏评论");
        },

        hide: function(postId) {
            var jDiv = jDivInit(postId);
            var len = jDiv.children("div.comments").children().length;
            var anchorText = len == 0 ? "添加评论" : "评论 (<b>" + len + "</b>)";

            jDiv.hide();
            jDiv.siblings("a").unbind("click").click(function() { comments.show(postId); }).html(anchorText);
            jDiv.children("div.comments").children().hide();
        },

        deleteComment: function(jImg, postId, deleteUrl) {
            if (confirm("真要删除此评论吗？")) {
                jImg.hide();
                appendLoaderImg(postId);
                $.post(deleteUrl, { dataNeeded: "forIIS7" }, function(json) {
                    showComments(postId, json);
                }, "json");
            }
        },

        updateTextCounter: function(textarea) {
            var length = textarea.value ? textarea.value.length : 0;
            var color = length > 270 ? "#f00" : length > 200 ? "#f60" : "#999";
            var jSpan = $(textarea).siblings("span.text-counter");
            jSpan.html((300 - length) + ' character' + (length == 299 ? '' : 's') + ' left').css("color", color);
        }
    };

} ();

$().ready(function() {
    comments.init();
});


