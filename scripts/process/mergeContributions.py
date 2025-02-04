import pandas as pd

# Load the data
pre_contribution_path = '/Users/kazuki-h/scripts/results/zookeeper_pre_contribution2.csv'
post_contribution_path = '/Users/kazuki-h/scripts/results/zookeeper_post_contribution2.csv'
output_path = 'merged_contributions2.csv'

try:
    # Read the CSV files
    pre_contribution_df = pd.read_csv(pre_contribution_path)
    post_contribution_df = pd.read_csv(post_contribution_path)
    
    # Merge the dataframes on 'repo_base' with outer join
    merged_df = pd.merge(pre_contribution_df, post_contribution_df, on='repo', how='outer')
    
    # Fill missing values with 0
    merged_df = merged_df.fillna(0)
    
    # Save the merged dataframe to a new CSV file
    merged_df.to_csv(output_path, index=False)
    
    print(f"Merge completed successfully! Output saved to: {output_path}")
except Exception as e:
    print(f"An error occurred: {e}")
