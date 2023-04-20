window.HELP_IMPROVE_VIDEOJS = false;

// Debounce bulma carousel next/prev to prevent race condition.
bulmaCarousel.prototype.next = debounce(bulmaCarousel.prototype.next, 300, true);
bulmaCarousel.prototype.prev = debounce(bulmaCarousel.prototype.prev, 300, true);

function debounce(func, wait, immediate) {
  var timeout;
  return function () {
    var context = this, args = arguments;
    var later = function () {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    var callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
};

function update_box_size() {
  let box = document.querySelector('.slider-item');
  let width = box.offsetWidth;

  // let height = box.offsetHeight;
  // Videos are lazy loading, until we get how to catch when video is fully loaded
  // we constrain height to be the right ratio cause width is loading correctly
  // while height seems to be halved
  ratio = 359 / 320
  let height = ratio * width;

  let boxes = document.querySelector('.legend-boxes');
  boxes.style.width = width + 'px';
  boxes.style.height = height + 'px';

  var overlay = document.querySelector('.is-overlay');

  // // Remove the previous clones
  document.querySelectorAll('.is-overlay-clone').forEach(e => e.remove());

  // // Create a copy of it
  function add_clone(element, index) {
    var clone = overlay.cloneNode(true);
    marginLeft = clone.marginLeft;

    clone.classList.add("is-overlay-clone");
    margin = clone.style.margin;
    clone.style.marginLeft = index * width + "px"
    element.append(clone)
  }

  document.querySelectorAll('.item').forEach((element, index) => {
    if (index > 0) {
      add_clone(element, index);
    }
  })
}

const mutationCallback = (mutationsList) => {
  for (const mutation of mutationsList) {
    update_box_size();
  }
}


$(document).ready(function () {
  const observer = lozad(); // lazy loads elements with default selector as '.lozad'
  observer.observe();

  var options = {
    initialSlide: 0,
    slidesToScroll: 1,
    slidesToShow: 3,
    loop: true,
    infinite: false,
    autoplay: false,
    autoplaySpeed: 3000,
    breakpoints: [{ changePoint: 480, slidesToShow: 1, slidesToScroll: 1 }, { changePoint: 768, slidesToShow: 2, slidesToScroll: 1 }],
  }

  // Initialize all div with carousel class
  bulmaCarousel.attach('#results-carousel', options);

  // Observe the box size change 
  const another_observer_2 = new MutationObserver(mutationCallback)
  toObserve_2 = document.querySelector('.slider-item');
  another_observer_2.observe(toObserve_2, { attributes: true, subtree: true, })
})