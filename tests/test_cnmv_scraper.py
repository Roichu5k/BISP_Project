import pytest
from unittest.mock import AsyncMock, MagicMock
from src.ingestion.cnmv_scraper import CNMVScraper

@pytest.mark.asyncio
async def test_get_relevant_information(mocker):
    # Mock playwright components
    mock_playwright = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    # Setup chain map
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    # Mock locator for the "OIR" links
    mock_link = AsyncMock()
    mock_link.inner_text.return_value = "Otra información relevante"
    mock_link.get_attribute.return_value = "/Otra-Informacion-Relevante/doc.pdf"
    
    mock_locator = AsyncMock()
    mock_locator.element_handles.return_value = [mock_link]
    
    # We want page.locator to return a mock locator with a non-zero count for the search bar
    # And return the link locator for the 'OIR' search
    def side_effect_locator(selector):
        m = MagicMock()
        m.count = AsyncMock(return_value=1)
        if "OIR" in selector:
            m.element_handles = AsyncMock(return_value=[mock_link])
        return m
        
    mock_page.locator = MagicMock(side_effect=side_effect_locator)
    mock_page.content = AsyncMock(return_value="<html>mocked content</html>")
    mock_page.expect_navigation = MagicMock(return_value=AsyncMock())

    # Patch the async_playwright context manager behavior
    mocker.patch("src.ingestion.cnmv_scraper.async_playwright", return_value=AsyncMock(start=AsyncMock(return_value=mock_playwright)))
    # We also need to mock stealth
    mocker.patch("src.ingestion.cnmv_scraper.Stealth.apply_stealth_async", return_value=None)

    async with CNMVScraper() as scraper:
        results = await scraper.get_relevant_information("Inditex")
        
        assert len(results) == 1
        assert results[0]["title"] == "Otra información relevante"
        assert results[0]["url"] == "https://www.cnmv.es/Otra-Informacion-Relevante/doc.pdf"
        assert results[0]["type"] == "OIR"
    
        # Verify page interactions
        mock_page.fill.assert_called_once()
        mock_page.click.assert_called_once()
