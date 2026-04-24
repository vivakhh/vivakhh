with open('/Users/david/사장님/guardian.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 2명 다 됐을 때 "가족 등록 완료" 버튼 숨기기
c = c.replace(
    "document.getElementById('add-btn')",
    "document.getElementById('add-btn')"
)

# add-btn이 add-card 안에 있으니까 add-card 자체를 숨김 처리
old = "  if(guardians.length>=2){\n    addCard.innerHTML=`<div style=\"background:rgba(0,229,255,0.05); border:1px solid var(--primary-container); border-radius:20px; padding:20px; text-align:center; color:var(--primary-container); font-size:14px; font-weight:700\">✅ 가족 2명이 모두 등록되었습니다.<br><span style=\"font-size:12px; font-weight:400; color:rgba(255,255,255,0.3)\">가족을 변경하려면 아래 삭제 버튼을 눌러주세요.</span></div>`;"
new = "  if(guardians.length>=2){\n    addCard.style.display='none';"

c = c.replace(old, new)

with open('/Users/david/사장님/guardian.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('완료!')
