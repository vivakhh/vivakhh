with open('/Users/david/사장님/guardian.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 정확한 텍스트로 교체
idx = c.find('가족에게 현재 약 드신 상태를')
if idx >= 0:
    end = c.find('</p>', idx)
    old_text = c[idx:end]
    print('찾은 텍스트:', repr(old_text))
    c = c[:idx] + '가족에게 약 복용 상태를\n    문자(SMS)로 즉시 알릴 수 있습니다.' + c[end:]
    with open('/Users/david/사장님/guardian.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print('완료!')
else:
    print('텍스트를 못 찾았습니다')
