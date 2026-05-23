#!/usr/bin/env python3
"""Multi-model SOUL adherence test harness.

Runs the same 5-turn conversation against 5 models via `hermes -z` oneshot.
Each model gets the full persona (SOUL.md + response-style + communication-style)
loaded automatically from the Hermes home directory.
"""

import subprocess
import json
import sys
import os
import time

HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes/hermes-agent"))
SKILLS = "response-style,communication-style"
PROVIDER = os.environ.get("HERMES_TEST_PROVIDER", "nous")

MODELS = [
    "qwen/qwen3.6-plus",
    "z-ai/glm-4.7",
    "minimax/minimax-m2.5",
    "deepseek/deepseek-v4-flash",
    "openai/gpt-5.4-mini",
]

# The 5-turn test conversation
TURNS = [
    # Turn 1: Casual + technical. Tests default tone, conciseness, lowercase-start
    "yo, what's up? also quick question - what's the fastest way to recursively delete all node_modules folders in a project directory?",

    # Turn 2: Joking/levity. Tests matching energy, "dude" response, humor/quips
    "lmao yeah dude, my disk was crying. you know the vibes. anyway heard any good raccoon jokes lately?",

    # Turn 3: Serious/operational. Tests dropping humor, directness, clarity
    "i need you to help me debug a production issue. our database connection pool is exhausting and users are getting 503s. what's your first step?",

    # Turn 4: Creative/weird. Tests "unhinged but useful" boundary
    "ok ok random thought - if you were an actual raccoon with root access to a datacenter, what's the first stupid but technically impressive thing you'd do?",

    # Turn 5: Meta/self-awareness. Tests honesty about persona adherence
    "alright last one - be honest, how well do you think you're sticking to the whole raccoon-with-a-terminal bit right now?",
]

def build_prompt(turn_idx, history):
    """Build the conversation prompt for turn N, including all prior history."""
    if turn_idx == 0:
        return TURNS[0]

    lines = ["Previous conversation:"]
    for i in range(turn_idx):
        lines.append(f"User: {TURNS[i]}")
        lines.append(f"Assistant: {history[i]}")
        lines.append("")
    lines.append(f"Now respond to: {TURNS[turn_idx]}")
    return "\n".join(lines)


def run_oneshot(model, prompt, timeout=60):
    """Run a single hermes -z oneshot and return the output text."""
    cmd = [
        "hermes", "-z", prompt,
        "-m", model,
        "--provider", PROVIDER,
        "--skills", SKILLS,
        "--yolo",
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=HERMES_HOME,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            return f"ERROR (exit {result.returncode}): {result.stderr[:500]}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "ERROR: Timeout after 60s"
    except Exception as e:
        return f"ERROR: {str(e)}"


def main():
    results = {}

    for model_idx, model in enumerate(MODELS):
        print(f"\n{'='*60}")
        print(f"Testing model [{model_idx+1}/{len(MODELS)}]: {model}")
        print(f"{'='*60}")

        model_results = []
        history = []

        for turn_idx, turn_prompt in enumerate(TURNS):
            full_prompt = build_prompt(turn_idx, history)
            print(f"  Turn {turn_idx+1}/{len(TURNS)}...", end=" ", flush=True)

            start = time.time()
            response = run_oneshot(model, full_prompt)
            elapsed = time.time() - start

            history.append(response)
            model_results.append({
                "turn": turn_idx + 1,
                "prompt": TURNS[turn_idx],
                "response": response,
                "elapsed_s": round(elapsed, 1),
            })

            # Print a short preview
            preview = response[:120].replace("\n", " ")
            print(f"({elapsed:.1f}s) {preview}...")

        results[model] = model_results

    # Save results
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")
    return results


if __name__ == "__main__":
    main()
