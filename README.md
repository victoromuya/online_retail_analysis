# Online Retail Analytics

An end-to-end data analysis project that cleans online retail transactions, explores sales trends, and presents insights in an interactive Streamlit dashboard.

## What's included

- `Raw_Online_Retail.xlsx`: source transaction data.
- `online_retail.ipynb` and `ONLINE_RETAIL_PROJECT.ipynb`: data cleaning, feature engineering, and exploratory analysis.
- `cleaned_online_retail.csv`: prepared dataset used by the dashboard.
- `app.py`: dashboard with sales overview, product rankings, customer analysis, time trends, and a searchable data explorer.

## Run the dashboard

With Python installed, run these commands from the repository root:

```sh
cd End-to-End
python -m pip install streamlit pandas numpy plotly
python -m streamlit run app.py
```

Open the local URL shown in the terminal. Keep `cleaned_online_retail.csv` in the same folder as `app.py`.

## Explore the notebooks

Install the additional notebook dependencies:

```sh
python -m pip install jupyter openpyxl matplotlib seaborn
jupyter notebook
```

Open either notebook from this folder to explore the analysis or regenerate the cleaned CSV from the Excel source.
