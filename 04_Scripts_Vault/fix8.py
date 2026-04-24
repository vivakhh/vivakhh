with open('/Users/david/사장님/guardian.html', 'r', encoding='utf-8') as f:
    c = f.read()

# "가족 등록 완료" 버튼 완전 제거
import re
c = re.sub(r'<button class="add-btn"[^>]*>가족 등록 완료</button>', '', c)

# add-card가 2명일때 숨김 - 이미 있는 로직 수정
c = c.replace(
    "if(guardians.length>=2){\n    addCard.style.display='none';",
    "if(guardians.length>=2){\n    addCard.style.display='none';\n    document.querySelector('.kakao-section').style.marginTop='24px';"
)

with open('/Users/david/사장님/guardian.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('완료!')
