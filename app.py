"""
🌐 오델로 웹 서버 - Flask + SocketIO 실시간 게임
Figma 디자인과 연동되는 웹 인터페이스
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
from othello_game import OthelloBoard, SuperOthelloAI, BLACK, WHITE, EMPTY, Move
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'othello_champion_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# 게임 세션 저장
game_sessions = {}

class GameSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.board = OthelloBoard()
        self.ai = SuperOthelloAI()
        self.current_player = BLACK  # 플레이어가 먼저
        self.game_over = False
        self.winner = None
        self.move_history = []
        
    def to_dict(self):
        """게임 상태를 딕셔너리로 변환"""
        return {
            'board': self.board.board.tolist(),
            'current_player': int(self.current_player),
            'game_over': self.game_over,
            'winner': int(self.winner) if self.winner is not None else None,
            'black_count': int(self.board.count_discs(BLACK)),
            'white_count': int(self.board.count_discs(WHITE)),
            'valid_moves': [(int(m.row), int(m.col)) for m in self.board.get_valid_moves(self.current_player)] if not self.game_over else [],
            'move_history': self.move_history
        }

@app.route('/')
def index():
    """메인 페이지 - 간단한 오델로 게임"""
    return render_template('minimal.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """새 게임 시작"""
    session_id = f"game_{int(time.time())}"
    game_sessions[session_id] = GameSession(session_id)
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'game_state': game_sessions[session_id].to_dict()
    })

@app.route('/api/make_move', methods=['POST'])
def make_move():
    """플레이어가 수를 둠"""
    data = request.json
    session_id = data.get('session_id')
    row = data.get('row')
    col = data.get('col')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Invalid session'})
    
    game = game_sessions[session_id]
    
    if game.game_over:
        return jsonify({'success': False, 'error': 'Game is over'})
    
    if game.current_player != BLACK:
        return jsonify({'success': False, 'error': 'Not your turn'})
    
    # 플레이어 수 실행
    if game.board.is_valid_move(row, col, BLACK):
        game.board.make_move(row, col, BLACK)
        game.move_history.append({
            'player': 'human',
            'row': int(row),
            'col': int(col),
            'timestamp': float(time.time())
        })
        
        # 게임 종료 체크
        if game.board.is_game_over():
            game.game_over = True
            game.winner = game.board.get_winner()
        else:
            game.current_player = WHITE
        
        # AI 턴 처리
        ai_move_result = None
        if not game.game_over and game.current_player == WHITE:
            ai_moves = game.board.get_valid_moves(WHITE)
            if ai_moves:
                # AI가 최고의 수 계산
                start_time = time.time()
                best_move = game.ai.get_best_move(game.board, WHITE)
                think_time = time.time() - start_time
                
                if best_move:
                    game.board.make_move(best_move.row, best_move.col, WHITE)
                    game.move_history.append({
                        'player': 'ai',
                        'row': int(best_move.row),
                        'col': int(best_move.col),
                        'score': int(best_move.score),
                        'think_time': float(think_time),
                        'timestamp': float(time.time())
                    })
                    
                    ai_move_result = {
                        'row': int(best_move.row),
                        'col': int(best_move.col),
                        'score': int(best_move.score),
                        'think_time': float(think_time)
                    }
            
            # 게임 종료 재체크
            if game.board.is_game_over():
                game.game_over = True
                game.winner = game.board.get_winner()
            else:
                game.current_player = BLACK
        
        return jsonify({
            'success': True,
            'game_state': game.to_dict(),
            'ai_move': ai_move_result
        })
    
    else:
        return jsonify({'success': False, 'error': 'Invalid move'})

@app.route('/api/game_state/<session_id>')
def get_game_state(session_id):
    """게임 상태 조회"""
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Invalid session'})
    
    return jsonify({
        'success': True,
        'game_state': game_sessions[session_id].to_dict()
    })

@app.route('/api/ai_hint/<session_id>')
def get_ai_hint(session_id):
    """AI 힌트 제공"""
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Invalid session'})
    
    game = game_sessions[session_id]
    if game.game_over or game.current_player != BLACK:
        return jsonify({'success': False, 'error': 'Cannot provide hint now'})
    
    # AI가 플레이어 입장에서 최고의 수 계산
    best_move = game.ai.get_best_move(game.board, BLACK)
    
    if best_move:
        return jsonify({
            'success': True,
            'hint': {
                'row': int(best_move.row),
                'col': int(best_move.col),
                'score': int(best_move.score)
            }
        })
    else:
        return jsonify({'success': False, 'error': 'No valid moves'})

@app.route('/api/pass', methods=['POST'])
def pass_turn():
    """턴 패스 처리"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id not in game_sessions:
            return jsonify({'success': False, 'error': 'Session not found'})
        
        session = game_sessions[session_id]
        board = session.board
        ai = session.ai
        
        # 현재 플레이어가 사람이어야 함
        if session.current_player != BLACK:
            return jsonify({'success': False, 'error': 'Not player turn'})
        
        # 정말로 둘 수 있는 수가 없는지 확인
        valid_moves = board.get_valid_moves(BLACK)
        if valid_moves:
            return jsonify({'success': False, 'error': 'You have valid moves, cannot pass'})
        
        # 플레이어 패스 - AI 턴으로 변경
        session.current_player = WHITE
        ai_move = None
        
        # AI가 둘 수 있는지 확인
        ai_valid_moves = board.get_valid_moves(WHITE)
        if ai_valid_moves:
            # AI가 수를 둠
            best_move = ai.get_best_move(board, WHITE)
            if best_move:
                board.make_move(best_move.row, best_move.col, WHITE)
                ai_move = {'row': int(best_move.row), 'col': int(best_move.col)}
            
            # 다시 플레이어 턴으로
            session.current_player = BLACK
        else:
            # AI도 둘 수 없음 - 게임 종료는 자동으로 처리됨
            pass
        
        return jsonify({
            'success': True,
            'game_state': session.to_dict(),
            'ai_move': ai_move,
            'message': 'Player passed'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# SocketIO 이벤트 (실시간 업데이트용)
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to Othello server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_game')
def handle_join_game(data):
    session_id = data.get('session_id')
    if session_id in game_sessions:
        emit('game_update', game_sessions[session_id].to_dict())

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
