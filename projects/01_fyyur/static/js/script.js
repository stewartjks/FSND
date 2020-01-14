window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

// Get all values of multi-select input elements (such as Genre)
function getMultiselectValues(multiselectElement) {
  var result = [];
  var options = multiselectElement && multiselectElement.options;
  var option;
  for (var i=0, iLen=options.length; i<iLen; i++){
    option = options[i];
    if (option.selected){
      result.push(option.value || option.text);
    }
  }
  result.map(function(selection) {
    return JSON.stringify(selection);
  });
  result = result.join(", ");
  return result;
}

// On form submit, create request for new show and handle response
function showFormSubmitHandler() {
  document.getElementById('create-show-form').onsubmit = function (e) {
    // Prevent default client redirect
      e.preventDefault();
    // Create POST with 'description' key-value pair in request body
      fetch('/shows/create', {
          method: 'POST',
          mode: 'same-origin',
          body: JSON.stringify({
              'artist_id': document.getElementById('artist_id').value,
              'venue_id': document.getElementById('venue_id').value,
              'start_time': document.getElementById('start_time').value
          }),
          headers: {
              'content-type': 'application/json',
          }
      });
  }
}

function artistFormSubmitHandler() {
  // On form submit, create request for new artist and handle response
  form = document.getElementsByClassName('form')[0];
  if (form.id == 'create-artist-form') {
    fetch_id = '';
    fetch_verb = 'create';
  }
  else if (form.id == 'edit-artist-form') {
    // Get artist ID from classList
    fetch_id = form.classList[1];
    fetch_verb = '/edit';
  }
  form.onsubmit = function(e) {
      // Prevent default client redirect
        e.preventDefault();
      // Get multi-select values
        genresElement = document.getElementById('genres');
        genresValues = getMultiselectValues(genresElement);
      // Create POST with 'description' key-value pair in request body
        fetch('/artists/' + fetch_id + fetch_verb, {
            method: 'POST',
            body: JSON.stringify({
                'name': document.getElementById('name').value,
                'city': document.getElementById('city').value,
                'state': document.getElementById('state').value,
                'phone': document.getElementById('phone').value,
                'genres': genresValues,
                'facebook-link': document.getElementById('facebook_link').value
            }),
            headers: {
                'content-type': 'application/json'
            }
        });
  };
}

function venueFormSubmitHandler() {
  // On form submit, create request for new venue and handle response
  form = document.getElementsByClassName('form')[0];
  if (form.id == 'create-venue-form') {
    fetch_id = '';
    fetch_verb = 'create';
  }
  else if (form.id == 'edit-venue-form') {
     // Get venue ID from classname 
     fetch_id = form.classList[1];
     fetch_verb = '/edit';
  }
  form.onsubmit = function(e) {
    // Prevent default client redirect
      e.preventDefault();
    // Create POST with 'description' key-value pair in request body
      fetch('/venues/'+ fetch_id + fetch_verb, {
          method: 'POST',
          body: JSON.stringify({
              'name': document.getElementById('name').value,
              'city': document.getElementById('city').value,
              'state': document.getElementById('state').value,
              'address': document.getElementById('address').value,
              'phone': document.getElementById('phone').value,
              'genres': document.getElementById('genres').value,
              'facebook_link': document.getElementById('facebook_link').value
          }),
          headers: {
              'content-type': 'application/json'
          }
      });
  };
}

var createShowForm = document.getElementById('create-show-form');
    if(createShowForm){
        showFormSubmitHandler();
    }

var createArtistForm = document.getElementById('create-artist-form');
var editArtistForm = document.getElementById('edit-artist-form');
if(createArtistForm || editArtistForm){
    artistFormSubmitHandler();
}

var createVenueForm = document.getElementById('create-venue-form');
var editVenueForm = document.getElementById('edit-venue-form');
if(createVenueForm || editVenueForm){
    venueFormSubmitHandler();
}