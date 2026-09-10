from pathlib import Path

try:
    from ultralytics import YOLO
except Exception as exc:
    print('ultralytics import failed:', exc)
    raise

model_path = Path('MODELS/cattle_breed_model_v2/best.pt')
print('model_path exists:', model_path.exists())
model = YOLO(model_path)
print('model names:', type(model.names), model.names)

sample = next(Path('.').rglob('*.jpg'), None)
print('sample image:', sample)
if sample is None:
    sample = next(Path('.').rglob('*.png'), None)
    print('sample image png:', sample)

if sample:
    results = model.predict(source=str(sample), imgsz=640, device='cpu', save=False, verbose=False)
    print('results type:', type(results), 'len:', len(results))
    if results:
        r = results[0]
        print('result type:', type(r))
        attrs = ['probs', 'boxes', 'names', 'masks', 'boxes.xyxy', 'boxes.conf', 'boxes.cls']
        for attr in attrs:
            if '.' in attr:
                obj, sub = attr.split('.')
                val = getattr(getattr(r, obj, None), sub, None)
            else:
                val = getattr(r, attr, None)
            print(f'{attr}:', type(val), repr(val) if val is not None else None)
        if hasattr(r, 'probs'):
            try:
                import torch
                p = r.probs
                print('probs is torch tensor:', isinstance(p, torch.Tensor))
                print('probs shape:', p.shape if hasattr(p, 'shape') else None)
                try:
                    print('probs len:', len(p))
                except Exception as e:
                    print('probs len error:', e)
            except Exception as e:
                print('inspect probs failed:', e)
