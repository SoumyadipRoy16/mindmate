        document.addEventListener('DOMContentLoaded', function() {
            const feedbackForm = document.getElementById('feedbackForm');
            const starLabels = document.querySelectorAll('.star-rating label');
            const starInputs = document.querySelectorAll('.star-rating input');
            let selectedStars = 0;

            feedbackForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const rating = document.querySelector('input[name="rating"]:checked');
                const feedbackMessage = document.getElementById('feedbackMessage').value.trim();

                if (rating && feedbackMessage) {
                    const formData = {
                        rating: rating.value,
                        feedbackMessage: feedbackMessage
                    };

                    console.log('Submitting feedback:', formData);

                    alert('Feedback submitted successfully!');

                    const formattedDate = new Date().toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: '2-digit'
                    });
                    addReview("Anonymous", formattedDate, selectedStars, formData.feedbackMessage);

                    // Clear the form
                    feedbackForm.reset();
                    starLabels.forEach(label => label.style.color = 'rgba(255, 255, 255, 0.3)');
                    selectedStars = 0;
                } else {
                    alert('Please provide both a rating and feedback message.');
                }
            });

            function addReview(name, date, rating, message) {
                const reviewList = document.getElementById('reviewList');

                const reviewItem = document.createElement('div');
                reviewItem.classList.add('review-item');

                const reviewAvatar = document.createElement('div');
                reviewAvatar.classList.add('review-avatar');

                const reviewContent = document.createElement('div');
                reviewContent.classList.add('review-content');

                const reviewHeader = document.createElement('div');
                reviewHeader.classList.add('review-header');

                const reviewName = document.createElement('div');
                reviewName.classList.add('review-name');
                reviewName.textContent = name;

                const reviewDate = document.createElement('div');
                reviewDate.classList.add('review-date');
                reviewDate.textContent = date;

                const reviewStars = document.createElement('div');
                reviewStars.classList.add('review-stars');
                reviewStars.innerHTML = '&#9733;'.repeat(rating);

                const reviewMessage = document.createElement('div');
                reviewMessage.classList.add('review-message');
                reviewMessage.textContent = message;

                reviewHeader.appendChild(reviewName);
                reviewHeader.appendChild(reviewDate);
                reviewContent.appendChild(reviewHeader);
                reviewContent.appendChild(reviewStars);
                reviewContent.appendChild(reviewMessage);
                reviewItem.appendChild(reviewAvatar);
                reviewItem.appendChild(reviewContent);

                reviewList.appendChild(reviewItem);
            }

            starLabels.forEach((label, index) => {
                label.addEventListener('click', () => {
                    const clickedIndex = Array.from(starLabels).indexOf(label);
                    starInputs.forEach((input, inputIndex) => {
                        if (inputIndex <= clickedIndex) {
                            input.checked = true;
                            selectedStars = clickedIndex + 1;
                        } else {
                            input.checked = false;
                        }
                    });
                    starLabels.forEach((lbl, lblIndex) => {
                        if (lblIndex <= clickedIndex) {
                            lbl.style.color = '#ffd700';
                        } else {
                            lbl.style.color = 'rgba(255, 255, 255, 0.3)';
                        }
                    });
                    console.log('Selected stars:', selectedStars);
                });
            });
        });