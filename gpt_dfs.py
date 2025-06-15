import pandas as pd

# Load the Excel file
df = pd.read_excel('dc2.xlsx', sheet_name="Sheet1")

test_dict = {}
for idx_row, a_row in df.iterrows():
    test_dict[a_row['start_node']] = a_row['end_node']
print(".........\n", test_dict)
# Create a mapping from start_node to the corresponding pipe (row)
start_node_map = {}
for idx, row in df.iterrows():
    start_node = row['start_node']
    start_node_map.setdefault(start_node, []).append(idx)

# Function for DFS traversal
def dfs(pipe_idx, visited, result):
    visited.add(pipe_idx)
    result.append(pipe_idx)
    end_node = df.loc[pipe_idx, 'end_node']
    # Check if there are child pipes starting from this end_node
    for child_idx in start_node_map.get(end_node, []):
        if child_idx not in visited:
            dfs(child_idx, visited, result)

# Identify parent pipes (those whose start_node is not an end_node of any other pipe)
all_start_nodes = set(df['start_node'])
all_end_nodes = set(df['end_node'])
root_start_nodes = all_start_nodes - all_end_nodes

# Find root pipes
root_pipes = df[df['start_node'].isin(root_start_nodes)]

# Final sorting order
visited = set()
sorted_indices = []

for idx in root_pipes.index:
    if idx not in visited:
        dfs(idx, visited, sorted_indices)

# Some pipes might not be connected — add any remaining ones
for idx in df.index:
    if idx not in visited:
        dfs(idx, visited, sorted_indices)

# Reorder dataframe
dfs_df = df.loc[sorted_indices].reset_index(drop=True)

# Save to a new Excel file
dfs_df.to_excel('sorted_dfs.xlsx', index=False)

print("Sorting complete. Output saved to 'sorted_output.xlsx'.")
