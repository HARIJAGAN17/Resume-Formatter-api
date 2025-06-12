import requests
from typing import List, Dict

def validate_hyperlinks(links: List[Dict], timeout: int = 5) -> Dict[str, List[Dict]]:
  
    valid_links = []
    invalid_links = []

    for link in links:
        url = link.get("uri", "").strip()
        if not url.lower().startswith(("http://", "https://")):
            invalid_links.append({**link, "reason": "Not a web URL"})
            continue

        try:
            response = requests.head(url, allow_redirects=True, timeout=timeout)
            if response.status_code < 400:
                valid_links.append(link)
            else:
                invalid_links.append({**link, "reason": f"HTTP {response.status_code}"})
        except requests.RequestException as e:
            invalid_links.append({**link, "reason": str(e)})

    return {
        "valid": valid_links,
        "invalid": invalid_links
    }