import pluggy
from typing import Generator, Dict, List, Any
from model import PluginResult, PluginQuery, AppResult
from settings import APPLICATION_NAME

hookspec = pluggy.HookspecMarker(APPLICATION_NAME + "-plugins")
class PluginSpecs:
    @hookspec
    def extract(self, query: PluginQuery) -> Generator[PluginResult, None, None]:
        pass
    @hookspec
    def transform(self, data: PluginResult) -> Generator[PluginResult, None, None]:
        pass
    @hookspec
    def load(self, data: PluginResult) -> Generator[PluginResult, None, None]:
        pass

hookspec_fixtures = pluggy.HookspecMarker(APPLICATION_NAME + "-fixtures")
class FixtureSpecs:
    @hookspec_fixtures
    def merge_results(self, kv_store: Dict[str, PluginResult]) -> AppResult:
        pass
    @hookspec_fixtures
    def get_table_headers(self) -> List[Dict[Any, Any]]:
        pass
    @hookspec_fixtures
    def get_properties(self) -> Dict[Any, Any]:
        pass
    @hookspec_fixtures
    def get_icon(self) -> str:
        pass