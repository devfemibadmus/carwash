(function ($) {

  "use strict";

  // background color when scroll 

  var initScrollNav = function() {
    var scroll = $(window).scrollTop();

    if (scroll >= 200) {
      $('.navbar.fixed-top').addClass("bg-black");
    }else{
      $('.navbar.fixed-top').removeClass("bg-black");
    }
  }

  $(window).scroll(function() {    
    initScrollNav();
  }); 

    // init Chocolat light box
    var initChocolat = function () {
      Chocolat(document.querySelectorAll('.image-link'), {
        imageSize: 'contain',
        loop: true,
      })
    }
  
  $(document).ready(function () {
  
    //testimonial swiper
   
    var swiper = new Swiper(".project-swiper", {
      slidesPerView: 4,
      spaceBetween: 30,
      navigation: {
        nextEl: ".icon-arrow-right",
        prevEl: ".icon-arrow-left",
      },
      breakpoints: {
        0: {
          slidesPerView: 1,
          spaceBetween: 10,

        },
        768: {
          slidesPerView: 3,
          spaceBetween: 10,

        },
        1400: {
          slidesPerView: 4,
          spaceBetween: 10,

        },
      }
    });


    $(".youtube").colorbox({
      iframe: true,
      innerWidth: 960,
      innerHeight: 585
    });


        // Animate on Scroll
        AOS.init({
          duration: 1000,
          once: true,
        })
    
        window.addEventListener("load", (event) => {
          //isotope
          $('.isotope-container').isotope({
            // options
            itemSelector: '.item',
            layoutMode: 'masonry'
          });
    
    
    
          // Initialize Isotope
          var $container = $('.isotope-container').isotope({
            // options
            itemSelector: '.item',
            layoutMode: 'masonry'
          });
    
          $(document).ready(function () {
            //active button
            $('.filter-button').click(function () {
              $('.filter-button').removeClass('active');
              $(this).addClass('active');
            });
          });
    
          // Filter items on button click
          $('.filter-button').click(function () {
            var filterValue = $(this).attr('data-filter');
            if (filterValue === '*') {
              // Show all items
              $container.isotope({ filter: '*' });
            } else {
              // Show filtered items
              $container.isotope({ filter: filterValue });
            }
          });
    
        });
    
    
        initChocolat();


  });


})(jQuery);
