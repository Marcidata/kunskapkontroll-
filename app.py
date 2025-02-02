import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Titel för appen
st.title("Köksglädje Databasanalys")

# Funktion för att ladda data från databasen
def load_data():
    conn = sqlite3.connect('Köksglädje.db')
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql(query, conn)
    
    st.write("### Tabeller i databasen:")
    st.write(tables)
    
    customers_df = pd.read_sql("SELECT * FROM Customers;", conn)
    products_df = pd.read_sql("SELECT * FROM Products;", conn)
    stores_df = pd.read_sql("SELECT * FROM Stores;", conn)
    transactions_df = pd.read_sql("SELECT * FROM Transactions;", conn)
    details_df = pd.read_sql("SELECT * FROM TransactionDetails;", conn)
    
    conn.close()
    
    return customers_df, products_df, stores_df, transactions_df, details_df

# Ladda data
customers_df, products_df, stores_df, transactions_df, details_df = load_data()

# Visa dataramen för kontroll
st.write("### Kunder:")
st.write(customers_df.head())

st.write("### Produkter:")
st.write(products_df.head())

st.write("### Butiker:")
st.write(stores_df.head())

st.write("### Transaktioner:")
st.write(transactions_df.head())

st.write("### Transaktionsdetaljer:")
st.write(details_df.head())

# Klassificera priser
def classify_price(price):
    return "Dyr" if price > 500 else "Billig"

products_df['PriceCategory'] = products_df['Price'].apply(classify_price)
st.write("### Produkter med prisklassificering:")
st.write(products_df[['ProductName', 'Price', 'PriceCategory']].head())

# Beräkna total försäljning
conn = sqlite3.connect('Köksglädje.db')
query_total_sales = "SELECT SUM(TotalPrice) as TotalSales FROM TransactionDetails;"
total_sales_df = pd.read_sql(query_total_sales, conn)
conn.close()
st.write(f"### Total försäljning: {total_sales_df.iloc[0]['TotalSales']} SEK")

# Hämta de mest sålda produkterna
conn = sqlite3.connect('Köksglädje.db')
query_best_selling = """
SELECT p.ProductName, SUM(td.Quantity) as TotalSold
FROM TransactionDetails td
JOIN Products p ON td.ProductID = p.ProductID
GROUP BY p.ProductName
ORDER BY TotalSold DESC
LIMIT 10;
"""
best_selling_df = pd.read_sql(query_best_selling, conn)
conn.close()

st.write("### Mest sålda produkter:")
st.write(best_selling_df)

# Skapa cirkeldiagram för mest sålda produkter
st.write("### Cirkeldiagram över mest sålda produkter:")
fig, ax = plt.subplots()
ax.pie(best_selling_df['TotalSold'], labels=best_selling_df['ProductName'], 
       colors=plt.cm.viridis(np.linspace(0, 1, len(best_selling_df))), 
       autopct='%1.1f%%', startangle=140, shadow=True)
ax.axis('equal')
st.pyplot(fig)
 
# visa produkter med pris  över 500 
with sqlite3.connect('Köksglädje.db') as conn:
    products_over_500 = pd.read_sql("SELECT ProductName, Price FROM Products WHERE Price > 500", conn)
st.write("### Produkter med pris över 500 kr:")
st.write(products_over_500)

# Visa produkter med pris över 1000 kr
with sqlite3.connect('Köksglädje.db') as conn:
    products_over_1000 = pd.read_sql("SELECT ProductName, Price FROM Products WHERE Price > 1000;", conn)
st.write("### Produkter med pris över 1000 kr:")
st.write(products_over_1000)

# Visa antal produkter per kategori
with sqlite3.connect('Köksglädje.db') as conn:
    categories_df = pd.read_sql("SELECT CategoryName, COUNT(*) AS ProductCount FROM Products GROUP BY CategoryName;", conn)
st.write("### Antal produkter per kategori:")
st.write(categories_df)

# Visa antal transaktioner per butik
with sqlite3.connect('Köksglädje.db') as conn:
    stores_df = pd.read_sql("SELECT S.StoreName, COUNT(T.TransactionID) AS TransactionCount FROM Transactions T JOIN Stores S ON T.StoreID = S.StoreID GROUP BY S.StoreName;", conn)
st.write("### Antal transaktioner per butik:")
st.write(stores_df)

# Beräkna medelpris per kategori
category_avg_price = products_df.groupby("CategoryName")["Price"].mean().reset_index()
st.write("### Medelpris per kategori:")
st.write(category_avg_price)

# Skapa diagram för medelpriser per produktkategori
with sqlite3.connect('Köksglädje.db') as conn:
    df = pd.read_sql("SELECT CategoryName, ProductName, Price FROM Products WHERE ProductName IS NOT NULL AND Price IS NOT NULL;", conn)

df = df[df['CategoryName'].isin(df['CategoryName'].value_counts()[df['CategoryName'].value_counts() >= 3].index)]

fig, axs = plt.subplots(len(df['CategoryName'].unique()) // 3 + 1, 3, figsize=(15, 20))
axs = axs.flatten()

fig.suptitle("Medelpriser per produktkategori", fontsize=20, y=1.02)
cmap = plt.cm.viridis

for i, category in enumerate(df['CategoryName'].unique()):
    avg_price = df[df['CategoryName'] == category].groupby('ProductName')['Price'].mean().sort_values()
    norm = plt.Normalize(avg_price.min(), avg_price.max())

    axs[i].barh(avg_price.index, avg_price.values, color=cmap(norm(avg_price.values)), edgecolor='black')
    axs[i].set_title(category)
    axs[i].set_xlabel("Medelpris (SEK)")
    axs[i].set_ylabel("Produktnamn")
    axs[i].grid(axis='x', linestyle='--', alpha=0.7)
    
    # Lägg till färgförklaring
    fig.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), ax=axs[i], orientation='vertical', label='Pris (SEK)')

# Ta bort tomma diagram
for j in range(i + 1, len(axs)):
    fig.delaxes(axs[j])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
st.pyplot(fig)

# Visa dagliga transaktioner och topp 10 kunder
transactions_df['TransactionDate'] = pd.to_datetime(transactions_df['TransactionDate'])
top_customers = transactions_df['CustomerID'].value_counts().head(10)
daily_transactions = transactions_df.groupby(transactions_df['TransactionDate'].dt.date).size()

fig, axs = plt.subplots(2, 1, figsize=(12, 10))

# Stapeldiagram för topp 10 kunder
axs[0].bar(top_customers.index.astype(str), top_customers.values, color='orange')
axs[0].set_title('Topp 10 mest aktiva kunder')
axs[0].tick_params(axis='x', rotation=45)

# Linjediagram för dagliga transaktioner
axs[1].plot(daily_transactions.index, daily_transactions.values, marker='o', color='blue')
axs[1].set_title('Dagliga transaktioner över tid')
axs[1].tick_params(axis='x', rotation=45)
axs[1].grid(True)

plt.tight_layout()
st.pyplot(fig)

# Visa korrelationsmatris
with sqlite3.connect('Köksglädje.db') as conn:
    products_df = pd.read_sql("SELECT * FROM Products;", conn)

numerical_data = products_df.select_dtypes(include=['float64', 'int64'])
corr = numerical_data.corr()

st.write("### Korrelationsmatris:")
st.write(corr)

# Skapa bar chart för korrelationer
corr_unstacked = corr.unstack().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10, 6))
corr_unstacked.plot(kind='bar', ax=ax)
ax.set_title('Bar Chart av korrelationer mellan variabler')
ax.set_ylabel('Korrelation')
ax.set_xlabel('Variabler')
st.pyplot(fig)


st.success("All analys är nu inkluderad i Streamlit-appen! 🚀")




