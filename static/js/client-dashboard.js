const stars = document.querySelectorAll('.star-rating i');
const ratingInput = document.getElementById('rating-input');

stars.forEach(star => {
    star.addEventListener('click', () => {
        const rating = parseInt(star.getAttribute('data-value'));
        ratingInput.value = rating;

        stars.forEach(s => {
            s.classList.remove('selected');
            s.style.color = '#ccc';
        });

        for (let i = 0; i < rating; i++) {
            stars[i].classList.add('selected');
            stars[i].style.color = 'gold';
        }
    });
});