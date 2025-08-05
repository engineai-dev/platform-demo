from engineai.sdk.dashboard.dashboard import Dashboard
from engineai.sdk.dashboard.dashboard import Page
from engineai.sdk.dashboard.dashboard import RootGrid
from engineai.sdk.dashboard.data.connectors import Snowflake
from engineai.sdk.dashboard.formatting import AxisNumberFormatting
from engineai.sdk.dashboard.formatting import NumberFormatting
from engineai.sdk.dashboard.formatting import NumberScale
from engineai.sdk.dashboard.layout import Card
from engineai.sdk.dashboard.layout import CardHeader
from engineai.sdk.dashboard.layout import Grid
from engineai.sdk.dashboard.layout import Row
from engineai.sdk.dashboard.layout import Tab
from engineai.sdk.dashboard.layout import TabSection
from engineai.sdk.dashboard.styling import color
from engineai.sdk.dashboard.styling.color import Palette
from engineai.sdk.dashboard.widgets import maps
from engineai.sdk.dashboard.widgets import pie
from engineai.sdk.dashboard.widgets.categorical import Categorical
from engineai.sdk.dashboard.widgets.categorical import ChartDirection
from engineai.sdk.dashboard.widgets.categorical import ColumnSeries
from engineai.sdk.dashboard.widgets.categorical import ValueAxis
from engineai.sdk.dashboard.widgets.components.charts.axis import scale
from engineai.sdk.dashboard.widgets.components.charts.styling import AreaSeriesStyling
from engineai.sdk.dashboard.widgets.components.charts.styling import ColumnSeriesStyling
from engineai.sdk.dashboard.widgets.components.charts.styling import enums
from engineai.sdk.dashboard.widgets.content import Content
from engineai.sdk.dashboard.widgets.content import MarkdownItem
from engineai.sdk.dashboard.widgets.tile import NumberStylingArrow
from engineai.sdk.dashboard.widgets.tile.content.items.number.item import NumberItem
from engineai.sdk.dashboard.widgets.tile.tile import Tile
from engineai.sdk.dashboard.widgets.timeseries import Timeseries
from engineai.sdk.dashboard.widgets.timeseries.axis.y_axis.y_axis import YAxis
from engineai.sdk.dashboard.widgets.timeseries.chart import Chart
from engineai.sdk.dashboard.widgets.timeseries.series.area import AreaSeries

introduction_items = {
    "title": "# Sample Dashboard Guide",
    "content": """
This sample dashboard demonstrates how you can visualise and interact with real data using our platform. It&apos;s designed to showcase the capabilities of our product, highlighting how code translates into visual insights through an OpenAPI data connector.

- **GitHub Project**: [Access the sample project](##############TODO) to see the full implementation.
- **SDK Guide**: [Explore the documentation](https://docs.engineai.com/sdk/core_concepts/overview.html) for supported widget types, data connectors, and advanced configuration options.

---

All data in this dashboard is sourced directly from the World Bank API, a trusted source of real-time and historical global development data.
If you want to build your own dashboards using this data, you can access the World Bank API for free — no API key required.
- **API Access**: [Access the free World Bank API](https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information) to use their data.

:world-bank: Copyright &copy; 2025 World Bank Group. All rights reserved.
""",
}

introductory_section = Content(
    data=introduction_items,
).add_items(MarkdownItem(data_key="title"), MarkdownItem(data_key="content"))


tiles = [
    Tile(
        data=Snowflake(
            slug="snowflake",
            query="SELECT * FROM WORLD_BANK_INDICATORS WHERE INDICATOR_ID='NY.GDP.MKTP.KD.ZG' AND YEAR=2020 AND COUNTRY_CODE='World';",
        ),
        items=[
            NumberItem(
                data_column="VALUE",
                label="Global GDP Growth (2020)",
                formatting=NumberFormatting(
                    scale=NumberScale.BASE, decimals=1, suffix=" %"
                ),
                styling=NumberStylingArrow(
                    data_column="VALUE",
                    color_divergent=color.Divergent(
                        mid_value=0,
                        mid_color=color.Palette.COCONUT_GREY,
                        above_color=color.Palette.BLUE_POSITIVE_4,
                        below_color=color.Palette.RED_NEGATIVE_4,
                    ),
                ),
            ),
        ],
    ),
    Tile(
        data=Snowflake(
            slug="snowflake",
            query="SELECT * FROM WORLD_BANK_INDICATORS WHERE INDICATOR_ID='EN.GHG.CO2.PC.CE.AR5' AND YEAR=2020 AND COUNTRY_CODE='World';",
        ),
        items=[
            NumberItem(
                data_column="VALUE",
                label="Global CO2 Emissions excluding LULUCF (Tons/capita 2020)",
                formatting=NumberFormatting(scale=NumberScale.BASE, decimals=1),
            ),
        ],
    ),
    Tile(
        data=Snowflake(
            slug="snowflake",
            query="SELECT * FROM WORLD_BANK_INDICATORS WHERE INDICATOR_ID='EG.FEC.RNEW.ZS' AND YEAR=2020 AND COUNTRY_CODE='World';",
        ),
        items=[
            NumberItem(
                data_column="VALUE",
                label="Global Renewable Energy (2020)",
                formatting=NumberFormatting(
                    scale=NumberScale.BASE, decimals=1, suffix=" %"
                ),
            ),
        ],
    ),
    Tile(
        data=Snowflake(
            slug="snowflake",
            query="SELECT COUNT(*) AS TOTAL FROM WORLD_BANK_COUNTRIES",
        ),
        items=[
            NumberItem(
                data_column="TOTAL",
                label="Countries Tracked",
            ),
        ],
    ),
]

gdp_levels_color_map = color.DiscreteMap(
    color.DiscreteMapIntervalItem(
        min_value=0,
        max_value=35000,
        exclude_max=True,
        color=color.Palette.BLUE_POSITIVE_4,
    ),
    color.DiscreteMapIntervalItem(
        min_value=35000,
        max_value=45000,
        exclude_max=True,
        color=color.Palette.COCONUT_GREY,
    ),
    color.DiscreteMapIntervalItem(
        min_value=45000,
        max_value=10000000,
        color=color.Palette.RED_NEGATIVE_4,
    ),
)

gdp_per_capita = Categorical(
    title="GDP Per Capita (2020)",
    data=Snowflake(
        slug="snowflake",
        query="SELECT DISTINCT COUNTRY_ID, COUNTRY_CODE, VALUE FROM WORLD_BANK_INDICATORS WHERE INDICATOR_ID='NY.GDP.PCAP.CD' AND YEAR=2020 AND COUNTRY_ID IN('CA', 'DE', 'FR', 'GB', 'IT', 'JP', 'US');",
    ),
    category_axis="COUNTRY_CODE",
    value_axis=ValueAxis(
        formatting=AxisNumberFormatting(
            scale=NumberScale.THOUSAND, prefix="$", decimals=2
        ),
        series=ColumnSeries(
            data_column="VALUE",
            name="GDP Per Capita",
            show_in_legend=False,
            styling=ColumnSeriesStyling(
                color_spec=gdp_levels_color_map,
                data_column="VALUE",
                marker_symbol=enums.MarkerSymbol.CIRCLE,
            ),
        ),
        title="GDP (USD)",
        scale=scale.AxisScalePositive(),
    ),
    direction=ChartDirection.HORIZONTAL,
)

gdp_by_country = maps.Geo(
    data=Snowflake(
        slug="snowflake",
        query="SELECT DISTINCT COUNTRY_ID, VALUE FROM WORLD_BANK_INDICATORS WHERE INDICATOR_ID='NY.GDP.PCAP.CD' AND YEAR=2020 AND COUNTRY_ID IN('CA', 'DE', 'FR', 'GB', 'IT', 'JP', 'US');",
    ),
    title="GDP by Country (2020)",
    region_column="COUNTRY_ID",
    series=maps.NumericSeries(
        data_column="VALUE",
        name="GDP",
        styling=maps.SeriesStyling(color_spec=gdp_levels_color_map),
    ),
)


tab1 = Tab(
    label="Economic Growth",
    content=Card(
        header=CardHeader(title="Economic Growth Analysis"),
        content=Grid(
            Row(
                gdp_per_capita,
                gdp_by_country,
                height=4.5,
            ),
        ),
    ),
    default_selected=True,
)

co2_emission_trends_chart = Chart(
    left_y_axis=YAxis(
        title="CO2 Per Capita (Mt)",
        series=[
            AreaSeries(
                data_column="VALUE_CA",
                name="Canada",
                styling=AreaSeriesStyling(color_spec=Palette.MINT_GREEN),
            ),
            AreaSeries(
                data_column="VALUE_DE",
                name="Germany",
                styling=AreaSeriesStyling(color_spec=Palette.GRASS_GREEN),
            ),
            AreaSeries(
                data_column="VALUE_FR",
                name="France",
                styling=AreaSeriesStyling(color_spec=Palette.LAVENDER_PURPLE),
            ),
            AreaSeries(
                data_column="VALUE_GB",
                name="United Kingdom",
                styling=AreaSeriesStyling(color_spec=Palette.SUNSET_ORANGE),
            ),
            AreaSeries(
                data_column="VALUE_IT",
                name="Italy",
                styling=AreaSeriesStyling(color_spec=Palette.SKY_BLUE),
            ),
            AreaSeries(
                data_column="VALUE_JP",
                name="Japan",
                styling=AreaSeriesStyling(color_spec=Palette.CHILI_RED),
            ),
            AreaSeries(
                data_column="VALUE_US",
                name="United States",
                styling=AreaSeriesStyling(color_spec=Palette.BUBBLEGUM_PINK),
            ),
        ],
    )
)

co2_emissions_trends = Timeseries(
    data=Snowflake(
        slug="snowflake",
        query="""SELECT DATE_PART(EPOCH_SECOND, TO_DATE(YEAR || '-01-01', 'YYYY-MM-DD')) * 1000 as date,
                    MAX(CASE WHEN COUNTRY_ID = 'CA' THEN VALUE END) as value_ca,
                    MAX(CASE WHEN COUNTRY_ID = 'DE' THEN VALUE END) as value_de,
                    MAX(CASE WHEN COUNTRY_ID = 'FR' THEN VALUE END) as value_fr,
                    MAX(CASE WHEN COUNTRY_ID = 'GB' THEN VALUE END) as value_gb,
                    MAX(CASE WHEN COUNTRY_ID = 'IT' THEN VALUE END) as value_it,
                    MAX(CASE WHEN COUNTRY_ID = 'JP' THEN VALUE END) as value_jp,
                    MAX(CASE WHEN COUNTRY_ID = 'US' THEN VALUE END) as value_us
                FROM WORLD_BANK_INDICATORS
                WHERE INDICATOR_ID='EN.GHG.CO2.MT.CE.AR5'
                    AND YEAR BETWEEN 2016 AND 2020
                    AND COUNTRY_ID IN ('CA', 'DE', 'FR', 'GB', 'IT', 'JP', 'US')
                GROUP BY YEAR
                ORDER BY YEAR""",
    ),
    date_column="DATE",
    charts=[co2_emission_trends_chart],
    title="CO2 Emission Trends",
)

co2_emission_by_country = Categorical(
    title="CO2 Emissions excluding LULUCF by Country (2020)",
    data=Snowflake(
        slug="snowflake",
        query="SELECT DISTINCT COUNTRY_ID, COUNTRY_CODE, VALUE FROM WORLD_BANK_INDICATORS WHERE INDICATOR_ID='EN.GHG.CO2.MT.CE.AR5' AND YEAR=2020 AND COUNTRY_ID IN('CA', 'DE', 'FR', 'GB', 'IT', 'JP', 'US');",
    ),
    category_axis="COUNTRY_CODE",
    value_axis=ValueAxis(
        formatting=AxisNumberFormatting(
            scale=NumberScale.BASE, decimals=2, suffix=" Mt"
        ),
        series=ColumnSeries(
            data_column="VALUE",
            name="CO2 Emissions",
            show_in_legend=False,
            styling=ColumnSeriesStyling(
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
                data_column="VALUE",
                marker_symbol=enums.MarkerSymbol.CIRCLE,
            ),
        ),
        title="CO2 Emissions (Million Tons)",
        scale=scale.AxisScalePositive(),
    ),
)

tab2 = Tab(
    label="Environmental Impact",
    content=Card(
        header=CardHeader(title="Environmental Impact Assessment"),
        content=Grid(
            Row(
                co2_emissions_trends,
                co2_emission_by_country,
                height=4.5,
            ),
        ),
    ),
)

energy_balance = pie.Pie(
    title="Renewable Energy Transition",
    data=Snowflake(
        slug="snowflake",
        query="""
            WITH avg_renewable AS (
                SELECT AVG(VALUE) as pct
                FROM (SELECT DISTINCT COUNTRY_ID, VALUE FROM WORLD_BANK_INDICATORS WHERE INDICATOR_ID='EG.FEC.RNEW.ZS' AND YEAR=2020 AND COUNTRY_ID IN('CA', 'DE', 'FR', 'GB', 'IT', 'JP', 'US'))
            )

            SELECT 'Renewable' as energy_type, pct as total_percentage FROM avg_renewable
            UNION ALL
            SELECT 'Non-Renewable' as energy_type, (100 - pct) as total_percentage FROM avg_renewable
            """,
    ),
    series=pie.Series(
        category_column="ENERGY_TYPE",
        data_column="TOTAL_PERCENTAGE",
        formatting=NumberFormatting(decimals=1, suffix="%"),
        styling=pie.SeriesStyling(
            data_column="ENERGY_TYPE",
            color_spec=color.DiscreteMap(
                color.DiscreteMapValueItem(value=15.9, color="#ABEDEC"),
                color.DiscreteMapValueItem(value=84.1, color="#1A7A78"),
            ),
        ),
    ),
)

renewables_by_country = Categorical(
    title="Renewables by Country (2020)",
    data=Snowflake(
        slug="snowflake",
        query="""SELECT DISTINCT COUNTRY_ID, COUNTRY_CODE,
                    VALUE as RENEWABLE_PERCENTAGE,
                    (100 - VALUE) as NON_RENEWABLE_PERCENTAGE
                FROM WORLD_BANK_INDICATORS
                WHERE INDICATOR_ID='EG.FEC.RNEW.ZS'
                    AND YEAR=2020
                    AND COUNTRY_ID IN('CA', 'DE', 'FR', 'GB', 'IT', 'JP', 'US')""",
    ),
    category_axis="COUNTRY_CODE",
    value_axis=ValueAxis(
        formatting=AxisNumberFormatting(
            scale=NumberScale.BASE, decimals=2, suffix=" %"
        ),
        series=[
            ColumnSeries(
                data_column="RENEWABLE_PERCENTAGE",
                name="Renewable",
                stack="energy_mix",
                styling=ColumnSeriesStyling(
                    color_spec="#ABEDEC",
                    data_column="RENEWABLE_PERCENTAGE",
                    marker_symbol=enums.MarkerSymbol.CIRCLE,
                ),
            ),
            ColumnSeries(
                data_column="NON_RENEWABLE_PERCENTAGE",
                name="Non-Renewable",
                stack="energy_mix",
                styling=ColumnSeriesStyling(
                    color_spec="#1A7A78",
                    data_column="NON_RENEWABLE_PERCENTAGE",
                    marker_symbol=enums.MarkerSymbol.CIRCLE,
                ),
            ),
        ],
        title="Energy Share (%)",
        scale=scale.AxisScalePositive(),
    ),
)

tab3 = Tab(
    label="Clean Energy",
    content=Card(
        header=CardHeader(title="Renewable Energy Transition"),
        content=Grid(
            Row(
                energy_balance,
                renewables_by_country,
                height=4.5,
            ),
        ),
    ),
)

Dashboard(
    workspace_slug="squad-papa",
    app_slug="sample-app-test",
    slug="world-bank-sample-dashboard",
    content=Page(
        title="G7 Energy & Emissions",
        content=RootGrid(
            Row(Card(content=introductory_section), height=3.25),
            Row(*tiles),
            TabSection(tab1, tab2, tab3),
        ),
    ),
)
