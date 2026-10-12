#!/bin/bash
# full render: 30 fps, 5 subframes per frame across a 180° shutter, float blend, BT.709 encode
T=/home/user/ApoheniaQuest/.claude/skills/jason-ad-film/tools
for s in ${SCENES:-persp indef high chosen}; do
  python3 - "$s" <<'PY'
import json,sys,re
s=sys.argv[1]; src=open('scenes.js').read()
L=int(re.search(s+r':\s*\{\s*len:\s*(\d+)',src).group(1))//2
n=5; plan=[{'o':f'{s}_{f:04d}_{k}.png','t':(f+k/n*0.5)/30,'f':f} for f in range(L) for k in range(n)]
json.dump(plan,open(f'plan_{s}.json','w'))
PY
  HTML="ins.html?s=$s" node render2.js plan_$s.json smp_$s 6 > /dev/null
  python3 $T/blend.py smp_$s plan_$s.json bl_$s > /dev/null
  ffmpeg -v error -y -framerate 30 -i bl_$s/f%04d.png -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 ins_$s.mp4
  rm -rf smp_$s; echo done $s
done
