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
    return {
        show: function(html) {
            if (html) {
                $("body").css("margin-top", "2.2em");
                $(".notify span").html(html);        
            }          
            $(".notify").fadeIn("slow");
            visible = true;
        },       
        close: function(doPostback) {
            if (doPostback) {
               $.post("/messages/markread/", { formdata: "required" });
            }
            $(".notify").fadeOut("fast");
            $("body").css("margin-top", "0");
            visible = false;
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
//Search Engine Keyword Highlight with Javascript
//http://scott.yang.id.au/code/se-hilite/
                Hilite={elementid:"content",exact:true,max_nodes:1000,onload:true,style_name:"hilite",style_name_suffix:true,debug_referrer:""};Hilite.search_engines=[["local","q"],["cnprog\\.","q"],["google\\.","q"],["search\\.yahoo\\.","p"],["search\\.msn\\.","q"],["search\\.live\\.","query"],["search\\.aol\\.","userQuery"],["ask\\.com","q"],["altavista\\.","q"],["feedster\\.","q"],["search\\.lycos\\.","q"],["alltheweb\\.","q"],["technorati\\.com/search/([^\\?/]+)",1],["dogpile\\.com/info\\.dogpl/search/web/([^\\?/]+)",1,true]];Hilite.decodeReferrer=function(_1){var _2=null;var _3=new RegExp("");for(var i=0;i<Hilite.search_engines.length;i++){var se=Hilite.search_engines[i];_3.compile("^http://(www\\.)?"+se[0],"i");var _6=_1.match(_3);if(_6){var _7;if(isNaN(se[1])){_7=Hilite.decodeReferrerQS(_1,se[1]);}else{_7=_6[se[1]+1];}if(_7){_7=decodeURIComponent(_7);if(se.length>2&&se[2]){_7=decodeURIComponent(_7);}_7=_7.replace(/\'|"/g,"");_7=_7.split(/[\s,\+\.]+/);return _7;}break;}}return null;};Hilite.decodeReferrerQS=function(_8,_9){var _a=_8.indexOf("?");var _b;if(_a>=0){var qs=new String(_8.substring(_a+1));_a=0;_b=0;while((_a>=0)&&((_b=qs.indexOf("=",_a))>=0)){var _d,val;_d=qs.substring(_a,_b);_a=qs.indexOf("&",_b)+1;if(_d==_9){if(_a<=0){return qs.substring(_b+1);}else{return qs.substring(_b+1,_a-1);}}}}return null;};Hilite.hiliteElement=function(_e,_f){if(!_f||_e.childNodes.length==0){return;}var qre=new Array();for(var i=0;i<_f.length;i++){_f[i]=_f[i].toLowerCase();if(Hilite.exact){qre.push("\\b"+_f[i]+"\\b");}else{qre.push(_f[i]);}}qre=new RegExp(qre.join("|"),"i");var _12={};for(var i=0;i<_f.length;i++){if(Hilite.style_name_suffix){_12[_f[i]]=Hilite.style_name+(i+1);}else{_12[_f[i]]=Hilite.style_name;}}var _14=function(_15){var _16=qre.exec(_15.data);if(_16){var val=_16[0];var k="";var _19=_15.splitText(_16.index);var _1a=_19.splitText(val.length);var _1b=_15.ownerDocument.createElement("SPAN");_15.parentNode.replaceChild(_1b,_19);_1b.className=_12[val.toLowerCase()];_1b.appendChild(_19);return _1b;}else{return _15;}};Hilite.walkElements(_e.childNodes[0],1,_14);};Hilite.hilite=function(){var q=Hilite.debug_referrer?Hilite.debug_referrer:document.referrer;var e=null;q=Hilite.decodeReferrer(q);if(q&&((Hilite.elementid&&(e=document.getElementById(Hilite.elementid)))||(e=document.body))){Hilite.hiliteElement(e,q);}};Hilite.walkElements=function(_1e,_1f,_20){var _21=/^(script|style|textarea)/i;var _22=0;while(_1e&&_1f>0){_22++;if(_22>=Hilite.max_nodes){var _23=function(){Hilite.walkElements(_1e,_1f,_20);};setTimeout(_23,50);return;}if(_1e.nodeType==1){if(!_21.test(_1e.tagName)&&_1e.childNodes.length>0){_1e=_1e.childNodes[0];_1f++;continue;}}else{if(_1e.nodeType==3){_1e=_20(_1e);}}if(_1e.nextSibling){_1e=_1e.nextSibling;}else{while(_1f>0){_1e=_1e.parentNode;_1f--;if(_1e.nextSibling){_1e=_1e.nextSibling;break;}}}}};if(Hilite.onload){if(window.attachEvent){window.attachEvent("onload",Hilite.hilite);}else{if(window.addEventListener){window.addEventListener("load",Hilite.hilite,false);}else{var __onload=window.onload;window.onload=function(){Hilite.hilite();__onload();};}}}