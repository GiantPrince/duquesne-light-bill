
from playwright.sync_api import sync_playwright

import smtplib
from email.message import EmailMessage

import os

from dotenv import load_dotenv

# constants

TOOLTIP_DATE_INDEX = 0
TOOLTIP_COST_INDEX = 2
ANIMATION_WAIT_TIME = 3000

# envs
load_dotenv()
LAST_N_DAYS=int(os.environ["LAST_N_DAYS"])
EMAIL_SUBJECT=os.environ["EMAIL_SUBJECT"]

# secrets
USERNAME=os.environ["DUQUESNE_LIGHT_USERNAME"]
PASSWORD=os.environ["DUQUESNE_LIGHT_PASSWORD"]

GMAIL_APP_PASSWORD=os.environ["GMAIL_APP_PASSWORD"]
GMAIL_SENDER=os.environ["GMAIL_SENDER"]
EMAIL_RECEIVER=os.environ["EMAIL_RECEIVER"]

def login(page):
    """Login duquesne light using the provided username and password"""
    username_input = page.locator('input[formcontrolname="username"]').first
    username_input.fill(USERNAME)

    password_input = page.locator('input[formcontrolname="password"]').first
    password_input.fill(PASSWORD)

    submit_button = page.locator('button[type="submit"]')
    submit_button.click()

    page.wait_for_load_state("load")

def extract_last_n_days_cost(page, n: int) -> tuple[list[str], list[tuple[str, str]]]:
    """
    Try to extract the cost data in last n days.
    Capture screenshots of the daily cost graph and also return date
    string with daily costs
    """
    n_costs = []
    texts = []
    chart = page.locator(".highcharts-container").first
    chart.wait_for(state="attached")
    points = page.locator("path.highcharts-point")

    count = points.count()
    for idx in range(max(0, count - n), count):
        point = points.nth(idx)
        point.hover(force=True)
        tooltip = page.locator(".highcharts-tooltip").last
        tooltip.wait_for(state="attached")
        tooltip_texts = tooltip.inner_text().splitlines()
        tooltip_text = '-'.join([tooltip_texts[TOOLTIP_DATE_INDEX], tooltip_texts[TOOLTIP_COST_INDEX]])
        texts.append((tooltip_texts[TOOLTIP_DATE_INDEX], tooltip_texts[TOOLTIP_COST_INDEX]))
        point.click(force=True)
        page.mouse.move(0, 0)
        chart.wait_for(state="visible")
        chart.scroll_into_view_if_needed()

        box = chart.bounding_box()
        page.wait_for_timeout(ANIMATION_WAIT_TIME)
        screenshot_path = f"{tooltip_text}.png"
        page.screenshot(
            path=screenshot_path,
            clip=box
        )
        page.locator('select[aria-label="Change view"]').select_option(label="Bill view")
        n_costs.append(screenshot_path)

    remain = n - count
    if remain > 0:
        button = page.get_by_role(
            "button",
            name="Scroll to previous bill range",
        )

        if button.is_disabled():
            return n_costs, texts
        else:
            button.click()
            previous_n_costs, previous_texts = extract_last_n_days_cost(page, remain)
            previous_n_costs.extend(n_costs)
            n_costs = previous_n_costs
            previous_texts.extend(texts)
            texts = previous_texts
    return n_costs, texts


def format_costs_table(costs):
    table = "Date                    Cost\n"
    table += "----------------------------\n"

    for date, cost in costs:
        table += f"{date:<22}{cost:>7}\n"

    return table

if __name__ == "__main__":

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        context = browser.new_context()

        page = context.new_page()

        page.goto("https://duquesnelight.com/energy-money-savings/my-electric-use")

        login(page)

        screenshots, texts = extract_last_n_days_cost(page, LAST_N_DAYS)

        receivers = EMAIL_RECEIVER.split(',')

        for receiver in receivers:
            msg = EmailMessage()
            msg["From"] = GMAIL_SENDER
            msg["To"] = receiver.strip()
            msg["Subject"] = EMAIL_SUBJECT

            msg.set_content(format_costs_table(texts))

            for screenshot in screenshots:
                with open(screenshot, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype="image",
                        subtype="png",
                        filename=screenshot,
                    )

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
                smtp.send_message(msg)

        print("Email sent!")
