from utils.contextvar import get_request_json_post_payload


class User:
    def __init__(self, email):
        self.email = email

    def get_details(self):
        return {"email": self.email}


class Question:
    def __init__(self, id, title, content, user):
        self.title = title
        self.content = content
        self.user = user
        self.id = id

    def get_details(self):
        return {
            "id": self.id,
            "content": self.content,
            "title": self.title,
            "user": self.user.get_details(),
        }


# @singleton_class
class QuestionManager:
    def __init__(self):
        self.users = {"sathwik@gmail.com": User("sathwik@gmail.com")}
        self.questions = {}
        self

    def add_question(self, request):
        payload = get_request_json_post_payload()
        title = payload["title"]
        content = payload["content"]
        user_email = payload["user_email"]
        user = self.users[user_email]
        if not user:
            return "User not found", {}, None
        current_latest_id = len(self.questions.keys())
        question = Question(current_latest_id + 1, title, content, user)
        self.questions[current_latest_id + 1] = question
        return "", {"question": question.get_details()}, None

    def get_all_questions(self):
        questions = [q.get_details() for q in self.questions.values()]
        return "", {"questions": questions}, None
