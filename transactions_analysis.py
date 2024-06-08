import pandas as pd
import matplotlib.pyplot as plt
import click
from datetime import datetime, timedelta
import re
import click_completion
import json

# Initialize the click-completion
click_completion.init()

# Function to load the description mapping from a JSON file
def load_description_mapping(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Load the description mapping
description_mapping = load_description_mapping('description_mapping.json')

def standardize_description(description, use_mapping=True):
    if use_mapping:
        return description_mapping.get(description.strip().lower(), description.strip().lower())
    else:
        return description.strip().lower()

def load_transactions(file_path):
    return pd.read_csv(file_path)

def preprocess_transactions(transactions, days, use_mapping):
    if 'Balance' in transactions.columns:
        transactions = transactions.drop(columns=['Balance'])
    
    transactions['Amount'] = transactions['Amount'].replace(r'[\$,]', '', regex=True).astype(float)
    transactions = transactions[transactions['Amount'] < 0]
    transactions['Date'] = pd.to_datetime(transactions['Date'])
    cutoff_date = datetime.now() - timedelta(days=days)
    transactions = transactions[transactions['Date'] >= cutoff_date]
    transactions['Description'] = transactions['Description'].apply(lambda x: standardize_description(x, use_mapping))
    
    return transactions

def show_trends(transactions, min_occurrences=2):
    recurring_transactions = transactions.groupby('Description').filter(lambda x: len(x) >= min_occurrences)
    trends = recurring_transactions.groupby('Description').agg({
        'Amount': ['sum', 'mean', 'count']
    }).reset_index()
    trends.columns = ['Description', 'Amount_sum', 'Amount_mean', 'Transaction_count']
    trends['Amount_mean'] = trends['Amount_mean'].round(2)
    trends = trends.sort_values(by='Transaction_count', ascending=False)
    
    return trends

def plot_trends(trends):
    plt.figure(figsize=(10, 6))
    total_amount = trends.groupby('Description')['Amount_sum'].sum()
    total_amount.sort_values(ascending=False).plot(kind='bar')
    plt.title('Total Amount by Description')
    plt.ylabel('Total Amount ($)')
    plt.xlabel('Description')
    plt.xticks(rotation=90)
    plt.show()

    pivot_table = trends.pivot_table(index='Description', values='Transaction_count', fill_value=0)
    plt.figure(figsize=(12, 8))
    plt.title('Heatmap of Transaction Counts by Description')
    plt.xlabel('Description')
    plt.ylabel('Transaction Count')
    plt.imshow(pivot_table.T, aspect='auto', cmap='viridis')
    plt.colorbar(label='Transaction Count')
    plt.xticks(range(len(pivot_table.index)), labels=pivot_table.index, rotation=90)
    plt.yticks(range(len(pivot_table.columns)), labels=pivot_table.columns)
    plt.show()

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--show-visualization', is_flag=True, help='Show visualizations of the trends.')
@click.option('--days', default=30, type=int, help='Number of days in the past to look at transactions.')
@click.option('--query', default=None, type=str, help='Query to filter transactions by description.')
@click.option('--raw', is_flag=True, help='Ignore description mapping.')
@click.option('--install-completion', is_flag=True, help='Install shell completion.')
@click.option('--export', is_flag=True, help='Export the results to a CSV file.')
def main(file_path, show_visualization, days, query, raw, install_completion, export):
    if install_completion:
        shell, path = click_completion.install()
        print(f'Completion installed for {shell}.')
        return
    
    transactions = load_transactions(file_path)
    transactions = preprocess_transactions(transactions, days, not raw)
    
    if query:
        escaped_query = re.escape(query.strip().lower())
        filtered_transactions = transactions[transactions['Description'].str.contains(escaped_query, case=False, na=False)]
        print(filtered_transactions[['Date', 'Description', 'Amount']].to_string(index=False))
        amount_sum = filtered_transactions['Amount'].sum()
        print(f"\nTotal Amount for '{query}': {amount_sum:.2f}")
    else:
        trends = show_trends(transactions)
        trends = trends.reset_index(drop=True)
        print(trends.to_string(index=False))
        if show_visualization:
            plot_trends(trends)
        if export:
            trends.to_csv('results.csv', index=False)
            print("Results exported to 'results.csv'.")

if __name__ == "__main__":
    main()
