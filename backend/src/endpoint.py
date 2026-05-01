from typing import List, Dict, Any, Tuple
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
import random
import time


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
    load_plugins_from_dir(pm, "src/plugins")

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
    load_plugins_from_dir(fixtures, "src/fixtures")
    results = fixtures.hook.merge_results(kv_store=KV_STORE)
    return results[0]

@app.get("/get-table-headers")
def get_table_headers() -> List[Dict[Any, Any]]:
    fixtures =  pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    load_plugins_from_dir(fixtures, "src/fixtures")
    results = fixtures.hook.get_table_headers()
    return results[0]

@app.get("/get-properties")
def get_properties() -> Dict[Any, Any]:
    fixtures =  pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    load_plugins_from_dir(fixtures, "src/fixtures")
    results = fixtures.hook.get_properties()
    return results[0]

@app.get("/get-icon")
def get_icon() -> str:
    fixtures =  pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    load_plugins_from_dir(fixtures, "src/fixtures")
    results = fixtures.hook.get_icon()
    return results[0]

if __name__ == "__main__":
    pass