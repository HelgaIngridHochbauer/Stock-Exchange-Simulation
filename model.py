import mesa

class TraderAgent(mesa.Agent):
    """
    A trader agent with a strategy.
    """

    def __init__(self, unique_id, model, strategy, start_cash=1000, start_stock=10):
        super().__init__(unique_id, model)

        # Agent properties
        self.strategy = strategy
        self.cash = start_cash

        # Portfolio now holds all available stocks
        self.portfolio = {name: start_stock for name in self.model.stock_names}

        # Strategy-specific properties
        self.value_thresholds = {
            name: self.random.uniform(35, 65) for name in self.model.stock_names
        }
        self.momentum_window = self.random.randint(2, 5)

    def get_net_worth(self):
        """
        Calculates the agent's total net worth (cash + value of all stocks).
        """
        stock_value = 0
        for stock_name, quantity in self.portfolio.items():
            if stock_name in self.model.prices:
                stock_value += quantity * self.model.prices[stock_name]
        return self.cash + stock_value

    def step(self):
        """
        The agent's "brain" or logic, called once per step.
        """

        if not self.model.stock_names:
            return
        stock_to_trade = self.random.choice(self.model.stock_names)

        current_price = self.model.prices[stock_to_trade]

        #  Apply "random" strategy
        if self.strategy == "random":
            if self.random.random() > 0.5:
                # Try to BUY
                if self.cash >= current_price:
                    self.model.place_buy_order(self, 1, stock_to_trade)
            else:
                # Try to SELL
                if self.portfolio[stock_to_trade] > 0:
                    self.model.place_sell_order(self, 1, stock_to_trade)

        #  "Momentum" Strategy
        elif self.strategy == "momentum":
            history = self.model.price_history[stock_to_trade]
            if len(history) > self.momentum_window:
                old_price = history[-self.momentum_window]

                if current_price > old_price:
                    if self.cash >= current_price:
                        self.model.place_buy_order(self, 1, stock_to_trade)
                elif current_price < old_price:
                    if self.portfolio[stock_to_trade] > 0:
                        self.model.place_sell_order(self, 1, stock_to_trade)

        #  "Value" Strategy
        elif self.strategy == "value":
            my_valuation = self.value_thresholds[stock_to_trade]

            if current_price < my_valuation:
                if self.cash >= current_price:
                    self.model.place_buy_order(self, 1, stock_to_trade)
            elif current_price > (my_valuation * 1.2):
                if self.portfolio[stock_to_trade] > 0:
                    self.model.place_sell_order(self, 1, stock_to_trade)


# 2. Exchange Agent

class ExchangeModel(mesa.Model):
    """
    The main model (ExchangeAgent) that manages the market.
    """

    def __init__(self, num_random=10, num_momentum=10, num_value=10, num_stocks=1):
        super().__init__()
        # Use strategy-specific counts
        self.num_agents = num_random + num_momentum + num_value
        self.num_stocks = num_stocks

        # Market Properties
        self.stock_names = [f"STOCK-{chr(65 + i)}" for i in range(self.num_stocks)]
        self.prices = {name: 50.0 + self.random.randint(-10, 10) for name in self.stock_names}
        self.price_history = {name: [price] for name, price in self.prices.items()}
        self.buy_orders = {name: [] for name in self.stock_names}
        self.sell_orders = {name: [] for name in self.stock_names}

        # Strategy-level tracking
        self.trades_by_strategy = {"random": 0, "momentum": 0, "value": 0}
        self.buys_by_strategy = {"random": 0, "momentum": 0, "value": 0}
        self.sells_by_strategy = {"random": 0, "momentum": 0, "value": 0}

        # Scheduler
        self.schedule = mesa.time.RandomActivation(self)

        # Create Agents
        agent_id = 0
        for i in range(num_random):
            agent = TraderAgent(agent_id, self, "random", 1000, 10)
            self.schedule.add(agent)
            agent_id += 1

        for i in range(num_momentum):
            agent = TraderAgent(agent_id, self, "momentum", 1000, 10)
            self.schedule.add(agent)
            agent_id += 1

        for i in range(num_value):
            agent = TraderAgent(agent_id, self, "value", 1000, 10)
            self.schedule.add(agent)
            agent_id += 1

        # DataCollector
        reporters = {}
        MAX_STOCKS_TO_PLOT = 5

        def get_price_reporter(stock_name):
            def reporter_func(model):
                if stock_name in model.prices:
                    return model.prices[stock_name]
                return None

            return reporter_func

        for i in range(MAX_STOCKS_TO_PLOT):
            stock_name = f"STOCK-{chr(65 + i)}"
            reporters[stock_name] = get_price_reporter(stock_name)

        self.datacollector = mesa.DataCollector(model_reporters=reporters)

    # Order Methods

    def place_buy_order(self, agent, quantity, stock_name):
        order = {"agent_id": agent.unique_id, "quantity": quantity, "strategy": agent.strategy}
        self.buy_orders[stock_name].append(order)

    def place_sell_order(self, agent, quantity, stock_name):
        order = {"agent_id": agent.unique_id, "quantity": quantity, "strategy": agent.strategy}
        self.sell_orders[stock_name].append(order)

    # Core Simulation Logic

    def match_trades(self):
        for stock_name in self.stock_names:
            buy_stock = self.buy_orders[stock_name]
            sell_stock = self.sell_orders[stock_name]
            self.random.shuffle(buy_stock)
            self.random.shuffle(sell_stock)

            matched_pairs_this_step = 0  # Keep track to avoid infinite loops if only self-trades exist

            while buy_stock and sell_stock:

                # Prevent infinite loops if only self-trades are left
                if matched_pairs_this_step > self.num_agents * 2:
                    break

                buy_order = buy_stock.pop(0)
                sell_order = sell_stock.pop(0)
                matched_pairs_this_step += 1  # Count the pair we pulled

                buyer = self.schedule.agents[buy_order["agent_id"]]
                seller = self.schedule.agents[sell_order["agent_id"]]

                # Check for self-trading
                if buyer.unique_id == seller.unique_id:
                    # If it's a self-trade, just discard both orders and try the next pair
                    continue

                trade_price = self.prices[stock_name]

                # Check if both parties can *still* complete the trade
                if buyer.cash >= trade_price and seller.portfolio[stock_name] > 0:
                    # If yes, execute the trade
                    buyer.cash -= trade_price
                    buyer.portfolio[stock_name] += 1

                    seller.cash += trade_price
                    seller.portfolio[stock_name] -= 1

                    # Track trades by strategy (ONLY count if trade happened)
                    self.trades_by_strategy[buyer.strategy] += 1
                    self.trades_by_strategy[seller.strategy] += 1
                # If validation fails OR it was a self-trade, the trade is dropped.

    def step(self):
        # 1. Reset strategy counters
        self.trades_by_strategy = {"random": 0, "momentum": 0, "value": 0}
        self.buys_by_strategy = {"random": 0, "momentum": 0, "value": 0}
        self.sells_by_strategy = {"random": 0, "momentum": 0, "value": 0}

        # 2. Run all agent 'step' methods
        self.schedule.step()

        # Tally pending orders *after* agents step
        for stock_name in self.stock_names:
            for order in self.buy_orders[stock_name]:
                self.buys_by_strategy[order["strategy"]] += 1
            for order in self.sell_orders[stock_name]:
                self.sells_by_strategy[order["strategy"]] += 1

        # 3. Update prices for each stock
        for stock_name in self.stock_names:
            buy_pressure = len(self.buy_orders[stock_name])
            sell_pressure = len(self.sell_orders[stock_name])

            if buy_pressure > sell_pressure:
                self.prices[stock_name] += 0.5
            elif sell_pressure > buy_pressure:
                self.prices[stock_name] -= 0.5
            self.prices[stock_name] = max(1.0, self.prices[stock_name])
            self.price_history[stock_name].append(self.prices[stock_name])

        # 4. Execute all trades
        self.match_trades()

        # 5. Log data
        self.datacollector.collect(self)

        # 6. Reset order books for the next step
        for stock_name in self.stock_names:
            self.buy_orders[stock_name] = []
            self.sell_orders[stock_name] = []


    # VISUALISATION METHODS

    #  Method for Server Visualization (HTML Version)

    def get_strategy_summary(self):
        """
        Returns the 3-column dashboard as formatted HTML.
        (Using your custom HTML and fixed variables)
        """
        style = """
        <style>
            .dashboard-container {
                display: flex;
                justify-content: space-around;
                font-size: 14px;
                font-family: sans-serif;
            }
            .strategy-column {
                border-collapse: collapse;
                width: 32%;
                border: 2px solid #ccc;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            }
            .strategy-column th {
                padding: 10px;
                border-bottom: 2px solid #ccc;
            }
            .strategy-column td {
                border-bottom: 1px solid #eee;
                padding: 8px 10px;
                text-align: center;

            }
            .header-random { background-color: #f09f2e; color: white; }
            .header-momentum { background-color: #5bde96; color: white; }
            .header-value { background-color: #de5b82; color: white; }

            .buy-row { color: #A94442; font-weight: bold; }
            .sell-row { color: #3C763D; font-weight: bold; }

            .category-title {
                text-align: left;
                font-weight: bold;
                padding-left: 10px;
                color: #555;
            }
        </style>
        """

        html = f"{style}<h2>Strategy Dashboard (Step: {self.schedule.steps})</h2>"
        html += "<div class='dashboard-container'>"

        # --- Build each column ---
        for strategy in ["random", "momentum", "value"]:
            html += "<table class='strategy-column'>"
            html += f"<tr><th class='header-{strategy}'>{strategy.upper()}</th></tr>"

            # --- Pending Orders (Yellow) ---
            html += "<tr><td class='category-title'>Pending Orders</td></tr>"
            html += f"<tr><td class='buy-row'>Buy Orders: {self.buys_by_strategy[strategy]}</td></tr>"
            html += f"<tr><td class='sell-row'>Sell Orders: {self.sells_by_strategy[strategy]}</td></tr>"

            # --- Completed Trades (Red/Green) ---
            html += "<tr><td class='category-title'>Completed This Step</td></tr>"
            html += f"<tr><td class='buy-row' style='color: #333;'>Total Trades: {self.trades_by_strategy[strategy]}</td></tr>"

            html += "<tr><td style='padding: 8px 10px;'>&nbsp;</td></tr>"

            html += "</table>"

        html += "</div>"
        return html

    #  Leaderboard Dashboard Function

    def get_market_leaders_dashboard(self):
        """
        Generates an HTML dashboard showing leaderboards and strategy performance.
        """


        all_agents = []
        for agent in self.schedule.agents:
            all_agents.append({
                "id": agent.unique_id,
                "strategy": agent.strategy,
                "net_worth": agent.get_net_worth()
            })


        all_agents.sort(key=lambda x: x["net_worth"], reverse=True)

        top_5 = all_agents[:5]  # Get first 5
        bottom_5 = all_agents[-5:]  # Get last 5
        bottom_5.reverse()  # Show poorest agent first


        strategy_wealth = {"random": [], "momentum": [], "value": []}
        for agent_dict in all_agents:
            # Need to check if the strategy key exists (if agent count is 0 for a type)
            if agent_dict["strategy"] in strategy_wealth:
                strategy_wealth[agent_dict["strategy"]].append(agent_dict["net_worth"])

        averages = {}
        for strategy, wealths in strategy_wealth.items():
            if wealths:
                averages[strategy] = sum(wealths) / len(wealths)
            else:
                averages[strategy] = 0  # Handle case with 0 agents of a type



        style = """
        <style>
            .leaderboard-container {
                display: flex;
                justify-content: space-around;
                font-size: 14px;
                font-family: sans-serif;
            }
            .leaderboard-column {
                border-collapse: collapse;
                width: 32%;
                border: 2px solid #ccc;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            }
            .leaderboard-column th {
                padding: 10px;
                border-bottom: 2px solid #ccc;
                font-size: 16px;
            }
            .leaderboard-column td {
                border-bottom: 1px solid #eee;
                padding: 8px 10px;
                text-align: left;
            }
            .header-top { background-color: #5cb85c; color: white; }
            .header-bottom { background-color: #d9534f; color: white; }
            .header-summary { background-color: #428bca; color: white; }

            .rank-1 { font-weight: bold; color: #C9B037; } /* Gold */
            .rank-2 { font-weight: bold; color: #B4B4B4; } /* Silver */
            .rank-3 { font-weight: bold; color: #A0724C; } /* Bronze */

            .strat-momentum { color: #5bde96; font-weight: bold; }
            .strat-value { color: #de5b82; font-weight: bold; }
            .strat-random { color: #f09f2e; font-weight: bold; }
        </style>
        """

        html = f"{style}<h2>Market Performance Dashboard</h2>"
        html += "<div class='leaderboard-container'>"

        # --- Top 5 Agents Column ---
        html += "<table class='leaderboard-column'>"
        html += "<tr><th class='header-top'>Top 5 Richest Agents</th></tr>"
        rank = 1
        for agent in top_5:
            html += f"""
                <tr>
                    <td>
                        <span class='rank-{rank if rank <= 3 else 'other'}'>#{rank}:</span>
                        Agent {agent['id']} (<span class='strat-{agent['strategy']}'>{agent['strategy']}</span>)
                        <span style="float: right; font-weight: bold;">${agent['net_worth']:.2f}</span>
                    </td>
                </tr>
            """
            rank += 1
        html += "</table>"

        #  Strategy Summary Column
        html += "<table class='leaderboard-column'>"
        html += "<tr><th class='header-summary'>Average Net Worth</th></tr>"
        html += f"""
            <tr>
                <td>
                    <span class='strat-momentum'>Momentum Avg:</span>
                    <span style="float: right; font-weight: bold;">${averages['momentum']:.2f}</span>
                </td>
            </tr>
            <tr>
                <td>
                    <span class='strat-value'>Value Avg:</span>
                    <span style="float: right; font-weight: bold;">${averages['value']:.2f}</span>
                </td>
            </tr>
            <tr>
                <td>
                    <span class='strat-random'>Random Avg:</span>
                    <span style="float: right; font-weight: bold;">${averages['random']:.2f}</span>
                </td>
            </tr>
        """
        html += "</table>"

        #  Bottom 5 Agents Column
        html += "<table class='leaderboard-column'>"
        html += "<tr><th class='header-bottom'>Top 5 Poorest Agents</th></tr>"
        rank = len(all_agents)
        for agent in bottom_5:
            html += f"""
                <tr>
                    <td>
                        <span>#{rank}:</span>
                        Agent {agent['id']} (<span class='strat-{agent['strategy']}'>{agent['strategy']}</span>)
                        <span style="float: right; font-weight: bold;">${agent['net_worth']:.2f}</span>
                    </td>
                </tr>
            """
            rank -= 1
        html += "</table>"

        html += "</div>"
        return html

