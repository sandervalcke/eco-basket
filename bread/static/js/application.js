$(document).ready(function(){
    $('#submitData').submit(addData);
});

function addData(){
    var data = new Object();
    data.type = 'file';
    data.info = { 'location': $('#dataLocation').val() };

    $.ajax({
        type: "POST",
        url:  "/api/v1.0/dbdata",
        contentType : "application/json",
        data : JSON.stringify(data),
    }).success(function(result){
        location.reload();
    }).error(function(result){
        console.log(result);
    });

    return false;
}