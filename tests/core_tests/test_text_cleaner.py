from unittest.mock import patch
from core.text_cleaner import TextCleaner
import pytest
import logging


class TestTextCleaner:

    def test_erase_bracked_source_citations_with_valid_citations(self):
        test_cases = [
            ("This is a test [1]", "This is a test"),
            ("Multiple citations [1, 2, 3] here", "Multiple citations  here"),
            ("Citation at end [42]", "Citation at end"),
            ("[1] Citation at start", "Citation at start"),
            ("Mixed [1] content [2, 3] here", "Mixed  content  here"),
            ("Numbers only [123]", "Numbers only"),
            ("Spaces in citation [1, 2, 3]", "Spaces in citation"),
            ("Multiple spaces [  1, 2, 3  ]", "Multiple spaces"),
        ]
        
        for input_text, expected in test_cases:
            result = TextCleaner.erase_bracked_source_citations(input_text)
            assert result == expected, f"Failed for input: '{input_text}'"

    def test_erase_bracked_source_citations_with_invalid_citations(self):

        test_cases = [
            ("This is a test [not a citation]", "This is a test [not a citation]"),
            ("Brackets with text [citation text]", "Brackets with text [citation text]"),
            ("Mixed [1] valid [invalid] citations", "Mixed  valid [invalid] citations"),
            ("[1] Valid [invalid text] mixed", "Valid [invalid text] mixed"),
            ("Empty brackets []", "Empty brackets"),
            ("Brackets with letters [abc]", "Brackets with letters [abc]"),
            ("Brackets with symbols [1-2]", "Brackets with symbols [1-2]"),
        ]
        
        for input_text, expected in test_cases:
            result = TextCleaner.erase_bracked_source_citations(input_text)
            assert result == expected, f"Failed for input: '{input_text}'"

    def test_erase_bracked_source_citations_edge_cases(self):
        test_cases = [
            ("", ""),
            ("No brackets here", "No brackets here"),
            ("[1]", ""),
            ("   [1]   ", ""),
            ("[1][2][3]", ""),
            ("[1] [2] [3]", ""),
            ("[[1]]", "[[1]]"),
            ("[1,2,3]", ""),
        ]
        
        for input_text, expected in test_cases:
            result = TextCleaner.erase_bracked_source_citations(input_text)
            assert result == expected, f"Failed for input: '{input_text}'"

    def test_erase_bracked_source_citations_invalid_inputs(self):

        test_cases = [
            (None, None),
            (123, 123),
            (True, True),
            ([], []),
            ({}, {}),
        ]
        
        for input_text, expected in test_cases:
            result = TextCleaner.erase_bracked_source_citations(input_text)
            assert result == expected, f"Failed for input: {input_text}"

    def test_clean_quiz_result_with_valid_data(self):

        input_data = {
            "summary": "This is a summary [1] with citation",
            "quiz": [
                {
                    "question": "What is the answer? [2]",
                    "options": [
                        "Option A [3]",
                        "Option B",
                        "Option C [4, 5]"
                    ],
                    "answer": "Correct answer [6]",
                    "real_answer": "Real answer [7]",
                    "user_answer": "User answer [8]",
                    "correction_and_explanation": "Explanation [9]",
                    "additional_context": "Context [10]"
                }
            ]
        }
        
        expected_data = {
            "summary": "This is a summary  with citation",
            "quiz": [
                {
                    "question": "What is the answer?",
                    "options": [
                        "Option A",
                        "Option B",
                        "Option C"
                    ],
                    "answer": "Correct answer",
                    "real_answer": "Real answer",
                    "user_answer": "User answer",
                    "correction_and_explanation": "Explanation",
                    "additional_context": "Context"
                }
            ]
        }
        
        result = TextCleaner.clean_quiz_result(input_data)
        assert result == expected_data

    def test_clean_quiz_result_with_mixed_citations(self):

        input_data = {
            "summary": "Summary with [1] valid and [invalid] citations",
            "quiz": [
                {
                    "question": "Question with [2] valid and [invalid text] citations",
                    "options": [
                        "Option with [3] valid citation",
                        "Option with [invalid] citation",
                        "Option without citations"
                    ],
                    "answer": "Answer [4]",
                    "real_answer": "Real answer [5]",
                    "user_answer": "User answer [6]",
                    "correction_and_explanation": "Explanation [7]",
                    "additional_context": "Context [8]"
                }
            ]
        }
        
        expected_data = {
            "summary": "Summary with  valid and [invalid] citations",
            "quiz": [
                {
                    "question": "Question with  valid and [invalid text] citations",
                    "options": [
                        "Option with  valid citation",
                        "Option with [invalid] citation",
                        "Option without citations"
                    ],
                    "answer": "Answer",
                    "real_answer": "Real answer",
                    "user_answer": "User answer",
                    "correction_and_explanation": "Explanation",
                    "additional_context": "Context"
                }
            ]
        }
        
        result = TextCleaner.clean_quiz_result(input_data)
        assert result == expected_data

    def test_clean_quiz_result_with_empty_data(self):
        test_cases = [
            ({}, {}),
            ({"summary": ""}, {"summary": ""}),
            ({"quiz": []}, {"quiz": []}),
            ({"summary": "", "quiz": []}, {"summary": "", "quiz": []}),
        ]
        
        for input_data, expected in test_cases:
            result = TextCleaner.clean_quiz_result(input_data)
            assert result == expected

    def test_clean_quiz_result_with_missing_fields(self):
        input_data = {
            "summary": "Summary [1]",
            "quiz": [
                {
                    "question": "Question [2]",
                    "options": ["Option [3]"],
                }
            ]
        }
        
        expected_data = {
            "summary": "Summary",
            "quiz": [
                {
                    "question": "Question",
                    "options": ["Option"],
                }
            ]
        }
        
        result = TextCleaner.clean_quiz_result(input_data)
        assert result == expected_data

    def test_clean_quiz_result_with_invalid_quiz_structure(self):
        input_data = {
            "summary": "Summary [1]",
            "quiz": [
                "Not a dict",
                {
                    "question": "Question [2]",
                    "options": "Not a list",
                },
                {
                    "question": "Question [3]",
                    "options": [
                        "Option [4]",
                        None,
                        123,
                    ]
                }
            ]
        }
        
        expected_data = {
            "summary": "Summary",
            "quiz": [
                "Not a dict",
                {
                    "question": "Question",
                    "options": "Not a list",
                },
                {
                    "question": "Question",
                    "options": [
                        "Option",
                        None,
                        123,
                    ]
                }
            ]
        }
        
        result = TextCleaner.clean_quiz_result(input_data)
        assert result == expected_data

    def test_clean_quiz_result_with_non_string_values(self):
        input_data = {
            "summary": 123,
            "quiz": [
                {
                    "question": 456,
                    "options": [
                        789,
                        "String option [1]",
                        None,
                    ],
                    "answer": True,
                    "real_answer": 0.5,
                    "user_answer": [],
                    "correction_and_explanation": {},
                    "additional_context": None,
                }
            ]
        }
        
        expected_data = {
            "summary": 123,
            "quiz": [
                {
                    "question": 456,
                    "options": [
                        789,
                        "String option",
                        None,
                    ],
                    "answer": True,
                    "real_answer": 0.5,
                    "user_answer": [],
                    "correction_and_explanation": {},
                    "additional_context": None,
                }
            ]
        }
        
        result = TextCleaner.clean_quiz_result(input_data)
        assert result == expected_data

    @patch('core.text_cleaner.logging.error')
    def test_clean_quiz_result_exception_handling(self, mock_logging_error):

        input_data = {
            "summary": "Summary [1]",
            "quiz": [
                {
                    "question": "Question [2]",
                    "options": ["Option [3]"],
                }
            ]
        }
        
        # Mock the erase_bracked_source_citations method to raise an exception
        with patch.object(TextCleaner, 'erase_bracked_source_citations', side_effect=Exception("Test exception")):
            result = TextCleaner.clean_quiz_result(input_data)
            
            # Should return the original data unchanged
            assert result == input_data
            
            # Should log the error
            mock_logging_error.assert_called_once()
            assert "Test exception" in mock_logging_error.call_args[0][0]

    def test_clean_quiz_result_with_nested_structures(self):
        input_data = {
            "summary": "Summary [1]",
            "quiz": [
                {
                    "question": "Question [2]",
                    "options": [
                        "Option [3]",
                        {
                            "nested": "Nested text [4]",
                            "list": ["List item [5]", "Another item"]
                        }
                    ],
                    "answer": "Answer [6]",
                }
            ],
            "metadata": {
                "description": "Description [7]",
                "tags": ["Tag [8]", "Another tag"]
            }
        }
        
        expected_data = {
            "summary": "Summary",
            "quiz": [
                {
                    "question": "Question",
                    "options": [
                        "Option",
                        {
                            "nested": "Nested text [4]",  # Should not be cleaned (not in target fields)
                            "list": ["List item [5]", "Another item"]  # Should not be cleaned
                        }
                    ],
                    "answer": "Answer",
                }
            ],
            "metadata": {
                "description": "Description [7]",  # Should not be cleaned (not in target fields)
                "tags": ["Tag [8]", "Another tag"]  # Should not be cleaned
            }
        }
        
        result = TextCleaner.clean_quiz_result(input_data)
        assert result == expected_data

    def test_clean_quiz_result_with_multiple_quiz_items(self):
        input_data = {
            "summary": "Summary [1]",
            "quiz": [
                {
                    "question": "Question 1 [2]",
                    "options": ["Option A [3]", "Option B [4]"],
                    "answer": "Answer 1 [5]",
                },
                {
                    "question": "Question 2 [6]",
                    "options": ["Option C [7]", "Option D [8]"],
                    "answer": "Answer 2 [9]",
                },
                {
                    "question": "Question 3 [10]",
                    "options": ["Option E [11]", "Option F [12]"],
                    "answer": "Answer 3 [13]",
                }
            ]
        }
        
        expected_data = {
            "summary": "Summary",
            "quiz": [
                {
                    "question": "Question 1",
                    "options": ["Option A", "Option B"],
                    "answer": "Answer 1",
                },
                {
                    "question": "Question 2",
                    "options": ["Option C", "Option D"],
                    "answer": "Answer 2",
                },
                {
                    "question": "Question 3",
                    "options": ["Option E", "Option F"],
                    "answer": "Answer 3",
                }
            ]
        }
        
        result = TextCleaner.clean_quiz_result(input_data)
        assert result == expected_data