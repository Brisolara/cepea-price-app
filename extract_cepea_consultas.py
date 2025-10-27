import asyncio, os, datetime as dt
from pathlib import Path
import pandas as pd
from playwright.async_api import async_playwright

CONSULTAS_URL = "https://www.cepea.org.br/br/consultas-ao-banco-de-dados-do-site.aspx"

COMMODITIES = [
    ("boi-gordo", "Boi gordo"),
    ("soja", "Soja"),
    ("milho", "Milho"),
    ("cafe", "Café"),
    ("acucar", "Açúcar"),
    ("etanol", "Etanol"),
]

DATE_FROM = os.environ.get("ETL_DATE_FROM")
DATE_TO   = os.environ.get("ETL_DATE_TO")

def _br_date(d: dt.date) -> str:
    return d.strftime("%d/%m/%Y")

async def fetch_excel(product_label: str, date_from: dt.date, date_to: dt.date, download_dir: Path) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(accept_downloads=True)
        page = await context.new_page()
        await page.goto(CONSULTAS_URL, wait_until="domcontentloaded")

        # Os seletores podem mudar; ajuste conforme necessário
        await page.select_option("select", label=product_label)

        diario = page.locator("input[type=radio][value='Diário']")
        if await diario.count() > 0:
            await diario.first.check()

        date_from_str = _br_date(date_from)
        date_to_str = _br_date(date_to)
        await page.fill("input[id*='DataDe']", date_from_str)
        await page.fill("input[id*='DataAte']", date_to_str)

        async with page.expect_download() as dl:
            await page.get_by_text("Gerar Excel").click()
        download = await dl.value
        target = download_dir / f"{product_label}_{date_from.isoformat()}_{date_to.isoformat()}.xlsx"
        await download.save_as(str(target))
        await browser.close()
        return target

async def main():
    today = dt.date.today()
    date_from = dt.date.fromisoformat(DATE_FROM) if DATE_FROM else today
    date_to   = dt.date.fromisoformat(DATE_TO) if DATE_TO else today
    download_dir = Path("data/raw") / today.isoformat()

    results = []
    for slug, label in COMMODITIES:
        try:
            path = await fetch_excel(label, date_from, date_to, download_dir)
            results.append((slug, str(path)))
            print("baixado:", slug, path)
        except Exception as e:
            print("falha:", slug, e)
    pd.DataFrame(results, columns=["slug","path"]).to_csv(download_dir / "manifest.csv", index=False)

if __name__ == "__main__":
    asyncio.run(main())
