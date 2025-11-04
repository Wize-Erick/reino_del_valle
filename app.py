from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import re

app = Flask(__name__)

@app.route("/scrape", methods=["POST"])
def scrape():
    """
    Endpoint que recibe una URL y devuelve título, stock y precios según existan o no variantes.
    """
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    try:
        # Configuración del navegador
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(options=opts)
        driver.set_window_size(1920, 1080)

        driver.get(url)
        print(f"Visitando: {url}")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "p.price"))
        )

        # Obtener título
        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, "h1.product_title.entry-title.wd-entities-title")
            product_title = title_elem.text.strip()
        except:
            product_title = "Título no encontrado"

        # Verificar stock
        try:
            driver.find_element(By.CSS_SELECTOR, "p.stock.out-of-stock.wd-style-bordered")
            stock_status = "Sin stock"
        except:
            stock_status = ""

        variantes = []

        # Caso 1: Existen swatches (variantes)
        try:
            td_element = driver.find_element(By.CSS_SELECTOR, "td.value.cell.with-swatches")
            divs = td_element.find_elements(By.CSS_SELECTOR, "div.wd-swatch.wd-text")

            if len(divs) > 0:
                print(f"Existen {len(divs)} variantes")
                for div in divs:
                    peso = div.text.strip().replace(" ", "")
                    driver.execute_script("arguments[0].scrollIntoView(true);", div)
                    div.click()
                    sleep(2)
                    try:
                        price_elem = driver.find_element(By.CSS_SELECTOR, "p.price span.woocommerce-Price-amount.amount bdi")
                        price = price_elem.text.strip()
                    except:
                        price = "No encontrado"
                    variantes.append({"peso": peso, "precio": price})
            else:
                print("No existen elementos dentro del td")

        # Caso 2: No existen variantes (tomar peso del título)
        except:
            print("No existen elementos (td con swatches no encontrado)")
            try:
                price_elem = driver.find_element(By.CSS_SELECTOR, "p.price span.woocommerce-Price-amount.amount bdi")
                price = price_elem.text.strip()

                # 🧠 Limpiar el título eliminando "(exo)" u otros paréntesis
                clean_title = re.sub(r"\(.*?\)", "", product_title).strip()

                # Extraer las últimas dos palabras limpias
                title_parts = clean_title.split()
                if len(title_parts) >= 2:
                    last_two = "".join(title_parts[-2:])  # Ej: ['1', 'kg'] → '1kg'
                else:
                    last_two = "N/A"

                variantes.append({"peso": last_two, "precio": price})

            except:
                variantes.append({"peso": "N/A", "precio": "No encontrado"})

        driver.quit()

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
