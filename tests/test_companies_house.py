from unittest.mock import MagicMock
import pytest
from src.ingestion.companies_house import CompaniesHouseClient

def test_search_company_success(mocker):
    # Mock httpx.Client.get
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "company_number": "12345678",
                "title": "TEST COMPANY LTD",
                "company_status": "active"
            }
        ]
    }
    mock_get.return_value = mock_response

    client = CompaniesHouseClient(api_key="fake_key")
    result = client.search_company("Test Company")
    
    assert result is not None
    assert result["company_number"] == "12345678"
    assert result["title"] == "TEST COMPANY LTD"
    
def test_get_company_profile(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "company_name": "TEST COMPANY LTD",
        "company_number": "12345678",
        "registered_office_address": {
            "country": "United Kingdom"
        }
    }
    mock_get.return_value = mock_response

    client = CompaniesHouseClient(api_key="fake_key")
    profile = client.get_company_profile("12345678")
    
    assert profile is not None
    assert profile["company_name"] == "TEST COMPANY LTD"

def test_get_filing_history(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "category": "accounts",
                "date": "2023-10-31",
                "links": {
                    "document_metadata": "https://frontend-doc-api.company-information.service.gov.uk/document/123"
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    client = CompaniesHouseClient(api_key="fake_key")
    history = client.get_filing_history("12345678")
    
    assert len(history) == 1
    assert history[0]["category"] == "accounts"
    assert "document_metadata" in history[0]["links"]
