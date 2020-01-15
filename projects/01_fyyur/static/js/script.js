window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

// Add handler(s) if the associated form / buttton exists on the current page
var createShowForm = document.getElementById('create-show-form');
var createArtistForm = document.getElementById('create-artist-form');
var createVenueForm = document.getElementById('create-venue-form');
var editArtistForm = document.getElementById('edit-artist-form');
var editVenueForm = document.getElementById('edit-venue-form');
var deleteArtist = document.getElementById('delete-artist-btn');
var deleteVenue = document.getElementById('delete-venue-btn');
var searchArtists = document.getElementById('search-artists');
var searchVenues = document.getElementById('search-venues');

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

// On form submit, create request for new show, artist, or venue and handle response

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
  var form = document.getElementsByClassName('form')[0];
  if (form.id == 'create-artist-form') {
    fetch_id = '';
    fetch_verb = 'create';
  }
  else if (form.id == 'edit-artist-form') {
    // Get artist ID from classList
    var fetch_id = form.classList[1];
    var fetch_verb = '/edit';
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

// Handle artist and venue deletions

function deleteArtistHandler() {
  var deleteBtn = document.getElementById('delete-artist-btn');
  var artist_id = document.getElementById('artist-id').innerHTML.toString();
  deleteBtn.onclick = function() {
    fetch('/artists/'+artist_id, {
      method: 'DELETE',
      body: JSON.stringify({
        'id': artist_id
      }),
      headers: {
        'content-type': 'application/json'
      }
    });
  };
}

function deleteVenueHandler() {
  var deleteBtn = document.getElementById('delete-venue-btn');
  var venue_id = document.getElementById('venue-id').innerHTML.toString();
  deleteBtn.onclick = function() {
    fetch('/venues/'+venue_id, {
      method: 'DELETE',
      body: JSON.stringify({
        'id': venue_id
      }),
      headers: {
        'content-type': 'application/json'
      }
    });
  };
}

// TODO Handle artist and venue searches

function searchArtistsHandler() { 
  searchArtists.onsubmit = function(e) {
    e.preventDefault();
    var artistSearchTerm = document.getElementById('artist-search-term').value.toString();
    fetch('/artists/search', {
      method: 'POST',
      body: JSON.stringify({
        'search_term': artistSearchTerm
      }),
      headers: {
        'content-type': 'application/json'
      }
    });
  };
}

function searchVenuesHandler() { 
  searchVenues.onsubmit = function(e) {
    e.preventDefault();
    var venueSearchTerm = document.getElementById('venue-search-term').value.toString();
    fetch('/venues/search', {
      method: 'POST',
      body: JSON.stringify({
        'search_term': venueSearchTerm
      }),
      headers: {
        'content-type': 'application/json'
      }
    });
  };
}

if(createShowForm){
        showFormSubmitHandler();
    }
if(createArtistForm || editArtistForm){
    artistFormSubmitHandler();
}
if(createVenueForm || editVenueForm){
    venueFormSubmitHandler();
}
if(deleteArtist){
  deleteArtistHandler();
}
if(deleteVenue){
  deleteVenueHandler();
}
if(searchArtists){
  searchArtistsHandler();
}
if(searchVenues){
  searchVenuesHandler();
}