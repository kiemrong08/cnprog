var lanai =
{
    /**
     * Finds any <pre><code></code></pre> tags which aren't registered for
     * pretty printing, adds the appropriate class name and invokes prettify.
     */
    highlightSyntax: function(){
        var styled = false;
        $("pre code").parent().each(function(){
            if (!$(this).hasClass('prettyprint')){
                $(this).addClass('prettyprint');
                styled = true;
            }
        });

        if (styled){
            prettyPrint();
        }
    }
};
