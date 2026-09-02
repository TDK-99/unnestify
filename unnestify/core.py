import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def check_col(id,df=None, path=None,silent=False):

    """
    Inspects a DataFrame or file to show nesting levels (max 3 levels, one nested column).

    Args:
        id: column name to use as primary key.
        df: DataFrame to inspect. Optional, but either df or path must be provided.
        path: file path to .json, .xlsx, .csv. Optional, but either df or path must be provided.
        silent: False to print the result (default), True to suppress output.

    Example:
        check_col("cve.id", df=my_dataframe)
        check_col("id", path="/home/user/data.json") or path=your_path_var
    """
    def check_col_in(df, id):


        list_col_lv1 = []
        for col in df.columns:
            primo_valore = df[col].iloc[0]
            if isinstance(primo_valore, dict):
                list_col_lv1.append(col)

        df_json = pd.json_normalize(df[list_col_lv1[0]].to_list())
        df_json["id"] = df[id].values
        
        list_col_lv2 = []
        for col in df_json.columns:
            primo_valore = df_json[col].iloc[0]
            if isinstance(primo_valore, list):
                list_col_lv2.append(col)


        lv3 = {}

        for x in list_col_lv2:
            df_temp = df_json[[id, x]].explode(x)
            primo = df_temp[x].iloc[0]
            if isinstance(primo, dict):
                df_creato = pd.json_normalize(df_temp[x].tolist())
                df_creato["id"] = df_temp[id].values
                lv3[x] = df_creato


        if not silent:
            print("level 1:\n" + "\n".join(list_col_lv1))
            print("------")
            print("level 2:\n" + "\n".join(list_col_lv2))
            print("------")
            print("level 3:")


            colonne= []

            for x, df_lv2 in lv3.items():
                colonne_str = [col for col in df_lv2.columns if col != "id"]
                print(f"{x}:")
                print("  " + "\n  ".join(colonne_str))
                print(" ")

        return list_col_lv1, list_col_lv2, lv3

    if (path) is None: 
        return check_col_in(df,id)

    else: 
        if path.endswith(".json"):
            df_json = pd.read_json(path)
            return check_col_in(df_json,id)

        elif path.endswith(".xlsx"):
            df_xlsx = pd.read_excel(path)
            return check_col_in(df_xlsx,id)

        elif path.endswith(".csv"):
            df_csv = pd.read_csv(path,encoding="utf-8")
            return check_col_in(df_csv,id)

        else: print("Data format not supported")


def visual_nest(id,df=None,path=None):

    """
    Visualizes the nesting structure of a DataFrame or file as a tree.
    Uses a graphical tree (matplotlib) if nodes <= 30, otherwise prints an ASCII tree.

    Args:
        id: column name to use as primary key.
        df: DataFrame to inspect. Optional, but either df or path must be provided.
        path: file path to .json, .xlsx, .csv. Optional, but either df or path must be provided.

    Example:
        visual_nest("id", df=my_dataframe)
        visual_nest("id", path="/home/user/data.json") or path=your_path_var
    """

    list_col_lv1, list_col_lv2, lv3 = check_col(id, path=path, silent=True)


    def tree_layout(G, root):
        pos = {}
        levels = {}
        for node in nx.bfs_tree(G, root):
            depth = nx.shortest_path_length(G, root, node)
            if depth not in levels:
                levels[depth] = []
            levels[depth].append(node)
        for depth, nodes in levels.items():
            for i, node in enumerate(nodes):
                pos[node] = (i - len(nodes)/2, -depth)
        return pos

    def print_tree(G, node, prefix="", is_last=True, is_root=True):
        if is_root:
            print(node)
        else:
            connector = "└── " if is_last else "├── "
            print(prefix + connector + node)
        children = list(G.successors(node))
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            if is_root:
                new_prefix = ""
            else:
                new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(G, child, new_prefix, is_last_child, is_root=False)

    G = nx.DiGraph()

    for col in list_col_lv1:
        G.add_edge("DataFrame", col)

    for col in list_col_lv2:
        G.add_edge(list_col_lv1[0], col)

    for nome_padre, df_figlio in lv3.items():
        for col in df_figlio.columns:
            if col != "id":
                G.add_edge(nome_padre, col)

    n_nodi = G.number_of_nodes()

    if n_nodi <= 30:
        plt.figure(figsize=(max(20, n_nodi * 1.5), 10))
        pos = tree_layout(G, "DataFrame")
        nx.draw(G, pos, with_labels=True, node_size=900, node_color="lightblue", font_size=12, arrows=False)
        plt.show()
    else:
        print("Too many nodes for graphical display, switching to text tree:")
        print_tree(G, "DataFrame")
        
