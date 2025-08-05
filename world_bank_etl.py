import os
import requests
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorldBankETL:
    def __init__(self):
        self.base_url = "https://api.worldbank.org/v2"
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "WorldBank-ETL/1.0", "Accept": "application/json"}
        )

        # Snowflake configuration
        self.snowflake_config = {
            "account": os.environ["SNOWFLAKE_ACCOUNT"],
            "user": os.environ["SNOWFLAKE_USER"],
            "password": os.environ["SNOWFLAKE_PASSWORD"],
            "database": os.environ["SNOWFLAKE_DATABASE"],
            "schema": os.environ["SNOWFLAKE_SCHEMA"],
            "warehouse": os.environ.get("SNOWFLAKE_WAREHOUSE"),
        }

        self.engine = self._create_snowflake_engine()

    def _create_snowflake_engine(self):
        """Create Snowflake SQLAlchemy engine"""
        url_params = {
            "account": self.snowflake_config["account"],
            "user": self.snowflake_config["user"],
            "password": self.snowflake_config["password"],
            "database": self.snowflake_config["database"],
            "schema": self.snowflake_config["schema"],
        }

        if self.snowflake_config["warehouse"]:
            url_params["warehouse"] = self.snowflake_config["warehouse"]

        url = URL(**url_params)
        return create_engine(url)

    def extract_countries(self) -> List[Dict[str, Any]]:
        """Extract country data from World Bank API"""
        logger.info("Extracting country data...")

        url = f"{self.base_url}/countries?format=json&per_page=500"
        response = self.session.get(url)
        response.raise_for_status()

        data = response.json()
        if len(data) > 1:
            countries = data[1]  # Skip metadata in first element
            logger.info(f"Extracted {len(countries)} countries")
            return countries
        return []

    def extract_indicators(
        self,
        country_codes: List[str],
        indicator_codes: List[str],
        date_range: str = "2016:2020",
    ) -> List[Dict[str, Any]]:
        """Extract indicator data for specific countries and indicators"""
        logger.info(f"Extracting indicators for {len(country_codes)} countries...")

        all_data = []

        for country in country_codes:
            for indicator in indicator_codes:
                url = f"{self.base_url}/countries/{country}/indicators/{indicator}"
                params = {"format": "json", "date": date_range, "per_page": 1000}

                try:
                    response = self.session.get(url, params=params)
                    response.raise_for_status()

                    data = response.json()
                    if len(data) > 1 and data[1]:
                        for record in data[1]:
                            record["extracted_at"] = datetime.now().isoformat()
                            all_data.append(record)

                        logger.info(
                            f"Extracted {len(data[1])} records for {country}-{indicator}"
                        )

                except Exception as e:
                    logger.error(f"Error extracting {country}-{indicator}: {e}")
                    continue

        logger.info(f"Total extracted records: {len(all_data)}")
        return all_data

    def transform_countries(self, countries_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Transform countries data into normalized format"""
        logger.info("Transforming countries data...")

        transformed = []
        for country in countries_data:
            record = {
                "country_id": country.get("id"),
                "country_code": country.get("iso2Code"),
                "country_name": country.get("name"),
                "capital_city": country.get("capitalCity"),
                "longitude": country.get("longitude"),
                "latitude": country.get("latitude"),
                "income_level": country.get("incomeLevel", {}).get("value"),
                "lending_type": country.get("lendingType", {}).get("value"),
                "region": country.get("region", {}).get("value"),
                "admin_region": country.get("adminregion", {}).get("value"),
                "transformed_at": datetime.now().isoformat(),
            }
            transformed.append(record)

        df = pd.DataFrame(transformed)
        df = df.dropna(subset=["country_id"])  # Remove records without country_id

        # Convert numeric columns
        numeric_cols = ["longitude", "latitude"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        logger.info(f"Transformed {len(df)} country records")
        return df

    def transform_indicators(
        self, indicators_data: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Transform indicators data into normalized format"""
        logger.info("Transforming indicators data...")

        transformed = []
        for record in indicators_data:
            item = {
                "country_id": record.get("country", {}).get("id"),
                "country_code": record.get("country", {}).get("value"),
                "indicator_id": record.get("indicator", {}).get("id"),
                "indicator_name": record.get("indicator", {}).get("value"),
                "year": record.get("date"),
                "value": record.get("value"),
                "unit": record.get("unit"),
                "obs_status": record.get("obs_status"),
                "decimal": record.get("decimal"),
                "extracted_at": record.get("extracted_at"),
                "transformed_at": datetime.now().isoformat(),
            }
            transformed.append(item)

        df = pd.DataFrame(transformed)
        df = df.dropna(subset=["country_id", "indicator_id", "year"])

        # Convert data types
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["decimal"] = pd.to_numeric(df["decimal"], errors="coerce")

        logger.info(f"Transformed {len(df)} indicator records")
        return df

    def load_to_snowflake(
        self, df: pd.DataFrame, table_name: str, if_exists: str = "replace"
    ):
        """Load DataFrame to Snowflake"""
        logger.info(f"Loading {len(df)} records to {table_name}...")

        try:
            df.to_sql(
                table_name,
                con=self.engine,
                if_exists=if_exists,
                index=False,
                method="multi",
                chunksize=1000,
            )
            logger.info(f"Successfully loaded data to {table_name}")

        except Exception as e:
            logger.error(f"Error loading to {table_name}: {e}")
            raise

    def run_etl(self):
        """Run the complete ETL pipeline"""
        logger.info("Starting World Bank ETL pipeline...")

        try:
            # Extract countries
            countries_raw = self.extract_countries()
            countries_df = self.transform_countries(countries_raw)
            self.load_to_snowflake(countries_df, "world_bank_countries")

            # Extract indicators for major countries and common indicators
            major_countries = [
                "CHN",
                "IND",
                "JPN",
                "DEU",
                "GBR",
                "FRA",
                "USA",
                "CAN",
                "MEX",
                "BRA",
                "ARG",
                "COL",
                "NGA",
                "EGY",
                "ZAF",
                "AUS",
                "NZL",
                "PNG",
            ]
            common_indicators = [
                "SP.POP.TOTL",  # Population, total
                "NY.GDP.MKTP.CD",  # GDP (current US$)
                "NY.GDP.PCAP.CD",  # GDP per capita (current US$)
                "SL.UEM.TOTL.ZS",  # Unemployment, total (% of total labor force)
                "SP.DYN.LE00.IN",  # Life expectancy at birth, total (years)
                "NY.GDP.MKTP.KD.ZG", # GDP growth (annual %)
                "EN.GHG.CO2.PC.CE.AR5", # Global CO2 Emissions excluding LULUCF (Tons/capita 2020)
                "EG.FEC.RNEW.ZS",  # Global Renewable Energy (2020)
                "EN.GHG.CO2.MT.CE.AR5", # CO2 Emissions excluding LULUCF by Country (2020)
                "SP.URB.TOTL.IN.ZS", # Urban population (% of total) - Urbanization level
                "SE.ADT.LITR.ZS", # Literacy rate, adult total (%) - Education level
            ]

            indicators_raw = self.extract_indicators(major_countries, common_indicators)
            indicators_df = self.transform_indicators(indicators_raw)
            self.load_to_snowflake(indicators_df, "world_bank_indicators")

            logger.info("ETL pipeline completed successfully!")

        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            raise


if __name__ == "__main__":
    # Validate environment variables
    required_vars = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
    ]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        exit(1)

    # Run ETL
    etl = WorldBankETL()
    etl.run_etl()
