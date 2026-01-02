from model import ExchangeModel
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer, TextElement
from mesa.visualization.UserParam import Slider


# HTML Element for the Strategy Dashboard - Display the 3-column strategy dashboard (Pending & Completed)
class StrategyDashboardElement(TextElement):

    def render(self, model):
        return model.get_strategy_summary()

#  HTML Element for the Leaderboard Dashboard - Display the new leaderboard and summary dashboard
class MarketLeadersElement(TextElement):

    def render(self, model):
        return model.get_market_leaders_dashboard()


class InfoElement(TextElement):

    def render(self, model):

        return """
        <p style='font-size: 12px; color: #555; text-align: center; margin-top: 10px;'>
            <b>Note:</b> Starting agent net worth is ~$1500, but varies slightly
            because initial stock prices are randomized at the start of each run.
        </p>
        """

#  Price Chart
price_chart = ChartModule(
    [
        {"Label": "STOCK-A", "Color": "#FF5733"},
        {"Label": "STOCK-B", "Color": "#33FF57"},
        {"Label": "STOCK-C", "Color": "#3357FF"},
        {"Label": "STOCK-D", "Color": "#FF33A1"},
        {"Label": "STOCK-E", "Color": "#33FFF6"},
    ],
    data_collector_name="datacollector"
)

#  Instantiate the dashboard elements
strategy_dashboard = StrategyDashboardElement()
market_leaders_dashboard = MarketLeadersElement()
info_note = InfoElement()

#  Model Parameters
model_params = {
    "num_random": Slider(
        "Number of Random Agents", 10, 0, 50, 1
    ),
    "num_momentum": Slider(
        "Number of Momentum Agents", 10, 0, 50, 1
    ),
    "num_value": Slider(
        "Number of Value Agents", 10, 0, 50, 1
    ),
    "num_stocks": Slider(
        "Number of Stocks", 1, 1, 5, 1
    )
}

# Server Setup
server = ModularServer(
    ExchangeModel,
    [
        price_chart,
        strategy_dashboard,
        market_leaders_dashboard,
        info_note
    ],
    "Stock Market Simulator",
    model_params
)

