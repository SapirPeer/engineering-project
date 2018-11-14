
/*Get search string from the website and parse it*/
function getSearchString() {
	var searchString =document.getElementById('searchInput').value;
	//parse the search strign
}
 		
function displayResults(){
	document.getElementById('searchEngine').className= "small";
	document.getElementById('searchEngine').classList.remove= "centered";
	document.getElementById('results-container').style.display = 'block';

}