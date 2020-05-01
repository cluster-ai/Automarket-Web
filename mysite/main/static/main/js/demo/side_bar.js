
/*
Making requests to the django database will need to be in HTTP form
	Use JQuery framework for generating requests

AJAX Use Cases: (not using it for now)
- Update a web page without reloading the page
- Request data from a server - after the page has loaded
- Receive data from a server - after the page has loaded
- Send data to a server - in the background
*/

//Requests sidebar data from database

$.ajax({
	url: 'sidebar_content/',
	data: {},
	dataType: 'json',
	success: function (data) {
		alert("success!")
		print(data)
	}
});