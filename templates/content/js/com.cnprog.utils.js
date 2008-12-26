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
