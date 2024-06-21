let recognition;
let isRecording = false;

function sendMessage(event) {
    if (event.key === 'Enter') {
        sendUserMessage();
    }
}

function sendMessageByButton() {
    sendUserMessage();
}

function sendUserMessage() {
    const userInput = document.getElementById('userInput').value;
    if (userInput.trim() === '') return;

    displayMessage(userInput, 'user');

    fetch(`/chat?message=${userInput}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(data.response, 'bot');
        displayRecommendations(data.article, data.exercises, data.professionals);
    })
    .catch(error => console.error('Error:', error));

    document.getElementById('userInput').value = '';
}

function displayMessage(message, sender) {
    const chat = document.getElementById('chat');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);

    const icon = document.createElement('img');
    icon.src = sender === 'user' ? '/static/user-icon.png' : '/static/bot-icon.png';
    messageElement.appendChild(icon);

    const textElement = document.createElement('span');
    textElement.textContent = message;
    messageElement.appendChild(textElement);

    chat.appendChild(messageElement);
    chat.scrollTop = chat.scrollHeight;
}


function displayRecommendations(article, exercises, professionals) {
    const chat = document.getElementById('chat');

    if (article && article.length > 0) {
        const articleElement = document.createElement('div');
        articleElement.classList.add('message', 'bot');
        articleElement.innerHTML = `<strong>Recommended Articles:</strong><br>`;
        article.forEach(item => {
            articleElement.innerHTML += `<a href="${item.link}" target="_blank">${item.title}</a><br>${item.summary}<br><br>`;
        });
        chat.appendChild(articleElement);
    }

    if (exercises && exercises.length > 0) {
        const exerciseElement = document.createElement('div');
        exerciseElement.classList.add('message', 'bot');
        exerciseElement.innerHTML = `<strong>Recommended Exercises:</strong><br>`;
        exerciseElement.innerHTML += exercises.map(exercise => `${exercise}<br>`).join('');
        chat.appendChild(exerciseElement);
    }

    if (professionals && professionals.length > 0) {
        const professionalElement = document.createElement('div');
        professionalElement.classList.add('message', 'bot');
        professionalElement.innerHTML = `<strong>Recommended Professionals:</strong><br>`;
        professionals.forEach(professional => {
            professionalElement.innerHTML += `${professional.Name} - ${professional.Specialization} - ${professional.Clinic}<br>`;
        });
        chat.appendChild(professionalElement);
    }

    chat.scrollTop = chat.scrollHeight;
}

function attachFile() {
    document.getElementById('fileInput').click();
}

function startRecording() {
    const voiceIcon = document.getElementById('voiceIcon');
    const userInput = document.getElementById('userInput');

    if (!isRecording) {
        recognition = new webkitSpeechRecognition(); // Create a new SpeechRecognition instance
        recognition.continuous = true; // Keep recognizing speech as long as the user is speaking
        recognition.lang = 'en-UK'; // Set the language (you can change this to match the language you want to recognize)
        recognition.onresult = event => {
            const last = event.results.length - 1;
            const spokenText = event.results[last][0].transcript;
            userInput.value = spokenText; // Write the spoken text into the input field
        };
        recognition.start(); // Start speech recognition
        isRecording = true;
        voiceIcon.src = 'static/voice_recording_icon.png'; // Change icon to indicate recording
    } else {
        recognition.stop(); // Stop speech recognition
        isRecording = false;
        voiceIcon.src = 'static/voice_icon.png'; // Revert icon back to original
    }
}

function sendAudioMessage(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');

    fetch('/upload_audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.transcription) {
            displayMessage(data.transcription, 'user');
        }
        displayMessage(data.response, 'bot');
    })
    .catch(error => console.error('Error:', error));
}

function toggleInfoBox() {
    const infoBox = document.getElementById('infoBox');
    infoBox.style.visibility = infoBox.style.visibility === 'visible' ? 'hidden' : 'visible';
}

function showTooltip() {
    document.getElementById('tooltip').style.visibility = 'visible';
}

function hideTooltip() {
    document.getElementById('tooltip').style.visibility = 'hidden';
}

document.addEventListener('DOMContentLoaded', () => {

    const selectElement = document.getElementById('illnessSelect');
    const illnesses = [
        "Anxiety disorders", 
        "Psychotic Disorders", 
        "Trauma and Stressor-Related Disorders", 
        "Obsessive-Compulsive and Related Disorders", 
        "Dissociative Disorders", 
        "Somatic Symptom and Related Disorders", 
        "Feeding and Eating Disorders", 
        "Sleep Disorders", 
        "Substance-Related and Addictive Disorders", 
        "Neurodevelopmental Disorders", 
        "Personality Disorders"
    ];

    illnesses.forEach(illness => {
        const option = document.createElement('option');
        option.value = illness;
        option.textContent = illness;
        selectElement.appendChild(option);
    });

    const generateButton = document.getElementById('generateButton');
    generateButton.addEventListener('click', loadInfo);

    const chatWithUsLink = document.getElementById('chatWithUsLink');
    chatWithUsLink.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default link behavior
        window.location.href = './index.html'; // Navigate to index.html
    });

    const mindmatesite = document.getElementById('mindmatesite');
    mindmatesite.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default link behavior
        window.location.href = './'; // Navigate to index.html
    });

    const managefeedback = document.getElementById('managefeedback');
    managefeedback.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default link behavior
        window.location.href = './feedback.html'; // Navigate to index.html
    });
});

function loadInfo() {
    const selectedIllness = document.getElementById('illnessSelect').value;
    if (selectedIllness === 'Choose the mental illness') return;

    fetch(`/get_info?illness=${selectedIllness}`)
        .then(response => response.json())
        .then(data => {
            const articlesContainer = document.getElementById('articles');
            const exercisesContainer = document.getElementById('exercises');
            const professionalsContainer = document.getElementById('professionals');

            // Clear previous content
            articlesContainer.innerHTML = '';
            exercisesContainer.innerHTML = '';
            professionalsContainer.innerHTML = '';

            // Display fetched data
            articlesContainer.innerHTML = `<h3>Articles:</h3><a href="${data.article}" target="_blank">${data.article}</a>`;
            exercisesContainer.innerHTML = `<h3>Exercises:</h3><pre>${data.exercises}</pre>`;
            professionalsContainer.innerHTML = `<h3>Professionals:</h3><ul>${data.professionals.map(pro => {
                const name = pro["Name: "];
                const specialization = pro["Specialization: "];
                const clinic = pro["Clinic: "];
                return `<li>${name} - ${specialization} - ${clinic}</li>`;
            }).join('')}</ul>`;
        });
}

function typeEffect(element, text) {
    let index = 0;
    function typing() {
        if (index < text.length) {
            element.append(text.charAt(index));
            index++;
            setTimeout(typing, 50); // Adjust the typing speed here
        }
    }
    typing();
}
