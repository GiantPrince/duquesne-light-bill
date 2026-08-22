
from playwright.sync_api import sync_playwright
import time

import smtplib
from email.message import EmailMessage

import os

USERNAME=os.environ["DUQUESNE_LIGHT_USERNAME"]
PASSWORD=os.environ["DUQUESNE_LIGHT_PASSWORD"]

GMAIL_PASSWORD=os.environ["GMAIL_PASSWORD"]
GMAIL_ADDRESS=os.environ["GMAIL_ADDRESS"]

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        page = context.new_page()

        page.goto("https://duquesnelight.com/energy-money-savings/my-electric-use")

        username_input = page.locator('input[formcontrolname="username"]').first
        username_input.fill(USERNAME)

        password_input = page.locator('input[formcontrolname="password"]').first
        password_input.fill(PASSWORD)

        submit_button = page.locator('button[type="submit"]')
        submit_button.click()

        page.wait_for_load_state("load")

        chart = page.locator(".highcharts-container").first

        chart.wait_for(state="attached")

        point = page.locator("path.highcharts-point").last

        point.hover()

        tooltip = page.locator(".highcharts-tooltip").last

        tooltip.wait_for(state="attached")

        tooltip_text = '\n'.join(tooltip.inner_text().splitlines()[:-1])
        

        change_view_selector = page.locator('select[aria-label="Change view"]').select_option(label="Day view")

        chart.wait_for(state="visible")

        chart.scroll_into_view_if_needed()

        box = chart.bounding_box()

        page.wait_for_timeout(3000)

        page.screenshot(
            path="chart.png",
            clip=box
        )

        msg = EmailMessage()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = GMAIL_ADDRESS
        msg["Subject"] = "Daily Duquesne Bill Chart"

        msg.set_content(f"{tooltip_text}")

        with open("chart.png", "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="image",
                subtype="png",
                filename="chart.png",
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            smtp.send_message(msg)

        print("Email sent!")
        