"""
This file defines the interfaces for the plugins and the fixtures.

A Plugin is an ETL chain that can be used to perform webscraping, read from a
database, or read from a REST API, transform the data, then load it into 
internal storage.

Fixtures are used to perform processing steps outside of the ETL processing
including:
  * Provide header structure to frontend
  * Provide properties to frontend
  * Provide an icon to the frontend
  * Merge the final results from the plugins

"""
# System imports
import os
from typing import Any, Dict, Generator, List

# 3rd party imports
import pluggy
from model import AppResult, PluginQuery, PluginResult

# Global variables
APPLICATION_NAME  = os.getenv("APPLICATION_NAME", "")

hookspec = pluggy.HookspecMarker(APPLICATION_NAME + "-plugins")
class PluginSpecs:
    """
    This class defines the interface for all plugins. All plugins need to
    implement an extract, transform, and a load method. Each plugin is executed
    within a chain that is part of a DAG. The DAG runs all of the Chains in 
    parallel. 
    """
    @hookspec
    def extract(self, query: PluginQuery) -> Generator[PluginResult, None, None]:
        """
        The extract method is used to pull data from various sources like REST
        APIs, web scraping, or databases. One source per plugin is a good rule
        of thumb.

        Parameters
        ----------
        query : PluginQuery
           A generic query sent from the frontend that includes any information
           required to extract the data.

        Yields
        ------
        Generator[PluginResult, None, None]
            A generator is returned so data can be streamed to the next step
            without having to gather it or wait for completion.
        """
        yield

    @hookspec
    def transform(
        self, data: PluginResult
    ) -> Generator[PluginResult, None, None]:
        """
        The transform method is used to clean, map, and transform the extracted 
        data into a into a standardized format.

        Parameters
        ----------
        data : PluginResult
            A generic result that contains one row of extractred data.

        Yields
        ------
        Generator[PluginResult, None, None]
            A generator is returned so data can be streamed to the next step
            without having to gather it or wait for completion.
        """
        yield

    @hookspec
    def load(self, data: PluginResult) -> Generator[PluginResult, None, None]:
        """
        The transformed, structured data is written into the destination system, 
        typically a data warehouse or data lake, but in our case it is used
        to marshall data into an internal storage.

        Parameters
        ----------
        data : PluginResult
            A generic result that contains one row of transformed data.

        Yields
        ------
        Generator[PluginResult, None, None]
            A generator is returned so data can be streamed to the next step
            without having to gather it or wait for completion.
        """
        yield


hookspec_fixtures = pluggy.HookspecMarker(APPLICATION_NAME + "-fixtures")
class FixtureSpecs:
    """
    Fixtures are used to perform processing steps outside of the ETL processing
    including:
        * Provide header structure to frontend
        * Provide properties to frontend
        * Provide an icon to the frontend
        * Merge the final results from the plugins
    """
    @hookspec_fixtures
    def merge_results(self, kv_store: Dict[str, PluginResult]) -> AppResult:
        """
        This method can be used to take the results from all of the plugins and 
        merge them together into a single coherent result.

        Parameters
        ----------
        kv_store : Dict[str, PluginResult]
            The in-memory store of results by plugin-name.

        Returns
        -------
        AppResult
            The final merged results.
        """
        pass

    @hookspec_fixtures
    def get_table_headers(self) -> List[Dict[Any, Any]]:
        """
        This method returns a list of objects that describe a single column of
        data for the frontend.

        Returns
        -------
        List[Dict[Any, Any]]
            A list of column definitions
        """
        return []

    @hookspec_fixtures
    def get_properties(self) -> Dict[Any, Any]:
        """
        Returns a dictionary of properties used to control various attributes
        of the frontend.

        Returns
        -------
        Dict[Any, Any]
            A dictionary of properties.
        """
        return {}

    @hookspec_fixtures
    def get_icon(self) -> str:
        """
        Returns an icon image used by the frontend.

        Returns
        -------
        str
            A base64 encoded string of the icon image.
        """
        return ""
