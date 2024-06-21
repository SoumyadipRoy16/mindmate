# MindMate: Personalized Mental Health Support

MindMate is an AI-driven web application designed to provide personalized mental health support using natural language processing and machine learning techniques. The application leverages the BERT model for intent classification and recommendation systems to suggest resources such as articles, exercises, and connections to mental health professionals based on user inputs.

![MindMate Demo](mindmate_logo.png)

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Setup](#setup)
  - [Clone the Repository](#clone-the-repository)
  - [Install Dependencies](#install-dependencies)
  - [Set up MongoDB](#set-up-mongodb)
  - [Run the Application](#run-the-application)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication**: Allows users to register and log in securely.
- **Dashboard**: Personalized user dashboard for managing profile information and preferences.
- **Chatbot Interface**: Interactive chat interface for users to communicate and receive mental health recommendations.
- **Voice Input**: Capability to process voice inputs using speech recognition.
- **Recommendation System**: Recommends articles, exercises, and mental health professionals based on user queries and profile.
- **Data Persistence**: Uses MongoDB for storing user data, preferences, and session information.

## Technologies

- **Python**: Flask web framework, PyTorch for deep learning.
- **Transformers**: BERT model for natural language understanding.
- **Flask-PyMongo**: Integration with MongoDB for database operations.
- **Beautiful Soup**: HTML parsing library.
- **SpeechRecognition**: Library for speech-to-text conversion.
- **HTML/CSS**: Frontend design and layout using Bootstrap.

## Setup

### Clone the Repository

```bash
git clone https://github.com/your_username/mindmate.git
cd mindmate
```
```bash
pip install -r requirements.txt
```
## Set up MongoDB
**Install MongoDB and start the service.**
**Create a database named mindmate and collections as required (users, articles, exercises, professionals).**

## Run the Application
```bash
python app.py
```
**Navigate to http://localhost:5000 in your web browser**

## Usage
- **Register/Login**: Create an account or log in to access personalized features.
- **Dashboard**: Update profile information and preferences.
- **Chatbot**: Interact with the chatbot to receive mental health recommendations.
- **Voice Input**: Click the microphone icon to provide voice inputs for analysis.
- **Articles/Exercises/Professionals**: Explore recommended resources based on your needs.

## Contributing
**Contributions are welcome! If you have suggestions or improvements, please fork the repository and create a pull request. For major changes, please open an issue first to discuss the proposed changes.**

## License
**This project is licensed under the MIT License - see the [LICENSE] file for details.**
