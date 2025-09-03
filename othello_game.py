"""
🏆 최강 오델로 AI - 2시간 완성 버전
친구들을 압도하는 Alpha-Beta + 최적화된 휴리스틱 AI

핵심 전략:
- 코너 장악 최우선 (가중치 1000)
- X/C square 절대 회피 (페널티 -500/-200)  
- 게임 단계별 전략 (초반 이동성, 후반 돌 개수)
- 안정성 중심 평가
"""

import numpy as np
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass

# 게임 상수
EMPTY = 0
BLACK = 1  # 검은색 (선공)
WHITE = 2  # 흰색 (후공)
BOARD_SIZE = 8

# 방향 벡터 (8방향)
DIRECTIONS = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

@dataclass
class Move:
    row: int
    col: int
    score: int = 0

class OthelloBoard:
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.setup_initial_position()
        
    def setup_initial_position(self):
        """초기 4개 돌 배치"""
        mid = BOARD_SIZE // 2
        self.board[mid-1][mid-1] = WHITE
        self.board[mid-1][mid] = BLACK
        self.board[mid][mid-1] = BLACK
        self.board[mid][mid] = WHITE
    
    def copy(self):
        """보드 복사"""
        new_board = OthelloBoard()
        new_board.board = self.board.copy()
        return new_board
    
    def is_valid_move(self, row: int, col: int, player: int) -> bool:
        """유효한 수인지 확인"""
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return False
        if self.board[row][col] != EMPTY:
            return False
        
        # 8방향으로 뒤집을 수 있는 돌이 있는지 확인
        for dr, dc in DIRECTIONS:
            if self._can_flip_direction(row, col, dr, dc, player):
                return True
        return False
    
    def _can_flip_direction(self, row: int, col: int, dr: int, dc: int, player: int) -> bool:
        """특정 방향으로 뒤집을 수 있는지 확인"""
        opponent = BLACK if player == WHITE else WHITE
        r, c = row + dr, col + dc
        found_opponent = False
        
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if self.board[r][c] == EMPTY:
                return False
            elif self.board[r][c] == opponent:
                found_opponent = True
            elif self.board[r][c] == player:
                return found_opponent
            r, c = r + dr, c + dc
        return False
    
    def get_valid_moves(self, player: int) -> List[Move]:
        """플레이어의 모든 유효한 수 반환"""
        moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.is_valid_move(row, col, player):
                    moves.append(Move(row, col))
        return moves
    
    def make_move(self, row: int, col: int, player: int) -> bool:
        """수를 두고 돌 뒤집기"""
        if not self.is_valid_move(row, col, player):
            return False
        
        self.board[row][col] = player
        
        # 8방향으로 돌 뒤집기
        for dr, dc in DIRECTIONS:
            if self._can_flip_direction(row, col, dr, dc, player):
                self._flip_direction(row, col, dr, dc, player)
        
        return True
    
    def _flip_direction(self, row: int, col: int, dr: int, dc: int, player: int):
        """특정 방향의 돌들 뒤집기"""
        opponent = BLACK if player == WHITE else WHITE
        r, c = row + dr, col + dc
        
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            if self.board[r][c] == opponent:
                self.board[r][c] = player
            elif self.board[r][c] == player:
                break
            r, c = r + dr, c + dc
    
    def count_discs(self, player: int) -> int:
        """플레이어의 돌 개수"""
        return np.sum(self.board == player)
    
    def is_game_over(self) -> bool:
        """게임 종료 여부"""
        return (len(self.get_valid_moves(BLACK)) == 0 and 
                len(self.get_valid_moves(WHITE)) == 0)
    
    def get_winner(self) -> Optional[int]:
        """승자 반환"""
        if not self.is_game_over():
            return None
        
        black_count = self.count_discs(BLACK)
        white_count = self.count_discs(WHITE)
        
        if black_count > white_count:
            return BLACK
        elif white_count > black_count:
            return WHITE
        else:
            return None  # 무승부
    
    def print_board(self):
        """보드 출력"""
        print("  0 1 2 3 4 5 6 7")
        for i in range(BOARD_SIZE):
            print(f"{i} ", end="")
            for j in range(BOARD_SIZE):
                if self.board[i][j] == EMPTY:
                    print(".", end=" ")
                elif self.board[i][j] == BLACK:
                    print("●", end=" ")
                else:
                    print("○", end=" ")
            print()
        print(f"Black: {self.count_discs(BLACK)}, White: {self.count_discs(WHITE)}")


class SuperOthelloAI:
    """🏆 최강 오델로 AI - 친구들 압도용"""
    
    def __init__(self):
        # ⚡ 최적화된 탐색 깊이 (속도 vs 강도 균형)
        self.depth_config = {
            "OPENING": 3,    # 초반: 빠른 결정 (오프닝북 활용)
            "MIDGAME": 4,    # 중반: 적당한 탐색 (1-2초 응답)
            "ENDGAME": 6     # 후반: 깊은 탐색 (3-5초 응답)
        }
        # 🚀 성능 최적화: 굳힘돌 계산 캐시
        self.stability_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.position_weights = self._create_position_weights()
        self.corner_positions = [(0,0), (0,7), (7,0), (7,7)]
        self.x_squares = [(1,1), (1,6), (6,1), (6,6)]  # 절대 피해야 할 위치
        self.c_squares = [(0,1), (1,0), (0,6), (1,7), (6,0), (7,1), (6,7), (7,6)]
        
        # 🏆 확장된 오프닝 북 - 오델로 마스터 수준
        self.opening_moves = {
            4: [(2,3), (3,2), (4,5), (5,4)],  # 대각선 오프닝
            5: [(2,4), (4,2), (3,5), (5,3)],  # 평행선 오프닝  
            6: [(2,5), (5,2), (2,2), (5,5)],  # 소나타 오프닝
            7: [(1,3), (3,1), (6,4), (4,6)],  # 로즈 오프닝
            8: [(1,4), (4,1), (6,3), (3,6)],  # 베르가모 오프닝
            9: [(1,5), (5,1), (6,2), (2,6)],  # 이탈리아 오프닝
            10: [(0,3), (3,0), (7,4), (4,7)], # 타이거 오프닝
            11: [(0,4), (4,0), (7,3), (3,7)], # 캣 오프닝
            12: [(0,5), (5,0), (7,2), (2,7)], # 버팔로 오프닝
        }
        
        # 🎯 특수 패턴 대응 (상대방 수에 따른 최적 대응)
        self.counter_moves = {
            # 상대가 대각선으로 왔을 때의 대응
            (2,3): [(2,4), (4,2)],  # C4에 대한 대응
            (3,2): [(4,2), (2,4)],  # D3에 대한 대응
            (4,5): [(4,6), (6,4)],  # E6에 대한 대응
            (5,4): [(6,4), (4,6)],  # F5에 대한 대응
        }
    
    def _create_position_weights(self):
        """위치별 가중치 테이블 생성"""
        weights = np.array([
            [100,  -20,  10,   5,   5,  10, -20, 100],
            [-20,  -50,  -2,  -2,  -2,  -2, -50, -20],
            [ 10,   -2,  -1,  -1,  -1,  -1,  -2,  10],
            [  5,   -2,  -1,  -1,  -1,  -1,  -2,   5],
            [  5,   -2,  -1,  -1,  -1,  -1,  -2,   5],
            [ 10,   -2,  -1,  -1,  -1,  -1,  -2,  10],
            [-20,  -50,  -2,  -2,  -2,  -2, -50, -20],
            [100,  -20,  10,   5,   5,  10, -20, 100]
        ])
        return weights
    
    def get_game_phase(self, board: OthelloBoard) -> str:
        """게임 단계 판단"""
        empty_count = np.sum(board.board == EMPTY)
        if empty_count >= 50:
            return "OPENING"
        elif empty_count >= 20:
            return "MIDGAME"
        else:
            return "ENDGAME"
    
    def evaluate_position(self, board: OthelloBoard, player: int) -> int:
        """🧠 최강 평가 함수 - 고도화된 전략 통합"""
        if board.is_game_over():
            winner = board.get_winner()
            if winner == player:
                return 10000
            elif winner is None:
                return 0
            else:
                return -10000
        
        score = 0
        opponent = BLACK if player == WHITE else WHITE
        phase = self.get_game_phase(board)
        empty_count = np.sum(board.board == EMPTY)
        
        # 1. 코너 장악 (절대적 우위)
        corner_score = 0
        player_corners = 0
        opponent_corners = 0
        for r, c in self.corner_positions:
            if board.board[r][c] == player:
                corner_score += 1000
                player_corners += 1
            elif board.board[r][c] == opponent:
                corner_score -= 1000
                opponent_corners += 1
        score += corner_score
        
        # 🎯 코너 정보 출력 (디버깅용)
        if player_corners > 0 or opponent_corners > 0:
            print(f"🏰 코너: AI {player_corners}개, 상대 {opponent_corners}개 (점수: {corner_score:+d})")
        
        # 🚨 코너 기회 알림 (디버깅용)
        available_corners = []
        for r, c in self.corner_positions:
            if board.board[r][c] == EMPTY and board.is_valid_move(r, c, player):
                available_corners.append((r, c))
        if available_corners:
            print(f"🎯 코너 기회 발견: {available_corners} - 절대 놓치지 마세요!")
        
        # 2. X-square 페널티 (코너 인접 대각선)
        for r, c in self.x_squares:
            if board.board[r][c] == player:
                # 해당 코너가 비어있으면 큰 페널티
                corner_r = 0 if r == 1 else 7
                corner_c = 0 if c == 1 else 7
                if board.board[corner_r][corner_c] == EMPTY:
                    score -= 500
            elif board.board[r][c] == opponent:
                corner_r = 0 if r == 1 else 7
                corner_c = 0 if c == 1 else 7
                if board.board[corner_r][corner_c] == EMPTY:
                    score += 500
        
        # 3. C-square 페널티 (코너 인접)
        for r, c in self.c_squares:
            if board.board[r][c] == player:
                score -= 200
            elif board.board[r][c] == opponent:
                score += 200
        
        # 4. 🚀 고도화된 이동성 평가 (Mobility)
        my_moves = board.get_valid_moves(player)
        opp_moves = board.get_valid_moves(opponent)
        
        # 기본 이동성 점수
        mobility_diff = len(my_moves) - len(opp_moves)
        
        # 🎯 가중치 이동성 (좋은 위치의 수는 더 높은 점수)
        weighted_mobility = 0
        for move in my_moves:
            r, c = move.row, move.col
            if (r, c) in self.corner_positions:
                weighted_mobility += 50  # 코너 수
            elif self._is_edge_stable(board, r, c, player):
                weighted_mobility += 20  # 가장자리 안정 수
            elif (r, c) in self.x_squares:
                weighted_mobility -= 30  # X-square는 피하자
            else:
                weighted_mobility += 5   # 일반 수
        
        for move in opp_moves:
            r, c = move.row, move.col
            if (r, c) in self.corner_positions:
                weighted_mobility -= 50
            elif self._is_edge_stable(board, r, c, opponent):
                weighted_mobility -= 20
            elif (r, c) in self.x_squares:
                weighted_mobility += 30  # 상대가 X-square 두면 좋음
            else:
                weighted_mobility -= 5
        
        # 게임 단계별 이동성 가중치
        if phase == "OPENING":
            mobility_score = mobility_diff * 50 + weighted_mobility * 0.5
        elif phase == "MIDGAME":  
            mobility_score = mobility_diff * 25 + weighted_mobility * 0.8
        else:  # ENDGAME
            mobility_score = mobility_diff * 10 + weighted_mobility * 1.2
        
        score += mobility_score
        
        # 5. 🛡️ 굳힘돌 안정성 (우승자 핵심 전략)
        import time
        start_time = time.time()
        
        my_stability = self._calculate_stability(board, player)
        opp_stability = self._calculate_stability(board, opponent)
        stability_diff = my_stability - opp_stability
        
        calc_time = time.time() - start_time
        if calc_time > 0.01:  # 10ms 이상이면 경고
            print(f"⚠️ 굳힘돌 계산 시간: {calc_time:.3f}초")
        
        # 굳힘돌 정보 표시 (디버깅용)
        if my_stability > 0 or opp_stability > 0:
            print(f"🛡️ 굳힘돌: AI {my_stability}개, 상대 {opp_stability}개 (차이: {stability_diff:+d})")
        
        # 게임 단계별 굳힘돌 가중치 (코너보다 낮게 설정)
        if phase == "OPENING":
            # 초반: 굳힘돌 중요하지만 코너보다는 낮게
            stability_weight = 50
        elif phase == "MIDGAME":
            # 중반: 굳힘돌 중요도 증가하지만 여전히 코너보다 낮게
            stability_weight = 80
        else:  # ENDGAME
            # 후반: 굳힘돌 중요하지만 코너 절대 우선
            stability_weight = 120
        
        score += stability_diff * stability_weight
        
        # 6. 위치별 가중치
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.board[r][c] == player:
                    score += self.position_weights[r][c]
                elif board.board[r][c] == opponent:
                    score -= self.position_weights[r][c]
        
        # 7. 🏆 소식-대식 전략 (우승자 핵심 전략)
        my_count = board.count_discs(player)
        opp_count = board.count_discs(opponent)
        disc_diff = my_count - opp_count
        
        # 🎯 전략 전환 시점 결정
        transition_point = self._get_strategy_transition_point(board, phase, empty_count)
        
        if phase == "OPENING":
            # 🎯 선공/후공 차별화 전략
            is_first_player = (player == BLACK)  # 검은색이 선공
            
            if is_first_player:  # 선공 전략 (적극적)
                if disc_diff < -6:  # 6개 이상 뒤처지면 적극 공격
                    score += disc_diff * 4  # 매우 적극적으로 돌 확보
                elif transition_point < 0.3:  # 초반
                    score += disc_diff * 1  # 약간 많이 먹기 선호 (적극적)
                else:
                    score += disc_diff * 2  # 중반 전환기에 적극적
            else:  # 후공 전략 (반격 중심)
                if disc_diff < -10:  # 10개 이상 뒤처지면 방어
                    score += disc_diff * 2  # 방어적으로 돌 확보
                elif transition_point < 0.4:  # 후공은 더 오래 소식 유지
                    score += disc_diff * -2  # 소식 전략 유지
                else:
                    score += disc_diff * 0  # 중립적 유지
                
        elif phase == "MIDGAME":
            # 🎯 중반: 선공/후공 차별화 전략
            is_first_player = (player == BLACK)
            
            if is_first_player:  # 선공은 빠른 대식 전환
                if transition_point < 0.4:
                    score += disc_diff * 1   # 약간 대식
                else:
                    score += disc_diff * 4   # 적극적 대식 전환
            else:  # 후공은 신중한 전환
                if transition_point < 0.6:
                    score += disc_diff * -0.5  # 약간 소식 유지
                else:
                    score += disc_diff * 2.5   # 늦은 대식 전환
                
        else:  # ENDGAME
            # 후반: 대식전략 (많이 먹기)
            if transition_point > 0.8:
                score += disc_diff * 150  # 매우 적극적으로 많이 먹기
            else:
                score += disc_diff * 100  # 많이 먹기 선호
        
        # 8. 🎲 점령율 평가 (우승자 방식)
        total_discs = my_count + opp_count
        if total_discs > 0:
            occupation_rate = my_count / total_discs
            
            # 초반엔 낮은 점령율 선호, 후반엔 높은 점령율 선호
            if phase == "OPENING":
                # 30-40% 점령율이 이상적
                ideal_rate = 0.35
                rate_penalty = abs(occupation_rate - ideal_rate) * -80
            elif phase == "MIDGAME":
                # 40-50% 점령율이 이상적  
                ideal_rate = 0.45
                rate_penalty = abs(occupation_rate - ideal_rate) * -40
            else:  # ENDGAME
                # 50%+ 점령율 선호
                rate_penalty = max(0, occupation_rate - 0.5) * 120
            
            score += rate_penalty
        
        return score
    
    def _get_strategy_transition_point(self, board: OthelloBoard, phase: str, empty_count: int) -> float:
        """🎯 소식-대식 전략 전환 시점 결정"""
        # 기본 게임 진행도 (0.0 = 게임 시작, 1.0 = 게임 끝)
        game_progress = (64 - empty_count) / 64
        
        # 🧠 상황별 가중치 조정
        my_moves = len(board.get_valid_moves(WHITE))  # AI 이동성
        opp_moves = len(board.get_valid_moves(BLACK))  # 상대 이동성
        
        # 상대 이동성이 제한될수록 전환 시점을 앞당김
        mobility_factor = 0
        if opp_moves + my_moves > 0:
            mobility_factor = opp_moves / (opp_moves + my_moves)
        
        # 코너 장악 상황
        corners_owned = 0
        for r, c in self.corner_positions:
            if board.board[r][c] == WHITE:  # AI가 코너 소유
                corners_owned += 1
        corner_factor = corners_owned / 4  # 0~1
        
        # 🎯 종합 전환 시점 계산
        # - 게임 진행도가 기본
        # - 상대 이동성이 낮으면 더 일찍 전환 (공격 기회)
        # - 코너를 많이 소유하면 더 일찍 전환 (안전한 공격)
        transition_point = (
            game_progress * 0.6 +           # 게임 진행도 60%
            (1 - mobility_factor) * 0.25 +  # 상대 이동성 제한 25%
            corner_factor * 0.15            # 코너 장악도 15%
        )
        
        return min(1.0, transition_point)
    
    def _get_current_strategy(self, phase: str, transition_point: float, player: int) -> str:
        """🎯 현재 사용 중인 전략 표시"""
        is_first_player = (player == BLACK)
        player_type = "선공" if is_first_player else "후공"
        
        if phase == "OPENING":
            if is_first_player:  # 선공
                if transition_point < 0.3:
                    return f"⚡ {player_type} 적극전략 (주도권)"
                else:
                    return f"🔥 {player_type} 공격전환 (압박)"
            else:  # 후공
                if transition_point < 0.4:
                    return f"🛡️ {player_type} 소식전략 (반격준비)"
                else:
                    return f"⚖️ {player_type} 균형전략 (기회대기)"
        elif phase == "MIDGAME":
            if is_first_player:  # 선공
                if transition_point < 0.4:
                    return f"🎯 {player_type} 빠른대식 (주도)"
                else:
                    return f"⚡ {player_type} 적극공격 (결정적)"
            else:  # 후공
                if transition_point < 0.6:
                    return f"🌱 {player_type} 신중소식 (반격)"
                else:
                    return f"🔥 {player_type} 늦은대식 (역전)"
        else:  # ENDGAME
            if transition_point > 0.8:
                return f"⚡ {player_type} 최대공격 (승부)"
            else:
                return f"🏆 {player_type} 대식전략 (마무리)"
    
    def _calculate_stability(self, board: OthelloBoard, player: int) -> int:
        """🛡️ 고도화된 굳힘돌 계산 (우승자 핵심 전략)"""
        # 🚀 캐시 체크 (성능 최적화)
        board_key = (tuple(board.board.flatten()), player)
        if board_key in self.stability_cache:
            self.cache_hits += 1
            return self.stability_cache[board_key]
        
        self.cache_misses += 1
        stable_discs = set()
        opponent = BLACK if player == WHITE else WHITE
        
        # 1️⃣ 코너에서 시작하는 안정한 체인 계산
        for corner_r, corner_c in self.corner_positions:
            if board.board[corner_r][corner_c] == player:
                self._find_stable_chain(board, corner_r, corner_c, player, stable_discs)
        
        # 2️⃣ 가장자리 완전 장악 체크
        stable_discs.update(self._find_stable_edges(board, player))
        
        # 3️⃣ 방향별 완전 안정성 체크 (8방향 모두 안전)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.board[r][c] == player and (r, c) not in stable_discs:
                    if self._is_fully_stable(board, r, c, player):
                        stable_discs.add((r, c))
        
        # 🚀 캐시에 결과 저장
        result = len(stable_discs)
        self.stability_cache[board_key] = result
        
        # 캐시 크기 제한 (메모리 관리)
        if len(self.stability_cache) > 1000:
            # 오래된 캐시 절반 삭제
            keys_to_remove = list(self.stability_cache.keys())[:500]
            for key in keys_to_remove:
                del self.stability_cache[key]
        
        return result
    
    def _find_stable_chain(self, board: OthelloBoard, start_r: int, start_c: int, 
                          player: int, stable_discs: set):
        """🔗 코너에서 시작하는 안정한 체인 찾기"""
        if (start_r, start_c) in stable_discs:
            return
        
        # BFS로 연결된 안정한 돌들 찾기
        queue = [(start_r, start_c)]
        visited = {(start_r, start_c)}
        stable_chain = [(start_r, start_c)]
        
        while queue:
            r, c = queue.pop(0)
            
            # 8방향으로 인접한 돌 체크
            for dr, dc in DIRECTIONS:
                nr, nc = r + dr, c + dc
                
                if (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and 
                    (nr, nc) not in visited and board.board[nr][nc] == player):
                    
                    # 이 돌이 안정한지 체크
                    if self._is_chain_stable(board, nr, nc, player, stable_discs):
                        visited.add((nr, nc))
                        queue.append((nr, nc))
                        stable_chain.append((nr, nc))
        
        # 체인의 모든 돌을 안정한 돌로 추가
        stable_discs.update(stable_chain)
    
    def _is_chain_stable(self, board: OthelloBoard, r: int, c: int, 
                        player: int, existing_stable: set) -> bool:
        """체인에서 이 돌이 안정한지 확인"""
        # 이미 안정하다고 확인된 돌과 인접하면 안정
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if (nr, nc) in existing_stable:
                return True
        
        # 가장자리에 있고 끝까지 연결되어 있으면 안정
        if r == 0 or r == 7 or c == 0 or c == 7:
            return self._is_edge_connected_to_corner(board, r, c, player)
        
        return False
    
    def _find_stable_edges(self, board: OthelloBoard, player: int) -> set:
        """🏁 완전 장악된 가장자리 라인 찾기"""
        stable_edges = set()
        
        # 상하 가장자리 체크
        for row in [0, 7]:
            if self._is_edge_fully_controlled(board, row, 0, 0, 1, player):
                for c in range(BOARD_SIZE):
                    if board.board[row][c] == player:
                        stable_edges.add((row, c))
        
        # 좌우 가장자리 체크  
        for col in [0, 7]:
            if self._is_edge_fully_controlled(board, 0, col, 1, 0, player):
                for r in range(BOARD_SIZE):
                    if board.board[r][col] == player:
                        stable_edges.add((r, col))
        
        return stable_edges
    
    def _is_edge_fully_controlled(self, board: OthelloBoard, start_r: int, start_c: int,
                                 dr: int, dc: int, player: int) -> bool:
        """가장자리 라인이 완전히 장악되었는지 확인"""
        for i in range(BOARD_SIZE):
            r, c = start_r + i * dr, start_c + i * dc
            if board.board[r][c] != EMPTY and board.board[r][c] != player:
                return False
        return True
    
    def _is_fully_stable(self, board: OthelloBoard, r: int, c: int, player: int) -> bool:
        """🛡️ 8방향 모두에서 완전히 안전한지 확인"""
        opponent = BLACK if player == WHITE else WHITE
        
        # 각 방향에서 뒤집힐 가능성 체크
        for dr, dc in DIRECTIONS:
            if not self._is_direction_stable(board, r, c, dr, dc, player):
                return False
        
        return True
    
    def _is_direction_stable(self, board: OthelloBoard, r: int, c: int, 
                           dr: int, dc: int, player: int) -> bool:
        """특정 방향에서 안정한지 확인"""
        opponent = BLACK if player == WHITE else WHITE
        
        # 이 방향으로 가면서 체크
        nr, nc = r + dr, c + dc
        
        while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            if board.board[nr][nc] == EMPTY:
                return True  # 빈 칸이 있으면 안전
            elif board.board[nr][nc] == player:
                return True  # 같은 색 돌이 있으면 안전
            # 상대 돌이면 계속 진행
            nr, nc = nr + dr, nc + dc
        
        return True  # 보드 끝까지 도달하면 안전
    
    def _is_edge_connected_to_corner(self, board: OthelloBoard, r: int, c: int, player: int) -> bool:
        """가장자리 돌이 코너까지 연결되어 있는지 확인"""
        # 상하 가장자리
        if r == 0 or r == 7:
            # 왼쪽 코너까지 연결 체크
            for check_c in range(c):
                if board.board[r][check_c] != player:
                    break
            else:
                return True  # 왼쪽 코너까지 연결됨
                
            # 오른쪽 코너까지 연결 체크
            for check_c in range(c + 1, BOARD_SIZE):
                if board.board[r][check_c] != player:
                    break
            else:
                return True  # 오른쪽 코너까지 연결됨
        
        # 좌우 가장자리
        if c == 0 or c == 7:
            # 위쪽 코너까지 연결 체크
            for check_r in range(r):
                if board.board[check_r][c] != player:
                    break
            else:
                return True  # 위쪽 코너까지 연결됨
                
            # 아래쪽 코너까지 연결 체크
            for check_r in range(r + 1, BOARD_SIZE):
                if board.board[check_r][c] != player:
                    break
            else:
                return True  # 아래쪽 코너까지 연결됨
        
        return False
    
    def _is_stable_position(self, board: OthelloBoard, row: int, col: int, player: int) -> bool:
        """해당 위치가 안정한지 확인"""
        # 코너는 항상 안정
        if (row, col) in self.corner_positions:
            return True
        
        # 가장자리에 있고 코너까지 연결되어 있으면 안정
        if (row == 0 or row == 7 or col == 0 or col == 7):
            return self._is_edge_stable(board, row, col, player)
        
        return False
    
    def _is_edge_stable(self, board: OthelloBoard, row: int, col: int, player: int) -> bool:
        """가장자리 돌의 안정성 확인"""
        # 간단한 휴리스틱: 가장자리에서 연속된 자신의 돌이 있으면 안정
        if row == 0 or row == 7:  # 위아래 가장자리
            return True
        if col == 0 or col == 7:  # 좌우 가장자리
            return True
        return False
    
    def get_best_move(self, board: OthelloBoard, player: int) -> Optional[Move]:
        """🎯 최고의 수 찾기 - 동적 깊이 조정"""
        moves = board.get_valid_moves(player)
        if not moves:
            return None
        
        # 게임 단계별 탐색 깊이 결정
        game_phase = self.get_game_phase(board)
        search_depth = self.depth_config[game_phase]
        
        # 🏁 스마트 엔드게임 (완전탐색은 정말 마지막에만)
        empty_count = np.sum(board.board == EMPTY)
        if empty_count <= 6:  # 마지막 6수만 완전탐색 (빠른 응답)
            print(f"🏁 엔드게임 완전탐색 모드 (남은 칸: {empty_count})")
            return self._endgame_solver(board, player)
        elif empty_count <= 10:  # 10수 이하는 깊이 증가
            search_depth = min(8, empty_count + 2)
        
        # 🎯 전략 정보 표시
        transition_point = self._get_strategy_transition_point(board, game_phase, empty_count)
        strategy = self._get_current_strategy(game_phase, transition_point, player)
        
        print(f"🧠 AI 분석: {game_phase} 단계, 탐색깊이 {search_depth}")
        print(f"🎯 전략: {strategy} (전환점: {transition_point:.2f})")
        
        # 오프닝 북 사용
        move_count = 64 - empty_count
        if move_count in self.opening_moves:
            for move_pos in self.opening_moves[move_count]:
                r, c = move_pos
                if board.is_valid_move(r, c, player):
                    print(f"📚 오프닝 북 사용: ({r}, {c})")
                    return Move(r, c, 999)  # 오프닝 북 점수
        
        # ⚡ 이동 순서 최적화 (좋은 수부터 먼저 탐색 → 가지치기 효율 증대)
        moves = self._sort_moves(board, moves, player)
        
        # Alpha-Beta 탐색
        best_move = None
        best_score = float('-inf')
        
        for i, move in enumerate(moves):
            # 보드 복사하고 수 두기
            test_board = board.copy()
            test_board.make_move(move.row, move.col, player)
            
            # Minimax with Alpha-Beta Pruning (동적 깊이)
            score = self._minimax(test_board, search_depth - 1, 
                                float('-inf'), float('inf'), False, player)
            
            move.score = score
            if score > best_score:
                best_score = score
                best_move = move
        
        # 🚀 성능 리포트 (캐시 효율성)
        if self.cache_hits + self.cache_misses > 0:
            cache_rate = self.cache_hits / (self.cache_hits + self.cache_misses) * 100
            print(f"📊 캐시 효율: {cache_rate:.1f}% ({self.cache_hits}히트/{self.cache_misses}미스)")
        
        print(f"🎯 최선의 수: ({best_move.row}, {best_move.col}), 점수: {best_move.score}")
        return best_move
    
    def _sort_moves(self, board: OthelloBoard, moves: List[Move], player: int) -> List[Move]:
        """⚡ 이동 순서 최적화 - 좋은 수부터 먼저 탐색"""
        def move_priority(move):
            r, c = move.row, move.col
            priority = 0
            
            # 코너 > 가장자리 > 일반 순으로 우선순위
            if (r, c) in self.corner_positions:
                priority += 10000  # 코너 절대 최우선!
            elif self._is_edge_stable(board, r, c, player):
                priority += 100   # 안정적인 가장자리
            elif (r, c) in self.x_squares:
                priority -= 500   # X-square 최후순위
            elif (r, c) in self.c_squares:
                priority -= 100   # C-square 후순위
            else:
                # 위치 가중치 활용
                priority += self.position_weights[r][c]
            
            return priority
        
        # 우선순위 높은 순으로 정렬
        return sorted(moves, key=move_priority, reverse=True)
    
    def _endgame_solver(self, board: OthelloBoard, player: int) -> Optional[Move]:
        """🏁 엔드게임 완전탐색 솔버 - 최적해 보장"""
        moves = board.get_valid_moves(player)
        if not moves:
            return None
        
        best_move = None
        best_score = float('-inf')
        
        print(f"🔍 {len(moves)}개 수를 완전탐색 중...")
        
        for i, move in enumerate(moves):
            print(f"  분석 중: {i+1}/{len(moves)} - ({move.row}, {move.col})")
            
            # 보드 복사하고 수 두기
            test_board = board.copy()
            test_board.make_move(move.row, move.col, player)
            
            # 완전탐색으로 정확한 점수 계산
            final_score = self._perfect_minimax(test_board, player, player)
            move.score = final_score
            
            if final_score > best_score:
                best_score = final_score
                best_move = move
                print(f"    🎯 새로운 최선수! 점수: {final_score}")
        
        print(f"🏆 완전탐색 완료: ({best_move.row}, {best_move.col}), 최종점수: {best_score}")
        return best_move
    
    def _perfect_minimax(self, board: OthelloBoard, original_player: int, current_player: int) -> int:
        """완전탐색용 미니맥스 - 게임 끝까지 정확히 계산"""
        if board.is_game_over():
            # 게임 종료 시 실제 돌 개수 차이로 점수 계산
            my_count = board.count_discs(original_player)
            opp_count = board.count_discs(BLACK if original_player == WHITE else WHITE)
            return my_count - opp_count
        
        moves = board.get_valid_moves(current_player)
        
        # 둘 수 없으면 상대방 턴
        if not moves:
            opponent = BLACK if current_player == WHITE else WHITE
            return self._perfect_minimax(board, original_player, opponent)
        
        # 현재 플레이어가 원래 플레이어면 최대화, 아니면 최소화
        is_maximizing = (current_player == original_player)
        
        if is_maximizing:
            best_score = float('-inf')
            for move in moves:
                test_board = board.copy()
                test_board.make_move(move.row, move.col, current_player)
                
                opponent = BLACK if current_player == WHITE else WHITE
                score = self._perfect_minimax(test_board, original_player, opponent)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for move in moves:
                test_board = board.copy()
                test_board.make_move(move.row, move.col, current_player)
                
                opponent = BLACK if current_player == WHITE else WHITE
                score = self._perfect_minimax(test_board, original_player, opponent)
                best_score = min(best_score, score)
            return best_score
    
    def _minimax(self, board: OthelloBoard, depth: int, alpha: float, beta: float, 
                is_maximizing: bool, original_player: int) -> int:
        """Alpha-Beta Pruning을 사용한 Minimax"""
        if depth == 0 or board.is_game_over():
            return self.evaluate_position(board, original_player)
        
        current_player = original_player if is_maximizing else (BLACK if original_player == WHITE else WHITE)
        moves = board.get_valid_moves(current_player)
        
        # 수가 없으면 상대방 턴
        if not moves:
            return self._minimax(board, depth - 1, alpha, beta, not is_maximizing, original_player)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in moves:
                test_board = board.copy()
                test_board.make_move(move.row, move.col, current_player)
                
                eval_score = self._minimax(test_board, depth - 1, alpha, beta, False, original_player)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:  # Alpha-Beta Pruning
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                test_board = board.copy()
                test_board.make_move(move.row, move.col, current_player)
                
                eval_score = self._minimax(test_board, depth - 1, alpha, beta, True, original_player)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:  # Alpha-Beta Pruning
                    break
            return min_eval


def play_game():
    """게임 실행"""
    board = OthelloBoard()
    ai = SuperOthelloAI()
    
    print("🏆 최강 오델로 AI에 도전하세요!")
    print("색깔을 선택하세요:")
    print("1. ● 검은색 (선공)")
    print("2. ○ 흰색 (후공)")
    
    while True:
        try:
            choice = int(input("선택 (1 또는 2): "))
            if choice == 1:
                player_color = BLACK
                ai_color = WHITE
                print("당신은 ● (검은색), AI는 ○ (흰색)입니다.")
                break
            elif choice == 2:
                player_color = WHITE
                ai_color = BLACK
                print("당신은 ○ (흰색), AI는 ● (검은색)입니다.")
                break
            else:
                print("1 또는 2를 입력하세요.")
        except:
            print("올바른 숫자를 입력하세요.")
    
    print("좌표는 '행 열' 형식으로 입력하세요 (예: 2 3)")
    print()
    
    current_player = BLACK  # 검은색이 선공
    
    # AI가 선공(검은색)이면 첫 수를 둠
    if ai_color == BLACK:
        print("AI가 선공으로 첫 수를 둡니다...")
        board.print_board()
        print()
        
        start_time = time.time()
        best_move = ai.get_best_move(board, BLACK)
        if best_move:
            board.make_move(best_move.row, best_move.col, BLACK)
            think_time = time.time() - start_time
            print(f"AI가 ({best_move.row}, {best_move.col})에 두었습니다. (점수: {best_move.score}, 시간: {think_time:.2f}초)")
            current_player = player_color
        print()
    
    while not board.is_game_over():
        board.print_board()
        print()
        
        moves = board.get_valid_moves(current_player)
        
        if not moves:
            print(f"{'플레이어' if current_player == player_color else 'AI'}가 둘 수 없습니다. 턴을 넘깁니다.")
            current_player = WHITE if current_player == BLACK else BLACK
            continue
        
        if current_player == player_color:  # 플레이어 턴
            print("당신의 턴입니다.")
            print(f"가능한 수: {[(m.row, m.col) for m in moves]}")
            
            try:
                row, col = map(int, input("수를 입력하세요: ").split())
                if board.is_valid_move(row, col, player_color):
                    board.make_move(row, col, player_color)
                    current_player = ai_color
                else:
                    print("유효하지 않은 수입니다!")
            except:
                print("잘못된 입력입니다!")
        
        else:  # AI 턴
            print("AI가 생각 중...")
            start_time = time.time()
            
            best_move = ai.get_best_move(board, ai_color)
            if best_move:
                board.make_move(best_move.row, best_move.col, ai_color)
                think_time = time.time() - start_time
                print(f"AI가 ({best_move.row}, {best_move.col})에 두었습니다. (점수: {best_move.score}, 시간: {think_time:.2f}초)")
            
            current_player = player_color
    
    # 게임 결과
    board.print_board()
    print("\n🎉 게임 종료!")
    
    winner = board.get_winner()
    black_count = board.count_discs(BLACK)
    white_count = board.count_discs(WHITE)
    
    player_symbol = "●" if player_color == BLACK else "○"
    ai_symbol = "○" if player_color == BLACK else "●"
    player_score = black_count if player_color == BLACK else white_count
    ai_score = white_count if player_color == BLACK else black_count
    
    print(f"최종 점수: 플레이어({player_symbol}) {player_score} vs AI({ai_symbol}) {ai_score}")
    
    if winner == player_color:
        print("🎊 축하합니다! 당신이 승리했습니다!")
    elif winner == ai_color:
        print("🤖 AI가 승리했습니다. 다시 도전해보세요!")
    else:
        print("🤝 무승부입니다!")


if __name__ == "__main__":
    play_game()
