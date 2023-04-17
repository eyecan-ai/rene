window.HELP_IMPROVE_VIDEOJS = false;

function update_box_size() {
  let box = document.querySelector('.slider-item');
  let width = box.offsetWidth;
  let height = box.offsetHeight;
  console.log(width, height)
  let rectangle = document.querySelector('.legend-boxes');
  rectangle.style.width = width + 'px';
  rectangle.style.height = height + 'px';

  var firstLegendBoxes = document.querySelector('.legend-boxes');

  // Remove the previous clones
  document.querySelectorAll('.legend-boxes-clone').forEach(e => e.remove());

  // Create a copy of it
  function add_clone(index) {
    var clone = firstLegendBoxes.cloneNode(true);
    marginLeft = clone.marginLeft;

    clone.classList.add("legend-boxes-clone");
    margin = clone.style.margin;
    clone.style.marginLeft = index * width + "px"
    clone.style.marginTop = - height + "px"

    // Inject it into the DOM
    firstLegendBoxes.after(clone);
  }

  document.querySelectorAll('.slider-item').forEach((e, index) => {
    if (index > 1) {
      add_clone(index - 1);
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
    slidesToScroll: 1,
    slidesToShow: 3,
    loop: false,
    infinite: false,
    autoplay: false,
    autoplaySpeed: 3000,
  }

  // Initialize all div with carousel class
  var carousels = bulmaCarousel.attach('.carousel', options);

  // Loop on each carousel initialized
  for (var i = 0; i < carousels.length; i++) {
    // Add listener to  event
    carousels[i].on('before:show', state => {
      console.log(state);
    });
  }

  // Access to bulmaCarousel instance of an element
  var element = document.querySelector('#my-element');
  if (element && element.bulmaCarousel) {
    // bulmaCarousel instance is available as element.bulmaCarousel
    element.bulmaCarousel.on('before-show', function (state) {
      console.log(state);
    });
  }



  bulmaSlider.attach();

  // Observe the box size change 
  const another_observer = new MutationObserver(mutationCallback)
  toObserve_1 = document.querySelector('.lozad');
  toObserve_2 = document.querySelector('.slider-item');
  another_observer.observe(toObserve_1, { attributes: true })
  another_observer.observe(toObserve_2, { attributes: true })
  update_box_size();




})