"""Programmatic assertion checks for storyboard-generator eval outputs.

Usage:
    python3 check_assertions.py <output.md> <eval_name> [--json]

Prints one line per checkable assertion: PASS | FAIL | GRADER (needs human/agent
judgment). Semantic assertions print GRADER and are graded separately.
"""
import json
import re
import sys

CJK = re.compile(r"[一-鿿]")
ASCII = re.compile(r"[A-Za-z]{4,}")

STYLE_TERMS = [
    "影调", "色调", "色温", "饱和度", "对比度", "高光", "阴影", "暗部",
    "主光", "低调", "高反差", "胶片", "颗粒", "剪影", "补色", "互补",
    "tonal", "palette", "temperature", "saturation", "contrast",
    "highlight", "shadow", "key light", "low-key", "film grain",
    "teal", "cyan", "orange", "amber", "complementary", "colour grade",
]
OBJECT_WORDS = ["球", "桌面", "桌子", "窗户", "建筑", "水面",
                "sphere", "ball", "table", "window", "building", "water"]
SCENE_WORDS = ["街道", "城市", "码头", "港口",
               "street", "city", "dock", "harbour", "waterfront"]
PALETTE_WORDS = ["暖", "冷", "青", "橙", "蓝",
                 "warm", "cool", "teal", "cyan", "orange", "amber", "blue"]


def found(text, keys):
    low = text.lower()
    return [k for k in keys if k.lower() in low]


def check_cine_terms(t):
    hits = found(t, STYLE_TERMS)
    return len(hits) >= 2, f"hit terms: {hits[:6]}"


def check_no_objects(t):
    hits = found(t, OBJECT_WORDS)
    return not hits, f"banned found: {hits}" if hits else "none"


def check_no_scene(t):
    hits = found(t, SCENE_WORDS)
    return not hits, f"banned found: {hits}" if hits else "none"


def check_bilingual_order(t):
    c = CJK.search(t)
    e = ASCII.search(t)
    if c is None or e is None:
        return False, f"cjk@{c.start() if c else None} ascii@{e.start() if e else None}"
    n_ascii = len(re.findall(r"[A-Za-z]", t))
    ok = c.start() < e.start() and n_ascii >= 100
    return ok, f"first CJK@{c.start()} first EN@{e.start()} EN letters={n_ascii}"


def check_ack(t):
    hits = found(t, ["收到剧本", "建议拆分", "script received"])
    return bool(hits), f"found: {hits}" if hits else "none"


def check_spatial(t):
    missing = []
    if "@1" not in t and "@1：" not in t:
        missing.append("人物代号(@1)")
    if "摄影机" not in t:
        missing.append("摄影机位置")
    if "光源" not in t:
        missing.append("光源方向")
    return not missing, f"missing: {missing}" if missing else "all present"


def shot_blocks(t):
    idxs = [m.start() for m in re.finditer(r"镜号", t)]
    blocks = []
    for i, s in enumerate(idxs):
        e = idxs[i + 1] if i + 1 < len(idxs) else len(t)
        blocks.append(t[s:e])
    return blocks


def check_fields7(t):
    blocks = shot_blocks(t)
    if not blocks:
        return False, "no 镜号 found"
    need = ["时长", "景别与摄影机", "风格与光线", "画面与动作", "摄影机运动", "台词"]
    bad = []
    for i, b in enumerate(blocks, 1):
        miss = [k for k in need if k not in b]
        if miss:
            bad.append(f"shot{i}: missing {miss}")
    return not bad, f"{len(blocks)} shots" + (f", {bad[:3]}" if bad else ", all fields present")


def check_shots_count(t):
    n = len(shot_blocks(t))
    return 3 <= n <= 5, f"{n} shots"


def check_bilingual_labels(t):
    low = t.lower()
    labels = ["shot:", "duration:", "style and lighting:", "image and action:",
              "camera movement:", "dialogue:"]
    framing = ("framing and camera:" in low) or ("framing & camera:" in low)
    hits = [l for l in labels if l in low]
    if framing:
        hits.append("framing and camera:")
    return len(hits) == 7, f"found {len(hits)}/7: {hits}"


def check_no_table(t):
    has_table = re.search(r"\|\s*-{2,}", t) is not None
    return not has_table, "table separator found" if has_table else "no table"


def check_closing_q(t):
    hits = found(t, ["是否符合预期", "继续规划"])
    return bool(hits), f"found: {hits}" if hits else "none"


def check_style_in_shots(t):
    style_lines = [ln for ln in t.splitlines()
                   if "风格与光线" in ln or "style and lighting" in ln.lower()]
    hits = [w for ln in style_lines for w in found(ln, PALETTE_WORDS)]
    return bool(hits), f"palette words in style lines: {hits[:8]}" if hits else "no palette words in style lines"


def check_no_style_requestion(t):
    bad = [ln for ln in t.splitlines()
           if "画面风格" in ln and ("？" in ln or "?" in ln)]
    return not bad, f"questioning lines: {bad[:2]}" if bad else "none"


CHECKS = {
    "style-reversal": [
        ("输出是可直接复用的提示词前缀，而不是逐图分析报告", "GRADER"),
        ("三张图合成为一个统一风格前缀，而非三份独立输出", "GRADER"),
        ("使用至少 2 个电影摄影/调色专业术语（影调、色调、色温、饱和度、对比度、高光、阴影、主光、低调照明、胶片颗粒等）", check_cine_terms),
        ("前缀不出现图中标志性物体（球、桌面、窗户、建筑、水面）", check_no_objects),
        ("前缀不出现具体场景名词（街道、城市、码头、港口）", check_no_scene),
        ("中文输出在前，英文输出在后", check_bilingual_order),
    ],
    "storyboard-script": [
        ("开头确认收到剧本并给出拆分建议", check_ack),
        ("包含空间规划四要素：人物代号、人物位置与动作、摄影机位置、光源方向", check_spatial),
        ("第一组每个镜头含全部 7 个字段（镜号/时长/景别与摄影机/风格与光线/画面与动作/摄影机运动/台词）", check_fields7),
        ("第一组镜头数为 3–5 个", check_shots_count),
        ("每个字段中英双语（对应英文标签 Shot/Duration/Framing and camera/Style and lighting/Image and action/Camera movement/Dialogue）", check_bilingual_labels),
        ("不使用 Markdown 表格", check_no_table),
        ("结尾询问本组是否符合预期、是否继续下一组", check_closing_q),
    ],
    "full-pipeline": [
        ("先输出风格前缀，再输出分镜", "GRADER"),
        ("风格前缀中英双语", "GRADER"),
        ("分镜中每个镜头的【风格与光线】体现前缀的色调（如暖橙/冷青/teal/warm/cool 等关键词）", check_style_in_shots),
        ("不再向用户询问画面风格（不重复提问已从参考图获得的信息）", check_no_style_requestion),
        ("第一组每个镜头含全部 7 个字段", check_fields7),
        ("每个字段中英双语", check_bilingual_labels),
        ("不使用 Markdown 表格", check_no_table),
    ],
}


def main():
    path, eval_name = sys.argv[1], sys.argv[2]
    with open(path, encoding="utf-8") as f:
        text = f.read()
    results = []
    for assertion, check in CHECKS[eval_name]:
        if check == "GRADER":
            results.append({"text": assertion, "passed": None, "evidence": "needs grader judgment"})
            continue
        passed, evidence = check(text)
        results.append({"text": assertion, "passed": passed, "evidence": evidence})
        status = "PASS" if passed else "FAIL"
        print(f"{status} | {assertion[:50]} | {evidence}")
    out = path.rsplit("/", 1)[0] + "/script_checks.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
