const startButton = document.getElementById("start-record-btn");
const resultText = document.getElementById("result-text");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.continuous = false;
recognition.interimResults = false;

startButton.addEventListener("click", () => {
    recognition.start();
});

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    resultText.value = transcript;
    recognition.stop();
};

recognition.onerror = (event) => {
    console.error(event.error);
};
