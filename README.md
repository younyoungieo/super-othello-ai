# 🏆 최강 오델로 AI - SuperOthelloAI

**친구들을 압도하는 마스터 레벨 오델로 AI 게임**

2시간 만에 완성된 고성능 오델로 AI로 친구들과의 대결에서 승리하세요! 🎮

![Othello Game](https://img.shields.io/badge/Game-Othello%2FReversi-green)
![AI Level](https://img.shields.io/badge/AI%20Level-Master-red)
![Response Time](https://img.shields.io/badge/Response-1~3sec-blue)

## ✨ 주요 기능

### 🧠 **마스터 레벨 AI**
- **동적 탐색 깊이**: 게임 단계별 최적화 (초반 3수 → 중반 4수 → 후반 6수)
- **엔드게임 완전탐색**: 마지막 6수는 수학적 최적해 보장
- **Alpha-Beta 가지치기**: 불필요한 탐색 제거로 빠른 응답
- **이동 순서 최적화**: 좋은 수부터 탐색하여 효율성 극대화

### 📚 **확장된 오프닝 북**
- **9가지 마스터 오프닝**: 소나타, 로즈, 베르가모, 이탈리아 등
- **특수 패턴 대응**: 상대 수에 따른 최적 카운터 전략
- **실전 이론 기반**: 오델로 챔피언십 수준의 오프닝

### 🎯 **정교한 전략**
- **코너 장악 우선**: 절대적 우위 확보 (1000점 가중치)
- **X/C-square 회피**: 위험한 수는 철저히 배제
- **가중치 이동성**: 좋은 위치의 수는 더 높은 점수
- **게임 단계별 전략**: 초반 이동성 → 후반 안정성

### 🎮 **완벽한 사용자 경험**
- **Figma 기반 디자인**: 아름다운 게임 보드
- **실시간 패스 시스템**: 둘 수 없을 때 자동 패스 버튼
- **AI 마지막 수 표시**: 빨간 테두리로 명확한 표시
- **로딩 애니메이션**: AI 사고 과정 시각화

## 🚀 빠른 시작

### 1. 설치
```bash
git clone https://github.com/younyoungieo/super-othello-ai.git
cd super-othello-ai
pip install -r requirements.txt
```

### 2. 실행
```bash
python3 app.py
```

### 3. 게임 시작
브라우저에서 `http://localhost:5001` 접속

## 🛠 기술 스택

- **Backend**: Python Flask
- **AI Engine**: Custom Alpha-Beta with Minimax
- **Frontend**: HTML5, CSS3, JavaScript
- **Real-time**: WebSocket (Flask-SocketIO)
- **Design**: Figma-based UI (MCP Server 연동)
- **Development**: MCP (Model Context Protocol) Server

## 📊 AI 성능

| 게임 단계 | 탐색 깊이 | 응답 시간 | 특징 |
|-----------|-----------|-----------|------|
| 초반 (OPENING) | 3수 | 0.5초 | 오프닝 북 활용 |
| 중반 (MIDGAME) | 4수 | 1-2초 | 균형잡힌 전략 |
| 후반 (ENDGAME) | 6수 | 3-5초 | 깊은 분석 |
| 엔드게임 | 완전탐색 | 5-10초 | 수학적 최적해 |

## 🎯 AI 전략 상세

### 평가 함수 구성요소
1. **코너 장악** (±1000점): 절대적 우위
2. **X-square 페널티** (-500점): 위험한 대각선 위치
3. **C-square 페널티** (-200점): 코너 인접 위치
4. **가중치 이동성**: 위치별 차등 점수
5. **안정성 평가**: 가장자리 돌의 안정도
6. **위치별 가중치**: 전략적 위치 보너스

### 오프닝 북
- **대각선 오프닝**: C4, D3, E6, F5
- **평행선 오프닝**: C5, D6, E3, F4
- **소나타 오프닝**: C6, D2, E7, F3
- **로즈 오프닝**: B4, D8, E1, G5
- **베르가모 오프닝**: B5, D1, E8, G4
- 그 외 4가지 마스터 패턴

## 🏆 게임 특징

- **패스 시스템**: 둘 수 없을 때 자동 감지 및 패스
- **게임 종료**: 양쪽 모두 패스 시 자동 종료
- **승부 판정**: 돌 개수로 승패 결정
- **실시간 점수**: 게임 진행 중 실시간 업데이트

## 🎨 디자인

- **Figma 기반**: MCP 서버를 통한 실시간 디자인 연동
- **전문적 UI**: 게임 보드 및 인터페이스 디자인
- **반응형**: 다양한 화면 크기 지원  
- **애니메이션**: 돌 놓기, 유효한 수 표시 등
- **직관적 UX**: 쉬운 조작과 명확한 피드백

## 📝 개발 과정

이 프로젝트는 **2시간 내 완성**을 목표로 개발되었습니다:

1. **1단계**: 기본 게임 로직 구현
2. **2단계**: 웹 인터페이스 개발
3. **3단계**: AI 알고리즘 구현
4. **4단계**: Figma 디자인 적용
5. **5단계**: AI 고도화 및 최적화

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🎮 즐거운 게임 되세요!

**친구들과의 대결에서 승리하고, 오델로 마스터가 되어보세요!** 🏆
