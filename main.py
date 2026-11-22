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
    try:
        while True:
            print_menu()
            choice = get_valid_int("선택: ", 1, 5)

            if choice == 1:
                print("\n[안내] 퀴즈 풀기 기능 준비 중입니다.")
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