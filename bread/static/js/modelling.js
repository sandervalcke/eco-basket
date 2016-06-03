
var submitModel = function(viewid, targetid, algoid){
    console.log("submit model", viewid, targetid, algoid);

    var data = new Object();
    data.sview_id   = viewid;
    data.target_id = targetid;
    data.algo_id   = algoid;

    $.ajax({
        type: "POST",
        url:  "/rank/api/v1.0/models",
        contentType : "application/json",
        data : JSON.stringify(data),
    }).success(function(result){
        location.reload();
    }).error(function(result){
        console.log(result);
    });

    return false;
}


var submitModels = function(){
    var algos   = $('.algobox:checked');
    var sviews  = $('.svbox:checked');
    var targets = $('.targetbox:checked');

    for (var ialgo = 0; ialgo < algos.length; ++ialgo){
      for (var iview = 0; iview < sviews.length; ++iview){
        for (var itarget = 0; itarget < targets.length; ++itarget){
          submitModel(sviews[iview].name, targets[itarget].name, algos[ialgo].name);
        }
      }
    }
};


$(document).ready(function(){
    $('#submitModelling').submit(submitModels);
});


//$('.bs-checkbox').click(function(){
//    var algos   = $('.algobox:checked');
//    var sviews  = $('.svbox:checked');
//    var targets = $('.targetbox:checked');
//
//    for (var ialgo = 0; ialgo < algos.length; ++ialgo){
//      for (var iview = 0; iview < sviews.length; ++iview){
//        for (var itarget = 0; itarget < targets.length; ++itarget){
//          submitModel(sviews[iview].name, targets[itarget].name, algos[ialgo].name);
//        }
//      }
//    }
//});
