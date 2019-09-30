# ChessRedditBot
A bot that looks for chess puzzles posted on reddit.com/r/chess and comments the solutions to them. One of the folders, "tensorflow_chessbot-chessfenbot", which is necessary to run this bot, was provided by Sameer Ansari at https://github.com/Elucidation/tensorflow_chessbot

Example of bot in operation: https://www.reddit.com/r/chess/comments/db6m8h/came_across_this_position_in_a_5_minute_game/f1yurhy/

To create your own ChessRedditBot:

1). Download all these files and put them in the same directory

2). Download Stockfish from https://stockfishchess.org/download/ under "Engine Binaries"
    and put the .exe file in the same directory as the other files.
    
3). Download all the files from the chessfenbot branch of tensorflow_chessbot, located here: https://github.com/Elucidation/tensorflow_chessbot/tree/chessfenbot and put the 
    downloaded folder containing the files in the same directory as the other files.

4). Download Tensorflow and SciPy using pip3.
    
5). Create an app on your Reddit account and put the information in "details.py".

6). Change the filepath in to the "grabfen" function in " helpers.py" to the filepath to the 
    chessfenbot folder as it appears on your computer.
    
7). Run "script.py".

NOTE: This program may not run on versions of python above 3.7.1
