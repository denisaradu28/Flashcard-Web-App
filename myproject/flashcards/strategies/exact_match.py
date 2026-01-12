from .answer_strategy import AnswerStrategy

class ExactMatchStrategy(AnswerStrategy):

    def check_answer(self, user_answer: str, correct_answer: str) -> bool:
        return user_answer.strip().lower() == correct_answer.strip().lower()