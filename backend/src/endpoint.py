from typing import List, Dict, Any
import importlib.util
import pathlib
import pluggy
from specs import PluginSpecs, FixtureSpecs
from settings import APPLICATION_NAME
import bonobo
from model import PluginQuery, ArbitrageQuery, PluginResult, AppResult
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
import os


origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KV_STORE = {}

def store_results(data: PluginResult):
    print(f"IN store_results. name={data.plugin_name}; data={data.plugin_data}")
    if data.plugin_name not in KV_STORE:
        KV_STORE[data.plugin_name] = []
    KV_STORE[data.plugin_name].append(data.plugin_data)


def load_plugins_from_dir(pm, directory):
    path = pathlib.Path(directory)
    for file in path.glob("*.py"):
        if file.name == "__init__.py":
            continue
            
        # Dynamically import the module
        spec = importlib.util.spec_from_file_location(file.stem, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Register the module with pluggy
        pm.register(module)

@app.post("/fetch")
def fetch(query: ArbitrageQuery) -> AppResult:
    # Setup Plugin Manager
    pm = pluggy.PluginManager(APPLICATION_NAME + "-plugins")
    pm.add_hookspecs(PluginSpecs)
   
    # Load plugins from the 'plugins' folder
    plugin_dir = os.getenv('PLUGINS_DIR')
    load_plugins_from_dir(pm, plugin_dir if plugin_dir else "src/plugins")

    arbitrage_query = ArbitrageQuery(isbn=query.isbn)
    plugin_query = PluginQuery[ArbitrageQuery](data=arbitrage_query)
    plugin_query.data = arbitrage_query
    graph = bonobo.Graph()
    graph.add_chain(store_results, _input=None)
    for name, plugin in pm.list_name_plugin():
        graph.add_chain(
            plugin.extract(plugin_query),
            plugin.transform,
            plugin.load,
            _output=store_results
        )
    bonobo.run(graph)

    fixtures =  pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)

    fixtures_dir = os.getenv('FIXTURES_DIR')
    load_plugins_from_dir(fixtures, fixtures_dir if fixtures_dir else "src/fixtures")
    results = fixtures.hook.merge_results(kv_store=KV_STORE)
    return results[0]

@app.get("/get-table-headers")
def get_table_headers() -> List[Dict[Any, Any]]:
    fixtures =  pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    fixtures_dir = os.getenv('FIXTURES_DIR')
    load_plugins_from_dir(fixtures, fixtures_dir if fixtures_dir else "src/fixtures")
    results = fixtures.hook.get_table_headers()
    return results[0]

@app.get("/get-properties")
def get_properties() -> Dict[Any, Any]:
    fixtures =  pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    fixtures_dir = os.getenv('FIXTURES_DIR')
    load_plugins_from_dir(fixtures, fixtures_dir if fixtures_dir else "src/fixtures")
    results = fixtures.hook.get_properties()
    return results[0]

@app.get("/get-icon")
def get_icon() -> str:
    fixtures =  pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    fixtures_dir = os.getenv('FIXTURES_DIR')
    load_plugins_from_dir(fixtures, fixtures_dir if fixtures_dir else "src/fixtures")
    results = fixtures.hook.get_icon()
    return results[0]

from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from playwright_recaptcha import recaptchav3
import random
import time
from playwright_stealth import stealth_sync
from typing import Tuple

if __name__ == "__main__":
    isbn = "9780679760849"
    url = "https://www.addall.com"
    
    # Open playwright and goto url
    with sync_playwright() as p:
         # Set the custom user agent here
        custom_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        try:
            with recaptchav3.SyncSolver(page) as solver:
                page.goto(url, timeout=60000)
                token = solver.solve_recaptcha()
                print(f"Generated v3 Token: {token}")
        except Exception as e:
            print(f"v3 EXCEPTION!!!! - {e}")
        
        stealth_sync(page)
        newform = page.locator("form[name='newform']")

        # 1. Locate the specific form (by ID, class, or text)
        isbn_select = newform.locator("select[name='type']")
        expect(isbn_select).to_have_count(1)
        time.sleep(random.uniform(2.0, 10.0))
        isbn_select.select_option(value="ISBN")

        search_input = newform.locator("input[id='query']")
        expect(search_input).to_have_count(1)
        search_input.type(isbn, delay=random.randint(50, 150))
        
        print("sleep prior after type")
        time.sleep(random.uniform(2.0, 10.0))
        with page.expect_navigation():
            # 1. Find bounding box
            box = page.locator("button[type='submit'][class='newbtn']").bounding_box()
            
            # 2. Calculate random point inside bounding box
            x = box["x"] + random.uniform(0, box["width"])
            y = box["y"] + random.uniform(0, box["height"])
            
            print("sleep prior to move")
            time.sleep(random.uniform(2.0, 10.0))

            # 3. Move mouse to that point
            page.mouse.move(x, y)

            print("sleep prior to click")
            # 4. Random wait
            time.sleep(random.uniform(2.0, 10.0))
                        
            # 5. Click
            page.mouse.click(x, y)
        
        page.wait_for_load_state("load")

        print(page.content())
        
        title = page.locator("div").locator("div[class='ntitle']").inner_text()
        author = page.locator("div").locator("div[class='nauthor']").inner_text()[3:]
        divs_locator = page.locator("div").locator("div[class='nrecordx']")
        divs = divs_locator.all()
        for div in divs:
            div_buyat = div.locator("div[class='buyat']")

            div_used = div_buyat.locator("div[class='used']")
            try:
                expect(div_used).to_have_count(1)
                continue
            except Exception as e:
                pass

            anchor_locator = div_buyat.locator("a")
            affiliate = anchor_locator.inner_text()
            url = f'{url}{anchor_locator.get_attribute("href")}'

            div_total = div.locator("div[class='total']")
            anchor_locator = div_total.locator("a")
            price = anchor_locator.inner_text()
            result = PluginResult[Tuple[str, str, str, float, str, str]](plugin_name="", plugin_data=(isbn, title, author, price, affiliate, url))
            print(result)

        browser.close()