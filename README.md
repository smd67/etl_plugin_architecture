# ETL Plugin Architecture
The ETL Plugin Architecture (EPA) is a generalized framework for rapidly developing projects that require data scraping. There are many freelance projects posted that require web scraping plus some minimal user interface. They are usually internal tools used for generating leads or finding buy opportunities on some product (books, real estate, stocks, etc.). EPA can be used to develop this type of tool quickly allowing me to charge less for development costs and you to get a workable solution more quickly. A new project will only require a set of fixtures and plugins to be written. The fixtures will control the look, feel, and content of the data displayed on the frontend. Plugins define a single thread of ETL processing and can be used to perform webscraping or reading from an API.

![Architecture](/images/etl_plugin_architecture.drawio.png)

## Abstractions
# Fixtures
Fixtures are used to perform processing steps outside of the ETL processing including:
    * Provide header structure to frontend
    * Provide properties to frontend
    * Provide an icon to the frontend
    * Merge the final results from the plugins

# Plugins
Plugins are customizable units that perform a single thread of ETL processing. All plugins need to implement an extract, transform, and a load method. Each plugin is executed within a chain that is part of a DAG. The DAG runs all of the Chains in parallel.
    * Extract - The extract method is used to pull data from various sources like REST APIs, web scraping, or databases.  
      One source per plugin is a good rule of thumb.
    * Transform - The transform method is used to clean, map, and transform the extracted data into a into a standardized 
      format.
    * Load -  The transformed, structured data is written into the destination system, typically a data warehouse or data 
      lake, also used to marshall data into an internal storage.

## Technology Stack
### Frontend
* Vue
* Javascript

### Backend
* Python
* Pluggy
* Bonobo
* Fast API
