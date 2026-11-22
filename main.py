from datetime import datetime
import json
import math
import os
import shutil
import sys
import time

if os.name == "nt":
    os.system("")
    import msvcrt

TIME_LIMIT = 15.0
STATE_FILE = "state.json"
BACKUP_FILE = "state.json.bak"

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


# ============================================================
# [유지보수 지점 2: 퀴즈 데이터 모델]
# 새로운 필드(예: 난이도, 해설, 카테고리)를 추가할 때 이 클래스를 수정합니다.
# ============================================================
class Quiz:
    """개별 퀴즈 한 문제의 데이터와 출력·정답 판별을 담당하는 모델 클래스"""

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

    def normalized_key(self) -> str:
        """대량 데이터 중복 검색(O(1) 해시 인덱싱)을 위한 정규화 키 생성"""
        return " ".join(self.question.strip().lower().split())

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quiz":
        if not isinstance(data, dict):
            raise ValueError("퀴즈 항목이 딕셔너리 형식이 아닙니다.")
        question = data.get("question")
        choices = data.get("choices")
        answer = data.get("answer")

        if not isinstance(question, str) or not question.strip():
            raise ValueError("유효하지 않은 문제 텍스트입니다.")
        if (
            not isinstance(choices, list)
            or len(choices) != 4
            or not all(isinstance(c, str) and c.strip() for c in choices)
        ):
            raise ValueError("보기는 4개의 비어 있지 않은 문자열 리스트여야 합니다.")
        if not isinstance(answer, int) or isinstance(answer, bool) or not (1 <= answer <= 4):
            raise ValueError("정답 번호는 1~4 사이의 정수여야 합니다.")

        return cls(question=question.strip(), choices=[c.strip() for c in choices], answer=answer)


def get_default_quizzes() -> list[Quiz]:
    """상담심리학 핵심 개념 5문제 기본 데이터"""
    defaults = [
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
    if len(defaults) != 5:
        raise RuntimeError(f"기본 퀴즈 개수 검증 실패: 예상 5개, 실제 {len(defaults)}개")
    return defaults


# ============================================================
# [입력 검증 계층]
# 사용자 입력의 빈칸, 공백, 문자 오입력, 범위 초과를 방어합니다.
# ============================================================
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


def get_non_empty_str(prompt: str) -> str:
    """빈칸이나 공백만 입력하는 것을 막아주는 문자열 입력 함수"""
    while True:
        text = input(prompt).strip()
        if not text:
            print("⚠️ 내용이 비어 있습니다. 글자를 입력해 주세요.")
            continue
        return text


# ============================================================
# [유지보수 지점 3: 데이터 저장 및 영속성(state.json)]
# 파일 경로, 백업 정책, JSON 스키마 구조를 변경할 때 이 클래스를 수정합니다.
# ============================================================
class QuizStorage:
    """state.json 기반 영속성 관리, 자동 백업, 무결성 검증 및 손상 복구를 담당하는 저장소 클래스"""

    def __init__(self, file_path: str = STATE_FILE, backup_path: str = BACKUP_FILE) -> None:
        self.file_path = file_path
        self.backup_path = backup_path

    def _validate_and_parse(self, raw_data: dict) -> tuple[list[Quiz], list[dict], int]:
        """로드된 JSON 데이터의 무결성 및 스키마 검증"""
        if not isinstance(raw_data, dict):
            raise ValueError("최상위 JSON 구조가 객체(dict)가 아닙니다.")

        raw_quizzes = raw_data.get("quizzes")
        raw_history = raw_data.get("score_history", [])
        raw_best = raw_data.get("best_score", 0)

        if not isinstance(raw_quizzes, list) or len(raw_quizzes) == 0:
            raise ValueError("quizzes 필드가 비어 있거나 리스트가 아닙니다.")

        quizzes = [Quiz.from_dict(item) for item in raw_quizzes]

        if not isinstance(raw_history, list):
            raise ValueError("score_history 필드가 리스트가 아닙니다.")

        validated_history: list[dict] = []
        for entry in raw_history:
            if not isinstance(entry, dict):
                raise ValueError("점수 기록 항목이 딕셔너리가 아닙니다.")
            validated_history.append(
                {
                    "round": int(entry["round"]),
                    "correct": int(entry["correct"]),
                    "total": int(entry["total"]),
                    "score": int(entry["score"]),
                }
            )

        best_score = int(raw_best)
        if validated_history:
            best_score = max(best_score, max(r["score"] for r in validated_history))

        return quizzes, validated_history, best_score

    def _backup_corrupted_file(self) -> None:
        """손상된 state.json 파일을 타임스탬프 백업 파일로 격리 보존"""
        if not os.path.exists(self.file_path):
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        corrupt_backup = f"{self.file_path}.corrupt.{timestamp}.bak"
        try:
            shutil.copy2(self.file_path, corrupt_backup)
            print(f"📦 손상된 파일을 '{corrupt_backup}'에 격리 백업했습니다.")
        except OSError as err:
            print(f"⚠️ 손상 파일 백업 중 오류 발생: {err}")

    def load_state(self) -> tuple[list[Quiz], list[dict], int]:
        """
        [로드 시점: 프로그램 시작 직후 호출]
        1. state.json 존재 시 파싱 및 무결성 검증
        2. 파일 없음(FileNotFoundError) 시 기본 5문제로 초기화 후 state.json 생성
        3. JSON 파싱/무결성 손상 시 손상 파일 백업 -> .bak 복구 시도 -> 실패 시 기본값 초기화
        """
        if not os.path.exists(self.file_path):
            quizzes = get_default_quizzes()
            print(f"ℹ️ 기존 '{self.file_path}' 파일이 없어 기본 {len(quizzes)}문제로 새 저장소를 생성합니다.")
            self.save_state(quizzes, [], 0, silent=True)
            return quizzes, [], 0

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            quizzes, history, best_score = self._validate_and_parse(raw_data)
            print(f"💾 '{self.file_path}' 로드 완료 (등록 퀴즈 {len(quizzes)}개 / 최고 점수 {best_score}점)")
            return quizzes, history, best_score
        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as err:
            print(f"\n⚠️ '{self.file_path}' 손상 감지 ({err}). 복구 절차를 시작합니다...")
            self._backup_corrupted_file()

            if os.path.exists(self.backup_path):
                try:
                    with open(self.backup_path, "r", encoding="utf-8") as bf:
                        backup_data = json.load(bf)
                    quizzes, history, best_score = self._validate_and_parse(backup_data)
                    print(f"✅ 정상 백업 파일('{self.backup_path}')로부터 데이터를 복구했습니다!")
                    self.save_state(quizzes, history, best_score, silent=True)
                    return quizzes, history, best_score
                except Exception:
                    print("⚠️ 백업 파일도 유효하지 않아 기본 초기 상태로 복구합니다.")

            quizzes = get_default_quizzes()
            self.save_state(quizzes, [], 0, silent=True)
            print(f"✅ 기본 {len(quizzes)}문제 상태로 안전하게 초기화 복구되었습니다.")
            return quizzes, [], 0
        except (PermissionError, OSError) as err:
            print(f"\n⚠️ 파일 읽기 권한/입출력 오류({err})가 발생하여 임시 기본 데이터로 실행합니다.")
            return get_default_quizzes(), [], 0

    def save_state(
        self,
        quizzes: list[Quiz],
        score_history: list[dict],
        best_score: int,
        silent: bool = False,
    ) -> bool:
        """
        [저장 시점: 퀴즈 추가 직후, 라운드 완료 직후, 정상/강제 종료 시 호출]
        저장 전 기존 정상 파일을 .bak으로 백업한 뒤 UTF-8 JSON으로 기록합니다.
        """
        if os.path.exists(self.file_path):
            try:
                shutil.copy2(self.file_path, self.backup_path)
            except OSError:
                pass

        payload = {
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "quiz_count": len(quizzes),
            "best_score": best_score,
            "quizzes": [q.to_dict() for q in quizzes],
            "score_history": score_history,
        }

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            if not silent:
                print(f"💾 상태가 '{self.file_path}'에 안전하게 저장되었습니다.")
            return True
        except (PermissionError, OSError) as err:
            print(f"⚠️ '{self.file_path}' 저장 실패 (권한/디스크 오류): {err}")
            return False


# ============================================================
# [타이머 및 시각 연출 계층]
# ============================================================
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
    """큰 초시계와 함께 제한시간 내에 숫자를 입력받는 기능"""
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
    bomb_art = r"""
          _.-^^---....,,--
      _--                  --_
     <                        >)
     |       💥 BOOM!! 💥      |
      \._                   _./
         ```--. . , ; .--'''
               | |   |
            .-=||  | |=-.
            `-=#$\%&\%$#=-'
               | ;  :|
      _____.,-#%&$@%#&#~,._____
    """
    print(f"\033[1;91m{bomb_art}\033[0m")


# ============================================================
# [게임 진행 컨트롤러 계층: QuizGame]
# 메뉴 제어, 퀴즈 라운드 진행, 대용량 인덱스 관리, 종료 시 상태 동기화를 담당합니다.
# ============================================================
class QuizGame:
    """퀴즈 게임의 전체 실행 흐름과 상태 동기화를 조율하는 컨트롤러 클래스"""

    def __init__(self, storage: QuizStorage) -> None:
        self.storage = storage
        self.quizzes, self.score_history, self.best_score = self.storage.load_state()
        # 대량(1,000개 이상) 퀴즈 환경에서도 O(1) 속도로 중복을 탐지하기 위한 해시 인덱스
        self._question_index: set[str] = {q.normalized_key() for q in self.quizzes}

    def print_menu(self) -> None:
        print("\n" + "=" * 52)
        print("   💣 시한폭탄 상담심리학 퀴즈 게임 💣")
        print(f"   (보유 문제: {len(self.quizzes)}개 | 최고 기록: {self.best_score}점)")
        print("=" * 52)
        print("1. 퀴즈 풀기 (제한시간 15초!)")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 저장 후 종료")
        print("=" * 52)

    def play_round(self) -> None:
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        total = len(self.quizzes)
        print(f"\n💣 시한폭탄 퀴즈를 시작합니다! (총 {total}문제 / 문제당 제한시간 {int(TIME_LIMIT)}초)")
        correct_count = 0

        for idx, quiz in enumerate(self.quizzes, start=1):
            quiz.display(idx, total)
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

        # ============================================================
        # [유지보수 지점 1: 점수 계산 로직]
        # 가중치, 시간 보너스, 감점 제도를 도입할 때 아래 계산식을 수정합니다.
        # ============================================================
        score = int((correct_count / total) * 100)
        if score > self.best_score:
            self.best_score = score

        self.score_history.append(
            {
                "round": len(self.score_history) + 1,
                "correct": correct_count,
                "total": total,
                "score": score,
            }
        )

        print("\n" + "=" * 52)
        print(f"🏆 최종 결과: {total}문제 중 {correct_count}문제 정답! ({score}점 / 최고 {self.best_score}점)")
        print("=" * 52)
        self.storage.save_state(self.quizzes, self.score_history, self.best_score)

    def add_quiz(self) -> None:
        print("\n" + "=" * 52)
        print("   ✏️ 새 상담심리학 퀴즈 추가")
        print("=" * 52)
        question = get_non_empty_str("문제 내용을 입력하세요: ")
        norm_key = " ".join(question.lower().split())

        if norm_key in self._question_index:
            print("⚠️ 이미 동일한 문제가 등록되어 있어 추가를 취소합니다.")
            return

        choices: list[str] = []
        for i in range(1, 5):
            choice_text = get_non_empty_str(f"보기 {i}번을 입력하세요: ")
            choices.append(choice_text)

        answer = get_valid_int("정답 번호를 입력하세요 (1~4): ", 1, 4)
        new_quiz = Quiz(question=question, choices=choices, answer=answer)
        self.quizzes.append(new_quiz)
        self._question_index.add(new_quiz.normalized_key())

        print(f"\n✅ 새 문제가 등록되었습니다! (현재 총 {len(self.quizzes)}문제)")
        self.storage.save_state(self.quizzes, self.score_history, self.best_score)

    def list_quizzes(self) -> None:
        total = len(self.quizzes)
        print("\n" + "=" * 52)
        print(f"   📋 등록된 퀴즈 목록 (총 {total}문제)")
        print("=" * 52)

        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        # 대량 문제 등록 시 가독성을 위한 페이지 단위 출력 지원
        page_size = 20
        for start in range(0, total, page_size):
            chunk = self.quizzes[start : start + page_size]
            for offset, quiz in enumerate(chunk, start=start + 1):
                print(f"\n[{offset}번 문제] {quiz.question}")
                for c_idx, choice in enumerate(quiz.choices, start=1):
                    mark = " ◀ (정답)" if c_idx == quiz.answer else ""
                    print(f"   {c_idx}. {choice}{mark}")

            if start + page_size < total:
                cont = input(f"\n--- 다음 페이지 보기 (Enter) / 목록 종료 (q): ").strip().lower()
                if cont == "q":
                    break
        print("\n" + "=" * 52)

    def show_scores(self) -> None:
        print("\n" + "=" * 52)
        print("   📊 나의 퀴즈 점수 기록")
        print("=" * 52)

        if not self.score_history:
            print("아직 퀴즈를 푼 기록이 없습니다. 1번을 눌러 도전해 보세요!")
            return

        for record in self.score_history:
            print(
                f"  • {record['round']}회차 도전: "
                f"{record['total']}문제 중 {record['correct']}문제 해체 성공 ({record['score']}점)"
            )

        avg_score = sum(r["score"] for r in self.score_history) / len(self.score_history)
        print("-" * 52)
        print(f"  🥇 최고 점수: {self.best_score}점  |  📈 평균 점수: {avg_score:.1f}점")
        print("=" * 52)

    def run(self) -> None:
        try:
            while True:
                self.print_menu()
                choice = get_valid_int("선택: ", 1, 5)

                if choice == 1:
                    self.play_round()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_scores()
                elif choice == 5:
                    self.storage.save_state(self.quizzes, self.score_history, self.best_score)
                    print("\n👋 현재 상태를 저장하고 게임을 안전하게 종료합니다.")
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️ 강제 종료 신호가 감지되었습니다. 현재까지의 상태를 동기화합니다...")
            self.storage.save_state(self.quizzes, self.score_history, self.best_score)
            print("👋 안전하게 프로그램을 종료합니다.")


def main() -> None:
    storage = QuizStorage()
    game = QuizGame(storage)
    game.run()


if __name__ == "__main__":
    main()