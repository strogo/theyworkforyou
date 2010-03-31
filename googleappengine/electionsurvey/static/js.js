$(function(){
    // Enable/disable more explanation fields at start according to status of radio buttons
    $('ul.questions textarea').attr('disabled', 'disabled');
    $('ul.questions > li').has('input:radio:checked').find('textarea').removeAttr('disabled');

    // Allow editing of more explanations when radio button has been pressed
    $('input:radio').change(function(){
        $(this).closest('ul.questions > li').find('textarea').removeAttr('disabled');
    });

    // Autosave the form when any part of it changes
    $('input:radio').add('ul.questions textarea').change(autosave_survey_form);
});

// Store form data on server so can come back to it later
function autosave_survey_form() {
    var token = $('input#token').val();
    // store all the form data
    var ser = $('form#electionsurvey').serialize();
    // submit it to the server
    $.ajax({ url: "/survey/autosave/" + token, context: document.body, type: 'POST', data: { 'ser': ser }, success: function(){
        $('div#autosave').stop(true, true).show().fadeOut(2000);
    }});
}

