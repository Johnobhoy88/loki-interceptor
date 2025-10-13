import requests

print("Testing minimal backend...")

# Test health
r = requests.get('http://127.0.0.1:5000/health')
print(f"Health: {r.status_code} {r.json()}")

# Test validation
payload = {
    'text': 'You are invited to a meeting.',
    'document_type': 'disciplinary_invitation',
    'modules': ['hr_scottish']
}
r = requests.post('http://127.0.0.1:5000/validate-document', json=payload)
print(f"Validation: {r.status_code} {r.json()}")

