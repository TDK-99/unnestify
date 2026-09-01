import pandas as pd


def check_col(id,df=None, path=None):

    """
    Inspects a DataFrame or file to show nesting levels (max 3 levels, one nested column).

    Args:
        id: column name to use as primary key.
        df: DataFrame to inspect. Optional, but either df or path must be provided.
        path: file path to .json, .xlsx, .csv. Optional, but either df or path must be provided.

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
            df_creato = pd.json_normalize(df_temp[x].tolist())
            df_creato["id"] = df_temp[id].values
            lv3[x] = df_creato

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
        check_col_in(df,id)

    else: 
        if path.endswith(".json"):
            df_json = pd.read_json(path)
            check_col_in(df_json,id)

        elif path.endswith(".xlsx"):
            df_xlsx = pd.read_excel(path)
            check_col_in(df_xlsx,id)

        elif path.endswith(".csv"):
            df_csv = pd.read_csv(path,encoding="utf-8")
            check_col_in(df_csv,id)

        else: print("Data format not supported")
        
