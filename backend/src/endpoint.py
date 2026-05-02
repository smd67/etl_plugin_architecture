"""
This file is an API implementation for all of the endpoints that the frontend
needs to operate.
    * get-table-headers - Returns the JSON definition aof the table headers to 
      the frontend by calling a user defined fixture.
    * get-properties - Returns a JSON dictionary that defines properties for the 
      frontend like a title, an icon image to display, and color options.
    * get-icon - Return the icon image used by the frontend.
    * fetch - fetches all of the data by running all of the plugins as 
      chains within a DAG. A merge fixture is called after the plugins are run.
"""

# System imports
import importlib.util
import os
import pathlib
from typing import Any, Dict, List

# 3rd party imports
import bonobo
import pluggy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from model import AppResult, PluginQuery, PluginResult
from specs import FixtureSpecs, PluginSpecs

# Global variables
application_name = os.getenv("APPLICATION_NAME")
APPLICATION_NAME: str = application_name if application_name else ""
KV_STORE: Dict[Any, Any] = {}

# Fast API declarations
origins = ["*"]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def store_results(data: PluginResult):
    """
    Stores the results of all of the pipeline runs with the Plug-in Name as key.

    Parameters
    ----------
    data : PluginResult
        An individual result of the etl process
    """
    print(f"IN store_results. name={data.plugin_name}; data={data.plugin_data}")
    if data.plugin_name not in KV_STORE:
        KV_STORE[data.plugin_name] = []
    KV_STORE[data.plugin_name].append(data.plugin_data)


def load_plugins_from_dir(pm: pluggy.PluginManager, directory: str):
    """
    Utility function to load all of the plugins from a specified directory.

    Parameters
    ----------
    pm : pluggy.PluginManager
        The plugin managere to store the plugin modules in.

    directory : str
        The name of the directory to load plugins from.
    """
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
def fetch(query: Dict[Any, Any]) -> AppResult:
    """
    Endpoint that fetches all of the data by running all of the plugins as 
    chains within a DAG. A merge fixture is called after the plugins are run.

    Parameters
    ----------
    query : Dict[Any, Any]
        A generic query that has data that the plugin understands.

    Returns
    -------
    AppResult
        A generic result that contains the data after the merge step completed.
    """
    
    # Setup Plugin Manager
    pm = pluggy.PluginManager(APPLICATION_NAME + "-plugins")
    pm.add_hookspecs(PluginSpecs)

    # Load plugins from the 'plugins' folder
    plugin_dir = os.getenv("PLUGINS_DIR")
    load_plugins_from_dir(pm, plugin_dir if plugin_dir else "src/plugins")

    plugin_query = PluginQuery[Dict[Any, Any]](data=query)

    # Create a Bonobo DAG and add chains to it. A chain is the extract,
    # transform, and load methods from a plugin run sequentially. Each chain,
    # however, is run in parallel. 
    graph = bonobo.Graph()
    graph.add_chain(store_results, _input=None)
    for name, plugin in pm.list_name_plugin():
        graph.add_chain(
            plugin.extract(plugin_query),
            plugin.transform,
            plugin.load,
            _output=store_results,
        )
    bonobo.run(graph)

    # After the DAG is run and all of the results are collected, the 
    # merge_results fixture is executed to perform final processing.
    fixtures = pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    fixtures_dir = os.getenv("FIXTURES_DIR")
    load_plugins_from_dir(
        fixtures, fixtures_dir if fixtures_dir else "src/fixtures"
    )
    results = fixtures.hook.merge_results(kv_store=KV_STORE)

    # Finally, the results are returned.
    return results[0]


@app.get("/get-table-headers")
def get_table_headers() -> List[Dict[Any, Any]]:
    """
    Endpoint that returns the JSON definition aof the table headers to the
    frontend by calling a user defined fixture.

    Returns
    -------
    List[Dict[Any, Any]]
        A list of objects where each element defines a column for the frontend
        table.
    """
    fixtures = pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    fixtures_dir = os.getenv("FIXTURES_DIR")
    load_plugins_from_dir(
        fixtures, fixtures_dir if fixtures_dir else "src/fixtures"
    )
    results = fixtures.hook.get_table_headers()
    return results[0]


@app.get("/get-properties")
def get_properties() -> Dict[Any, Any]:
    """
    Endpoint that returns a JSON dictionary that defines properties for the 
    frontend like a title, an icon image to display, and color options.

    Returns
    -------
    Dict[Any, Any]
        A dictionary of various properties.
    """
    fixtures = pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    fixtures_dir = os.getenv("FIXTURES_DIR")
    load_plugins_from_dir(
        fixtures, fixtures_dir if fixtures_dir else "src/fixtures"
    )
    results = fixtures.hook.get_properties()
    return results[0]


@app.get("/get-icon")
def get_icon() -> str:
    """
    Enpoint that runs a fixture to return the icon image used by the frontend.

    Returns
    -------
    str
        A base64 encoded string of the icon image.
    """
    fixtures = pluggy.PluginManager(APPLICATION_NAME + "-fixtures")
    fixtures.add_hookspecs(FixtureSpecs)
    fixtures_dir = os.getenv("FIXTURES_DIR")
    load_plugins_from_dir(
        fixtures, fixtures_dir if fixtures_dir else "src/fixtures"
    )
    results = fixtures.hook.get_icon()
    return results[0]


if __name__ == "__main__":
    pass
