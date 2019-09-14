import chess.engine
import subprocess
import re

def reverse_fen(fen: str) -> str:
    '''
    This function takes a FEN and outputs the reverse
    of the FEN.
    '''
    
    # If there is a letter at the end of the FEN denoting
    # whose turn it is, that letter is kept at the end and
    # everything before it is reversed.
    if fen[-3:] in (' w ', ' b '):
        return fen[:-3][::-1] + fen[-3:]


    # Otherwise, the whole string is reversed. 
    return fen[::-1]

def is_flipped(fen: str, turn: str) -> bool:
    '''
    This function takes a FEN and a string identifying
    whether it is white's or black's turn and outputs a
    boolean representing whether the FEN displays the player
    whose turn it is at the bottom of the board.
    '''
    
    # Find the fourth instance of / in the FEN, as that denotes
    # the horizontal middle line of the chess board dividing
    # the upper four rows and the bottom four rows.
    middle_idx = [i for i, n in enumerate(fen) if n == '/'][4]
    first_upper = 0
    second_upper = 0


    # Now, find how many White pieces (uppercase letters) there
    # are in the top four rows, and how many White pieces there
    # are in the bottom four rows.
    for i in range(middle_idx):
        if fen[i].isupper():
            first_upper += 1
    for i in range(middle_idx, len(fen)):
        if fen[i].isupper():
            second_upper += 1


    if first_upper<second_upper:
        
        # If there are more White pieces in the bottom four rows and
        # it is White's turn, return False (the board is not flipped
        # and White is indeed at the bottom).
        #
        # If there are more White pieces in the bottom four rows and
        # it is Black's turn, return True (the board is flipped 
        # and Black is not at the bottom).
        if turn == 'white':
            return False
        else:
            return True
    elif first_upper>second_upper:
        
        # If there are more White pieces in the top four rows and
        # it is White's turn, return True (the board is flipped 
        # and White is not at the bottom).
        #
        # If there are more White pieces in the top four rows and
        # it is Black's turn, return False (the board is flipped 
        # and Black is indeed at the bottom).
        if turn == 'white':
            return True
        else:
            return False
    else:
        # If there are an equal number of White pieces in the top and
        # bottom four rows of the board, return False (we will assume
        # that the board is not flipped). 
        return False


def grab_fen(url: str, turn: str) -> str:
    '''
    This function takes a url and a string identifying
    whether is white's or black's turn. It then outputs
    a string representing the FEN of the chess position
    in the image the url leads to.
    '''
    # The below string is a command that is entered into command prompt
    # and the output is recorded in the variable 'r'. 
    complete_string = "cd C:\\Users\\Raymond\\Desktop\\Chess Bot\\tensorflow_chessbot-chessfenbot && tensorflow_chessbot.py --url %s" % (url)
    r = str(subprocess.check_output(complete_string, shell=True, timeout=5))


    # The anticipated accuracy of the FEN produced is captured by the
    # below regular expression and is only accepted if 70% or over.
    # Otherwise, an Assertion Error is raised.
    if float(re.search('(\d{2,3})(.\d%)', r).group(0)[:-1]) < 70.0:
        print("The image linked below isn't clear to me", float(re.search('(\d{2,3})(.\d%)', r).group(0)[:-1]))
        raise AssertionError


    # The beginning and ending indexes of the FEN string in 'r' is
    # determined. 
    begin_idx = r.index('Predicted FEN: ') + 15
    end_idx = r.index('\\r\\nFinal Certainty')


    # Stockfish can only analyze positions accurately if White is at the
    # bottom of the board. So, we will use the function 'is_flipped' to
    # determine if White is at the bottom.
    if turn == 'white':
        # If it is White's turn and White is not at the bottom of the
        # board, the reverse of the FEN is returned. Otherwise, the
        # FEN is returned as normal.
        if is_flipped(r[begin_idx:end_idx], 'white'):
            return reverse_fen(r[begin_idx:end_idx]) + ' w '
        return r[begin_idx:end_idx] + ' w '
    
    else:
        # If it is Black's turn and White is at the bottom of the
        # board, the FEN is returned as normal. Otherwise, the
        # reverse of the FEN is returned.
        if is_flipped(r[begin_idx:end_idx], 'black'):
            return r[begin_idx:end_idx] + ' b '
        return reverse_fen(r[begin_idx:end_idx]) + ' b '
        



def grab_line(fen: str, turn: str) -> str or float:
    '''
    This function takes a FEN and a string identifying
    whether it is white's or black's turn. It then outputs
    whether white or black has the advantage in the chess
    position represented by the FEN, the advantage, and the
    best continuation as judged by Stockfish 10.
    '''
    # The engine used is Stockfish 10
    engine = chess.engine.SimpleEngine.popen_uci("stockfish_10_x64.exe")
    player = ''
    line = ''


    # Stockfish analyzes the FEN at a depth of 20 nodes and stores the
    # analysis in an object named 'analysis'
    with engine.analysis(chess.Board(fen), chess.engine.Limit(depth=20)) as analysis:


        # Retrieving the best continuation line of moves from 'analysis'.
        for info in analysis:
            line = info.get('pv')


        # 'advantage' stores the advantage in number of pawns from
        # White's perspective.
        advantage = int(str(info.get('score').white())[1:])/100
        if str(info.get('score').white())[0] == '+':
            # If White has the advantage in the FEN...
            player = 'White'
        elif str(info.get('score').white())[0] == '-':
            # If Black has the advantage in the FEN...
            player = 'Black'
        elif str(info.get('score').white())[0] == '#' and str(info.get('score').white())[1] == '+':
            # If White has a checkmating advantage in the FEN...
            player = 'White'
            advantage = 'checkmate in %d' % (abs(int(advantage*100)))
        elif str(info.get('score').white())[0] == '#' and str(info.get('score').white())[1] == '-':
            # If Black has a checkmating advantage in the FEN...
            player = 'Black'
            advantage = 'checkmate in %d' % (abs(int(advantage*100)))

    engine.quit()
    
    # The best continuation line is split up by move
    line = [move for move in re.split('( )(?=\d)', chess.Board(fen).variation_san(line)) if move != ' ']
    

    # The comment to be posted is constructed, with spoiler tags and
    # new lines.
    comment = ''
    for move in line[:3]:
        comment += f"\n\n>!{move}!<"
        
    return player, advantage, comment

