var showMessage = function(object, msg) {
    var div = $('<div class="vote-notification"><h3>' + msg + '</h3>(点击消息框关闭)</div>');

    div.click(function(event) {
        $(".vote-notification").fadeOut("fast", function() { $(this).remove(); });
    });

    object.parent().append(div);
    div.fadeIn("fast");
};

var notify = function() {
    var visible = false;
    var cookie_name = 'message_silent';
    var setCookie= function (value) {
		var date = new Date();
		date.setTime(date.getTime()+(24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
		document.cookie = cookie_name+"="+value+expires+"; path=/";
    };
        
    var readCookie= function () {
		var nameEQ = cookie_name + "=";
		var ca = document.cookie.split(';');
		for(var i=0;i < ca.length;i++) {
			var c = ca[i];
			while (c.charAt(0)==' ') c = c.substring(1,c.length);
			if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
		}
		return null;
    };
    
    return {
        show: function(html) {
            var k = readCookie();
            if(k != 11){
                if (html) {
                    $("body").css("margin-top", "2.2em");
                    $(".notify span").html(html);        
                }          
                $(".notify").fadeIn("slow");
                visible = true;
            }
            else
                $("body").css("margin-top", "0");
        },       
        close: function(doPostback) {
            if (doPostback) {
               $.post("/messages/markread/", { formdata: "required" });
            }
            $(".notify").fadeOut("fast");
            $("body").css("margin-top", "0");
            visible = false;
            setCookie(1);
        },     
        isVisible: function() { return visible; }     
    };
} ();

function appendLoader(containerSelector) {
    $(containerSelector).append('<img class="ajax-loader" src="/content/images/indicator.gif" title="读取中..." alt="读取中..." />');
}

function removeLoader() {
    $("img.ajax-loader").remove();
}

function setupFormValidation(formSelector, validationRules, validationMessages, onSubmitCallback) {
    enableSubmitButton(formSelector);
    $(formSelector).validate({
        rules: (validationRules ? validationRules : {}),
        messages: (validationMessages ? validationMessages : {}),
        errorElement: "span",
        errorClass: "form-error",
        errorPlacement: function(error, element) {
            var span = element.next().find("span.form-error");
            if (span.length == 0) {
                span = element.parent().find("span.form-error");
            }
            span.replaceWith(error);
        },
        submitHandler: function(form) {
            disableSubmitButton(formSelector);
            
            if (onSubmitCallback)
                onSubmitCallback();
            else
                form.submit();
        }
    });
}

function enableSubmitButton(formSelector) {
    setSubmitButtonDisabled(formSelector, false);
}
function disableSubmitButton(formSelector) {
    setSubmitButtonDisabled(formSelector, true);
}
function setSubmitButtonDisabled(formSelector, isDisabled) { 
    $(formSelector).find("input[type='submit']").attr("disabled", isDisabled ? "true" : "");    
}

var CPValidator = function(){
    return {
        getQuestionFormRules : function(){
            return {
                tags: {
                    required: true,
                    maxlength: 105
                },  
                text: {
                    required: true,
                    minlength: 10
                },
                title: {
                    required: true,
                    minlength: 10
                }
            };
        },
        getQuestionFormMessages: function(){
            return {
                tags: {
                    required: " 标签不能为空。",
                    maxlength: " 最多5个标签，每个标签长度小于20个字符。"
                },
                text: {
                    required: " 内容不能为空。",
                    minlength: jQuery.format(" 请输入至少 {0} 字符。")
                },
                title: {
                    required: " 请输入标题。",
                    minlength: jQuery.format(" 请输入至少 {0} 字符。")
                }
            };
        }
    };
}();
