# storyboard-generator — AI 电影分镜助手 / AI Storyboard Assistant

一个 Claude Code skill，做两件事：

1. **风格反推**：多张参考截图（数量不限）→ 合成统一视觉风格 → 输出可复用的提示词前缀（中文在前、英文在后，电影摄影/调色术语，不含图中人物/物体/具体场景）
2. **分镜生成**：剧本 → 按 15–20 秒 / 3–5 镜拆分 → 空间与光线规划（人物代号、位置与动作、摄影机位置、光源方向，经用户确认）→ 每个镜头 7 个字段的双语分镜（镜号/时长/景别与摄影机/风格与光线/画面与动作/摄影机运动/台词），不使用表格

两阶段可独立使用，也可串联：先反推风格前缀，再以它为画面风格生成分镜。

## 安装

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Yiz-C/storyboard-generator.git ~/.claude/skills/storyboard-generator
```

## 使用

- 「帮我把这个剧本做成分镜」（+ 剧本）→ 阶段二
- 「分析这几张参考图的风格，写个可复用的提示词」（+ 截图，可粘贴或给文件路径）→ 阶段一
- 两者一起给 → 先阶段一，风格前缀自动成为阶段二画面风格

注意：图片分析需要视觉能力正常的会话；在无法显示图片的环境中，把截图内容用文字描述传入同样可以工作。

## 评测

`eval/` 是评测工作区：用例定义（`evals/evals.json`）、合成参考图生成器（`scripts/gen_fixtures.py`）、程序化断言（`scripts/check_assertions.py`）和迭代结果。

iteration-1（3 用例 × 有/无 skill 对比）：

| 用例 | 有 skill | 无 skill |
|---|---|---|
| 风格反推 | 6/6 (100%) | 2/6 (33%) |
| 分镜生成 | 7/7 (100%) | 0/7 (0%) |
| 全流程 | 7/7 (100%) | 1/7 (14%) |
| **合计** | **20/20 (100%)** | **3/20 (15.8%)** |

详细数据与逐条证据见 `eval/iteration-1/benchmark.json` 和各 run 目录下的 `grading.json`。

```bash
# 重新生成合成参考图
python3 eval/scripts/gen_fixtures.py
# 对某次输出跑程序化断言
python3 eval/scripts/check_assertions.py <output.md> <style-reversal|storyboard-script|full-pipeline>
```

---

# English

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
