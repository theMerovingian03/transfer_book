$(document).ready(function() {
    $(".clickable-row").click(function(event) {
      // Check if the clicked element is an anchor tag
      if ($(event.target).is('a')) {
        // Allow the anchor tag's default behavior (e.g., redirecting to a different page)
        return;
      }
  
      // Redirect to the URL specified in the data-href attribute
      window.location = $(this).data("href");
    });
  });

  function goBack() {
    window.history.back();
  }