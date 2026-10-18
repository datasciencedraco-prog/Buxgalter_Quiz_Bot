"""
Unit tests for the DOCX question parser.
Creates an in-memory .docx file matching the +++/=== template and asserts correct answers and options.
"""

import io
from docx import Document
import pytest

from parser import parse_docx, parse_text, parse_question_block


def create_in_memory_docx(text_content: str) -> io.BytesIO:
    """Helper to build an in-memory DOCX file from string content."""
    doc = Document()
    for line in text_content.split("\n"):
        doc.add_paragraph(line)
    stream = io.BytesIO()
    doc.save(stream)
    stream.seek(0)
    return stream


def test_standard_hash_marker_in_docx():
    content = """+++
What is the capital of Uzbekistan?
===
Samarkand
===
#Tashkent
===
Bukhara
+++"""
    stream = create_in_memory_docx(content)
    questions = parse_docx(stream)
    assert len(questions) == 1
    q = questions[0]
    assert q["question"] == "What is the capital of Uzbekistan?"
    assert len(q["options"]) == 3
    assert q["options"] == ["Samarkand", "Tashkent", "Bukhara"]
    assert q["correct_option_id"] == 1
    assert q["options"][q["correct_option_id"]] == "Tashkent"


def test_plus_marker_in_docx():
    content = """+++
Which planet is closest to the Sun?
===
+ Mercury
===
Venus
===
Earth
===
Mars
+++"""
    stream = create_in_memory_docx(content)
    questions = parse_docx(stream)
    assert len(questions) == 1
    q = questions[0]
    assert q["question"] == "Which planet is closest to the Sun?"
    assert len(q["options"]) == 4
    assert q["correct_option_id"] == 0
    assert q["options"][0] == "Mercury"


def test_check_emoji_and_symbol_markers():
    content = """+++
What is 2 + 2?
===
3
===
✅ 4
===
5
+++
+++
What is the speed of light approximately?
===
100 km/s
===
✓ 300,000 km/s
===
1,000,000 km/s
+++"""
    stream = create_in_memory_docx(content)
    questions = parse_docx(stream)
    assert len(questions) == 2

    # Check first question (emoji check mark)
    assert questions[0]["question"] == "What is 2 + 2?"
    assert questions[0]["options"] == ["3", "4", "5"]
    assert questions[0]["correct_option_id"] == 1

    # Check second question (unicode check mark)
    assert questions[1]["question"] == "What is the speed of light approximately?"
    assert questions[1]["options"] == ["100 km/s", "300,000 km/s", "1,000,000 km/s"]
    assert questions[1]["correct_option_id"] == 1


def test_boundary_options_lengths():
    # Test min options (2 options)
    min_content = """+++
Is Python interpreted?
===
#Yes
===
No
+++"""
    q_min = parse_docx(create_in_memory_docx(min_content))
    assert len(q_min) == 1
    assert len(q_min[0]["options"]) == 2
    assert q_min[0]["correct_option_id"] == 0
    assert q_min[0]["options"][0] == "Yes"

    # Test max options (10 options)
    options_text = "\n===\n".join([f"Option {i}" if i != 5 else f"#Option {i}" for i in range(1, 11)])
    max_content = f"+++\nChoose option 5\n===\n{options_text}\n+++"
    q_max = parse_docx(create_in_memory_docx(max_content))
    assert len(q_max) == 1
    assert len(q_max[0]["options"]) == 10
    assert q_max[0]["correct_option_id"] == 4
    assert q_max[0]["options"][4] == "Option 5"


def test_malformed_blocks_ignored_gracefully():
    content = """+++
Only one option (invalid)
===
#Single Option
+++
+++
Too many options (> 10 options)
===
#Opt 1
===
Opt 2
===
Opt 3
===
Opt 4
===
Opt 5
===
Opt 6
===
Opt 7
===
Opt 8
===
Opt 9
===
Opt 10
===
Opt 11
+++
+++
No correct marker
===
Option A
===
Option B
+++
+++
Multiple correct markers
===
#Option A
===
+Option B
===
Option C
+++
+++
Valid Question
===
Wrong
===
#Right
+++"""
    stream = create_in_memory_docx(content)
    questions = parse_docx(stream)
    # Only the last valid question should be parsed
    assert len(questions) == 1
    assert questions[0]["question"] == "Valid Question"
    assert questions[0]["options"] == ["Wrong", "Right"]
    assert questions[0]["correct_option_id"] == 1


def test_marker_stripping_and_whitespace():
    content = """+++
Testing marker cleanup
===
#    Leading Spaces Removed   
===
Normal Option
+++"""
    questions = parse_docx(create_in_memory_docx(content))
    assert len(questions) == 1
    assert questions[0]["options"][0] == "Leading Spaces Removed"
    assert questions[0]["correct_option_id"] == 0
