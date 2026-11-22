import math
import os
import sys
import time

if os.name == "nt":
    os.system("")
    import msvcrt

TIME_LIMIT = 15.0

BIG_DIGITS = {
    "0": [" ### ", "#   #", "#   #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "  ## ", " #   ", "#####"],
    "3": [" ### ", "#   #", "  ## ", "#   #", " ### "],
    "4": ["#   #", "#   #", "#####", "    #", "    #"],
    "5": ["#####", "#    ", "#### ", "    #", "#### "],
    "6": [" ### ", "#    ", "#### ", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "  #  ", "  #  "],
    "8": [" ### ", "#   #", " ### ", "#   #", " ### "],
    "9": [" ### ", "#   #", " ####", "    #", " ### "],
}


class Quiz:
    """개별 퀴즈 한 문제를 표현하는 문제 카드 클래스"""

    def __init__(self, question: str, choices: list[str], answer: int) -> None:
        self.question = question
        self.choices = choices
        self.answer = answer

    def display(self, index: int, total: int) -> None:
        print("\n" + "=" * 52)
        print(f"[문제 {index}/{total}] {self.question}\n")
        for idx, choice in enumerate(self.choices, start=1):
            print(f"  {idx}. {choice}")
        print("-" * 52)

    def check_answer(self, user_answer: int) -> bool:
        return user_answer == self.answer

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=int(data["answer"]),
        )


def get_default_quizzes() -> list[Quiz]:
    """상담심리학 핵심 개념 5문제 기본 데이터"""
    return [
        Quiz(
            question="[행동주의] 스키너의 조작적 조건형성에서 시끄러운 알람을 끄기 위해 일어나는 것처럼, 혐오 자극을 제거해 행동의 빈도를 높이는 원리는?",
            choices=["정적 강화", "부적 강화", "정적 처벌", "부적 처벌"],
            answer=2,
        ),
        Quiz(
            question="[인간중심상담] 칼 로저스가 제시한 상담자의 3대 태도 중 하나인 '일치성(Congruence)'이 의미하는 바는?",
            choices=[
                "상담자와 내담자의 가치관이 완전히 일치하는 상태",
                "내담자의 말에 무조건 동의하고 맞장구쳐 주는 태도",
                "상담자의 내적 감정과 외적 표현이 모순 없이 진실된 상태",
                "상담 이론과 실제 기법이 정확히 일치하는 상태",
            ],
            answer=3,
        ),
        Quiz(
            question="[인지치료] 아론 벡의 인지치료에서 말하는 인지적 왜곡 중 '개인화(Personalization)'에 해당하는 사례는?",
            choices=[
                "자신과 무관한 외부의 부정적 사건을 모두 자기 탓으로 돌리는 것",
                "내담자 성향에 맞춘 개인별 맞춤형 상담 계획을 세우는 것",
                "타인의 마음을 근거 없이 지레짐작하여 단정 짓는 것",
                "사소한 실수 하나만으로 자신을 완전히 실패자로 규정하는 것",
            ],
            answer=1,
        ),
        Quiz(
            question="[방어기제] 무의식적으로 용납할 수 없는 충동과 정반대되는 행동(예: 미워하는 사람에게 과도하게 친절을 베풂)을 하는 방어기제는?",
            choices=[
                "합리화(Rationalization)",
                "전치(Displacement)",
                "승화(Sublimation)",
                "반동형성(Reaction Formation)",
            ],
            answer=4,
        ),
        Quiz(
            question="[정신분석] 상담 과정에서 '상담자'가 자신의 과거 미해결된 갈등이나 감정을 '내담자'에게 무의식적으로 투사하는 현상은?",
            choices=[
                "전이(Transference)",
                "역전이(Countertransference)",
                "저항(Resistance)",
                "라포(Rapport)",
            ],
            answer=2,
        ),
    ]


def get_valid_int(prompt: str, min_val: int, max_val: int) -> int:
    """공백 제거, 빈 입력, 문자 입력, 범위 초과를 방어하는 정수 입력 함수"""
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("⚠️ 입력이 비어 있습니다. 숫자를 입력해 주세요.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("⚠️ 숫자가 아닙니다. 올바른 숫자를 입력해 주세요.")
            continue

        if not (min_val <= value <= max_val):
            print(f"⚠️ 잘못된 입력입니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.")
            continue
        return value


def build_timer_lines(remaining: float, prompt: str, buf: str, warn_msg: str) -> list[str]:
    """문제 아래에 크게 표시할 숫자 초시계와 도화선 화면 생성"""
    sec_int = 0 if remaining <= 0 else min(15, math.ceil(remaining))
    sec_str = f"{sec_int:02d}"
    d1 = BIG_DIGITS[sec_str[0]]
    d2 = BIG_DIGITS[sec_str[1]]

    bars = max(0, min(15, math.ceil(remaining)))
    fuse = "#" * bars + "." * (15 - bars)

    if remaining <= 5.0:
        color = "\033[1;91m"
        alert = "  🚨 폭발 직전!! 서두르세요!!"
    elif remaining <= 10.0:
        color = "\033[1;93m"
        alert = "  ⚠️ 시간이 절반도 안 남았습니다!"
    else:
        color = "\033[1;92m"
        alert = ""
    reset = "\033[0m"

    lines = [f"{color}  ⏱️  남은 시간 (폭발까지){alert}{reset}"]
    for row in range(5):
        lines.append(f"{color}       {d1[row]}   {d2[row]}{reset}")
    lines.append(f"{color}  도화선: [{fuse}] {max(0.0, remaining):4.1f}초{reset}")

    input_line = f"  {prompt}{buf}"
    if warn_msg:
        input_line += f"  ({warn_msg})"
    lines.append(input_line)
    return lines


def get_timed_int(prompt: str, min_val: int, max_val: int, time_limit: float) -> tuple[int | None, float]:
    """큰 초시계와 함께 제한시간 내에 숫자를 입력받는 함수"""
    start_time = time.time()

    if os.name == "nt" and sys.stdin.isatty():
        buf = ""
        warn_msg = ""
        lines = build_timer_lines(time_limit, prompt, buf, warn_msg)
        sys.stdout.write("\n".join(lines))
        sys.stdout.flush()

        while True:
            elapsed = time.time() - start_time
            remaining = time_limit - elapsed
            if remaining <= 0:
                lines = build_timer_lines(0.0, prompt, buf, warn_msg)
                sys.stdout.write("\r\033[7A" + "\033[K\n".join(lines) + "\033[K\n")
                sys.stdout.flush()
                return None, elapsed

            lines = build_timer_lines(remaining, prompt, buf, warn_msg)
            sys.stdout.write("\r\033[7A" + "\033[K\n".join(lines) + "\033[K")
            sys.stdout.flush()

            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch == "\x03":
                    raise KeyboardInterrupt
                elif ch in ("\r", "\n"):
                    raw = buf.strip()
                    if not raw:
                        warn_msg = "⚠️ 숫자를 입력하세요!"
                        buf = ""
                        continue
                    try:
                        val = int(raw)
                    except ValueError:
                        warn_msg = "⚠️ 숫자만 입력하세요!"
                        buf = ""
                        continue
                    if not (min_val <= val <= max_val):
                        warn_msg = f"⚠️ {min_val}~{max_val} 사이 입력!"
                        buf = ""
                        continue
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return val, time.time() - start_time
                elif ch == "\x08":
                    buf = buf[:-1]
                    warn_msg = ""
                elif ch in ("\x00", "\xe0"):
                    msvcrt.getwch()
                else:
                    if len(buf) < 10:
                        buf += ch
                    warn_msg = ""

            time.sleep(0.05)
    else:
        print(f"⏱️ 제한시간 {int(time_limit)}초! 정답을 입력하세요.")
        val = get_valid_int(prompt, min_val, max_val)
        elapsed = time.time() - start_time
        if elapsed > time_limit:
            return None, elapsed
        return val, elapsed


def print_bomb_explosion() -> None:
    print(
        r"""
\033[1;91m          _.-^^---....,,--
      _--                  --_
     <                        >)
     |       💥 BOOM!! 💥      |
      \._                   _./
         ```--. . , ; .--'''
               | |   |
            .-=||  | |=-.
            `-=#$%&%$#=-'
               | ;  :|
      _____.,-#%&$@%#&#~,._____\033[0m
        """
    )


def play_quizzes(quizzes: list[Quiz]) -> None:
    if not quizzes:
        print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
        return

    print(f"\n💣 시한폭탄 퀴즈를 시작합니다! (총 {len(quizzes)}문제 / 문제당 제한시간 {int(TIME_LIMIT)}초)")
    correct_count = 0

    for idx, quiz in enumerate(quizzes, start=1):
        quiz.display(idx, len(quizzes))
        user_answer, elapsed = get_timed_int("정답 입력 (1~4): ", 1, 4, TIME_LIMIT)

        if user_answer is None or elapsed > TIME_LIMIT:
            print_bomb_explosion()
            print(f"⏰ 제한시간 {int(TIME_LIMIT)}초가 지나 폭탄이 터졌습니다!")
            print(f"💡 정답은 {quiz.answer}번({quiz.choices[quiz.answer - 1]})이었습니다.")
            time.sleep(2)
        elif quiz.check_answer(user_answer):
            correct_count += 1
            print(f"✅ 정답입니다! ({elapsed:.1f}초 만에 폭탄 해체 성공!)")
            time.sleep(1.5)
        else:
            print_bomb_explosion()
            print("❌ 오답입니다! 잘못된 선을 잘라 폭탄이 터졌습니다!")
            print(f"💡 정답은 {quiz.answer}번({quiz.choices[quiz.answer - 1]})입니다.")
            time.sleep(2)

    score = int((correct_count / len(quizzes)) * 100)
    print("\n" + "=" * 52)
    print(f"🏆 최종 결과: {len(quizzes)}문제 중 {correct_count}문제 정답! ({score}점)")
    print("=" * 52)


def print_menu() -> None:
    print("\n" + "=" * 52)
    print("   💣 시한폭탄 상담심리학 퀴즈 게임 💣")
    print("=" * 52)
    print("1. 퀴즈 풀기 (제한시간 15초!)")
    print("2. 퀴즈 추가")
    print("3. 퀴즈 목록")
    print("4. 점수 확인")
    print("5. 종료")
    print("=" * 52)


def main() -> None:
    quizzes = get_default_quizzes()
    try:
        while True:
            print_menu()
            choice = get_valid_int("선택: ", 1, 5)

            if choice == 1:
                play_quizzes(quizzes)
            elif choice == 2:
                print("\n[안내] 퀴즈 추가 기능 준비 중입니다.")
            elif choice == 3:
                print("\n[안내] 퀴즈 목록 기능 준비 중입니다.")
            elif choice == 4:
                print("\n[안내] 점수 확인 기능 준비 중입니다.")
            elif choice == 5:
                print("\n👋 게임을 안전하게 종료합니다.")
                break
    except (KeyboardInterrupt, EOFError):
        print("\n\n⚠️ 강제 종료 신호가 감지되어 안전하게 프로그램을 종료합니다.")


if __name__ == "__main__":
    main()