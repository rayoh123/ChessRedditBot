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
url_express = '(https://i.)(imgur.com/|redd.it/)(\w+)(.png|.jpg)'
incomplete_imgur_url = '(https://imgur.com\/)(\w+)'
title_express = '((([Bb]lack|[Ww]hite) to )|(for ([Bb]lack|[Ww]hite))|(([Bb]lack|[Ww]hite) win))'
white_express = '(([Ww]hite to )|(for [Ww]hite)|([Ww]hite win))'
turn = ''
image_url = ''


while True:
    for submission in reddit_instance.subreddit('chess').new(limit=300):
        # 1). Checks if the submission has not already been commented on by
        # the program.
        # 2). Checks the submission's title to see if the post is a
        # puzzle
        # 3). Checks for a proper url to the chess position's image
        # for both link posts and text posts
        if submission.id not in commented          and \
        re.search(title_express, submission.title) and \
        (re.match(incomplete_url, submission.url)  or \
        re.match(url_express, submission.url)      or \
        re.search(url_express, submission.selftext)):            

            # Identifies from the title whose turn it is supposed to be.
            if re.search(white_express, submission.title): turn = 'white'
            else                                         : turn = 'black'

            # Pulls the chessboard image's url either from the submission's url
            # or the submission's body of text using a regular expression.
            #
            # If the url is an imgur url that is incomplete (isn't a link
            # to the image itself), the url is modified and a '.png' is added
            # to the end of it to make it a direct link to the image.
            if re.match(incomplete_imgur_url, submission.url): image_url = submission.url[:8] + 'i.' + submission.url[8:] + '.png'
            elif re.match(url_express, submission.url)       : image_url = submission.url 
            elif re.search(url_express, submission.selftext) : image_url = re.search(url_express, submission.selftext).group(0)
                

            try:
                # This try clause catches two possible exceptions:
                # 1). If the computer cannot read a FEN at all from
                # the chess position.
                # 2). If the FEN the computer produces is of an illegal
                # position.
                #
                # The user will be notified by the grab_fen function if
                # there is no chessboard detected. 
                fen = helpers.grab_fen(image_url, turn)
                player, advantage, comment = helpers.grab_line(fen, turn)
            except:
                # If an exception is caught, the user is notified of what the
                # failed Reddit submission was and the submission ID is noted
                # in the txt file so it is not processed again by the bot.
                print("Just skipped this one: ", submission.url, '\n')
                with open('commented.txt', 'a') as f:
                    f.write(submission.id + '\n')
                continue
                

            # Commenting below the Reddit submission.
            if type(advantage) == float:
                submission.reply(f"I'm a bot and I solved it! {player} has an advantage of >!{advantage} pawns!<. The best continuation is: {comment}")
            else:
                submission.reply(f"I'm a bot and I solved it! {player} has an advantage of >!{advantage}!<. The best continuation is: {comment}")

            # Notifying the user of the successful comment.
            print("Just solved this one: ", submission.url, '\n')

            # Noting the submission's ID so it is not processed
            # by the bot again.
            commented.append(submission.id)
            with open('commented.txt', 'a') as f:
                f.write(submission.id + '\n')


    # Posts containing chess puzzles are not made that often
    # in the subreddit so a wait of 20 minutes is implemented
    # before each batch of searches.
    time.sleep(1200)
        
