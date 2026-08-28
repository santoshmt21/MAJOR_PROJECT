from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
body = {
    'breed': 'Gir',
    'category': 'Dairy_Lactating',
    'weight_kg': 400,
    'age_months': 48,
    'milk_yield_l': 18,
    'bcs': 2.8,
    'activity_level': 'Medium',
    'health_status': 'Lumpy_Skin_Disease'
}
resp = client.post('/nutrition-recommendation', json=body)
print(resp.status_code)
print(resp.text)
