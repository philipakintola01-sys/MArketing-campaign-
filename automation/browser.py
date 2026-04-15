from playwright.async_api import async_playwright
import os
import asyncio

class SocialPoster:
    def __init__(self):
        self.user_data_dir = "./browser_data"

    async def post_to_linkedin(self, content: str, image_path: str = None) -> str:
        email = os.getenv("LINKEDIN_EMAIL")
        password = os.getenv("LINKEDIN_PASSWORD")
        if not email or not password or "your_email" in email:
            return "Failure: Missing or invalid LINKEDIN_EMAIL or LINKEDIN_PASSWORD in environment variables."

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                await page.goto("https://www.linkedin.com/login")
                await page.fill("#username", email)
                await page.fill("#password", password)
                await page.click("button[type='submit']")
                
                # Wait for feed to load (timeout after 15 seconds)
                try:
                    await page.wait_for_url("**/feed/**", timeout=15000)
                except Exception:
                    await browser.close()
                    return "Failure: Could not log in to LinkedIn. CAPTCHA or incorrect password."
                
                # Post logic
                await page.click(".share-box-feed-entry__trigger")
                await page.fill(".ql-editor", content)
                
                if image_path:
                    # Not implemented completely, placeholder
                    pass
                
                await page.click(".share-actions__primary-action")
                await asyncio.sleep(5) # Let it publish
                await browser.close()
                return "Successfully published to LinkedIn."
        except Exception as e:
            return f"Failure: Exception during LinkedIn browser automation - {str(e)}"

    async def post_to_x(self, content: str) -> str:
        username = os.getenv("X_USERNAME")
        password = os.getenv("X_PASSWORD")
        if not username or not password or "your_x" in username:
            return "Failure: Missing or invalid X_USERNAME or X_PASSWORD in environment variables."

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Navigate to X login
                await page.goto("https://x.com/i/flow/login")

                # Handle multi-step login
                await page.wait_for_selector("input[autocomplete='username']", timeout=15000)
                await page.fill("input[autocomplete='username']", username)
                await page.click("button:has-text('Next')")
                
                # Password step
                await page.wait_for_selector("input[type='password']", timeout=10000)
                await page.fill("input[type='password']", password)
                await page.click("button[data-testid='LoginForm_Login_Button']")
                
                # Wait for timeline
                try:
                    await page.wait_for_selector("a[data-testid='SideNav_NewTweet_Button']", timeout=20000)
                except Exception:
                    await browser.close()
                    return "Failure: Could not log in to X. It might be requesting email verification or a CAPTCHA."

                # Compose Tweet
                await page.click("a[data-testid='SideNav_NewTweet_Button']")
                await page.wait_for_selector("div.public-DraftEditor-content")
                await page.fill("div.public-DraftEditor-content", content)
                
                # Click Post
                await page.click("button[data-testid='tweetButton']")
                await asyncio.sleep(5)
                await browser.close()
                return "Successfully published to X (Twitter)."
        except Exception as e:
            return f"Failure: Exception during X browser automation - {str(e)}"

    async def post_to_instagram(self, content: str, image_path: str):
        return "Failure: Instagram posting not yet supported by backend architecture."
