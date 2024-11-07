// ============================================ EVENTS ===================================================

//set up profile button events
var profileButton = document.querySelector("#clickable_profile");
var editProfileText = profileButton.getElementsByTagName("p")[0];

//mouse events
profileButton.addEventListener("mouseover", ()=> { editProfileText.style.visibility = 'visible'; });
profileButton.addEventListener("mouseout", () => {editProfileText.style.visibility = 'hidden';});

//click events
profileButton.addEventListener("click", () => {
    setDefaultEditProfile();
    document.getElementById("edit_profile_popup").style.visibility = 'visible';
    grayOut(true);
})


// ======================================== FUNCTIONS =================================================

//set default profile edit popup values
function setDefaultEditProfile() {
    var profileForm = document.getElementById("edit_profile_form");
    var inputs = profileForm.getElementsByTagName("input");
    inputs[0].value = document.getElementById("name").innerHTML;
    inputs[1].value = document.getElementById("title").innerHTML;

    var bio = profileForm.getElementsByTagName("textarea")[0];
    bio.value = document.querySelector(".content").getElementsByTagName("p")[0].innerText;
}

function saveProfileEdits() {
    var profileForm = document.getElementById("edit_profile_form");
    var inputs = profileForm.getElementsByTagName("input");

    document.getElementById("name").innerText = inputs[0].value;
    document.getElementById("title").innerText = inputs[1].value;

    var bio = profileForm.getElementsByTagName("textarea")[0];
    document.querySelector(".content").getElementsByTagName("p")[0].innerText = bio.value;

    hideProfilePopup();
}

function hideProfilePopup() {
    document.getElementById("edit_profile_popup").style.visibility = 'hidden';
    grayOut(false);

}

function showGallery() {
    document.getElementById('gallery').style.display = 'grid';
    document.getElementById('badges').style.display = 'none';
    document.getElementById('events').style.display = 'none';

    changeBoldedNav(0);
  }


function showBadges() {
    document.getElementById('badges').style.display = 'block';
    document.getElementById('gallery').style.display = 'none';
    document.getElementById('events').style.display = 'none';

    changeBoldedNav(1);
}

function showEvents() {
    document.getElementById('events').style.display = 'block';
    document.getElementById('gallery').style.display = 'none';
    document.getElementById('badges').style.display = 'none';

    changeBoldedNav(2);
}

function showPostPopup() {
    document.getElementById("add_post_popup").style.visibility = 'visible';
    grayOut(true);
}

function hidePostPopup() {
    document.getElementById("add_post_popup").style.visibility = 'hidden';
    grayOut(false);
}

function showDatabasePost(databasePost) {

    var cleanStr = cleanJsonString(databasePost);

    if(databasePost != null && databasePost != "")
    {
        let postJson = JSON.parse(cleanStr);
        let userJson = postJson["user"];
        let postImages = postJson["images"];

        //adjust the post popup's DOM 
        document.getElementById("post_content").innerText = postJson["caption"];

        //set image if there is one
        if(postImages.length > 0)
            document.getElementById("post_image").src = "/uploads/" + postImages[0]['name'];   
        else
            document.getElementById("post_image").src = "../static/images/raven.png";
    
        let date = new Date(Date.parse(postJson["datePosted"]));
        document.getElementById("post-time").innerText = "• " + date.toLocaleDateString();

        //set user who posted the post's details
        document.getElementById("posted-by").innerText = userJson["username"]

        if(userJson["profileImage"] != null)
            document.getElementById("profile_pic").src = "/uploads/" + userJson["profileImage"]["name"]

        document.getElementById("html_postID").value = postJson["postID"];  //invisible value used for deleting
        //make it visible
        document.getElementById("post_popup").style.visibility = 'visible';
        grayOut(true);
    
    }
}

function deletePost() {
    document.getElementById("confirmation_popup").style.visibility = 'visible';
}
function hideConfirmation() {
    document.getElementById("confirmation_popup").style.visibility = 'hidden';

}

//removes escape characters and turns them into their escaped forms (e.g., a new line becomes \n)
    //so JSON.parse doesn't get mad
function cleanJsonString(stringToClean)
{
    let returnStr = stringToClean.replace(/\\+/g, "\\\\");
    returnStr = returnStr.replace(/\n+/g, "\\n");
    returnStr = returnStr.replace(/\t+/g, "\\t");
    returnStr = returnStr.replace(/\/+/g, "\\/");
    
    returnStr = returnStr.replace(/(\b|\f|\r|)*/g, "");
    return returnStr;
}

//TODO: DELETE ME (replaced by showDatabasePost)
function showSocialPost(postString) {

    if(postString != null && postString != "")
    {
        let postJson = JSON.parse(postString);

        //adjust the post popup's DOM 
        document.getElementById("post_image").src = postJson["image"];
        document.getElementById("post_likes").innerText = postJson["likes"] + " likes";
        document.getElementById("post_content").innerText = postJson["content"];

        //make it visible
        document.getElementById("post_popup").style.visibility = 'visible';
        grayOut(true);
    
    }
}

function hideSocialPost() {
    document.getElementById("post_popup").style.visibility = 'hidden';
    grayOut(false);

}

function showEventPopup(eventString)
{
    if(eventString != null && eventString != "")
    {
        let eventJson = JSON.parse(eventString);
        //adjust the post popup's DOM 
     
        //make it visible
        document.getElementById("event_popup").style.visibility = 'visible';
        grayOut(true);
    
    }
}
function hideEventPopup()
{
    document.getElementById("event_popup").style.visibility = 'hidden';
    grayOut(false);

}

function grayOut(shouldGray)
{
    if(shouldGray)
    {
        document.getElementById('gray_out').style.visibility = 'visible';
        document.getElementsByTagName('body')[0].style.setProperty('overflow-y', 'hidden');


    }
    else
    {
        document.getElementById('gray_out').style.visibility = 'hidden';
        document.getElementsByTagName('body')[0].style.setProperty('overflow-y', 'scroll');

    }
}

function changeBoldedNav(boldIndex)
{
    let column = document.getElementById('mini_nav');

    //loop the nav bar elements
    let elements = column.getElementsByTagName('li');
    for(let i = 0; i < elements.length; i++)
    {
        //the style of the current li's a tag
        let style = elements[i].getElementsByTagName("a")[0].style;

        //bold it when selected
        if(i == boldIndex)
        {
            style.setProperty("font-weight", "600");
            style.setProperty("color", "#1d1d1d");
        }
        //set it to normal
        else
        {
            style.setProperty("font-weight", "400");
            style.setProperty("color", "#818181");

        }
    }

}

