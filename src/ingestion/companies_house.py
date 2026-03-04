import os
import httpx
import logging

logger = logging.getLogger(__name__)

class CompaniesHouseClient:
    """Client for the UK Companies House REST API."""
    
    BASE_URL = "https://api.company-information.service.gov.uk"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("CH_API_KEY")
        if not self.api_key:
            logger.warning("No CH_API_KEY found in environment variables. Requests will fail if unauthorized.")
            
        self.client = httpx.Client(
            auth=(self.api_key, ""),
            base_url=self.BASE_URL,
            timeout=10.0
        )

    def search_company(self, company_name: str) -> dict | None:
        """Search for a company by name and return the top match."""
        response = self.client.get("/search/companies", params={"q": company_name, "items_per_page": 1})
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            if items:
                return items[0]
        else:
            logger.error(f"Search failed: {response.status_code} - {response.text}")
        return None

    def get_company_profile(self, company_number: str) -> dict | None:
        """Get the full company profile by its company number."""
        response = self.client.get(f"/company/{company_number}")
        if response.status_code == 200:
            return response.json()
        logger.error(f"Failed to fetch profile for {company_number}: {response.status_code}")
        return None

    def get_filing_history(self, company_number: str, category: str = "accounts") -> list[dict]:
        """
        Get filing history. Category defaults to 'accounts' to fetch financial reports.
        """
        response = self.client.get(f"/company/{company_number}/filing-history", params={"category": category})
        if response.status_code == 200:
            return response.json().get("items", [])
        logger.error(f"Failed to fetch filing history for {company_number}: {response.status_code}")
        return []
        
    def close(self):
        self.client.close()
