function appendLoader(containerSelector) {
    $(containerSelector).append('<img class="ajax-loader" src="/content/images/indicator.gif" title="读取中..." alt="读取中..." />');
}

function removeLoader() {
    $("img.ajax-loader").remove();
}

function setupFormValidation(formSelector, validationRules, onSubmitCallback) {
    enableSubmitButton(formSelector);
    $(formSelector).validate({
        rules: (validationRules ? validationRules : {}),
        errorElement: "span",
        errorClass: "form-error",
        errorPlacement: function(error, element) {
            var span = element.prev().find("span.form-error");
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
function setSubmitButtonDisabled(formSelector, isDisabled) { // Don't call me, call my friends above..
    $(formSelector).find("input[type='submit']").attr("disabled", isDisabled ? "true" : "");    
}

function showAjaxError(insertionSelector, msg) {
    var div = $('<div class="error-notification"><h2>' + msg + '</h2>(click on this box to close)</div>');
    var fadeOut = function() {
        $(".error-notification").fadeOut("fast", function() { $(this).remove(); });
    };
        
    div.click(function(event) {
        fadeOut();
    });
    
    $(insertionSelector).append(div);
    div.fadeIn("fast");
    
    setTimeout(fadeOut, 1000 * 30);
}

