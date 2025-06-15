import requests
from typing import List, Dict

def validate_hyperlinks(links: List[Dict], timeout: int = 5) -> Dict[str, List[Dict]]:
    valid_links = []
    invalid_links = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    for link in links:
        url = link.get("uri", "").strip().lower()

        # Skip email links entirely
        if url.startswith("mailto:"):
            continue

        # Only allow HTTP/HTTPS URLs
        if not url.startswith(("http://", "https://")):
            invalid_links.append({**link, "reason": "Not a web URL"})
            continue

        # Manually trust LinkedIn
        if "linkedin.com" in url:
            valid_links.append(link)
            continue

        try:
            response = requests.get(
                url,
                headers=headers,
                allow_redirects=True,
                timeout=timeout,
                verify=False,
                stream=True
            )

            if response.status_code < 400:
                valid_links.append(link)
            else:
                invalid_links.append({**link, "reason": f"HTTP {response.status_code}"})

        except requests.RequestException as e:
            invalid_links.append({**link, "reason": str(e)})

    # Deduplicate by 'uri'
    def deduplicate(links_list):
        seen = set()
        unique = []
        for link in links_list:
            uri = link["uri"]
            if uri not in seen:
                seen.add(uri)
                unique.append(link)
        return unique

    return {
        "valid": deduplicate(valid_links),
        "invalid": deduplicate(invalid_links)
    }
