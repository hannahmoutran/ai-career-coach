import re
import openai
from time import time, sleep
from halo import Halo
import textwrap
import yaml
import pyperclip
import os

def input_with_commands(prompt):
    """
    Get input from the user, with support for fetching content from the clipboard and loading from a file.
    """
    text = input(prompt).strip()

    if text == "help":
        print("Commands:")
        print("  Type:/paste, then press enter to paste in a text file, such as the job listing or your resume.")
        print("  Type:/load and type the name of your file to load content from a file that is saved in the same folder as this program")
        return input_with_commands(prompt)
    
    if text == "/paste":
        text = pyperclip.paste().strip()
        print(text)
        return text
    
    if text.startswith("/load "):
        filename = text.split(" ", 1)[1]
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read().strip()
                print(content)
                return content
        else:
            print(f"File '{filename}' not found.")
            return input_with_commands(prompt)
    
    return text


###     file operations


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


###     API functions


def chatbot(conversation, model="gpt-3.5-turbo-16k", temperature=0, max_tokens=8000):
    max_retry = 7
    retry = 0
    while True:
        try:
            spinner = Halo(text='Thinking...', spinner='dots')
            spinner.start()
            
            response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
            text = response['choices'][0]['message']['content']

            spinner.stop()
            
            return text, response['usage']['total_tokens']
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            exit(5)


def chat_print(text):
    formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in text.split('\n')]
    formatted_text = '\n'.join(formatted_lines)
    print('\n\n\nCHATBOT:\n\n%s' % formatted_text)


if __name__ == '__main__':
    openai.api_key = open_file('key_openai.txt').strip()
    
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
    user_messages = list()
    all_messages = list()
    print('\n\nTell me about the job you are applying for.\nTo input long texts, type help.\nWhen you are ready to move on to the next step, type DONE.')
    
    ## INTAKE
    
    while True:
        # get user input
        text = input_with_commands('\n\nJob Seeker (remember to type help for long texts) : ').strip()
        if text == 'DONE':
            break
        user_messages.append(text)
        all_messages.append('Job Seeker : %s' % text)
        conversation.append({'role': 'user', 'content': text})
        response, tokens = chatbot(conversation)
        conversation.append({'role': 'assistant', 'content': response})
        all_messages.append('INTAKE: %s' % response)
        print('\n\nCareer Coach Extraordinaire:\n\n%s' % response)
    
    ## NOTES
    
    print('\n\nGenerating Notes')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_02_prepare_notes.md')})
    text_block = '\n\n'.join(all_messages)
    chat_log = '<<BEGIN Job Seeker INTAKE CHAT>>\n\n%s\n\n<<END Job Seeker INTAKE CHAT>>' % text_block
    save_file('logs/log_%s_chat.txt' % time(), chat_log)
    conversation.append({'role': 'user', 'content': chat_log})
    notes, tokens = chatbot(conversation)
    save_file('logs/log_%s_notes.txt' % time(), notes)
    print('\n\nNotes from conversation:\n\n%s' % notes)
    
    ## GENERATING COVER LETTER

    print('\n\nGenerating Cover Letter...Remember to always edit before sending!')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_03_writer.md')})
    conversation.append({'role': 'user', 'content': notes})
    cover_letter, tokens = chatbot(conversation)
    save_file('logs/log_%s_writer.txt' % time(), cover_letter)
    print('\n\nCover Letter:\n\n%s' % cover_letter)

    ## INTERVIEW PREP

    print('\n\nNotes on Preparing for the Interview')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_04_interviewprep.md')})
    conversation.append({'role': 'user', 'content': notes})
    interview_notes, tokens = chatbot(conversation)
    save_file('logs/log_%s_interviewprep.txt' % time(), interview_notes)
    print('\n\nHow to Prep for the Interview:\n\n%s' % interview_notes)

    ## ONLINE PRESENCE AND RELATED JOBS

    print('\n\nTips for Improving Online Presence and Searching for Related Jobs')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_05_careercoach.md')})
    conversation.append({'role': 'user', 'content': notes})
    career_recommendations, tokens = chatbot(conversation)
    save_file('logs/log_%s_careercoach.txt' % time(), career_recommendations)
    print('\n\nOnline Presence and Related Jobs:\n\n%s' % career_recommendations)
