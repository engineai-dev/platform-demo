"""World Bank Global Economic Atlas Dashboard"""

import os

from engineai.sdk.dashboard import dashboard
from engineai.sdk.dashboard import formatting
from engineai.sdk.dashboard import layout
from engineai.sdk.dashboard.data.connectors import HttpGet
from engineai.sdk.dashboard.data.connectors import Snowflake
from engineai.sdk.dashboard.styling import color
from engineai.sdk.dashboard.widgets import categorical
from engineai.sdk.dashboard.widgets import content
from engineai.sdk.dashboard.widgets import maps
from engineai.sdk.dashboard.widgets import pie
from engineai.sdk.dashboard.widgets import table
from engineai.sdk.dashboard.widgets import tile
from engineai.sdk.dashboard.widgets import timeseries
from engineai.sdk.dashboard.widgets.components.charts import styling
from engineai.sdk.dashboard.widgets.components.charts.axis import scale

introduction_items = {
    "title": "# Sample Dashboard Guide",
    "content": """
This sample dashboard demonstrates how you can visualise and interact with real data using our platform. It&apos;s designed to showcase the capabilities of our product, highlighting how code translates into visual insights through [data connectors](https://docs.engineai.com/sdk/core_concepts/data/data_connectors.html).

- **SDK Guide**: [Explore the documentation](https://docs.engineai.com/sdk/core_concepts/overview.html) for supported widget types, data connectors, and advanced configuration options.

---

All data in this dashboard is sourced from the World Bank API, a trusted source of real-time and historical global development data.
If you want to build your own dashboards using this data, you can access the World Bank API for free — no API key required.
- **API Access**: [Access the free World Bank API](https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information) to use their data.

:world-bank: Copyright &copy; 2025 World Bank Group. All rights reserved.
""",
}

introductory_section = content.Content(
    data=introduction_items,
).add_items(
    content.MarkdownItem(data_key="title"),
    content.MarkdownItem(data_key="content"),
)

tiles = [
    tile.Tile(
        data=HttpGet(
            slug="http-world-bank-api-connector",
            path="/country/1W/indicator/NY.GDP.MKTP.KD.ZG?date=2020&format=json",
        )._1._0,
        items=[
            tile.NumberItem(
                data_column="value",
                label="Global GDP Growth (2020)",
                formatting=formatting.NumberFormatting(
                    scale=formatting.NumberScale.BASE,
                    decimals=1,
                    suffix="%",
                ),
            ),
        ],
    ),
    tile.Tile(
        data=HttpGet(
            slug="http-world-bank-api-connector",
            path="/country/1W/indicator/EN.GHG.CO2.PC.CE.AR5?date=2020&format=json",
        )._1._0,
        items=[
            tile.NumberItem(
                data_column="value",
                label="Global CO2 Emissions excluding LULUCF (Tons/capita 2020)",
                formatting=formatting.NumberFormatting(
                    scale=formatting.NumberScale.BASE,
                    decimals=1,
                ),
            ),
        ],
    ),
    tile.Tile(
        HttpGet(
            slug="http-world-bank-api-connector",
            path="/country/1W/indicator/EG.FEC.RNEW.ZS?date=2020&format=json",
        )._1._0,
        items=[
            tile.NumberItem(
                data_column="value",
                label="Global Renewable Energy (2020)",
                formatting=formatting.NumberFormatting(
                    scale=formatting.NumberScale.BASE,
                    decimals=1,
                    suffix="%",
                ),
            ),
        ],
    ),
    tile.Tile(
        data=HttpGet(
            slug="http-world-bank-api-connector",
            path="/country/ARG;AUS;BRA;CAN;CHN;COL;DEU;EGY;FRA;GBR;IND;JPN;MEX;NGA;NZL;PNG;USA;ZAF?format=json",
        )._0,
        items=[
            tile.NumberItem(
                data_column="total",
                label="Countries Tracked",
            ),
        ],
    ),
]

general_overview = table.Table(
    title="Top Countries by GDP for Each Region",
    data=Snowflake(
        slug="snowflake-world-bank-connector",
        query="""
            SELECT wbi.COUNTRY_NAME, wbc.REGION,
                MAX(CASE WHEN wbi.INDICATOR_ID = 'NY.GDP.PCAP.CD' THEN wbi.VALUE END) as gdp_per_capita,
                MAX(CASE WHEN wbi.INDICATOR_ID = 'SP.POP.TOTL' THEN wbi.VALUE END) as total_population,
                MAX(CASE WHEN wbi.INDICATOR_ID = 'SL.UEM.TOTL.ZS' THEN wbi.VALUE END) as unemployment_rate,
                MAX(CASE WHEN wbi.INDICATOR_ID = 'SP.DYN.LE00.IN' THEN wbi.VALUE END) as life_expectancy,
                MAX(CASE WHEN wbi.INDICATOR_ID = 'SP.URB.TOTL.IN.ZS' THEN wbi.VALUE END) as urbanization_level,
            FROM WORLD_BANK_INDICATORS wbi
            JOIN WORLD_BANK_COUNTRIES wbc ON wbi.COUNTRY_CODE = wbc.COUNTRY_CODE
            WHERE wbi.INDICATOR_ID IN ('NY.GDP.PCAP.CD', 'SP.POP.TOTL', 'SL.UEM.TOTL.ZS', 'SP.DYN.LE00.IN', 'SP.URB.TOTL.IN.ZS')
                AND wbi.YEAR = 2020
                AND wbi.COUNTRY_CODE != '1W'
            GROUP BY wbi.COUNTRY_CODE, wbi.COUNTRY_NAME, wbi.YEAR, wbc.REGION
            ORDER BY wbc.REGION
        """,
    ),
    columns=[
        table.TextColumn(
            data_column="COUNTRY_NAME",
            label="Country",
        ),
        table.TextColumn(
            data_column="REGION",
            label="Region",
        ),
        table.NumberColumn(
            data_column="GDP_PER_CAPITA",
            label="GDP per Capita",
            formatting=formatting.NumberFormatting(
                scale=formatting.NumberScale.BASE,
                prefix="$",
                decimals=2,
            ),
        ),
        table.NumberColumn(
            data_column="TOTAL_POPULATION",
            formatting=formatting.NumberFormatting(
                scale=formatting.NumberScale.DYNAMIC_ABSOLUTE,
                decimals=0,
            ),
        ),
        table.NumberColumn(
            data_column="UNEMPLOYMENT_RATE",
            formatting=formatting.NumberFormatting(
                scale=formatting.NumberScale.BASE,
                decimals=2,
                suffix="%",
            ),
        ),
        table.NumberColumn(
            data_column="LIFE_EXPECTANCY",
            formatting=formatting.NumberFormatting(
                scale=formatting.NumberScale.DYNAMIC_ABSOLUTE,
                decimals=0,
            ),
        ),
        table.NumberColumn(
            data_column="URBANIZATION_LEVEL",
            formatting=formatting.NumberFormatting(
                scale=formatting.NumberScale.BASE,
                decimals=2,
                suffix="%",
            ),
        ),
    ],
    has_search_box=True,
)

gdp_growth = timeseries.Timeseries(
    title="GDP Growth Over Time",
    data=Snowflake(
        slug="snowflake-world-bank-connector",
        query=f"""
            SELECT DATE_PART(EPOCH_SECOND, TO_DATE(YEAR || '-01-01', 'YYYY-MM-DD')) * 1000 as date, VALUE
            FROM WORLD_BANK_INDICATORS
            WHERE INDICATOR_ID='NY.GDP.MKTP.CD'
                AND YEAR BETWEEN 2016 AND 2020
                AND COUNTRY_NAME = {general_overview.selected.COUNTRY_NAME}
            ORDER BY YEAR
        """,
    ),
    date_column="DATE",
    charts=[
        timeseries.Chart(
            left_y_axis=timeseries.YAxis(
                title="GDP (US$)",
                series=[
                    timeseries.LineSeries(
                        data_column="VALUE",
                        name="GDP",
                    ),
                ],
            )
        )
    ],
    period_selector=timeseries.PeriodSelector(
        timeseries.Period.ALL,
    ),
)

country_vs_region = categorical.Categorical(
    title=f"{general_overview.selected.COUNTRY_NAME} vs {general_overview.selected.REGION}",
    data=Snowflake(
        slug="snowflake-world-bank-connector",
        query=f"""
            WITH global_co2 AS (
                SELECT VALUE as global_total
                FROM WORLD_BANK_INDICATORS
                WHERE INDICATOR_ID = 'EN.GHG.CO2.MT.CE.AR5'
                    AND YEAR = 2020
                    AND COUNTRY_NAME = 'World'
            ),
            regional_co2 AS (
                SELECT SUM(wbi.VALUE) as regional_total
                FROM WORLD_BANK_INDICATORS wbi
                JOIN WORLD_BANK_COUNTRIES wbc ON wbi.COUNTRY_NAME = wbc.COUNTRY_NAME
                WHERE wbi.INDICATOR_ID = 'EN.GHG.CO2.MT.CE.AR5'
                    AND wbi.YEAR = 2020
                    AND wbc.REGION = (SELECT REGION FROM WORLD_BANK_COUNTRIES WHERE COUNTRY_NAME = {general_overview.selected.COUNTRY_NAME})
            ),
            regional_avg AS (
                SELECT
                    wbi.INDICATOR_ID,
                    AVG(wbi.VALUE) as regional_value
                FROM WORLD_BANK_INDICATORS wbi
                JOIN WORLD_BANK_COUNTRIES wbc ON wbi.COUNTRY_NAME = wbc.COUNTRY_NAME
                WHERE wbi.INDICATOR_ID IN ('NY.GDP.MKTP.KD.ZG', 'EG.FEC.RNEW.ZS', 'SL.UEM.TOTL.ZS')
                    AND wbi.YEAR = 2020
                    AND wbc.REGION = (SELECT REGION FROM WORLD_BANK_COUNTRIES WHERE COUNTRY_NAME = {general_overview.selected.COUNTRY_NAME})
                GROUP BY wbi.INDICATOR_ID
            )
            SELECT
                CASE
                    WHEN wbi.INDICATOR_ID = 'NY.GDP.MKTP.KD.ZG' THEN 'GDP Growth'
                    WHEN wbi.INDICATOR_ID = 'EG.FEC.RNEW.ZS' THEN 'Renewable Energy'
                    WHEN wbi.INDICATOR_ID = 'SL.UEM.TOTL.ZS' THEN 'Unemployment Rate'
                    WHEN wbi.INDICATOR_ID = 'EN.GHG.CO2.MT.CE.AR5' THEN 'Global CO2 Emissions'
                END as indicator,
                CASE
                    WHEN wbi.INDICATOR_ID = 'EN.GHG.CO2.MT.CE.AR5' THEN
                        ROUND((MAX(CASE WHEN wbi.COUNTRY_NAME = {general_overview.selected.COUNTRY_NAME} THEN wbi.VALUE END) / gc.global_total) * 100, 2)
                    ELSE MAX(CASE WHEN wbi.COUNTRY_NAME = {general_overview.selected.COUNTRY_NAME} THEN wbi.VALUE END)
                END as country_value,
                CASE
                    WHEN wbi.INDICATOR_ID = 'EN.GHG.CO2.MT.CE.AR5' THEN
                        ROUND((rc.regional_total / gc.global_total) * 100, 2)
                    ELSE ra.regional_value
                END as regional_value
            FROM WORLD_BANK_INDICATORS wbi
            CROSS JOIN global_co2 gc
            CROSS JOIN regional_co2 rc
            LEFT JOIN regional_avg ra ON wbi.INDICATOR_ID = ra.INDICATOR_ID
            WHERE wbi.INDICATOR_ID IN ('NY.GDP.MKTP.KD.ZG', 'EG.FEC.RNEW.ZS', 'SL.UEM.TOTL.ZS', 'EN.GHG.CO2.MT.CE.AR5')
                AND wbi.YEAR = 2020
                AND wbi.COUNTRY_NAME = {general_overview.selected.COUNTRY_NAME}
            GROUP BY wbi.INDICATOR_ID, gc.global_total, rc.regional_total, ra.regional_value
        """,
    ),
    category_axis="INDICATOR",
    value_axis=categorical.ValueAxis(
        title="Share (%)",
        series=[
            categorical.ColumnSeries(
                data_column="COUNTRY_VALUE",
                name=f"{general_overview.selected.COUNTRY_NAME}",
            ),
            categorical.ColumnSeries(
                data_column="REGIONAL_VALUE",
                name=f"{general_overview.selected.REGION} Average",
            ),
        ],
        scale=scale.AxisScaleDynamic(),
        formatting=formatting.AxisNumberFormatting(
            scale=formatting.NumberScale.DYNAMIC_ABSOLUTE, suffix="%", decimals=2
        ),
    ),
)

general_overview_tab = layout.Tab(
    label="General Overview",
    content=layout.Grid(
        layout.Row(
            layout.Card(
                header=layout.CardHeader(title="Overview of Global Indicators"),
                content=general_overview,
            )
        ),
        layout.Row(
            layout.Card(
                content=layout.Grid(
                    layout.Row(
                        gdp_growth,
                        country_vs_region,
                    )
                )
            )
        ),
    ),
)


gdp_levels_color_map = color.DiscreteMap(
    color.DiscreteMapIntervalItem(
        min_value=0,
        max_value=15000,
        exclude_max=True,
        color=color.Palette.BLUE_POSITIVE_4,
    ),
    color.DiscreteMapIntervalItem(
        min_value=15000,
        max_value=35000,
        exclude_max=True,
        color=color.Palette.COCONUT_GREY,
    ),
    color.DiscreteMapIntervalItem(
        min_value=35000,
        max_value=70000,
        color=color.Palette.RED_NEGATIVE_4,
    ),
)

gdp_per_capita = categorical.Categorical(
    title="GDP Per Capita by Region (2020)",
    data=Snowflake(
        slug="snowflake-world-bank-connector",
        query="""
            SELECT wbc.REGION, AVG(wbi.VALUE) as avg_gdp_per_capita
            FROM WORLD_BANK_INDICATORS wbi
            JOIN WORLD_BANK_COUNTRIES wbc ON wbi.COUNTRY_CODE = wbc.COUNTRY_CODE
            WHERE wbi.INDICATOR_ID = 'NY.GDP.PCAP.CD' AND wbi.YEAR = 2020 AND wbi.COUNTRY_CODE != '1W'
            GROUP BY wbc.REGION
            ORDER BY avg_gdp_per_capita DESC
        """,
    ),
    category_axis="REGION",
    value_axis=categorical.ValueAxis(
        title="GDP (USD)",
        series=categorical.ColumnSeries(
            name="GDP Per Capita",
            data_column="AVG_GDP_PER_CAPITA",
            show_in_legend=False,
            styling=styling.ColumnSeriesStyling(
                color_spec=gdp_levels_color_map,
                marker_symbol=styling.enums.MarkerSymbol.CIRCLE,
            ),
        ),
        scale=scale.AxisScalePositive(),
        formatting=formatting.AxisNumberFormatting(
            scale=formatting.NumberScale.BASE,
            prefix="$",
            decimals=2,
        ),
    ),
    direction=categorical.ChartDirection.HORIZONTAL,
)

gdp_by_country = maps.Geo(
    title="GDP per Capita by Country (2020)",
    data=Snowflake(
        slug="snowflake-world-bank-connector",
        query="""
            SELECT DISTINCT COUNTRY_CODE, VALUE
            FROM WORLD_BANK_INDICATORS
            WHERE INDICATOR_ID = 'NY.GDP.PCAP.CD' AND YEAR = 2020 AND COUNTRY_CODE != '1W'
        """,
    ),
    region_column="COUNTRY_CODE",
    series=maps.NumericSeries(
        name="GDP",
        data_column="VALUE",
        styling=maps.SeriesStyling(color_spec=gdp_levels_color_map),
        formatting=formatting.NumberFormatting(
            scale=formatting.NumberScale.BASE,
            decimals=2,
            prefix="$",
        ),
    ),
)

economic_growth_tab = layout.Tab(
    label="Economic Growth",
    content=layout.Card(
        header=layout.CardHeader(title="Economic Growth Analysis"),
        content=layout.Grid(
            layout.Row(
                gdp_per_capita,
                gdp_by_country,
            ),
        ),
    ),
)


co2_emissions_trends = timeseries.Timeseries(
    title="CO2 Emission Trends by Region",
    data=Snowflake(
        slug="snowflake-world-bank-connector",
        query="""
            SELECT DATE_PART(EPOCH_SECOND, TO_DATE(wbi.YEAR || '-01-01', 'YYYY-MM-DD')) * 1000 as date,
                AVG(CASE WHEN wbc.REGION = 'North America' THEN wbi.VALUE END) as north_america,
                AVG(CASE WHEN wbc.REGION = 'Europe & Central Asia' THEN wbi.VALUE END) as europe_central_asia,
                AVG(CASE WHEN wbc.REGION = 'East Asia & Pacific' THEN wbi.VALUE END) as east_asia_pacific,
                AVG(CASE WHEN wbc.REGION = 'Latin America & Caribbean' THEN wbi.VALUE END) as latin_america_caribbean,
                AVG(CASE WHEN wbc.REGION = 'Middle East, North Africa, Afghanistan & Pakistan' THEN wbi.VALUE END) as middle_east_north_africa,
                AVG(CASE WHEN wbc.REGION = 'Sub-Saharan Africa' THEN wbi.VALUE END) as sub_saharan_africa,
                AVG(CASE WHEN wbc.REGION = 'South Asia' THEN wbi.VALUE END) as south_asia
            FROM WORLD_BANK_INDICATORS wbi
            JOIN WORLD_BANK_COUNTRIES wbc ON wbi.COUNTRY_CODE = wbc.COUNTRY_CODE
            WHERE wbi.INDICATOR_ID='EN.GHG.CO2.MT.CE.AR5'
                AND wbi.YEAR BETWEEN 2016 AND 2020
            GROUP BY wbi.YEAR
            ORDER BY wbi.YEAR
        """,
    ),
    date_column="DATE",
    charts=[
        timeseries.Chart(
            left_y_axis=timeseries.YAxis(
                title="CO2 Per Capita (Metric Tons)",
                series=[
                    timeseries.AreaSeries(
                        data_column="NORTH_AMERICA",
                        name="North America",
                        styling=color.Palette.MINT_GREEN,
                    ),
                    timeseries.AreaSeries(
                        data_column="EUROPE_CENTRAL_ASIA",
                        name="Europe & Central Asia",
                        styling=color.Palette.SUNSET_ORANGE,
                    ),
                    timeseries.AreaSeries(
                        data_column="EAST_ASIA_PACIFIC",
                        name="East Asia & Pacific",
                        styling=color.Palette.GRASS_GREEN,
                    ),
                    timeseries.AreaSeries(
                        data_column="LATIN_AMERICA_CARIBBEAN",
                        name="Latin America & Caribbean",
                        styling=color.Palette.LAVENDER_PURPLE,
                    ),
                    timeseries.AreaSeries(
                        data_column="MIDDLE_EAST_NORTH_AFRICA",
                        name="Middle East & North Africa",
                        styling=color.Palette.CHILI_RED,
                    ),
                    timeseries.AreaSeries(
                        data_column="SUB_SAHARAN_AFRICA",
                        name="Sub-Saharan Africa",
                        styling=color.Palette.BUBBLEGUM_PINK,
                    ),
                    timeseries.AreaSeries(
                        data_column="SOUTH_ASIA",
                        name="South Asia",
                        styling=color.Palette.ALMOND_BROWN,
                    ),
                ],
            )
        )
    ],
    period_selector=timeseries.PeriodSelector(
        timeseries.Period.ALL,
    ),
)

co2_emission_by_country = categorical.Categorical(
    title="CO2 Emissions excluding LULUCF by Region (2020)",
    data=Snowflake(
        slug="snowflake-world-bank-connector",
        query="""
            SELECT wbc.REGION, AVG(wbi.VALUE) as avg_co2_emissions
            FROM WORLD_BANK_INDICATORS wbi
            JOIN WORLD_BANK_COUNTRIES wbc ON wbi.COUNTRY_CODE = wbc.COUNTRY_CODE
            WHERE wbi.INDICATOR_ID = 'EN.GHG.CO2.MT.CE.AR5' AND wbi.YEAR = 2020 AND wbi.COUNTRY_CODE != '1W'
            GROUP BY wbc.REGION
        """,
    ),
    category_axis="REGION",
    value_axis=categorical.ValueAxis(
        title="CO2 Emissions (Metric Tons)",
        series=categorical.ColumnSeries(
            name="CO2 Emissions",
            data_column="AVG_CO2_EMISSIONS",
            show_in_legend=False,
            styling=styling.ColumnSeriesStyling(
                color_spec=color.DiscreteMap(
                    color.DiscreteMapIntervalItem(
                        min_value=0,
                        max_value=50,
                        exclude_max=True,
                        color="#2CCECB",
                    ),
                    color.DiscreteMapIntervalItem(
                        min_value=50,
                        max_value=100,
                        exclude_max=True,
                        color="#ABEDEC",
                    ),
                    color.DiscreteMapIntervalItem(
                        min_value=100,
                        max_value=300,
                        exclude_max=True,
                        color=color.Palette.BANANA_YELLOW,
                    ),
                    color.DiscreteMapIntervalItem(
                        min_value=300,
                        max_value=1000,
                        exclude_max=True,
                        color=color.Palette.SUNSET_ORANGE,
                    ),
                    color.DiscreteMapIntervalItem(
                        min_value=1000,
                        max_value=5000,
                        exclude_max=True,
                        color=color.Palette.TIGER_ORANGE,
                    ),
                    color.DiscreteMapIntervalItem(
                        min_value=5000,
                        max_value=1000000,
                        color=color.Palette.RED_NEGATIVE_4,
                    ),
                ),
                marker_symbol=styling.enums.MarkerSymbol.CIRCLE,
            ),
        ),
        scale=scale.AxisScalePositive(),
        formatting=formatting.AxisNumberFormatting(
            scale=formatting.NumberScale.BASE,
            decimals=2,
            suffix=" Mt",
        ),
    ),
)

environmental_impact_tab = layout.Tab(
    label="Environmental Impact",
    content=layout.Card(
        header=layout.CardHeader(title="Environmental Impact Assessment"),
        content=layout.Grid(
            layout.Row(
                co2_emissions_trends,
                co2_emission_by_country,
            ),
        ),
    ),
)


energy_balance = pie.Pie(
    title="Renewable Energy Transition",
    data=Snowflake(
        slug="snowflake-world-bank-connector",
        query="""
            WITH avg_renewable AS (
                SELECT AVG(VALUE) as pct
                FROM (
                    SELECT DISTINCT COUNTRY_CODE, VALUE
                    FROM WORLD_BANK_INDICATORS
                    WHERE INDICATOR_ID='EG.FEC.RNEW.ZS' AND YEAR=2020 AND COUNTRY_CODE != '1W'
                )
            )
            SELECT 'Renewable' as energy_type, ROUND(pct, 1) as total_percentage FROM avg_renewable
            UNION ALL
            SELECT 'Non-Renewable' as energy_type, ROUND((100 - pct), 1) as total_percentage FROM avg_renewable
        """,
    ),
    series=pie.Series(
        name="",
        category_column="ENERGY_TYPE",
        data_column="TOTAL_PERCENTAGE",
        formatting=formatting.NumberFormatting(decimals=1, suffix="%"),
        styling=pie.SeriesStyling(
            color_spec=color.DiscreteMap(
                color.DiscreteMapValueItem(value=24.4, color="#ABEDEC"),
                color.DiscreteMapValueItem(value=75.6, color="#1A7A78"),
            ),
        ),
    ),
)

renewables_by_country = categorical.Categorical(
    title="Renewables by Country (2020)",
    data=Snowflake(
        slug="snowflake-world-bank-connector",
        query="""
            SELECT DISTINCT COUNTRY_CODE,
                COUNTRY_NAME,
                VALUE as RENEWABLE_PERCENTAGE,
                (100 - VALUE) as NON_RENEWABLE_PERCENTAGE
            FROM WORLD_BANK_INDICATORS
            WHERE INDICATOR_ID = 'EG.FEC.RNEW.ZS' AND YEAR = 2020 AND COUNTRY_CODE != '1W'
        """,
    ),
    category_axis="COUNTRY_NAME",
    value_axis=categorical.ValueAxis(
        title="Energy Share (%)",
        series=[
            categorical.ColumnSeries(
                data_column="RENEWABLE_PERCENTAGE",
                name="Renewable",
                stack="energy_mix",
                styling=styling.ColumnSeriesStyling(
                    color_spec="#ABEDEC",
                    marker_symbol=styling.enums.MarkerSymbol.CIRCLE,
                ),
            ),
            categorical.ColumnSeries(
                data_column="NON_RENEWABLE_PERCENTAGE",
                name="Non-Renewable",
                stack="energy_mix",
                styling=styling.ColumnSeriesStyling(
                    color_spec="#1A7A78",
                    marker_symbol=styling.enums.MarkerSymbol.CIRCLE,
                ),
            ),
        ],
        scale=scale.AxisScalePositive(),
        formatting=formatting.AxisNumberFormatting(
            scale=formatting.NumberScale.BASE,
            decimals=2,
            suffix=" %",
        ),
    ),
)

clean_energy_tab = layout.Tab(
    label="Clean Energy",
    content=layout.Card(
        header=layout.CardHeader(title="Renewable Energy Transition"),
        content=layout.Grid(
            layout.Row(
                energy_balance,
                renewables_by_country,
            ),
        ),
    ),
)

dashboard.Dashboard(
    workspace_slug=os.environ.get("WORKSPACE_SLUG", "demo-workspace"),
    app_slug=os.environ.get("APP_SLUG", "demo-app"),
    slug=os.environ.get("DASHBOARD_SLUG", "demo-dashboard"),
    content=dashboard.Page(
        title="Global Economic Atlas",
        content=[
            layout.Card(content=introductory_section),
            layout.Row(*tiles),
            layout.TabSection(
                general_overview_tab,
                economic_growth_tab,
                environmental_impact_tab,
                clean_energy_tab,
            ),
        ],
    ),
)
