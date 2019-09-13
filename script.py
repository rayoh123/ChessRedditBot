###########################################################################################
###   The tensorflow_chessbot-chessfenbot folder used in this program
###   is from Sameer Ansari at https://github.com/Elucidation/tensorflow_chessbot
###   
###

import time
import praw
import details
import re
import helpers

###  LOGGING INTO REDDIT  ###
reddit_instance = praw.Reddit(user_agent=        'raymond_ouyang_1',
                              client_id=         details.client_id,
                              client_secret=     details.secret,
                              password=          details.password,
                              username=          details.username)


### OPENING/CREATING COMMENTED FILE AND RETRIEVING ID'S ###
f = open('commented.txt', 'r')
commented = list(filter(None, f.read().split('\n')))
f.close()


### COLLECTING TARGET POSTS ###
target_id = []
url_express = '(https://i.)(imgur.com/|redd.it/)'
title_express = '(([Bb]lack|[Ww]hite) to )'
white_express = '([Ww]hite to )'
turn = ''
winner = ''

while True:
    for submission in reddit_instance.subreddit('chess').new(limit=300):
        
        if submission.id not in commented       and \
        re.search(title_express, submission.title)    and \
        submission.selftext==""                 and \
        re.match(url_express, submission.url):
            
            if re.search(white_express, submission.title):
                turn = 'white'
            else:
                turn = 'black'
                
            try:
                fen = helpers.grab_fen(submission.url, turn)
                score, advantage, line = helpers.grab_line(fen, turn)
            except:
                print("Just skipped this one: ", submission.url)
                with open('commented.txt', 'a') as f:
                    f.write(submission.id + '\n')
                continue

            if type(advantage) == float:
                submission.reply(f"I'm a bot and I solved it! >!{score}!< has an advantage of >!{advantage} pawns!<. The best continuation is: {line}")
            else:
                submission.reply(f"I'm a bot and I solved it! >!{score}!< has an advantage of >!{advantage}!<. The best continuation is: {line}")
                
            print("Just solved this one: ", submission.url)
            
            commented.append(submission.id)
            with open('commented.txt', 'a') as f:
                f.write(submission.id + '\n')

                
    time.sleep(1200)
        
