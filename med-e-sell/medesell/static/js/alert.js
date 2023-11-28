setTimeout(function() {
    var alerts = document.getElementsByClassName('hide');
    for (var i = 0; i < alerts.length; i++) {
      alerts[i].style.display = 'none';
    }
  }, 3000);