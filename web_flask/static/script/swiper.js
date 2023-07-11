import Swiper from 'https://cdn.jsdelivr.net/npm/swiper@10/swiper-bundle.min.mjs'

$(document).ready(function() {
    var swiper = new Swiper(".mySwiper", {
        effect: "flip",
        grabCursor: true,
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
            renderBullet: function (index, className) {
            return '<span class="' + className + '">' + (index + 1) + "</span>";
          },
        },
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
    });
});
