with open('/Users/david/사장님/guardian.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 관계 섹션 전체 제거
import re
c = re.sub(r'<div class="input-group">\s*<label class="input-label">관계</label>.*?</div>\s*</div>', '</div>', c, flags=re.DOTALL)

# selectRelation 함수도 필요없으니 selectedRelation 체크 제거
c = c.replace("if(!name||!phone||!selectedRelation){alert('정보를 모두 입력해주세요!');return;}", "if(!name||!phone){alert('이름과 전화번호를 입력해주세요!');return;}")
c = c.replace("{name,phone,relation:selectedRelation}", "{name,phone,relation:'가족'}")

with open('/Users/david/사장님/guardian.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('완료!')
