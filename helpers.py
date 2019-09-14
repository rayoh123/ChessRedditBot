import chess.engine
import subprocess
import re

def reverse_fen(fen: str) -> str:
    '''
    This function takes a FEN and outputs the reverse
    of the FEN.
    '''
    
    if fen[-3:] in (' w ', ' b '):
        return fen[:-3][::-1] + fen[-3:]
    return fen[::-1]

def is_flipped(fen: str, turn: str) -> bool:
    '''
    This function takes a FEN and a string identifying
    whether it is white's or black's turn and outputs a
    boolean representing whether the FEN displays the player
    whose turn it is at the bottom of the board.
    '''

    middle_idx = [i for i, n in enumerate(fen) if n == '/'][4]
    first_upper = 0
    second_upper = 0

    for i in range(middle_idx):
        if fen[i].isupper():
            first_upper += 1
    for i in range(middle_idx, len(fen)):
        if fen[i].isupper():
            second_upper += 1

    if first_upper<second_upper:
        if turn == 'white':
            return False
        else:
            return True
    elif first_upper>second_upper:
        if turn == 'white':
            return True
        else:
            return False
    else:
        return False


def grab_fen(url: str, turn: str) -> str:
    '''
    This function takes a url and a string identifying
    whether is white's or black's turn. It then outputs
    a string representing the FEN of the chess position
    in the image the url leads to.
    '''
    
    complete_string = "cd C:\\Users\\Raymond\\Desktop\\Chess Bot\\tensorflow_chessbot-chessfenbot && tensorflow_chessbot.py --url %s" % (url)
    r = str(subprocess.check_output(complete_string, shell=True, timeout=5))
    if float(re.search('(\d{2,3})(.\d%)', r).group(0)[:-1]) < 70.0:
        print("The image linked below isn't clear to me", float(re.search('(\d{2,3})(.\d%)', r).group(0)[:-1]))
        raise AssertionError
    begin_idx = r.index('Predicted FEN: ')
    end_idx = r.index('\\r\\nFinal Certainty')

    if turn == 'white':
        
        if is_flipped(r[(begin_idx+15):end_idx], 'white'):
            return reverse_fen(r[(begin_idx+15):end_idx]) + ' w '
        return r[(begin_idx+15):end_idx] + ' w '
    
    else:
        
        if is_flipped(r[(begin_idx+15):end_idx], 'black'):
            return r[(begin_idx+15):end_idx] + ' b '
        return reverse_fen(r[(begin_idx+15):end_idx]) + ' b '
        



def grab_line(fen: str, turn: str) -> str or float:
    '''
    This function takes a FEN and a string identifying
    whether it is white's or black's turn. It then outputs
    whether white or black has the advantage in the chess
    position represented by the FEN, the advantage, and the
    best continuation as judged by Stockfish 10.
    '''

    engine = chess.engine.SimpleEngine.popen_uci("stockfish_10_x64.exe")
    score = ''
    line = ''
    with engine.analysis(chess.Board(fen), chess.engine.Limit(depth=20)) as analysis:
        
        for info in analysis:
            line = info.get('pv')


        advantage = int(str(info.get('score').white())[1:])/100
        if str(info.get('score').white())[0] == '+':
            score = 'White'
        elif str(info.get('score').white())[0] == '-':
            score = 'Black'
        elif str(info.get('score').white())[0] == '#' and str(info.get('score').white())[1] == '+':
            score = 'White'
            advantage = 'checkmate in %d' % (abs(int(advantage*100)))
        elif str(info.get('score').white())[0] == '#' and str(info.get('score').white())[1] == '-':
            score = 'Black'
            advantage = 'checkmate in %d' % (abs(int(advantage*100)))

        
    line = [move for move in re.split('( )(?=\d)', chess.Board(fen).variation_san(line)) if move != ' ']
    engine.quit()


    final_line = ''
    for move in line[:3]:
        final_line += f"\n\n>!{move}!<"
        
    return score, advantage, final_line

