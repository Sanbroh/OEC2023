window.onload = function() {
  // Immediately go to recommended location
  document.getElementById("framed-map").src = "https://www.google.com/maps/embed/v1/place?key=AIzaSyDGkzF9CQuX540YmPxCMSiMJlPEIsB9_hM&q=London+Health+Science+Centre+Victoria,London+Ontario";
}

// Keep default location link for later use
const linkDef = "https://www.google.com/maps/embed/v1/place?key=AIzaSyDGkzF9CQuX540YmPxCMSiMJlPEIsB9_hM";

function submitData(elm) {
  console.log("Submitted Data!");
  // var long = document.getElementById("long").value;
  // var lat = document.getElementById("lat").value;
  // console.log(long);
  // console.log(lat);

  // Filter Location
  var locationM = document.getElementById("location").value.replace(" ", "+");

  // Location default if empty
  if (locationM == "") {
    locationM = "Western+University,London+Ontario";
  }

  // Link formatting for change
  var linkM = linkDef + "&q=" + locationM;
  console.log(linkM);
  console.log(document.getElementById("framed-map").src);

  // Alter code and prevent window refresh
  document.getElementById("framed-map").src = linkM;
  event.preventDefault();
}
