import json
import sys


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    Rule of thumb: 1 token ~= 4 characters.
    """
    if not text:
        return 0
    return len(text) // 4


def estimate_tokens_from_file(file_path: str) -> int:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return estimate_tokens(content)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return 0


def estimate_tokens_from_json(data) -> int:
    text = json.dumps(data)
    return estimate_tokens(text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python estimate_token_usage.py <file_path_or_string>")
        sys.exit(1)

    input_arg = sys.argv[1]

    # Check if it's a file
    import os

    if os.path.exists(input_arg):
        tokens = estimate_tokens_from_file(input_arg)
        print(f"Estimated tokens in file '{input_arg}': {tokens}")
    else:
        tokens = estimate_tokens(input_arg)
        print(f"Estimated tokens in string: {tokens}")
