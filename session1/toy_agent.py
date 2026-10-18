"""Section 7 — the hand-rolled agent loop, before any framework.

Same one-shot call as plain_call.py, now called in a LOOP with a tool it can
choose to use. Nothing was upgraded: we only changed how many times we call the
model and what we feed back in.

    python toy_agent.py
"""
from plain_call import ask_llm

MAX_STEPS = 5

# A tool is just a function the model is allowed to call. This one is faked so
# the session runs offline and deterministically — Session 2 replaces it with
# the real tools in ../tools.py.
FAKE_RESULTS = {
    "csk playing xi": "Gaikwad, Dhoni, Jadeja, Pathirana, Chahar confirmed. Pathirana back from a niggle.",
    "mi playing xi":  "Rohit, Bumrah, Hardik, Tilak Varma confirmed.",
    "pitch":          "Chepauk: slow turner, spinners favoured, chasing is hard.",
}


def web_search(query: str) -> str:
    """Pretend to search the web. Returns a canned line for a few known queries."""
    for key, value in FAKE_RESULTS.items():
        if key in query.lower():
            return value
    return f"No results for '{query}'. Try: CSK playing XI, MI playing XI, pitch."


SYSTEM = """Each turn reply with ONE line:
THINK: <reasoning>
ACTION: search <query>   # to look something up
ANSWER: <final answer>   # when you're done"""


def run(task: str, verbose: bool = True) -> str:
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user",   "content": task}]

    for step in range(MAX_STEPS):          # never loop forever
        reply = ask_llm(messages)          # one model call
        messages.append({"role": "assistant", "content": reply})
        if verbose:
            print(f"[{step + 1}] {reply.strip()}")

        if "ANSWER:" in reply:
            return reply.split("ANSWER:", 1)[1].strip()

        if "ACTION: search" in reply:
            query = reply.split("ACTION: search", 1)[1].strip().splitlines()[0]
            observation = web_search(query)          # run the tool
            if verbose:
                print(f"    OBS  {observation}")
            messages.append({"role": "user", "content": f"OBSERVATION: {observation}"})

    return "(hit the step limit without answering)"


if __name__ == "__main__":
    print(run("Who should I captain for CSK vs MI at Chepauk?"))
