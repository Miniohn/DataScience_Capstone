import logging

logger = logging.getLogger(__name__)

class BlockAgent:
    def __init__(self):
        self.warning_threshold = 3
        self.reset_threshold = 5
        self.block_duration_days = 7
        self.blocked = False
        self.total_offense_count = 0
        self.blocked_message = (
            f"You have been temporarily blocked due to repeated inappropriate behavior. "
            f"You can try again after {self.block_duration_days} days."
        )
        self.responses = {
            "are you crazy? go to hell": (
                "Please avoid using threatening or harassing language. "
                f"If inappropriate messages are sent more than {self.warning_threshold} times, "
                f"you will be blocked for {self.block_duration_days} days."
            ),
            "u r such a loser": (
                "Let's focus on positive and loving communication. "
                f"If inappropriate messages are sent more than {self.warning_threshold} times, "
                f"you will be blocked for {self.block_duration_days} days."
            ),
            "u r a lier": (
                "Let's focus on positive and loving communication. "
                f"If inappropriate messages are sent more than {self.warning_threshold} times, "
                f"you will be blocked for {self.block_duration_days} days."
            )
        }

    def process(self, user_input: str) -> str:
        normalized_input = user_input.strip().lower()
        print(f"[BlockAgent] Input received: {user_input}")
        print(f"[BlockAgent] Normalized input: {normalized_input}")

        if self.blocked:
            print(f"[BlockAgent] User is blocked.")
            if self.total_offense_count + 1 == self.reset_threshold:
                # 누적 5번째 입력일 경우 자동 초기화
                print(f"[BlockAgent] Reached {self.reset_threshold} offenses. Resetting...")
                self.reset()
                return "Your status has been reset. Let's begin again with a clean slate."
            else:
                self.total_offense_count += 1
                return self.blocked_message

        if normalized_input in self.responses:
            self.total_offense_count += 1
            print(f"[BlockAgent] Offense count: {self.total_offense_count}")

            if self.total_offense_count >= self.warning_threshold:
                self.blocked = True
                print(f"[BlockAgent] Threshold reached. User is now blocked.")
                return self.blocked_message

            return self.responses[normalized_input]

        print(f"[BlockAgent] No offensive content detected.")
        return None

    def reset(self):
        self.blocked = False
        self.total_offense_count = 0
        print(f"[BlockAgent] Agent reset: offense count cleared and block lifted.")
