# 📈 Live Supply Chain Risk Forecaster 📰

This is an end-to-end Data Science project that builds a live web dashboard to analyze supply chain risk. The application fetches real-time news headlines, uses a Hugging Face transformer model for sentiment analysis, and forecasts potential stock market disruption.

---

### ## Project Workflow ⚙️

1.  **Data Ingestion:**
    * Historical stock data is downloaded using `yfinance`.
    * Live and historical news headlines are fetched from a News API (e.G., GNews).
2.  **Model Training (Offline):**
    * A **Sentiment Model** is fine-tuned on financial news to understand "Negative," "Positive," and "Neutral" sentiment.
    * A **Time-Series Forecasting Model** is trained to predict the next day's stock price using two features: *yesterday's stock price* and *yesterday's average news "panic" score*.
    * The trained models are saved.
3.  **Live Dashboard (Online):**
    * A `streamlit` web app loads the saved models.
    * On user request ("Refresh"), the app fetches the latest news and stock data.
    * It uses the models to provide a **real-time risk score** and a **market trend forecast**.

---

### ## Tech Stack 🛠️

* **Language:** Python 3.8+
* **Data Manipulation:** Pandas, NumPy
* **Data Fetching:** `yfinance`, News API
* **AI / ML:** `scikit-learn`, `transformers` (Hugging Face), `torch`
* **Web Framework:** Streamlit
* **Environment:** Conda

---

### ## How to Set Up and Run This Project

Follow these steps to set up the project on your local machine.

#### Step 1: Clone the Repository
```bash
git clone [https://github.com/Diyapratap22/supply-chain-forecaster.git](https://github.com/Diyapratap22/supply-chain-forecaster.git)
cd supply-chain-forecaster
Step 2: Create and Activate the Conda Environment
Bash

conda create -n supplychain_env python=3.8 -y
conda activate supplychain_env
Step 3: Install Required Libraries
(You will need to create a requirements.txt file for this to work. For now, just run the manual install.)

Bash

pip install streamlit pandas yfinance transformers torch scikit-learn
Step 4: Add Your Secret API Key 🤫
You must create this file. It is ignored by Git so your secrets are safe.

Create a new file in the main folder named config.py.

Inside this file, add your News API key:

Python

NEWS_API_KEY = "paste-your-real-api-key-here"
Step 5: Run the Streamlit App! 🚀
Bash

streamlit run app.py
```bash
git clone [https://github.com/Diyapratap22/supply-chain-forecaster.git](https://github.com/Diyapratap22/supply-chain-forecaster.git)
cd supply-chain-forecaster
