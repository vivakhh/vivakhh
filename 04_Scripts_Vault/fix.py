with open('/Users/david/사장님/guardian.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace(
    '<span>가족에게 알리기</span>',
    '<span>문자로 알리기 (SMS)</span>'
)
c = c.replace(
    'id="kakao-btn">',
    'id="sms-btn" style="background:#1a73e8;margin-bottom:12px">'
)
c = c.replace(
    "window.open(`https://sharer.kakao.com/talk/friends/picker/easylink?app_key=8088ae3fd80ed9cb91544a037bce4c63",
    "const ph=guardians[0].phone.replace(/-/g,''); window.location.href='sms:'+ph+'?body='+encodedMsg; //"
)
with open('/Users/david/사장님/guardian.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('완료!')
