#with open("internship_log.txt", "w", encoding="utf-8") as file:
#    file.write("Day 4: Python File Handling\n")
#    file.write("Learned reading and writing files.\n")
#    file.write("Practiced exception handling.\n")
#print("File created successfully.")

#with open("internship_log.txt","w")as file:
 #   file.write("DAY 4 task this is a demo\n")
#print("File created successfully.")

#with open("internship_log.txt","a")as file:
#    file.write("This is append example.\n")
#print("New entry added")

import pandas as pd
from jupyter_core.migrate import regex

df = pd.read_csv("stationery_retail_sales_RAW_uncleaned.csv")
# print(df.shape)
# print(df.head())
# print(df.tail())
# print(df.columns)
#
# print(df.info())
# print("\nMissing values:")
# print(df.isna().sum())
# print("\nData types:")
# print(df.dtypes)
clean_df=df.copy()

cols = ["Unit_Price", "Unit_Cost", "Sales", "Profit"]

for col in cols:
    clean_df[col] = (
        clean_df[col]
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")

clean_df["Quantity"] = (
    clean_df["Quantity"]
    .str.replace(" units", "", regex=False)
    .str.strip()
)

clean_df["Quantity"] = pd.to_numeric(
    clean_df["Quantity"], errors="coerce"
)
# print(clean_df[cols + ["Quantity"]].dtypes)
#
# print(clean_df[cols + ["Quantity"]].head(10))

def clean_discount(value):
    if pd.isna(value) or str(value).strip() in ["-", "N/A", "unknown", ""]:
        return float("nan")
    value = str(value).strip()
    if "%" in value:
        return float(value.replace("%", "")) / 100
    return float(value)


clean_df["Discount"] = clean_df["Discount"].apply(clean_discount)
# print(clean_df["Discount"].value_counts(dropna=False))
# print(clean_df["Discount"].dtype)

clean_df["Order_Date"] = pd.to_datetime(
    clean_df["Order_Date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

# print(clean_df["Order_Date"].dtype)
#print(clean_df["Order_Date"].isna().sum())
# print(clean_df["Order_Date"].head(10))

text_cols = [
    "Customer_ID", "Customer_Type", "Region",
    "City", "Product_ID", "Product_Name", "Category"
]
for col in text_cols:
    clean_df[col] = clean_df[col].str.strip()
    clean_df[col] = clean_df[col].replace(
        ["", "-", "N/A", "n/a", "unknown", "Unknown"],
        float("nan"))# OR clean_df[col].str.replace(" ","",regex=False)
    clean_df[col]=clean_df[col].str.replace("  "," ",regex=False)

for col in ["Region", "City", "Customer_Type", "Category", "Product_Name"]:
    clean_df[col] = clean_df[col].str.title()

#for col in ["Region", "City", "Customer_Type", "Category"]:
    #print(f"\n{col}:")
    # print(clean_df[col].value_counts(dropna=False))

recoverable_sales = (
    clean_df["Sales"].isna()
    & clean_df["Quantity"].notna()
    & clean_df["Unit_Price"].notna()
    & clean_df["Discount"].notna()
)
clean_df.loc[recoverable_sales, "Sales"] = (
    clean_df.loc[recoverable_sales, "Quantity"]
    * clean_df.loc[recoverable_sales, "Unit_Price"]
    * (1 - clean_df.loc[recoverable_sales, "Discount"])
)
# print("Sales recovered:", recoverable_sales.sum())
# print("Sales still missing:", clean_df["Sales"].isna().sum())

missing_quantity = clean_df.loc[
    clean_df["Quantity"].isna(),
    ["Transaction_Line_ID", "Product_Name", "Unit_Price", "Discount", "Sales"]
]
# print(missing_quantity)

missing_cost = clean_df.loc[
    clean_df["Unit_Cost"].isna(),
    ["Transaction_Line_ID", "Product_ID", "Product_Name", "Quantity", "Sales", "Profit"]
]
# print(missing_cost)

missing_discount = clean_df.loc[
    clean_df["Discount"].isna(),
    ["Transaction_Line_ID", "Quantity", "Unit_Price", "Sales"]
]
# print(missing_discount)

clean_df["Calculated_Sales"] = (
    clean_df["Quantity"]
    * clean_df["Unit_Price"]
    * (1 - clean_df["Discount"])
)
clean_df["Sales_Difference"] = (
    clean_df["Sales"] - clean_df["Calculated_Sales"]
)
sales_mismatch = clean_df.loc[
    clean_df["Sales_Difference"].abs() > 0.01,
    ["Transaction_Line_ID", "Quantity", "Unit_Price",
     "Discount", "Sales", "Calculated_Sales", "Sales_Difference"]
]

# print(sales_mismatch)
# print("Mismatched rows:", len(sales_mismatch))
recoverable_sales = (
    clean_df["Sales"].isna()
    & clean_df["Quantity"].notna()
    & clean_df["Unit_Price"].notna()
    & clean_df["Discount"].notna()
)
clean_df.loc[recoverable_sales, "Sales"] = (
    clean_df.loc[recoverable_sales, "Quantity"]
    * clean_df.loc[recoverable_sales, "Unit_Price"]
    * (1 - clean_df.loc[recoverable_sales, "Discount"])
)
# print("Recovered:", recoverable_sales.sum())
# print("Sales still missing:", clean_df["Sales"].isna().sum())

clean_df["Calculated_Profit"] = (
    clean_df["Sales"] - (clean_df["Unit_Cost"] * clean_df["Quantity"])
)

clean_df["Profit_Difference"] = (
    clean_df["Profit"] - clean_df["Calculated_Profit"]
)

profit_mismatch = clean_df.loc[
    clean_df["Profit_Difference"].abs() > 0.01,
    ["Transaction_Line_ID", "Sales", "Unit_Cost",
     "Quantity", "Profit", "Calculated_Profit", "Profit_Difference"]
]

# print(profit_mismatch)
# print("Profit mismatches:", len(profit_mismatch))

recoverable_quantity = (
    clean_df["Quantity"].isna()
    & clean_df["Sales"].notna()
    & clean_df["Unit_Price"].notna()
    & clean_df["Discount"].notna()
    & (clean_df["Unit_Price"] != 0)
)
# print("Potential rows:", recoverable_quantity.sum())
# clean_df["Calculated_Quantity"] = (
#     clean_df["Sales"]
#     / (clean_df["Unit_Price"] * (1 - clean_df["Discount"]))
# )
# print(
#     clean_df.loc[
#         clean_df["Quantity"].isna(),
#         ["Transaction_Line_ID", "Sales", "Unit_Price",
#          "Discount", "Calculated_Quantity"]
#     ]
# )

recoverable_cost = (
    clean_df["Unit_Cost"].isna()
    & clean_df["Sales"].notna()
    & clean_df["Profit"].notna()
    & clean_df["Quantity"].notna()
    & (clean_df["Quantity"] != 0)
)
# print("Potential rows:", recoverable_cost.sum())
# clean_df["Calculated_Unit_Cost"] = (
#     (clean_df["Sales"] - clean_df["Profit"])
#     / clean_df["Quantity"]
# )
# print(
#     clean_df.loc[
#         clean_df["Unit_Cost"].isna(),
#         ["Transaction_Line_ID", "Sales", "Profit",
#          "Quantity", "Calculated_Unit_Cost"]
#     ]
# )

recoverable_discount = (
    clean_df["Discount"].isna()
    & clean_df["Sales"].notna()
    & clean_df["Quantity"].notna()
    & clean_df["Unit_Price"].notna()
    & (clean_df["Quantity"] != 0)
    & (clean_df["Unit_Price"] != 0)
)
# print("Potential rows:", recoverable_discount.sum())
# clean_df["Calculated_Discount"] = (
#     1 - (
#         clean_df["Sales"]
#         / (clean_df["Quantity"] * clean_df["Unit_Price"])
#     )
# )
# print(
#     clean_df.loc[
#         clean_df["Discount"].isna(),
#         ["Transaction_Line_ID", "Sales", "Quantity",
#          "Unit_Price", "Calculated_Discount"]
#     ]
# )

# print("Exact duplicates:", clean_df.duplicated().sum())

# print("Duplicate line IDs:",
#       clean_df["Transaction_Line_ID"].duplicated().sum())

# for col in ["Region", "City", "Category", "Customer_Type", "Product_Name"]:
#     print(f"\n--- {col} ---")
#     print(clean_df[col].value_counts(dropna=False))

# print(clean_df["Quantity"].describe())

# print(clean_df.loc[
#     clean_df["Quantity"] < 0,
#     ["Transaction_Line_ID", "Quantity", "Sales", "Profit"]
# ])
# print(clean_df[["Unit_Price", "Unit_Cost"]].describe())
# print(clean_df.loc[
#     (clean_df["Unit_Price"] <= 0) | (clean_df["Unit_Cost"] < 0),
#     ["Transaction_Line_ID", "Product_Name", "Unit_Price", "Unit_Cost"]
# ])
# print(clean_df["Discount"].describe())

# print(clean_df.loc[
#     (clean_df["Discount"] < 0) | (clean_df["Discount"] > 1),
#     ["Transaction_Line_ID", "Discount"]
# ])
# print("Earliest:", clean_df["Order_Date"].min())
# print("Latest:", clean_df["Order_Date"].max())
# print("Missing:", clean_df["Order_Date"].isna().sum())

recoverable_profit = (
    clean_df["Profit"].isna()
    & clean_df["Sales"].notna()
    & clean_df["Unit_Cost"].notna()
    & clean_df["Quantity"].notna()
)
clean_df.loc[recoverable_profit, "Profit"] = (
    clean_df.loc[recoverable_profit, "Sales"]
    - (
        clean_df.loc[recoverable_profit, "Unit_Cost"]
        * clean_df.loc[recoverable_profit, "Quantity"]
    )
)

# print("Profit recovered:", recoverable_profit.sum())
# print("Profit still missing:", clean_df["Profit"].isna().sum())

recoverable_quantity = (
    clean_df["Quantity"].isna()
    & clean_df["Sales"].notna()
    & clean_df["Unit_Price"].notna()
    & clean_df["Discount"].notna()
    & (clean_df["Unit_Price"] != 0)
    & (clean_df["Discount"] != 1)
)

# print("Quantity rows that can be investigated:", recoverable_quantity.sum())
clean_df["Calculated_Quantity"] = (
    clean_df["Sales"] /
    (clean_df["Unit_Price"] * (1 - clean_df["Discount"]))
)
quantity_check = clean_df.loc[
    recoverable_quantity,
    ["Transaction_Line_ID", "Sales", "Unit_Price",
     "Discount", "Calculated_Quantity"]
]
# print(quantity_check)
# print(quantity_check["Calculated_Quantity"].round(2))
#clean_df.to_csv("Cleaned_Data.csv", index=False)
clean_df.loc[recoverable_quantity, "Quantity"] = (
    clean_df.loc[recoverable_quantity, "Calculated_Quantity"]
)
# print("Quantity missing:", clean_df["Quantity"].isna().sum())
# print("Quantity recovered:", recoverable_quantity.sum())

# print(clean_df["Unit_Cost"].isna().sum())

recoverable_cost=(clean_df["Unit_Cost"].isna()
          & clean_df["Sales"].notna()
          & clean_df["Profit"].notna()
          & clean_df["Quantity"].notna()
          & clean_df["Quantity"]!=0)
# print("Recoverable Unit_Cost rows:", recoverable_cost.sum())

clean_df["Calculated_Unit_Cost"]=((clean_df["Sales"]-clean_df["Profit"])
                       / clean_df["Quantity"])
cost_check = clean_df.loc[
    recoverable_cost,
    ["Transaction_Line_ID", "Product_Name", "Quantity",
     "Sales", "Profit", "Calculated_Unit_Cost"]
]

# print(cost_check)
clean_df.loc[recoverable_cost, "Unit_Cost"] = (
    clean_df.loc[recoverable_cost, "Calculated_Unit_Cost"]
)


# print("Unit_Cost missing:", clean_df["Unit_Cost"].isna().sum())

recoverable_discount = (
    clean_df["Discount"].isna()
    & clean_df["Sales"].notna()
    & clean_df["Quantity"].notna()
    & clean_df["Unit_Price"].notna()
    & (clean_df["Quantity"] != 0)
    & (clean_df["Unit_Price"] != 0)
)

# print("Recoverable Discount rows:", recoverable_discount.sum())
clean_df["Calculated_Discount"] = (
    1 - clean_df["Sales"] /
    (clean_df["Quantity"] * clean_df["Unit_Price"])
)
discount_check = clean_df.loc[
    recoverable_discount,
    ["Transaction_Line_ID", "Quantity", "Unit_Price",
     "Sales", "Calculated_Discount"]
]
# print(discount_check)
clean_df.loc[recoverable_discount, "Discount"] = (
    clean_df.loc[recoverable_discount, "Calculated_Discount"]
)
# print("Discount missing:", clean_df["Discount"].isna().sum())

# missing_customer = clean_df.loc[
#     clean_df["Customer_ID"].isna(),
#     ["Transaction_Line_ID", "Order_ID", "Customer_Type", "Region", "City"]
# ]
#
# print(missing_customer)
# clean_df.groupby("Order_ID")["Customer_ID"].nunique()
# missing_customer = clean_df.loc[
#     clean_df["Customer_ID"].isna(),
#     ["Transaction_Line_ID", "Order_ID", "Customer_Type", "Region", "City"]
# ]
# print(missing_customer)
# clean_df.groupby("Order_ID")["Customer_ID"].nunique()
# customer_type_check = (
#     clean_df.groupby("Customer_ID")["Customer_Type"]
#     .nunique()
# )
# print(customer_type_check.value_counts())
# missing_type_rows = clean_df.loc[
#     clean_df["Customer_Type"].isna(),
#     ["Transaction_Line_ID", "Customer_ID", "Order_ID", "Region", "City"]
# ]
# print(missing_type_rows)
# missing_city_rows = clean_df.loc[
#     clean_df["City"].isna(),
#     ["Transaction_Line_ID", "Customer_ID", "Order_ID", "Region"]
# ]
# print(missing_city_rows)
# city_check = clean_df.groupby("Customer_ID")["City"].nunique()
# print(city_check.value_counts())


#print(clean_df.isna().sum())
# print(clean_df.dtypes)
# print(clean_df.info())

# print("Total quantity:", clean_df["Quantity"].sum())
# print("Total sales:", clean_df["Sales"].sum())
# print("Total profit:", clean_df["Profit"].sum())
# print("Distinct orders:", clean_df["Order_ID"].nunique())

original_columns = [
    "Transaction_Line_ID", "Order_ID", "Order_Date",
    "Customer_ID", "Customer_Type", "Region", "City",
    "Product_ID", "Product_Name", "Category", "Quantity",
    "Unit_Price", "Unit_Cost", "Discount", "Sales", "Profit"
]

final_df = clean_df[original_columns].copy()
# print((clean_df.isna().mean()*100).round(2))
missing_customer = clean_df.loc[
    clean_df["Customer_ID"].isna(),
    ["Transaction_Line_ID", "Order_ID", "Customer_Type", "Region", "City"]
]

# print(missing_customer)

type_map = (
    clean_df.groupby("Customer_ID")["Customer_Type"]
    .agg(lambda x: x.dropna().unique())
)

# print(type_map.head())

recoverable_type = (
    clean_df["Customer_Type"].isna()
    & clean_df["Customer_ID"].notna()
    & clean_df["Customer_ID"].map(type_map).apply(
        lambda x: isinstance(x, (list, tuple)) and len(x) == 1
    )
)

clean_df.loc[recoverable_type, "Customer_Type"] = (
    clean_df.loc[recoverable_type, "Customer_ID"].map(type_map).apply(lambda x: x[0])
)

# print("Customer_Type recovered:", recoverable_type.sum())
# print("Customer_Type missing:", clean_df["Customer_Type"].isna().sum())

missing_city_rows = clean_df.loc[
    clean_df["City"].isna(),
    ["Transaction_Line_ID", "Customer_ID", "Order_ID", "Region"]
]

# print(missing_city_rows)
city_check = clean_df.groupby("Customer_ID")["City"].nunique()
# print(city_check.value_counts())
city_map = clean_df.groupby("Customer_ID")["City"].agg(
    lambda x: x.dropna().unique()
)
recoverable_city = (
    clean_df["City"].isna()
    & clean_df["Customer_ID"].notna()
    & clean_df["Customer_ID"].map(city_map).apply(
        lambda x: isinstance(x, (list, tuple)) and len(x) == 1
    )
)

clean_df.loc[recoverable_city, "City"] = (
    clean_df.loc[recoverable_city, "Customer_ID"]
    .map(city_map)
    .apply(lambda x: x[0])
)

# print("City recovered:", recoverable_city.sum())
# print("City still missing:", clean_df["City"].isna().sum())

# print(clean_df.isna().sum())
# print("Exact duplicate rows:", clean_df.duplicated().sum())
# print("Duplicate Transaction_Line_ID:", clean_df["Transaction_Line_ID"].duplicated().sum())
# print("Missing Transaction_Line_ID:", clean_df["Transaction_Line_ID"].isna().sum())
# print("Invalid Quantity:", (clean_df["Quantity"] <= 0).sum())
# print("Invalid Unit_Price:", (clean_df["Unit_Price"] <= 0).sum())
# print("Invalid Unit_Cost:", (clean_df["Unit_Cost"] < 0).sum())
# print("Invalid Discount:", ((clean_df["Discount"] < 0) | (clean_df["Discount"] > 1)).sum())
# print("Invalid Sales:", (clean_df["Sales"] < 0).sum())
# print("Invalid Profit:", clean_df["Profit"].isna().sum())
sales_valid = clean_df[
    ["Quantity", "Unit_Price", "Discount", "Sales"]
].notna().all(axis=1)

sales_calc = (
        clean_df.loc[sales_valid, "Quantity"]
        * clean_df.loc[sales_valid, "Unit_Price"]
        * (1 - clean_df.loc[sales_valid, "Discount"])
)

sales_mismatch_count = (
        (clean_df.loc[sales_valid, "Sales"] - sales_calc).abs() > 0.01
).sum()

profit_valid = clean_df[
    ["Sales", "Unit_Cost", "Quantity", "Profit"]
].notna().all(axis=1)

profit_calc = (
        clean_df.loc[profit_valid, "Sales"]
        - clean_df.loc[profit_valid, "Unit_Cost"]
        * clean_df.loc[profit_valid, "Quantity"]
)

profit_mismatch_count = (
        (clean_df.loc[profit_valid, "Profit"] - profit_calc).abs() > 0.01
).sum()

print("Sales rows validated:", sales_valid.sum())
print("Sales mismatches:", sales_mismatch_count)

print("Profit rows validated:", profit_valid.sum())
print("Profit mismatches:", profit_mismatch_count)

print("Earliest date:", clean_df["Order_Date"].min())
print("Latest date:", clean_df["Order_Date"].max())

print("Total rows:", len(clean_df))
print("Total quantity:", clean_df["Quantity"].sum())
print("Total sales:", clean_df["Sales"].sum())
print("Total profit:", clean_df["Profit"].sum())
print("Distinct orders:", clean_df["Order_ID"].nunique())
print("Distinct products:", clean_df["Product_ID"].nunique())
print("Distinct regions:", clean_df["Region"].nunique())

original_columns = [
    "Transaction_Line_ID",
    "Order_ID",
    "Order_Date",
    "Customer_ID",
    "Customer_Type",
    "Region",
    "City",
    "Product_ID",
    "Product_Name",
    "Category",
    "Quantity",
    "Unit_Price",
    "Unit_Cost",
    "Discount",
    "Sales",
    "Profit"
]

final_df = clean_df[original_columns].copy()

print(final_df.shape)
print(final_df.columns.tolist())
print(final_df.dtypes)
print(final_df.isna().sum())
# print("Rows affected:", clean_df.isna().any(axis=1).sum())
missing_summary = final_df.isna().sum().to_frame("Missing_Count")

final_df.to_csv("Final_Cleaned_Data.csv", index=False)
cleaning_log = pd.DataFrame({
    "Column": ["Quantity", "Unit_Cost", "Discount", "Profit",
              "Customer_Type", "City", "Customer_ID"],
    "Action": [
        "Recovered using Sales formula",
        "Recovered using Profit formula",
        "Recovered using Sales formula",
        "Recovered using verified formula",
        "Investigated; unrecoverable",
        "Investigated; unrecoverable",
        "Investigated; unrecoverable"
    ],
    "Recovered_Rows": [18, 35, 63, 20, 0, 0, 0],
    "Status": [
        "Completed", "Completed", "Completed", "Completed",
        "Retained missing values", "Retained missing values",
        "Retained missing values"
    ]
})

with pd.ExcelWriter("Final_Cleaned_Data.xlsx", engine="openpyxl") as writer:
    final_df.to_excel(writer, sheet_name="Cleaned_Data", index=False)
    missing_summary.to_excel(writer, sheet_name="Missing_Summary")
    cleaning_log.to_excel(writer, sheet_name="Cleaning_Log", index=False)
# print(df.isnull().sum())
#print(df["Category"].unique())
# print(df["Region"].unique())
#print(df["Transaction_Line_ID"].duplicated().sum())
# print(df["Order_ID"].duplicated().sum())
# df["Category"]=(df["Category"].str.strip().str.title().str.replace("  "," ",regex=False))
# print(df["Category"].unique())
# df["Unit_Price"] = (df["Unit_Price"].astype("string").str.replace("₹", "", regex=False).str.replace(",", "", regex=False))
# df["Unit_Price"] = pd.to_numeric(df["Unit_Price"],errors="coerce")
# df["Quantity"]=(df["Quantity"].astype("string").str.replace(" units","",regex=False))
# df["Quantity"]=pd.to_numeric(df["Quantity"],errors="coerce")

#print(df["Category"].value_counts(dropna=False))
#print(df.groupby("Category")["Sales"].sum())

#print("Total transaction lines:", len(df))
#print("Unique orders:", df["Order_ID"].nunique())
#print("Unique customers:", df["Customer_ID"].nunique())
#print(df["Product_Name"].value_counts())
#print(df.groupby("Product_Name")["Quantity"].sum())
#missing = df.isna().sum()
#print(missing[missing > 0])
#
# df["Unit_Price"] = (df["Unit_Price"].astype("string").str.replace("₹", "", regex=False).str.replace(",", "", regex=False))
# df["Unit_Price"] = pd.to_numeric(df["Unit_Price"],errors="coerce")