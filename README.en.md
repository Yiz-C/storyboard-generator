# storyboard-generator — AI Storyboard Assistant

[中文](README.md) | English

A Claude Code skill that does two things:

1. **Style reversal**: multiple reference stills (any number) → a unified visual style → a reusable prompt prefix (Chinese first, English after; professional cinematography and colour-grading terminology; no characters, objects or specific settings from the stills)
2. **Storyboard generation**: a script → split into groups of ~15–20 s / 3–5 shots → a spatial and lighting plan (character IDs, positions and actions, camera position, light direction, confirmed by the user) → bilingual shot descriptions with 7 fields each (Shot / Duration / Framing and camera / Style and lighting / Image and action / Camera movement / Dialogue), without tables

The two stages work independently or chained: extract the style prefix first, then use it as the visual style for storyboarding.

## Installation

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Yiz-C/storyboard-generator.git ~/.claude/skills/storyboard-generator
```

## Usage

- "Turn this script into a storyboard" (+ script) → Stage 2
- "Analyse the style of these reference stills and write a reusable prompt" (+ stills, pasted or as file paths) → Stage 1
- Provide both → Stage 1 first, then the style prefix automatically becomes the visual style for Stage 2

Note: image analysis requires a vision-capable session. In environments where images cannot be displayed, passing textual descriptions of the stills works the same way.

## Evals

`eval/` is the evaluation workspace: test-case definitions (`evals/evals.json`), a synthetic reference-still generator (`scripts/gen_fixtures.py`), programmatic assertion checks (`scripts/check_assertions.py`) and iteration results.

Iteration 1 (3 test cases × with/without skill):

| Test case | With skill | Without skill |
|---|---|---|
| Style reversal | 6/6 (100%) | 2/6 (33%) |
| Storyboard generation | 7/7 (100%) | 0/7 (0%) |
| Full pipeline | 7/7 (100%) | 1/7 (14%) |
| **Total** | **20/20 (100%)** | **3/20 (15.8%)** |

Detailed data and per-assertion evidence live in `eval/iteration-1/benchmark.json` and each run's `grading.json`.

```bash
# Regenerate the synthetic reference stills
python3 eval/scripts/gen_fixtures.py
# Run programmatic assertions on an output
python3 eval/scripts/check_assertions.py <output.md> <style-reversal|storyboard-script|full-pipeline>
```
