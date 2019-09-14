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


### BODY OF THE PROGRAM ###
target_id = []
url_express = '(https://i.)(imgur.com/|redd.it/)'
title_express = '(([Bb]lack|[Ww]hite) to )'
white_express = '([Ww]hite to )'
turn = ''

while True:
    for submission in reddit_instance.subreddit('chess').hot(limit=300):
        # 1). Checks if the submission has not already been commented on by
        # the program.
        # 2). Checks the submission's title to see if the post is a
        # puzzle
        # 3). Checks to see that the submission's body is empty to ensure
        # it is a link-post and not a text-post.
        # 4). Makes sure the submission's link is an image.
        if submission.id not in commented          and \
        re.search(title_express, submission.title) and \
        submission.selftext==""                    and \
        re.match(url_express, submission.url):
            
            # Identifies from the title whose turn it is supposed to be.
            if re.search(white_express, submission.title):
                turn = 'white'
            else:
                turn = 'black'

            # This try clause catches two possible exceptions:
            # 1). If the computer cannot read a FEN at all from
            # the chess position.
            # 2). If the FEN the computer produces is of an illegal
            # position.
            try:
                fen = helpers.grab_fen(submission.url, turn)
                player, advantage, comment = helpers.grab_line(fen, turn)
            except:
                # If an exception is caught, the user is notified of what the
                # failed Reddit submission was and the submission ID is noted
                # in the txt file so it is not processed again by the bot.
                print("Just skipped this one: ", submission.url)
                with open('commented.txt', 'a') as f:
                    f.write(submission.id + '\n')
                continue

            # Commenting below the Reddit submission.
            if type(advantage) == float:
                submission.reply(f"I'm a bot and I solved it! {player} has an advantage of >!{advantage} pawns!<. The best continuation is: {comment}")
            else:
                submission.reply(f"I'm a bot and I solved it! {player} has an advantage of >!{advantage}!<. The best continuation is: {comment}")

            # Notifying the user of the successful comment.
            print("Just solved this one: ", submission.url)

            # Noting the submission's ID so it is not processed
            # by the bot again.
            commented.append(submission.id)
            with open('commented.txt', 'a') as f:
                f.write(submission.id + '\n')


    # Posts containing chess puzzles are not made that often
    # in the subreddit so a wait of 20 minutes is implemented
    # before each batch of searches.
    time.sleep(1200)
        
