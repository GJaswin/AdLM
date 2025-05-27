import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup # Moved import here as it's always used

async def get_all_external_links_with_playwright(url: str, wait_time: int = 15) -> set[str]:
    """
    Opens a website using Playwright, waits for the network to be idle,
    and retrieves all external links, excluding links pointing to the same website.

    Args:
        url (str): The URL of the website to open.
        wait_time (int): The maximum time (in seconds) to wait for network to be idle.

    Returns:
        set: A set of unique absolute URLs for external links found on the page.
    """
    external_links = set()
    original_netloc = urlparse(url).netloc

    async with async_playwright() as p:
        browser = None
        try:
            # Launch a Chromium browser instance (you can also choose 'firefox' or 'webkit')
            browser = await p.chromium.launch(headless=True) # Set headless=False to see the browser UI
            page = await browser.new_page()

            # Navigate to the URL and wait until the initial 'load' event fires
            await page.goto(url, wait_until="load")

            # Wait for network to be idle (no more than 0 network connections for at least 500ms).
            # This is a common heuristic for content completion, including most dynamic elements.
            print(f"Waiting for network to be idle for up to {wait_time} seconds...")
            await page.wait_for_load_state("networkidle", timeout=wait_time * 1000)
            print("Network is largely idle.")

            # Get the page content after waiting
            content = await page.content()

            soup = BeautifulSoup(content, 'html.parser')

            for link_tag in soup.find_all('a', href=True):
                href = link_tag['href']
                absolute_url = urljoin(url, href)

                # Only consider HTTP/HTTPS links
                if not (absolute_url.startswith('http://') or absolute_url.startswith('https://')):
                    continue

                # Get the netloc (domain) of the found link
                found_netloc = urlparse(absolute_url).netloc

                # Exclude links pointing to the same domain
                if found_netloc != original_netloc:
                    external_links.add(absolute_url)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if browser:
                await browser.close() # Ensure the browser is closed

    return external_links

async def main(target_url):
    target_url = input("Enter the URL of the website: ")

    print(f"\nRetrieving external links from: {target_url} (using Playwright, this may take a moment)")
    links = await get_all_external_links_with_playwright(target_url) 

    if links:
        print(f"\nFound {len(links)} unique external links:")
        for link in sorted(list(links)):
            print(link)
    else:
        print("No external links found or an error occurred.")
    return links

if __name__ == "__main__":
    asyncio.run(main())