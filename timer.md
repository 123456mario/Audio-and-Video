# Xilica 타이머 구현 가이드 (오디오 클럭 해결법)

## 문제점 (Problem)
- **"Signal loop detected"** 에러 때문에 로직 모듈(NOT, Delay 등)을 서로 연결하여 반복시키는 것이 불가능합니다.
- Lua 스크립트가 작동하려면 외부에서 1초마다 신호(Pulse)를 줘야 합니다.

## 해결책 (Solution): 오디오 클럭 회로
오디오 신호를 이용하여 심장박동(Pulse)을 만듭니다. 이 방법은 연결 에러가 발생하지 않습니다.

### 단계별 따라하기 (Step-by-Step)

#### 1. "Sine Tone" 모듈 추가
- **위치**: Component Library -> **Generators**
- **설정 (Settings)**:
  - **Frequency (주파수)**: `1.0 Hz` (이 값이 타이머 속도입니다)
  - **Level**: `0 dB`
  - **Mute**: OFF (꺼짐 상태 확인)

#### 2. "Level Trigger" 모듈 추가
- **위치**: Component Library -> **Dynamics**
- 만약 없다면 `RMS Meter`를 사용하셔도 됩니다.
- **설정 (Settings)**:
  - **Threshold**: `-30 dB` (왼쪽 슬라이더)
  - **Attack/Release**: `10 ms` (빠른 반응 속도)

#### 3. 선 연결 (Connect Wires)
1. **[Sine Tone]**의 오디오 출력(초록색)을 ----> **[Level Trigger]**의 오디오 입력(초록색)에 연결합니다.
2. **[Level Trigger]**의 로직 출력(보라색/삼각형 핀)을 ----> **[Lua Script]**의 **2번 핀**에 연결합니다.

#### 4. 최종 확인
- 파워 버튼(Lua 1번 핀 연결)을 켭니다.
- 이제 타이머 숫자가 `0, 1, 2, ...` 순서로 올라갑니다.
