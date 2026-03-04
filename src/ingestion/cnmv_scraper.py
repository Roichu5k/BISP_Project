import asyncio
import logging
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

class CNMVScraper:
    """Scraper for the Spanish CNMV (Comisión Nacional del Mercado de Valores) website."""

    BASE_URL = "https://www.cnmv.es/Portal/home.aspx"
    SEARCH_URL = "https://www.cnmv.es/portal/Consultas/BusquedaPorEntidad.aspx"

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        # Ensure we run headlessly in production, but we can set to False to debug
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.stealth = Stealth()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_relevant_information(self, company_name: str) -> list[dict]:
        """
        Navigates to the CNMV portal, searches for the company, and extracts 'Otra Información Relevante' (OIR) links.
        """
        page = await self.context.new_page()
        # Apply stealth to bypass basic anti-bot measures like Cloudflare/Akamai
        await self.stealth.apply_stealth_async(page)
        
        results = []
        try:
            logger.info(f"Navigating to CNMV search portal for: {company_name}")
            await page.goto(self.SEARCH_URL, wait_until="networkidle")
            
            # This is a hypothetical selector pattern based on standard ASP.NET structures
            # It will need to be refined if the HTML is inspected directly via browser tools.
            search_input_selector = "input[type='text'][id*='Busqueda']"
            search_button_selector = "input[type='submit'][id*='Buscar']"
            
            # If the search bar doesn't exist, CNMV might have changed its DOM. We return raw HTML to debug.
            if await page.locator(search_input_selector).count() == 0:
                logger.warning(f"Search input not found on {self.SEARCH_URL}. Attempting manual link extraction.")
                raw_html = await page.content()
                with open("cnmv_debug_snapshot.html", "w") as f:
                    f.write(raw_html)
                return [{"error": "Search input not found. Downloaded raw HTML snapshot for debugging."}]

            await page.fill(search_input_selector, company_name)
            
            # Using asyncio.gather to wait for navigation while clicking
            async with page.expect_navigation(wait_until="domcontentloaded", timeout=10000):
                await page.click(search_button_selector)
            
            logger.info("Search submitted, analyzing results table...")
            
            # Hypothetical extraction logic for 'Información Privilegiada' or 'Otra Información Relevante'
            links = await page.locator("a[href*='OIR']").element_handles()
            for link in links:
                text = await link.inner_text()
                href = await link.get_attribute("href")
                if href:
                    results.append({
                        "title": text.strip(),
                        "url": f"https://www.cnmv.es{href}" if href.startswith("/") else href,
                        "type": "OIR"
                    })
                    
        except Exception as e:
            logger.error(f"Error scraping CNMV for {company_name}: {e}")
            # En caso de fallo, intentamos guardar un snapshot del DOM para evaluar si hubo un captcha
            raw_html = await page.content()
            with open("cnmv_error_snapshot.html", "w") as f:
                f.write(raw_html)
        finally:
            await page.close()
            
        return results

# Example usage (for testing module directly):
if __name__ == "__main__":
    async def run_test():
        async with CNMVScraper() as scraper:
            print("Running CNMV Scraper Test for Inditex...")
            res = await scraper.get_relevant_information("Inditex")
            print(f"Results: {res}")
            
    asyncio.run(run_test())
