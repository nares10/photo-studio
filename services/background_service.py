from typing import Dict, Any, Optional
import requests
import base64

def remove_background(
    api_key: str,
    image_data: bytes = None,
    image_url: str = None,
    content_moderation: bool = False
) -> Dict[str, Any]:
    
    url = "https://engine.prod.bria-api.com/v2/image/edit/remove_background"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Prepare request data
    data = {
        'visual_input_content_moderation': content_moderation
    }

    # Add image data
    if image_url:
        data['image_url'] = image_url
    elif image_data:
        data['image'] = base64.b64encode(image_data).decode('utf-8')
    else:
        raise ValueError("Either image_data or image_url must be provided")
    
    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        return response.json()
    except Exception as e:
        raise Exception(f"Erase foreground failed: {str(e)}")
