from pathlib import Path
import json
import torch
from ultralytics import YOLO
from PIL import Image
import numpy as np

model_path = Path('MODELS/cattle_breed_model_v2/best.pt')
cls_path = Path('MODELS/class_names.json')
print('model exists', model_path.exists())
print('class names exists', cls_path.exists())
if not model_path.exists() or not cls_path.exists():
    raise SystemExit('missing model or class names')
with open(cls_path) as f:
    class_names = json.load(f)
print('class count', len(class_names))

model = YOLO(model_path)
print('model names count', len(model.names))

img = next(Path('NEW_DATASET/train').rglob('*.jpg'), None)
print('sample image', img)
if img is None:
    raise SystemExit('no image sample')

img_arr = np.array(Image.open(img).convert('RGB'))
results = model.predict(source=img_arr, device='cpu', imgsz=640, save=False, verbose=False)
print('results len', len(results))
res = results[0]
print('has probs', hasattr(res, 'probs'))
probs = getattr(res, 'probs', None)
print('probs', type(probs), probs)
print('probs data type', type(getattr(probs, 'data', probs)))

scores = getattr(probs, 'data', probs)
if not isinstance(scores, torch.Tensor):
    scores = torch.as_tensor(scores, device='cpu')
else:
    scores = scores.to('cpu')
print('scores shape', scores.shape, 'dim', scores.dim())
print('scores len', len(scores))
print('topk begin')
top5_probs, top5_idx = torch.topk(scores, k=min(5, len(class_names)))
print('topk done', top5_probs, top5_idx)
print('top5', [class_names[i.item()] for i in top5_idx])
print('done')
