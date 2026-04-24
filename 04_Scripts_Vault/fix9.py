with open('/Users/david/사장님/community.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 빠른 버튼 그룹 전체 제거
import re
c = re.sub(r'<div class="quick-cheer-group">.*?</div>', '', c, flags=re.DOTALL)

with open('/Users/david/사장님/community.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('완료!')
