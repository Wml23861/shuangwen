# -*- coding: utf-8 -*-
import re, sys

path = r"E:\爽文\新书项目\正文\第一卷\05_第五章_周家的价码.md"
with open(path, encoding="utf-8") as f:
    text = f.read()

lines = [l for l in text.split("\n") if l.strip() and not l.startswith("#")]
body = "\n".join(lines)

hanzi = len(re.findall(r"[一-鿿]", body))

# split into sentences by 。！？“” boundaries keeping quote sentences
sents = re.split(r"(?<=[。！？])", body.replace("\n", ""))
sents = [s.strip() for s in sents if s.strip()]

def hz(s): return len(re.findall(r"[一-鿿]", s))

short = sum(1 for s in sents if hz(s) <= 10)
long_sents = [(hz(s), s) for s in sents if hz(s) > 30]
quote_sents = [s for s in sents if "“" in s]
q_marks = body.count("？")
excl = body.count("！")
modal = sum(body.count(w) for w in ["呢", "吧", "啊", "嘛"])

print(f"汉字: {hanzi}")
print(f"总句数: {len(sents)}")
print(f"短句(<=10字): {short} ({short*100//len(sents)}%)")
print(f"长句(>30字): {len(long_sents)}")
for n, s in long_sents: print(f"   [{n}字] {s[:50]}")
print(f"引号句: {len(quote_sents)}")
print(f"问句(？): {q_marks}")
print(f"感叹号(！): {excl}")
print(f"语气词(呢吧啊嘛): {modal}")

# red lines
for pat, name in [(r"——|—|–|－", "破折号"), (r"……|\.\.\.", "省略号"), (r"忽然|突然", "忽然/突然"),
                  (r"作者|读者|小说|剧情|上一章|下一章|本章", "元叙事")]:
    m = re.findall(pat, body)
    if m: print(f"红线[{name}]: {len(m)} 处 {m[:5]}")

# paragraph-initial punctuation (excluding opening quote)
bad_para = [l[:20] for l in lines if re.match(r"^[，。！？、；：）]", l)]
if bad_para: print(f"段首标点: {bad_para}")

# 地说 check
m = re.findall(r"\w+地说", body)
if m: print(f"对话副词标签: {m}")

# 金句-ish / 作者腔 check
for pat in ["他终于", "这一刻", "原来", "所谓", "这就是", "从这一刻"]:
    if pat in body: print(f"作者腔[{pat}]: 命中")
