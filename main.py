import os
from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText

# Email config
EMAIL_ADDRESS = "vinamansur2@gmail.com"
EMAIL_PASSWORD = os.environ("EMAIL_PASSWORD")
EMAIL_TO = "vinamansur2@gmail.com"
UCI = os.environ("UCI")
IRCC_PASSWORD = os.environ("IRCC_PASSWORD")


def home():
    try:
        run()
        return "IRCC status check completed and email sent!"
    except Exception as e:
        return f"Error occurred: {str(e)}"


def send_email(updated_date, body):
    msg = MIMEText(body.inner_html(), 'html')
    msg['Subject'] = f"PR Application - Last update: {updated_date}"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)


def run():
    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://ircc-tracker-suivi.apps.cic.gc.ca/en/login", timeout=30000)

            page.locator("#uci").fill(UCI)
            page.locator("#password").fill(IRCC_PASSWORD)
            page.locator("#sign-in-btn").click()

            page.wait_for_selector("text=Application Status Tracker", timeout=15000)

            label = page.get_by_text("Updated:")
            date_span = label.evaluate_handle("el => el.nextElementSibling")
            updated_date = date_span.evaluate("el => el.textContent")

            page.locator("a", has_text="View").first.click()
            page.wait_for_selector("text=Application details", timeout=15000)

            content = page.locator("section").nth(1)

            #content = "PR Updates - Vinicius Machado Mansur"

            #page.locator('.my-auto.mx-2.chip-text').evaluateAll((elements) => {

            #})

            send_email(updated_date, content)
        finally:
            if browser:
                browser.close()


if __name__ == "__main__":
    run()
