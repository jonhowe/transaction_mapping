
# Transactions Analysis Script

This script analyzes debit/checking account transactions from a CSV file to identify recurring transactions and optionally visualize trends.

## Usage

```bash
python transactions_analysis.py <file_path> [OPTIONS]
```

## Arguments

- `<file_path>`: Path to the CSV file containing transaction data.

## Options

- `--show-visualization`: Show visualizations of the trends.
- `--days INTEGER`: Number of days in the past to look at transactions [default: 30].
- `--query TEXT`: Query to filter transactions by description.
- `--raw`: Ignore description mapping and use raw descriptions.
- `--install-completion`: Install shell completion.

## Examples

- Default usage with 30 days look-back period:
  ```bash
  python transactions_analysis.py sample_transactions.csv
  ```
  **Sample Output:**
  ```
  Description                        Amount_sum  Amount_mean  Transaction_count
  Amazon                             -399.80     -19.99       20
  Netflix                            -99.90      -9.99        10
  Spotify                            -75.00      -15.00       5
  Starbucks                          -18.00      -4.50        4
  ```

- Generate visualizations and use 60 days look-back period:
  ```bash
  python transactions_analysis.py sample_transactions.csv --show-visualization --days 60
  ```
  **Sample Output:**
  ```
  Description                        Amount_sum  Amount_mean  Transaction_count
  Amazon                             -399.80     -19.99       20
  Netflix                            -99.90      -9.99        10
  Spotify                            -75.00      -15.00       5
  Starbucks                          -18.00      -4.50        4
  ```
  **Visualizations:**
  - Bar plot of total amount by description.
  ![Figure_1](https://github.com/jonhowe/transaction_mapping/assets/3604046/5648e891-c030-4d04-bcbf-7ca58e947909)
  - Heatmap of transaction counts by description.
  ![heatmap](https://github.com/jonhowe/transaction_mapping/assets/3604046/9360cd23-3ecd-4bba-931e-b364050dd5ad)

- Query transactions with descriptions containing "Amazon Marketplace" within the last 30 days:
  ```bash
  python transactions_analysis.py sample_transactions.csv --query "Amazon Marketplace"
  ```
  **Sample Output:**
  ```
       Date                   Description                      Amount
  2024-05-09  Amazon Marketplace                                 -19.99
  2024-05-08  Amazon Marketplace                                 -19.99
  2024-04-26  Amazon Marketplace                                 -19.99
  2024-04-24  Amazon Marketplace                                 -19.99

  Total Amount for 'Amazon Marketplace': -79.96
  ```

- Run the script with raw descriptions (ignoring the mapping):
  ```bash
  python transactions_analysis.py sample_transactions.csv --raw
  ```
  **Sample Output:**
  ```
  Description                        Amount_sum  Amount_mean  Transaction_count
  amazon marketplace                 -199.90     -19.99       10
  netflix subscription               -99.90      -9.99        10
  spotify subscription               -75.00      -15.00       5
  starbucks                          -18.00      -4.50        4
  ```

- Install shell completion:
  ```bash
  python transactions_analysis.py --install-completion
  ```

## Requirements

- Python 3.x
- `pandas`
- `matplotlib`
- `click`
- `click-completion`

Install the required packages using pip:

```bash
pip install pandas matplotlib click click-completion
```

## CSV File Format

The CSV file must contain the following fields:
- `Date`: The date of the transaction.
- `Description`: The description of the transaction.
- `Comments`: Comments about the transaction (this field is ignored by the script).
- `Check Number`: The check number (this field is ignored by the script).
- `Amount`: The amount of the transaction.
- `Balance`: The balance after the transaction (this field is optional and will be ignored by the script).

## Description Mapping

The script uses a `description_mapping.json` file to standardize transaction descriptions. This JSON file contains mappings from various transaction descriptions to a standardized form. Here is an example of what the `description_mapping.json` file looks like:

```json
{
    "amazon marketplace": "Amazon",
    "netflix subscription": "Netflix",
    "spotify subscription": "Spotify",
    "starbucks": "Starbucks",
    "walmart supercenter": "Walmart",
    "shell gas station": "Shell",
    "uber eats": "Uber",
    "lyft ride": "Lyft",
    "best buy": "Best Buy",
    "target store": "Target"
}
```

### Editing the `description_mapping.json` File

To edit the `description_mapping.json` file, open it in a text editor and add or modify the mappings as needed. Ensure that the file remains in valid JSON format.

### Function

The `description_mapping.json` file maps various transaction descriptions to standardized forms to facilitate easier analysis and grouping of similar transactions.

### Relationship with the `--raw` Parameter

When the `--raw` parameter is used, the script ignores the `description_mapping.json` file and uses the raw descriptions from the CSV file. This can be useful if you want to see the original transaction descriptions without any standardization.

## Mid-level Detail of the Script's Functionality

### Functions

#### `load_description_mapping(file_path)`

Loads the description mapping from a JSON file.

#### `standardize_description(description, use_mapping=True)`

Standardizes the description to ensure consistent formatting by mapping duplicate descriptions to a canonical form if `use_mapping` is `True`.

#### `load_transactions(file_path)`

Loads transactions from a CSV file into a pandas DataFrame.

#### `preprocess_transactions(transactions, days, use_mapping)`

Preprocesses transactions by:
- Removing currency symbols and converting to numeric types.
- Filtering to include only transactions with negative values.
- Filtering transactions by date (within the specified number of days).
- Standardizing descriptions if `use_mapping` is `True`.

#### `show_trends(transactions, min_occurrences=2)`

Shows trends for recurring transactions by:
- Grouping transactions by 'Description' and filtering groups with at least `min_occurrences`.
- Calculating sum, mean, and count for 'Amount'.
- Sorting trends by the highest count in descending order.

#### `plot_trends(trends)`

Plots trends for recurring transactions:
- Bar plot of total amount by description.
- Heatmap of transaction counts by description.

### Main Function

The `main` function orchestrates the loading, preprocessing, analysis, and optional visualization of transaction data based on provided command-line options. It also handles the installation of shell completion if the `--install-completion` option is used.

### Command-line Interface

Implemented using the `click` library, the script provides a user-friendly command-line interface with options for displaying visualizations, querying specific transactions, and using raw descriptions without mapping.

## License

This script is licensed under the MIT License. See the LICENSE file for more details.

