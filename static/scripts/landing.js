        document.addEventListener('DOMContentLoaded', () => {
            const text = "Welcome to mindmate: an AI-driven tool that helps users manage their mental well-being effectively";
            const headerTextElement = document.getElementById('headerText');

            function typeEffect(element, text) {
                let index = 0;
                function typing() {
                    if (index < text.length) {
                        element.textContent += text.charAt(index);
                        index++;
                        setTimeout(typing, 50); // Adjust the typing speed here
                    }
                }
                typing();
            }

            typeEffect(headerTextElement, text);
        });

        function openModal(modalId) {
            document.querySelector(modalId).style.display = "block";
            document.body.style.overflow = "hidden"; // Prevent scrolling of background content
        }

        function closeModal(modalId) {
            document.querySelector(modalId).style.display = "none";
            document.body.style.overflow = "auto"; // Restore scrolling to background content
        }

        document.getElementById('registerLink').addEventListener('click', function() {
            openModal('#registerModal');
        });

        document.getElementById('loginLink').addEventListener('click', function() {
            openModal('#loginModal');
        });