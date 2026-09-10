from pathlib import Path
import json
import torch
import numpy as np
from PIL import Image

print('device', torch.device('cuda' if torch.cuda.is_available() else 'cpu'))

# load class names
cls_path = Path('MODELS/class_names.json')
with open(cls_path) as f:
    class_names = json.load(f)
print('loaded class names', len(class_names))

# load YOLO
from ultralytics import YOLO
yolo_path = Path('MODELS/cattle_breed_model_v2/best.pt')
print('yolo exists', yolo_path.exists())
YOLO_MODEL = YOLO(yolo_path)
print('yolo names len', len(YOLO_MODEL.names))

# load ViT if exists
vit_path = Path('MODELS/ViT_Results_85Plus/best_vit_small_patch16_224_cattle.pth')
VIT_MODEL = None
if vit_path.exists():
    import timm
    ckpt = torch.load(vit_path, map_location='cpu')
    # find state dict
    state_dict = (
        ckpt.get('model_state_dict')
        or ckpt.get('state_dict')
        or ckpt.get('model')
        or (ckpt if isinstance(ckpt, dict) and any(k.startswith(('blocks.','patch_embed.','cls_token')) for k in ckpt) else None)
    )
    if state_dict is None:
        print('vit: no state_dict found, skipping ViT')
    else:
        head_key = next((k for k in state_dict if k in ('head.weight','classifier.weight','fc.weight')), None)
        if head_key is None:
            print('vit: no head key found, skipping ViT')
        else:
            num_classes = state_dict[head_key].shape[0]
            model = timm.create_model('vit_small_patch16_224', pretrained=False, num_classes=num_classes)
            model.load_state_dict(state_dict, strict=True)
            model.eval()
            VIT_MODEL = model
            print('vit loaded num_classes', num_classes)
else:
    print('vit checkpoint not found at', vit_path)

# prepare ViT transform
from torchvision import transforms
VIT_TRANSFORM = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])

# choose sample images from val
img_paths = list(Path('cattle_dataset/val').rglob('*.jpg'))[:5]
if not img_paths:
    img_paths = list(Path('cattle_dataset/train').rglob('*.jpg'))[:5]
print('using images:', img_paths)

results = []
for img_p in img_paths:
    print('\n---', img_p)
    rec = {'image': str(img_p)}
    img = Image.open(img_p).convert('RGB')
    np_img = np.array(img)

    # YOLO predict
    yres = YOLO_MODEL.predict(source=np_img, device='cpu', imgsz=640, save=False, verbose=False)
    if not yres:
        rec['yolo'] = None
    else:
        r = yres[0]
        probs = getattr(r, 'probs', None)
        if probs is None:
            rec['yolo'] = None
        else:
            scores = getattr(probs,'data',probs)
            if not isinstance(scores, torch.Tensor):
                scores = torch.as_tensor(scores)
            topk = torch.topk(scores, k=min(5, len(class_names)))
            tp, ti = topk
            rec['yolo'] = [{'class': class_names[i.item()] if i.item()<len(class_names) else str(i.item()), 'confidence': float(p.item())} for p,i in zip(tp,ti)]

    # ViT predict
    if VIT_MODEL is None:
        rec['vit'] = None
    else:
        t = VIT_TRANSFORM(img).unsqueeze(0)
        with torch.no_grad():
            logits = VIT_MODEL(t)
            probs = torch.softmax(logits, dim=1)[0]
            topk = torch.topk(probs, k=min(5, len(class_names)))
            tp, ti = topk
            rec['vit'] = [{'class': class_names[i.item()] if i.item()<len(class_names) else str(i.item()), 'confidence': float(p.item())} for p,i in zip(tp,ti)]

    print('yolo top1', rec['yolo'][0] if rec['yolo'] else None)
    print('vit top1', rec['vit'][0] if rec['vit'] else None)
    results.append(rec)

# write results
out = Path('MODELS/prediction_results.json')
with open(out,'w') as f:
    json.dump(results,f,indent=2)
print('wrote', out)
