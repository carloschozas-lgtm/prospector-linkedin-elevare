import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def find_linkedin_profiles(cargo, industria, ubicacion="Chile", count=10):
    """
    Busca perfiles de LinkedIn usando Serper.dev (Google Search API).
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return {"error": "SERPER_API_KEY no configurada en .env"}

    url = "https://google.serper.dev/search"
    
    query = f'site:linkedin.com/in/ "{cargo}" "{industria}" "{ubicacion}"'
    
    payload = json.dumps({
        "q": query,
        "num": count
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        results = response.json()
        
        profiles = []
        if "organic" in results:
            for item in results["organic"]:
                if "linkedin.com/in/" in item.get("link", ""):
                    profiles.append({
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet")
                    })
        return profiles
    except Exception as e:
        return {"error": f"Error en búsqueda: {str(e)}"}
