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