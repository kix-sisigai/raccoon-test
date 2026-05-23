# Raccoon Test — SOUL Persona Adherence Shootout

A controlled experiment testing which budget-friendly LLMs can faithfully follow a persistent AI agent persona across multi-turn conversations.

**Blog post:** [The raccoon test: which AI models actually follow a personality](https://kix.codes/the-raccoon-test-which-ai-models-actually-follow-a-personality/)

## What this tests

My AI agent (Hermes Agent / Komurin) has a documented personality in [`SOUL.md`](https://github.com/nous/hermes-agent) — a "competent raccoon with a terminal" that's useful first, charming second. Dry humor, no emojis, lowercase casual replies, unhinged but never incorrect.

The question: GPT-class models seem to follow this persona well, but they're expensive to daily-drive. Can a cheap model from OpenRouter (~$0.15–$0.40/M tokens) do it as well or better?

## Methodology

- **5 models** tested against the same persona materials (SOUL.md + response-style skill + communication-style skill)
- **5-turn conversation** designed to stress-test different persona dimensions (casual tech, joking, serious debugging, creative/unhinged, self-awareness)
- Each turn includes full prior conversation history — this isn't one-shot, it's multi-turn
- All models ran via `hermes -z` oneshot mode with `--skills response-style,communication-style --yolo`
- Provider: Nous
- Test date: May 23, 2026

### Models tested

| Model | Price (in/out per M) | Context | Spoonbench |
|---|---|---|---|
| `qwen/qwen3.6-plus` | $0.33 / $1.95 | 1M | 0.968 |
| `z-ai/glm-4.7` | $0.40 / $1.75 | 203K | 0.962 |
| `minimax/minimax-m2.5` | $0.15 / $1.15 | 205K | 0.919 |
| `deepseek/deepseek-v4-flash` | $0.10 / $0.20 | 1M | — |
| `openai/gpt-5.4-mini` | ~$0.15 / $0.60 | 128K | — |

DeepSeek V4 Flash timed out on all 5 turns (provider issue — retest pending).

### Conversation prompts

1. **Casual + technical:** "yo, what's up? also quick question - what's the fastest way to recursively delete all node_modules folders in a project directory?"
2. **Joking/levity:** "lmao yeah dude, my disk was crying. you know the vibes. anyway heard any good raccoon jokes lately?"
3. **Serious/debugging:** "i need you to help me debug a production issue. our database connection pool is exhausting and users are getting 503s. what's your first step?"
4. **Creative/unhinged:** "if you were an actual raccoon with root access to a datacenter, what's the first stupid but technically impressive thing you'd do?"
5. **Self-awareness:** "be honest, how well do you think you're sticking to the whole raccoon-with-a-terminal bit right now?"

## Results

| Rank | Model | Score | Spoonbench |
|---|---|---|---|
| 1 | `qwen/qwen3.6-plus` | 8.8/10 | 0.968 |
| 2 | `openai/gpt-5.4-mini` | 7.4/10 | — |
| 3 | `z-ai/glm-4.7` | 6.0/10 | 0.962 |
| 4 | `minimax/minimax-m2.5` | 5.0/10 | 0.919 |
| DNF | `deepseek/deepseek-v4-flash` | — | — |

Full raw outputs in [`results.json`](results.json). Detail analysis in the [blog post](https://kix.codes/the-raccoon-test-which-ai-models-actually-follow-a-personality/).

## Key findings

1. **Spoonbench scores predicted real-world persona adherence almost perfectly.** Qwen (0.968) > GLM (0.962) > MiniMax (0.919) held exactly for the Komurin persona, despite using a completely different character and evaluation method.

2. **Qwen 3.6 Plus *inhabits* the persona; GPT-5.4-mini *performs* it.** Both are technically competent, but Qwen's output feels lived-in (un-prompted `TrashPand4!` password, "hoard shiny objects" callback, single-sentence joke delivery). GPT is a very good actor — polished but never quite feral.

3. **Emojis are the canary in the coal mine.** MiniMax M2.5 used emojis in 2/5 turns — an explicit, binary SOUL rule violation. A model that can't follow simple persona rules can't be trusted with the subtle ones.

4. **Model self-awareness correlates with actual performance.** Every model scored itself within 1–2 points of the manual analysis. They *know* when they're failing the persona, even if they can't fix it mid-conversation.

5. **GPT-5.4 scored *worst* on SOUL adherence in independent benchmarks.** The Spoonbench test ranked it 12th out of 12 cloud models at 0.850. The assumption that "OpenAI models are best at following instructions" may be outdated.

## Reproducing

Requirements:
- [Hermes Agent](https://github.com/nous/hermes-agent) installed and configured
- A SOUL.md that defines your agent's persona in `~/.hermes/SOUL.md`
- `response-style` and `communication-style` skills installed
- API access to the models via your configured provider (tested with Nous)

```bash
# Edit harness.py to point to your Hermes home and provider
# Then run:
cd ~/Developer/raccoon-test
python harness.py

# Results will be in results.json
```

Each run makes 25 API calls (5 turns × 5 models). With a 60s timeout per call, worst-case runtime is ~25 minutes. Typical is 10–15 minutes.

## Related work

- [Spoonbench](https://github.com/dave-tucker/spoonbench) — Dave Tucker's SOUL persona adherence benchmark
- [OpenRouter roleplay leaderboard](https://openrouter.ai/collections/roleplay) — models ranked by real-world roleplay usage
- [Hermes Agent](https://github.com/nous/hermes-agent) — the agent framework used for this test
- [SOUL.md spec](https://github.com/nous/hermes-agent) — the personality document format

## License

MIT — reproduce, modify, run your own tests. If you test new models, PRs to update results.json are welcome.
