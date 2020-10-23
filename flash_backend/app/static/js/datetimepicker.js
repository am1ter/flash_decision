// Select boxes

let start_date = new Date();
start_date.setMonth(start_date.getMonth() - 1);

$(function () {
    $('#datetimepicker').datetimepicker(
        {
            format:'DD/MM/YYYY HH:mm',
            defaultDate: start_date
        }
    );
});
