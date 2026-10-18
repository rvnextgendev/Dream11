"""Section 1 — the one-shot call. This is the 'before' half of the whole session.

Run it, ask it a question about today's match, and watch it answer confidently
from stale training data with no way to check anything. That gap is the reason
the rest of the course exists.

    python plain_call.py
"""
from dotenv import load_dotenv, find_dotenv
from groq import Groq

# The Groq SDK reads GROQ_API_KEY from the ENVIRONMENT, not from .env on its own —
# so load the .env first. Forgetting this line is the most common Session 1 error.
load_dotenv(find_dotenv(usecwd=True))

MODEL = "openai/gpt-oss-120b"
client = Groq()


def ask_llm(messages: list[dict]) -> str:
    """One model call in, one string out. Used by toy_agent.py too."""
    resp = client.chat.completions.create(model=MODEL, messages=messages)
    return resp.choices[0].message.content


if __name__ == "__main__":
    answer = ask_llm([{"role": "user", "content": "Who should I captain today?"}])
    print(answer)
    print("\n-- notice: a confident guess, from stale training data,")
    print("   with no way to check today's line-up.")
