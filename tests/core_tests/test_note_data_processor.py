import pytest
from core.note_data_processor import NoteDataProcessor


class FakeRepo:
    def __init__(self):
        self.calls = []
        self.rows = []
        self.storage = {}

    # ApiKeyRepository-like
    def get_all_api_keys(self):
        self.calls.append("get_all_api_keys")
        return self.rows

    def update_api_key(self, api_key_id):
        self.calls.append(("update_api_key", api_key_id))

    def insert_api_key(self, api_key):
        self.calls.append(("insert_api_key", api_key))
        return 42

    # NoteRepository-like
    def insert_note(self, name, content):
        self.calls.append(("insert_note", name))
        return 7

    # NoteHashtagRepository-like
    def insert_note_hashtags(self, note_id, tags):
        self.calls.append(("insert_note_hashtags", note_id, tuple(tags)))

    # SummaryRepository-like
    def insert_summary(self, note_id, summary):
        self.calls.append(("insert_summary", note_id))

    # QuestionRepository-like
    def insert_question(self, note_id, question, question_type, answer):
        self.calls.append(("insert_question", question))
        qid = len(self.storage) + 1
        self.storage[qid] = {"question": question}
        return qid

    # OptionRepository-like
    def insert_options(self, question_id, options):
        self.calls.append(("insert_options", question_id, tuple(options)))


def build_repos():
    api = FakeRepo()
    note = FakeRepo()
    note_hashtag = FakeRepo()
    question = FakeRepo()
    option = FakeRepo()
    summary = FakeRepo()
    return {
        "api_key_repository": api,
        "note_repository": note,
        "note_hashtag_repository": note_hashtag,
        "question_repository": question,
        "option_repository": option,
        "summary_repository": summary,
    }


def test_process_api_key_insert_when_not_exists():
    repos = build_repos()
    # no existing keys
    repos["api_key_repository"].rows = []
    p = NoteDataProcessor(repos)
    key_id = p.process_api_key("KEY")
    assert key_id == 42
    assert ("insert_api_key", "KEY") in repos["api_key_repository"].calls


def test_process_api_key_update_when_exists():
    repos = build_repos()
    repos["api_key_repository"].rows = [(5, "KEY", None)]
    p = NoteDataProcessor(repos)
    key_id = p.process_api_key("KEY")
    assert key_id == 5
    assert ("update_api_key", 5) in repos["api_key_repository"].calls


def test_process_note_and_tags():
    repos = build_repos()
    p = NoteDataProcessor(repos)
    note_id = p.process_note("title", "content", ["t1", "t2"])
    assert note_id == 7
    assert ("insert_note", "title") in repos["note_repository"].calls
    assert any(call[0] == "insert_note_hashtags" for call in repos["note_hashtag_repository"].calls)


def test_process_summary():
    repos = build_repos()
    p = NoteDataProcessor(repos)
    p.process_summary(7, "sum")
    assert ("insert_summary", 7) in repos["summary_repository"].calls


def test_process_quiz_questions():
    repos = build_repos()
    p = NoteDataProcessor(repos)
    quiz = [
        {"question": "Q1", "question_type": "multiple_choice", "answer": "A", "options": ["A", "B"]},
        {"question": "Q2", "question_type": "short_answer", "answer": "X"},
    ]
    mapping = p.process_quiz_questions(7, quiz)
    assert mapping["Q1"] == 1
    assert mapping["Q2"] == 2
    # options inserted for first only
    assert any(call[0] == "insert_options" for call in repos["option_repository"].calls)


def test_validate_inputs_errors():
    repos = build_repos()
    p = NoteDataProcessor(repos)
    with pytest.raises(ValueError):
        p.validate_inputs(" ", "n", [], "c", {}, "m")
    with pytest.raises(ValueError):
        p.validate_inputs("k", " ", [], "c", {}, "m")
    with pytest.raises(ValueError):
        p.validate_inputs("k", "n", "not-list", "c", {}, "m")
    with pytest.raises(ValueError):
        p.validate_inputs("k", "n", [], " ", {}, "m")
    with pytest.raises(ValueError):
        p.validate_inputs("k", "n", [], "c", "not-dict", "m")
    with pytest.raises(ValueError):
        p.validate_inputs("k", "n", [], "c", {}, " ")
