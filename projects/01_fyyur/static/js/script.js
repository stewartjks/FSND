window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

// TODO modify to trigger form submission payload
  // document.getElementById('create-todo-form').onsubmit = function (e) {
    // Prevent default client redirect
      // e.preventDefault();
      // activeList = document.getElementById('active-list-id').innerHTML
  //   // Create POST with 'description' key-value pair in request body
  //   fetch('../todos/create', {
  //       method: 'POST',
  //       body: JSON.stringify({
  //           'description': document.getElementById('description').value,
  //           'current-list': document.getElementById('active-list-id').innerHTML,
  //       }),
  //       headers: {
  //           'content-type': 'application/json'
  //       }
  //   // Convert response from string to JSON
  //   }).then(function(response) {
  //       return response.json();
  //   }).then(function(jsonResponse){
  //       const liItem = document.createElement('LI');
  //       // Populate new todo's description into a new list item
  //       liItem.innerHTML =  jsonResponse['description'];
  //       document.getElementById('todos-list').appendChild(liItem);
  //       document.getElementById('error').className = 'hidden';
  //       // liItem.classList.add(todoClasses);
  //   }).catch(function () {
  //       // Show (hidden by default) error message if AJAX request fails at any point
  //       return document.getElementById('error').classList.remove('hidden');
  //   });