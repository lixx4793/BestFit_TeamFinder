function showPost() {
$('#postCreater').css('top', '10%');
$('#scrim').css('display', 'inline-block');
}

function scrimTriger(caseNum) {
  switch (caseNum) {
    case 1:
      hidePost();
      break;
    default:
      hidePost();
  }
}

function hidePost() {
  $('#postCreater').css('top', '-100%');
  $('#scrim').css('display', 'none');
}

function submitForm(status) {

  $('#formStatus').val(status);
  $('#subButton').click();

}


// <img class="removeImg"
// src = "https://www.materialui.co/materialIcons/action/highlight_remove_grey_192x192.png"
// onclick="hideSelf(this)" select = false>

function selectTag(tag, tagId) {
// get count values
  var countDiv = document.getElementById("countDiv");
  var currentCount = countDiv.value;

//  add count values
  countDiv.value += 1;
// create image for delete with value = count
  var form = document.getElementById("mainForm");
  var node = document.createElement("INPUT");
  node.setAttribute("type", "text");
  node.style.display = "none";
  // node.display.style = "display:none";
  node.name = "tags[]";
  node.id = "inputTag"+tagId;
  node.value = tagId;
  form.appendChild(node);
 var img = document.createElement("img");
 img.src = "https://www.materialui.co/materialIcons/action/highlight_remove_grey_192x192.png";
 img.className = "removeImg";
 tag.style.pointerEvents =  "none";
 img.onclick = function(){hideSelf(tagId)}

 tag.parentNode.appendChild(img);




}

function hideSelf(tagId) {
  var id = "tag" + tagId;
  var tagid = "inputTag"+tagId;
  var input = document.getElementById(tagid);
  input.parentNode.removeChild(input);
  var container = document.getElementById(id);
  var img = container.getElementsByTagName("img")[0];
  img.parentNode.removeChild(img);
  container.getElementsByTagName("span")[0].style.pointerEvents = "fill";

}


function hideUpdate(){
  document.getElementById('uploadpop').style.display='none';
}
