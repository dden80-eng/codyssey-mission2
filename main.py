class Quiz:
    """개별 퀴즈 한 문제를 표현하는 문제 카드 클래스"""

    def __init__(self, question: str, choices: list[str], answer: int) -> None:
        self.question = question
        self.choices = choices
        self.answer = answer

    def display(self, index: int) -> None:
        print("\n" + "-" * 44)
        print(f"[문제 {index}] {self.question}\n")
        for idx, choice in enumerate(self.choices, start=1):
            print(f"  {idx}. {choice}")
        print("-" * 44)

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


def print_menu() -> None:
    print("\n" + "=" * 44)
    print("   💣 시한폭탄 상담심리학 퀴즈 게임 💣")
    print("=" * 44)
    print("1. 퀴즈 풀기 (제한시간 15초!)")
    print("2. 퀴즈 추가")
    print("3. 퀴즈 목록")
    print("4. 점수 확인")
    print("5. 종료")
    print("=" * 44)


def main() -> None:
    quizzes = get_default_quizzes()
    try:
        while True:
            print_menu()
            choice = get_valid_int("선택: ", 1, 5)

            if choice == 1:
                print(f"\n[안내] 퀴즈 풀기 기능 준비 중입니다. (현재 {len(quizzes)}문제 대기 중)")
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