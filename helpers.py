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
    #
    # Then, find whether the White king is in the lower four
    # rows of the board, or in other words, whether White is
    # at the bottom of the board.
    middle_idx = [i for i, n in enumerate(fen) if n == '/'][3]
    white_king_in_lower = False
    if "K" in fen[middle_idx:]:
        white_king_in_lower = True


    # Now, find out if the player whose turn it is is in the bottom
    # four rows of the chess position represented by the FEN.
    if turn == 'white':
        # If it's White's turn and his king is at the bottom
        # of the board, that means the board is not flipped.
        # Otherwise, the board is flipped.
        if white_king_in_lower:
            return False
        return True
    else:
        # If it's Black's turn and the White king is at the
        # bottom of the board, that means the board is
        # flipped. Otherwise, the board is not flipped.
        if white_king_in_lower:
            return True
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
    complete_string = "cd C:\\CHANGE THIS TO YOUR OWN FILE PATH\\ChessRedditBot-master\\tensorflow_chessbot-chessfenbot && tensorflow_chessbot.py --url %s" % (url)
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
    with engine.analysis(chess.Board(fen), chess.engine.Limit(depth=24)) as analysis:


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

