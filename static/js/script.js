/* ====================================
               Preloader
======================================= */
$(window).on('load', function () { // make sure that whole site is loaded
  $('#status').fadeOut();
  $('#preloader').delay(450).fadeOut('slow');
});



/* ====================================
               Navigation
======================================= */
//* Show and Hide grey Nav *//

$(function () {
  // show/hide nav on page load
  showHideNav();

  $(window).scroll(function () {
    // show/hide nav on window's scroll
    showHideNav();
  });

  function showHideNav() {
    if ($(window).scrollTop() > 50) {
      // show grey nav
      $(".navbar").addClass("grey-nav-top");
      // show white logo
      $(".navbar-brand img").attr("src", "/static/img/logo/logo-original-name2.png");
      // show back to top
      $(".btn-back-to-top").fadeIn();
    } else {
      // hide grey nav
      $(".navbar").removeClass("grey-nav-top");
      // show logo
      $(".navbar-brand img").attr("src", "/static/img/logo/logo-original-name.png");
      // hide back to top
      $(".btn-back-to-top").fadeOut();
    }
  }

});

/* ====================================
              Search Box
======================================= */
$('#dropdown-items li').on('click', function () {
  $('#dropdown_title').html($(this).find('a').html());
});


/* ====================================
              Animation
======================================= */
// animation when scroll
// $(function () {
//      new WOW().init(); 
// });

// // home animation on page load
// $(window).on('load', function() {

//     $("#home-heading-1").addClass("animated fadeInDown");
//     $("#home-heading-2").addClass("animated fadeInLeft");
//     $("#home-separator").addClass("animated zoomIn");
//     $("#home-heading-3").addClass("animated zoomIn");
//     $("#home-reservation").addClass("animated fadeInUp");
//     $("#arrow-down i").addClass("animated fadeInDown infinite");

// });

/* ====================================
                Home
======================================= */
$(document).ready(function () {
  // HomePage Carousel 
  $('#myCarousel-client').carousel({
    interval: false
  })
  $('#myCarousel-team').carousel({
    interval: false
  })
  $('#myTestimonial').carousel({
    interval: 3000
  })

  // Add Smooth Scrolling
  $("a.smooth-scroll").click(function (event) {

    event.preventDefault();

    var target = $(this).attr("href"); //Get the target
    var scrollToPosition = $(target).offset().top

    $('html').animate({
      'scrollTop': scrollToPosition
    }, 1250, function () {
      window.location.hash = "" + target;
      // Jump to the top of the div with same id
      // Force page to back to the end of the animation
      $('html').animate({
        'scrollTop': scrollToPosition
      }, 0);
    });

    $('body').append("called");

  });

});

/* ====================================
              Search Result
======================================= */

// Show & Hide List
// Building Designer
$('.open-list1').click(function () {
  $('#building-designer-list').slideDown();
  $('.close-list1').show();
  $('.open-list1').hide();
});

$('.close-list1').click(function () {
  $('#building-designer-list').slideUp();
  $('.open-list1').show();
  $('.close-list1').hide();
});

// Home Builder
$('.open-list2').click(function () {
  $('#home-builder-list').slideDown();
  $('.close-list2').show();
  $('.open-list2').hide();
});

$('.close-list2').click(function () {
  $('#home-builder-list').slideUp();
  $('.open-list2').show();
  $('.close-list2').hide();
});

// Interior Decorator
$('.open-list3').click(function () {
  $('#interior-decorator-list').slideDown();
  $('.close-list3').show();
  $('.open-list3').hide();
});

$('.close-list3').click(function () {
  $('#interior-decorator-list').slideUp();
  $('.open-list3').show();
  $('.close-list3').hide();
});

// Home Remodeler
$('.open-list4').click(function () {
  $('#home-remodeler-list').slideDown();
  $('.close-list4').show();
  $('.open-list4').hide();
});

$('.close-list4').click(function () {
  $('#home-remodeler-list').slideUp();
  $('.open-list4').show();
  $('.close-list4').hide();
});

// Landscape Constractor
$('.open-list5').click(function () {
  $('#lanscape-list').slideDown();
  $('.close-list5').show();
  $('.open-list5').hide();
});

$('.close-list5').click(function () {
  $('#lanscape-list').slideUp();
  $('.open-list5').show();
  $('.close-list5').hide();
});

/* ====================================
              Pagination
======================================= */
$(document).ready(function () {
  $("#tab").pagination({
    items: 4,
    contents: 'contents',
    previous: '《',
    next: '》',
    position: 'bottom',
  });
});


// $('#nav-item a').on('click', function (e) {
//   // sets the input field's value to the data value of the clicked a element
//   $('#nav-type').val($(this).data('value'));
// });

/* Comment */
// $(document).ready(function () {
//   $(".editor-header a").click(function (e) {
//     e.preventDefault();

//     var _val = $(this).data("role"),
//       _sizeValIn = parseInt($(this).data("size-val") + 1),
//       _sizeValRe = parseInt($(this).data("size-val") - 1),
//       _size = $(this).data("size");
//     if (_size == "in-size") {
//       document.execCommand(_val, false, _sizeValIn + "px");
//     } else {
//       document.execCommand(_val, false, _sizeValRe + "px");
//     }
//   });
// });

// $(document).ready(function () {
//   var $text = $("#text"),
//     $submit = $("#comment-button input[type='submit']"),
//     $listComment = $(".list-comments"),
//     $loading = $(".loading"),
//     _data,
//     $totalCom = $(".total-comment");

//   $totalCom.text($(".list-comments > div").length);

//   $($submit).click(function () {
//     if ($text.html() == "") {
//       alert("Plesea write a comment!");
//       $text.focus();
//     } else {
//       _data = $text.html();
//       $.ajax({
//         // type: "POST",
//         // url: 'post_info_update/<int:post_id>',
//         data: _data,
//         cache: false,
//         success: function (html) {
//           $loading.show().fadeOut(300);
//           $listComment.append("<div>" + _data + "</div>");
//           $text.html("");
//           $totalCom.text($(".list-comments > div").length);
//         }
//       });
//       return false;
//     }
//   });
// });