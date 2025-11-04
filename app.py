from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import re, os, time

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
            })
            page.goto(url, timeout=45000)

            # Esperar que cargue el precio
            page.wait_for_selector("p.price", timeout=10000)

            # Obtener título
            try:
                product_title = page.locator("h1.product_title.entry-title.wd-entities-title").inner_text().strip()
            except:
                product_title = "Título no encontrado"

            # Verificar stock
            stock_status = ""
            if page.locator("p.stock.out-of-stock.wd-style-bordered").count() > 0:
                stock_status = "Sin stock"

            variantes = []
            try:
                swatches = page.locator("td.value.cell.with-swatches div.wd-swatch.wd-text")
                count = swatches.count()
                if count > 0:
                    for i in range(count):
                        peso = swatches.nth(i).inner_text().strip().replace(" ", "")
                        swatches.nth(i).click()
                        time.sleep(1)
                        try:
                            price = page.locator("p.price span.woocommerce-Price-amount.amount bdi").inner_text().strip()
                        except:
                            price = "No encontrado"
                        variantes.append({"peso": peso, "precio": price})
                else:
                    raise Exception("Sin variantes visibles")
            except:
                try:
                    price = page.locator("p.price span.woocommerce-Price-amount.amount bdi").inner_text().strip()
                    clean_title = re.sub(r"\(.*?\)", "", product_title).strip()
                    parts = clean_title.split()
                    last_two = "".join(parts[-2:]) if len(parts) >= 2 else "N/A"
                    variantes.append({"peso": last_two, "precio": price})
                except:
                    variantes.append({"peso": "N/A", "precio": "No encontrado"})

            browser.close()

        return jsonify({
            "url": url,
            "title": product_title,
            "stock": stock_status,
            "variants": variantes,
            "status": "ok"
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"url": url, "error": str(e), "status": "failed"}), 500


@app.route("/")
def home():
    return "✅ Flask + Playwright API is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
