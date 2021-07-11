function IndexPage(){
$(".error-msg").hide();
var urldata =  $("#searchme").val();
if (!urldata){
  return 
}

$.ajax({
  type: "POST",
  url: '/v1/driveurl',
  data: JSON.stringify({"url":urldata}),
  dataType:"json",
  contentType: 'application/json',

  success: function (data,status,xhr) {
    $(".error-msg").hide();
    $(".error-msg").show();
    var errorMsg =  data["status"];
    $(".error").text( errorMsg);

  },
  error: function (data) {
    $(".error-msg").hide();
    $(".error-msg").show();
    var errorMsg =  data.responseJSON["error"];
    $(".error").text( errorMsg);

  }
});
}
function PutClear(e) {
    if (e.which == 13) {
      $('.search-submit').click();
      return false;
    }
  $(".svg-icon").css("visibility","visible");

}
function ClearInput() {

  $(".input-val").val("");
  $(".svg-icon").css("visibility","hidden");
}

function setGetParameter(paramName)
{
    var  paramValue = $("#searchme").val();
    if (!paramValue){
      return
    }
    var url = `${window.location.href}search`;
    console.log(url);
    var hash = location.hash;
    url = url.replace(hash, '');
    if (url.indexOf(paramName + "=") >= 0)
    {
        var prefix = url.substring(0, url.indexOf(paramName + "=")); 
        var suffix = url.substring(url.indexOf(paramName + "="));
        suffix = suffix.substring(suffix.indexOf("=") + 1);
        suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
        url = prefix + paramName + "=" + paramValue + suffix;
    }
    else
    {
    if (url.indexOf("?") < 0)
        url += "?" + paramName + "=" + paramValue;
    else
        url += "&" + paramName + "=" + paramValue;
    }
    console.log(url);
    window.location.href = url + hash;
}

function setGetSearch(paramName)
{
    var  paramValue = $(".input-val").val();
    if (!paramValue){
      return
    }
    var url = window.location.href;
    console.log(url);
    var hash = location.hash;
    url = url.replace(hash, '');
    if (url.indexOf(paramName + "=") >= 0)
    {
        var prefix = url.substring(0, url.indexOf(paramName + "=")); 
        var suffix = url.substring(url.indexOf(paramName + "="));
        suffix = suffix.substring(suffix.indexOf("=") + 1);
        suffix = (suffix.indexOf("&") >= 0) ? suffix.substring(suffix.indexOf("&")) : "";
        url = prefix + paramName + "=" + paramValue + suffix;
    }
    else
    {
    if (url.indexOf("?") < 0)
        url += "?" + paramName + "=" + paramValue;
    else
        url += "&" + paramName + "=" + paramValue;
    }
    console.log(url);
    window.location.href = url + hash;
}
function hideError(){
    $(".error-msg").hide();
}