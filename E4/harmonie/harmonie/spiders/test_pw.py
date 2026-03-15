import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("--- ÉTAPE 1 : Session Warming ---")
        await page.goto("https://www.musicshopeurope.com/")
        
        # Gestion des Cookies (image_910d39.png)
        try:
            await page.click("button:has-text('Accept all')", timeout=5000)
            print("Cookies acceptés.")
        except:
            print("Bandeau cookies non détecté.")

        # Gestion du Popup Pays (image_910d39.png)
        try:
            await page.click("text=close X", timeout=3000)
            print("Popup pays fermé.")
        except:
            print("Pas de popup pays.")

        print("--- ÉTAPE 2 : Test URL Française ---")
        # Ton URL avec les filtres en français
        target_url = "https://www.musicshopeurope.com/partitions/band/orchestre-d-harmonie/type%20de%20produit=conducteur%20-15=%20parties/?sort=Marketable+from_desc"
        
        # On attend que la navigation soit stable
        response = await page.goto(target_url, wait_until="networkidle")
        
        print(f"Statut reçu : {response.status}")
        
        if response.status == 200:
            # Test ultime : Est-ce qu'on voit au moins un produit ?
            products = await page.query_selector_all(".product-title")
            print(f"Nombre de produits trouvés : {len(products)}")
        else:
            print("Toujours en 404. Vérifie si l'URL ne change pas quand tu navigues à la main.")

        print("\nFenêtre ouverte pour 2 minutes d'inspection...")
        await asyncio.sleep(120)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())