# Stock Market Agent Simulator

An agent-based simulation of a small stock market where prices emerge dynamically from the interactions of various traders. This project uses the **MESA** framework to simulate a decentralized market environment managed by a central Exchange Agent.

## Key Features

* **Multi-Stock Simulation:** Supports multiple concurrent stocks (e.g., STOCK-A, STOCK-B) within the same environment.
* **Emergent Dynamic Pricing:** Prices are not hard-coded; they emerge from the balance of supply (sell orders) and demand (buy orders) placed by agents at each step.
* **Matching Engine:** A centralized logic that matches orders and executes trades while strictly preventing self-trading.
* **Transactional Integrity:** Includes "match-time" validation to ensure agents cannot spend cash they don't have or sell inventory they don't own, preventing insolvency.
* **Real-Time Visualization:** A web-based dashboard featuring live price graphs, strategy performance logs, and a market leaderboard.

<img width="1871" height="925" alt="image" src="https://github.com/user-attachments/assets/98fa3a0a-49ce-48c8-a7b1-b1987f492520" />

---

##  Agent Design

### TraderAgent
The primary goal of each trader is to maximize their final cash balance.
* **Momentum Strategy:** Buys when the price is rising and sells when it is falling.
* **Value Strategy:** Buys if the price is below their personal "fair value" and sells if it is significantly higher. 
    * *Note: "Fair Value" is a personal opinion randomly assigned to each agent upon creation.*
* **Random Strategy:** Executes buy and sell orders at random intervals.

### ExchangeAgent (The Manager)
The ExchangeAgent facilitates the market by:
1.  Managing the central **Order Book**.
2.  Matching buy and sell orders.
3.  Updating prices based on market pressure.
4.  Hosting the GUI and data dashboards.

---

## Simulation Mechanics

### Initialization
To ensure immediate market activity, the simulation begins with:
* **Randomized Prices:** Initial stock prices are set around a base value (e.g., $50 ± $10).
* **Agent Endowments:** Every agent starts with **$1,000 cash** and **10 units of every stock** available in the market.

### Visualization Dashboard
Built with MESA’s visualization tools, the dashboard includes:
* **Live Price Graph:** Shows real-time price history ($Y$-axis: Price, $X$-axis: Time/Ticks).
  <img width="1149" height="477" alt="Screenshot 2026-01-09 103922" src="https://github.com/user-attachments/assets/a0ab666c-4279-44ae-9ada-30fbd9adc50a" />

* **Strategy Dashboard:** A 3-column view showing pending orders and trades completed in the last step for each strategy type.
  <img width="1187" height="512" alt="Screenshot 2026-01-09 103904" src="https://github.com/user-attachments/assets/f9e29b32-e1b3-4f69-a431-530e45614771" />

* **Market Performance:** A leaderboard showing the richest/poorest agents and the average net worth per strategy group.

<img width="1194" height="493" alt="Screenshot 2026-01-09 103911" src="https://github.com/user-attachments/assets/5f92bae0-64ff-46b8-b257-08c3831c2ccc" />

---

## 📁 Project Structure

* `model.py`: Contains the core logic for the `TraderAgent` and `ExchangeModel` (matching engine and data collection).
* `server.py`: Defines the visualization interface, custom HTML dashboards, and user-adjustable sliders.
* `run.py`: The entry point script to launch the MESA visualization server.

---

## 🛠️ Getting Started

### Prerequisites
* Python 3.8+
* Mesa Framework
* NumPy (optional)

### Installation
1.  Install the required MESA library:
    ```bash
    pip install mesa
    ```

### How to Run
1.  Navigate to the project directory in your terminal.
2.  Launch the simulation:
    ```bash
    python run.py
    ```
3.  Open your browser and go to: `http://127.0.0.1:8521/`

---
*Developed as part of the ISML Course Project.*
