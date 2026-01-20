#!/usr/bin/env python3

import asyncio
import httpx

async def test_creation():
    # Start the app
    async with httpx.AsyncClient(base_url='http://localhost:5000', timeout=10) as client:
        try:
            # Login first
            login = await client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin'})
            if login.status_code != 200:
                print(f"Login failed: {login.status_code} - {login.text}")
                return
            
            token = f"Bearer {login.json()['access_token']}"
            print(f"Login successful, token received")
            
            # Try to create product with problematic barcode
            p1 = {'description': 'A', 'barcode': '036000291452', 'price_per_unit': 1}
            resp = await client.post('/api/v1/products', json=p1, headers={'Authorization': token})
            print(f'Product creation status: {resp.status_code}')
            print(f'Response text: {resp.text}')
            
            if resp.status_code == 201:
                print(f"Product created successfully: {resp.json()}")
            else:
                print(f"Product creation failed")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_creation())