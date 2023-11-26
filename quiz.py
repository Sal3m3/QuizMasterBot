from pyexpat import model
from dotenv import load_dotenv
import os
import telebot
from bs4 import BeautifulSoup
import requests
import openai
import sqlite3
import re

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TEMPERATURE = 0.2
MAX_PROMPT_SIZE = 4096
MAX_TOKENS = 100
NUMBER_OF_QUESTIONS = 7


model_id = 'gpt-3.5-turbo'

# Set instance of telegram bot and connect to database
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
conn = sqlite3.connect('users.db', check_same_thread=False)


# Show single question with it's options to user 
def display_question(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    cursor = conn.cursor()
    result = cursor.execute("SELECT question, option_1, option_2, option_3, option_4, answer, id FROM questions_list WHERE user_id=? AND completed = 0", (message.chat.id,))
    question = result.fetchone()
    print(question)
    
    correct = question[5].split(" ")[1][0]
    button1 = telebot.types.InlineKeyboardButton("\U00000031\U0000fe0f\U000020e3", callback_data='1 {0} {1}'.format(correct, question[6]))
    button2 = telebot.types.InlineKeyboardButton("\U00000032\U0000fe0f\U000020e3", callback_data='2 {0} {1}'.format(correct, question[6]))
    button3 = telebot.types.InlineKeyboardButton("\U00000033\U0000fe0f\U000020e3", callback_data='3 {0} {1}'.format(correct, question[6]))
    button4 = telebot.types.InlineKeyboardButton("\U00000034\U0000fe0f\U000020e3", callback_data='4 {0} {1}'.format(correct, question[6]))
    keyboard.row(button1, button2)
    keyboard.row(button3, button4)
    
    opt1 = question[1].replace("1:", "\U00000031\U0000fe0f\U000020e3")
    opt2 = question[2].replace("2:", "\U00000032\U0000fe0f\U000020e3")
    opt3 = question[3].replace("3:", "\U00000033\U0000fe0f\U000020e3")
    opt4 = question[4].replace("4:", "\U00000034\U0000fe0f\U000020e3")
    
    bot.send_message(message.chat.id, f"""\U00002728 {question[0]}\n {opt1}\n {opt2}\n {opt3}\n {opt4}""",reply_markup=keyboard)

# Handles different inputs from user, including answers for each question
@bot.callback_query_handler(func=lambda call:True)
def handle_callback_query(call):
    cursor = conn.cursor()
    # Handle event when "Stats button is pressed"
    if call.data == "stats":
        result = cursor.execute("SELECT id, cor_ans FROM users ORDER BY cor_ans DESC")
        leaderboard = result.fetchall()
        for i in range (len(leaderboard)):
            if leaderboard[i][0] == call.message.chat.id:
                position = (i + 1)
                result = cursor.execute("SELECT cor_ans, ttl_ans, runs FROM users WHERE id =?", (call.message.chat.id,))
                ans = result.fetchone()
                accuracy = round(ans[0]/ans[1] * 100)
                bot.send_message(call.message.chat.id, f"""\U0001f4cbSTATISTICS\U0001f4cb\nTotal runs: {ans[2]}\nAverage accuracy: {accuracy}%\nGlobal position: {position} place""")
                break
        else:
            bot.send_message(call.message.chat.id, "\U000026d4ERROR! Please register via /start command.")

    # Handle event when "Delete Acc" button is pressed   
    elif call.data == "delete":
        cursor.execute("DELETE FROM users WHERE id=?", (call.message.chat.id,))
        cursor.execute("DELETE FROM questions_list WHERE user_id=?", (call.message.chat.id,))
        bot.send_message(call.message.chat.id, "\U0000267bYour account has been deleted successfully. If you want to continue you are welcome to register via /start command. Otherwise good luck!\U0001f44b")
    
    # If none of previous events occured - handle answer from user
    else:
        temp = call.data.split(" ")
        result = cursor.execute("SELECT question, answer FROM questions_list WHERE id=?", (temp[2],))
        cur_question = result.fetchone()
        qst = cur_question[0] 
        correct = cur_question[1].split(":")[1]
        if temp[0] == temp[1]:
            
            bot.send_message(call.message.chat.id, f"{qst}\n\U0001f7e2 {correct}")
            cursor.execute("UPDATE users SET current_correct = current_correct + 1, current_total = current_total + 1 WHERE id = ?", (call.message.chat.id,))
            conn.commit()
        else:
            bot.send_message(call.message.chat.id, f"{qst}\n\U0001f534 The right answer is: {correct}")
            cursor.execute("UPDATE users SET current_total = current_total + 1 WHERE id = ?", (call.message.chat.id,))
            conn.commit()

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        cursor.execute("UPDATE questions_list SET completed =1 WHERE id=?", (temp[2],))
        conn.commit()

        # If questions remained - move to the next question
        result = cursor.execute("SELECT COUNT(id) FROM questions_list WHERE completed = 0 AND user_id=?",(call.message.chat.id,))
        q_count = result.fetchone()[0]
        
        if q_count > 0:
            display_question(call.message)
        else:
            result = cursor.execute("SELECT current_correct, current_total FROM users WHERE id = ?", (call.message.chat.id,))
            run_summary = result.fetchone()
            awesome = {6, 7}
            good = {4, 5, 6}
            bad = {1, 2, 3}
            if run_summary[0] in awesome:
                bot.send_message(call.message.chat.id, f"""\U0001f389 Congratulations! Your score is {run_summary[0]} out of {run_summary[1]}.\nOutstanding work! \U0001f680""")
            elif run_summary[0] in good:
                bot.send_message(call.message.chat.id, f"""\U0001f44d Nice done! Your score is {run_summary[0]} out of {run_summary[1]}.\nKeep up the good work! \U0001f525""")
            elif run_summary[0] in bad:
                bot.send_message(call.message.chat.id, f"""\U0001f44f Great effort! You scored {run_summary[0]} out of {run_summary[1]}!\nDon't worry if you didn't do as well as you hoped, keep practicing and you'll get better! \U0001f4aa""")
            
            # End run by cleaning current values and updating values for total answers from user
            cursor.execute("UPDATE users SET cor_ans = cor_ans + current_correct, ttl_ans = ttl_ans + current_total, current_correct = 0, current_total = 0, runs = runs + 1 WHERE id = ?", (call.message.chat.id,))
            conn.commit()
            keyboard = telebot.types.InlineKeyboardMarkup()
            stats_button = telebot.types.InlineKeyboardButton("\U0001f4caStatistics", callback_data="stats")
            delete_button = telebot.types.InlineKeyboardButton("\U0001f5d1Delete Acc", callback_data="delete")
            keyboard.add(stats_button, delete_button)
            bot.send_message(call.message.chat.id, "\U0001f52eTo continue just send me another URL. Also you can visit your stats or delete account.", reply_markup=keyboard)

    
# Handle '/start' command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id=?", (message.chat.id,))
    username = cursor.fetchone()
    if username:
        bot.reply_to(message, f"""\U0001F44B Hello, {username[0]}! I'm your learning bot. Send me a URL and I will generate trivia questions for you!""")
    else:
        username = message.from_user.username
        if not username:
            username = message.from_user.first_name
        if not username:
            username="Anonymous"
        cursor.execute("INSERT INTO users (id, username) VALUES (?, ?)", (message.chat.id, username))
        conn.commit()
        bot.reply_to(message, f"""\U0001F44B Hello, {username[0]}! I'm your learning bot. Send me a URL and I will generate trivia questions for you!""")

    
# Handle URLs sent by user
@bot.message_handler(content_types=['text'])
def handle_input(message):

    # Check if user has uncompleted runs
    cursor = conn.cursor()
    cursor.execute("SELECT current_correct, current_total FROM users WHERE id=?", (message.chat.id,))
    result = cursor.fetchall()
    if result[0] != 0 or result[1] != 0:
        cursor.execute("UPDATE users SET current_correct = 0, current_total = 0")
        cursor.execute("DELETE FROM questions_list WHERE id=? AND completed=0", (message.chat.id,))
        conn.commit()
    url = ""

    # Check if input is a URL
    if message is not None:
        if message.text.startswith('http'):
            url = message.text
        elif message.text.find("http") != -1:
            url = message.text[message.text.find("http"):]

    # Print an error message if URL is not obtained     
    if not url:
        bot.send_message(message.chat.id, "\U0001f6d1ERROR. Please provide valid URL.")
    else:
        # Extract text from URL
        bot.reply_to(message, "\U0001f551Okay, let's figure this out...")
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'html.parser')
        text_list = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 25:
                text_list.append(text)
        
        combined_text= " ".join(text_list)
        combined_text = re.sub(r"[\[\d+\]]", "", combined_text)
        print(combined_text)
        conversation = []
        print ("LENGTH: "+str(len(combined_text)))
        if len(combined_text) > 13999:
            truncated_text = combined_text[:13999]
        else:
            truncated_text = combined_text

    # Craft prompt to openAI API
        conversation.append({'role': 'system', 'content': f"""Generate {NUMBER_OF_QUESTIONS} trivia-like questions. 
    Start your question with the word "Question:" followed by a brief, descriptive statement that summarizes the topic of the question.
    Include a list of answer options, formatted as "Option 1:", "Option 2:", etc.
    Make sure that the correct answer is among the list of answer options, and clearly indicate which answer is correct.
    End your question with "Correct answer:" followed by the correct answer option.
    For example:

    Question: In what year was the first iPhone released?
    Option 1: 2005
    Option 2: 2006
    Option 3: 2007
    Option 4: 2009
    Correct answer: Option 3: 2007

    Question: Who is the author of "The Catcher in the Rye"?
    Option 1: Ernest Hemingway
    Option 2: J.D. Salinger
    Option 3: F. Scott Fitzgerald
    Option 4: Stephen King
    Correct answer: Option 2: J.D. Salinger\n{truncated_text}"""})
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=conversation,
            temperature=TEMPERATURE,
        )
        print(response,"\n-----------\n")
        print(response["choices"][0]["message"]["content"])
        questions = response.choices[0]["message"]["content"]
    
        # Parse response from API and save all questions to database
        cursor = conn.cursor()
        for para in questions.split('\n\n'):
            if para.startswith('Question:'):
                question_text = para.split('\n')[0].lstrip('Question: ')
                options = [option.lstrip('Option ') for option in para.split('\n')[1:-1]]
                correct_answer = para.split('\n')[-1].lstrip('Correct answer: ')
                #questions_list.append({'question': question_text, 'options': options, 'answer': correct_answer})
                cursor.execute("INSERT INTO questions_list (user_id, question, option_1, option_2, option_3, option_4, answer) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (message.chat.id, question_text, options[0], options[1], options[2], options[3], correct_answer))
                conn.commit()
        
        display_question(message)
        
bot.polling()

