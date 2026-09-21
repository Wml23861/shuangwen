import re, sys
path = sys.argv[1] if len(sys.argv) > 1 else r'E:\爽文\新书项目\正文\第一卷\05_第五章_内部价.md'
text = open(path, encoding='utf-8').read()
body = re.sub(r'^#.*$', '', text, flags=re.M)
hanzi = len(re.findall(r'[一-鿿]', body))
sents = [s for s in re.split(r'[。？！]', body) if re.search(r'[一-鿿]', s)]
def slen(s): return len(re.findall(r'[一-鿿]', s))
short = sum(1 for s in sents if slen(s) <= 10)
long_ = sum(1 for s in sents if slen(s) > 30)
quotes = len(re.findall(r'“[^”]*”', body))
q = body.count('？')
ex = body.count('！')
yj = sum(body.count(w) for w in ['呢', '吧', '啊', '嘛'])
dash = body.count('——')
ell = body.count('……')
sudden = len(re.findall(r'忽然|突然', body))
bad_para = len(re.findall(r'\n\s*[—…]', body))
meta = len(re.findall(r'于是|然后|他意识到', body))
print(f'汉字:{hanzi} 句:{len(sents)} 短句:{short}({short*100//len(sents)}%) 长句:{long_} 引号句:{quotes} 问句:{q} 感叹号:{ex} 语气词:{yj}')
print(f'红线: 破折号:{dash} 省略号:{ell} 忽然突然:{sudden} 段首标点:{bad_para} 于是/然后/他意识到:{meta}')
for s in sents:
    if slen(s) > 30:
        print('LONG:', s.strip().replace(chr(10), '/'))
