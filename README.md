# QuizMasterBot
#### Video Demo:  https://youtu.be/2vON-OfPDgM


# Project Description

Have you ever encountered a problem where you are trying to learn something new, but struggling to keep in memory all miscellaneous details? This program aims at that issue. The purpose of this bot is to create an online learning tool that will help users to interact with text on the website. This project is a Python-based chatbot that provides a quiz-like experience for users. The chatbot interacts and registers the user via /start command, then it waits until the user sends a message containing URL. When URL is obtained, paragraph text is extracted from the page and then inserted into the OpenAI API prompt. When a response from the API is obtained, it parses the result and inserts each particular question with supposed answering options into the questions_list table in the database. Then, for each item in the questions_list table function display_question() is being called. It shows a user message containing questions and then 4 buttons representing each answering option (only one of them is correct). The decorated function handle_callback_query() handles events when buttons are pressed, depending on correctness of the answer, users will encounter different types of responses and also different results will be inserted into the "users" table. Each run is supposed to consist of 7 questions. At the end of each run, users will see a different type of message, depending on the results of the current run. Also, at the end of each run, two buttons additionally occur: "Statistics" and "Delete account". The first one will show the user's current number of completed runs, average accuracy and position in the global table. The second one lets a user to delete all his data from the database, which includes id, username, scores, and a list of answered questions. Users are free to start a new run at every moment of the interaction just by sending a new URL to the bot, but that means that previous run progress will be deleted and the run will not be marked as completed.It utilizes the Telegram Bot API for communication and UI, BeautifulSoup to parse contents of the web-page, OpenAI API to process provided text and generate questions, a SQLite database for storing user information and quiz data.

## Features

- User Registration: Users can register with the chatbot using the `/start` command. Their information, such as chat ID and username, is stored in the SQLite database.
- Input Evaluation: The chatbot takes message as input, if message contains URL - 
- Quiz Interaction: The chatbot presents questions to registered users and receives their answers.
- Answer Evaluation: The chatbot evaluates user answers and provides feedback on whether they are correct or incorrect.
- Score Tracking: The chatbot keeps track of each user's correct and total answers, providing them with their current score after each set of questions.
- Multiple Sets of Questions: The chatbot retrieves sets of questions from the database for users to answer. Each set typically consists of five questions.
- Database Integration: The chatbot utilizes a SQLite database to store user information, quiz questions, and user performance data.

## Dependencies

The following dependencies are required to run the chatbot:

- Python (version 3.0 or higher)
- Python-Telegram-Bot library
- SQLite3
- BeautifulSoup
- OpenAI library

## .env
To run this program, it is required to set up envioramental variables. The file containing those should be named ".env" and located in the program's main directory. It should be structured like this:
OPENAI_API_KEY=(your openai token)
TELEGRAM_BOT_TOKEN=(your telegram API token)


## Setup and Usage

1. Clone the repository to your local machine.
2. Install the required dependencies.
3. Set up a Telegram Bot and obtain the API token.
4. Create openAI account and obtain API token.
5. Create the .env file with your Telegram Bot API token and openAI API token database information.
6. Run the Python script to start the chatbot.


## Contributors

- [Ivan Hudz](https://github.com/me50/Sal3m3)

## Acknowledgments

- The Telegram Bot API for providing the means to interact with users through the Telegram messaging platform.
- OpenAI API for providing powerful tool to interact with the data
- SQLite for the lightweight and embedded database management system used in the project.

