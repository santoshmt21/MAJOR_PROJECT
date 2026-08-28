from pathlib import Path
import json
p=Path('cattle_dataset/train')
if not p.exists():
    print('train path missing', p)
    raise SystemExit(1)
classes=sorted([d.name for d in p.iterdir() if d.is_dir()])
out=Path('MODELS/class_names.json')
out.parent.mkdir(parents=True, exist_ok=True)
with open(out,'w') as f:
    json.dump(classes,f,indent=2)
print('wrote', out)
print('num classes', len(classes))
