import urllib.request
from PIL import ImageFile
import chess.engine
import subprocess
import re

def grab_fen(url: str, turn: str) -> str:
    '''
    This function takes a string representing a url
    and another string identifying whether it is white's or black's turn.
    It then outputs a string representing the FEN of the chess
    position in the image the url leads to.
    '''
    
    complete_string = "cd C:\\YOUR COMPLETED FILE PATH TO 'CHESS BOT' HERE\\Chess Bot\\tensorflow_chessbot-chessfenbot && tensorflow_chessbot.py --url %s" % (url)
    r = str(subprocess.check_output(complete_string, shell=True, timeout=5))
    if float(re.search('(\d{2,3})(.\d%)', r).group(0)[:-1]) < 60.0:
        print("here", float(re.search('(\d{2,3})(.\d%)', r).group(0)[:-1]))
        raise AssertionError
    begin_idx = r.index('Predicted FEN: ')
    end_idx = r.index('\\r\\nFinal Certainty')

    if turn == 'white':
        return r[(begin_idx+15):end_idx] + ' w '
    else:
        return r[(begin_idx+15):end_idx][::-1] + ' b '
        
    


def grab_line(fen: str, turn: str) -> str:
    '''
    This function takes a FEN and a string identifying whether it is white's or
    black's turn. It then outputs whether white or black has the advantage
    in the chess position represented by the FEN, the advantage, and the best
    continuation as judged by Stockfish 10.
    '''
    
    engine = chess.engine.SimpleEngine.popen_uci("stockfish_10_x64.exe")
    score = ''
    line = ''
    with engine.analysis(chess.Board(fen)) as analysis:
        for info in analysis:
            # Unusual stop condition.
            if info.get("hashfull", 0) > 900:
                advantage = str(int(str(info.get('score').white())[1:])/100)
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
                    
                line = [str(move)[-6:] for move in info.get("pv")]
                break
    engine.quit()
    final_line = ''
    i = 1
    if turn == 'white':
        for j in range(0, len(line[:20]), 2):
            try:
                final_line += '\n\n>!%d. %s ' % (i, line[j])
                final_line += '%s!<'      % (line[j+1])
            except:
                break
            i += 1
        if final_line[-2:] != '!<': final_line += '!<'
        
    else:
        final_line += '\n\n>!1. ... '
        for j in range(0, len(line[:20]), 2):
            try:
                final_line += '%s!<\n\n'       % (line[j])
                i += 1
                final_line += '>!%d. %s '  % (i, line[j+1])
            except:
                break
        if final_line[-4:] != '!<\n\n': final_line += '!<'
        
    return score, advantage, final_line




















    
    

    
    
    
    
























    
    
    
    
