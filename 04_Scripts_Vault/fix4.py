with open('/Users/david/사장님/guardian.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace(
    '가족에게 현재 약 드신 상태를<br>카톡으로 즉시 공유할 수 있습니다.',
    '가족에게 약 복용 상태를<br>문자(SMS)로 즉시 알릴 수 있습니다.'
)
c = c.replace(
    '카톡 가족 알림',
    '가족 알림'
)
with open('/Users/david/사장님/guardian.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('완료!')
