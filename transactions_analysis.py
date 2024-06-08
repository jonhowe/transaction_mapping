
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
    """
    Standardize the description to ensure consistent formatting.
    
    Args:
        description (str): The original description.
        use_mapping (bool): Flag to use description mapping.
    
    Returns:
        str: The standardized description.
    """
    if use_mapping:
        return description_mapping.get(description.strip().lower(), description.strip().lower())
    else:
        return description.strip().lower()

def load_transactions(file_path):
    """
    Load transactions from a CSV file into a pandas DataFrame.
    
    Args:
        file_path (str): The path to the CSV file.
    
    Returns:
        pd.DataFrame: DataFrame containing the transactions.
    """
    return pd.read_csv(file_path)

def preprocess_transactions(transactions, days, use_mapping):
    """
    Preprocess transactions by removing currency symbols, converting to numeric types,
    filtering to include only transactions with negative values, and filtering by date.
    
    Args:
        transactions (pd.DataFrame): DataFrame containing the transactions.
        days (int): Number of days in the past to look at transactions.
        use_mapping (bool): Flag to use description mapping.
    
    Returns:
        pd.DataFrame: Preprocessed DataFrame.
    """
    # Remove the Balance column if it exists
    if 'Balance' in transactions.columns:
        transactions = transactions.drop(columns=['Balance'])
    
    # Remove currency symbols and commas from Amount, then convert to numeric
    transactions['Amount'] = transactions['Amount'].replace(r'[\$,]', '', regex=True).astype(float)
    
    # Filter to include only transactions with negative values
    transactions = transactions[transactions['Amount'] < 0]
    
    # Convert 'Date' column to datetime format
    transactions['Date'] = pd.to_datetime(transactions['Date'])
    
    # Filter transactions to only include those within the specified number of days
    cutoff_date = datetime.now() - timedelta(days=days)
    transactions = transactions[transactions['Date'] >= cutoff_date]
    
    # Standardize descriptions
    transactions['Description'] = transactions['Description'].apply(lambda x: standardize_description(x, use_mapping))
    
    return transactions

def show_trends(transactions, min_occurrences=2):
    """
    Show trends for recurring transactions by aggregating data.
    
    Args:
        transactions (pd.DataFrame): DataFrame containing the transactions.
        min_occurrences (int): Minimum number of occurrences for a transaction to be considered recurring.
    
    Returns:
        pd.DataFrame: DataFrame containing the trends for recurring transactions.
    """
    # Group by 'Description' and filter groups with at least min_occurrences
    recurring_transactions = transactions.groupby('Description').filter(lambda x: len(x) >= min_occurrences)
    
    # Group by 'Description' and calculate sum, mean, and count for 'Amount'
    trends = recurring_transactions.groupby('Description').agg({
        'Amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    # Flatten the multi-level columns
    trends.columns = ['Description', 'Amount_sum', 'Amount_mean', 'Transaction_count']
    
    # Format the mean to two decimal points
    trends['Amount_mean'] = trends['Amount_mean'].round(2)
    
    # Sort trends by the highest count in descending order
    trends = trends.sort_values(by='Transaction_count', ascending=False)
    
    return trends

def plot_trends(trends):
    """
    Plot trends for recurring transactions.
    
    Args:
        trends (pd.DataFrame): DataFrame containing the trends for recurring transactions.
    """
    # Plot total amount by Description
    plt.figure(figsize=(10, 6))
    total_amount = trends.groupby('Description')['Amount_sum'].sum()
    total_amount.sort_values(ascending=False).plot(kind='bar')
    plt.title('Total Amount by Description')
    plt.ylabel('Total Amount ($)')
    plt.xlabel('Description')
    plt.xticks(rotation=90)
    plt.show()

    # Heatmap of transaction counts by Description
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
def main(file_path, show_visualization, days, query, raw, install_completion):
    """
    Main function to load transactions, show trends, and plot trends.
    
    Args:
        file_path (str): The path to the CSV file.
        show_visualization (bool): Flag to indicate whether to show visualizations.
        days (int): Number of days in the past to look at transactions.
        query (str): Query to filter transactions by description.
        raw (bool): Flag to ignore description mapping.
        install_completion (bool): Flag to install shell completion.
    """
    if install_completion:
        shell, path = click_completion.install()
        print(f'Completion installed for {shell}.')
        return
    
    # Load the transactions from the CSV file
    transactions = load_transactions(file_path)
    
    # Preprocess transactions
    transactions = preprocess_transactions(transactions, days, not raw)
    
    if query:
        # Escape special characters in the query
        escaped_query = re.escape(query.strip().lower())
        # Filter transactions by description query
        filtered_transactions = transactions[transactions['Description'].str.contains(escaped_query, case=False, na=False)]
        # Print the filtered transactions without check number, comments, or balance
        print(filtered_transactions[['Date', 'Description', 'Amount']].to_string(index=False))
        # Calculate and print the sum of the Amount column
        amount_sum = filtered_transactions['Amount'].sum()
        print(f"\nTotal Amount for '{query}': {amount_sum:.2f}")
    else:
        # Show trends for recurring transactions
        trends = show_trends(transactions)
        
        # Reset the index for a clean printout
        trends = trends.reset_index(drop=True)
        
        # Print trends without the index
        print(trends.to_string(index=False))
        
        # Plot trends if the flag is set
        if show_visualization:
            plot_trends(trends)

if __name__ == "__main__":
    main()
