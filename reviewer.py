import os
from dotenv import load_dotenv
import openai
import argparse


PROMPT = """
You will receive a file contents as text
Generate a code review for the file. Indicate what changes could be made to improve
its style, performance, readability, and maintainability. If there are any reputable
libraries that could be introduced to improve the code suggest them. Be kind and constructive.
For each suggested change, include lines number to which you are referring
"""

# FILE_CONTENT = """
# def mystery(x,y):
#     return x**y
# """


def code_review(file_path, model):
    """
    Purpose: Open the file to review the code by OPEN AI
    """

    with open(file_path, "r") as file:  # pylint: disable=unspecified-encoding
        # Comment:
        content = file.read()
    # end open file
    generated_code_review = make_code_review_request(content, model)
    print(
        "🐍 File: AI_practice/reviewer.py | Line: 33 | ~ generated_code_review"
    )
    print("🐍", generated_code_review)


def make_code_review_request(file_content, model):
    """
    Purpose: one
    """
    messages = [
        {"role": "system", "content": PROMPT},
        {
            "role": "user",
            "content": f"Code review the following file: {file_content}",
        },
    ]

    res = openai.ChatCompletion.create(model=model, messages=messages)
    return res["choices"][0]["message"]["content"]


# end def


def main():
    """
    Purpose: Getting the arguments on the script
    file: will be the file we are going to improve. Ex: `tree.py`
    model: The AI model we are going to use. Ex: `--model gpt-4`
    """
    parser = argparse.ArgumentParser(
        description="Simple code REviewer for a file"
    )
    parser.add_argument("file")
    parser.add_argument("--model", default="gpt-3.5-turbo")
    args = parser.parse_args()
    code_review("tree.py", args.model)


if __name__ == "__main__":
    load_dotenv()  # Using this it will automatic look on .env

    openai.api_key = os.getenv(
        "OPENAI_API_KEY"
    )  # Providing the specific variable I want
    main()
