from playwright.sync_api import sync_playwright
import json

def capturar_xhr(url):
    xhrs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def intercept_response(response):
            if response.request.resource_type == 'xhr':
                try:
                    body = response.json()
                    xhrs.append({
                        "url": response.url,
                        "json": body
                    })
                except:
                    pass

        page.on("response", intercept_response)
        print("🧭 Acesse a página e interaja com os elementos...")
        page.goto(url)
        input("👉 Pressione ENTER para continuar depois de interagir com a página...")
        browser.close()

    return xhrs
