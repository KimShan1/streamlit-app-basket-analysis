import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import matplotlib as mpl

# Create Streamlit app
st.title("Basket Analysis and Association Rules")

# Add sliders for user input
min_support = st.slider("Select minimum support", min_value=0.01, max_value=1.0, value=0.05, step=0.01)
min_threshold = st.slider("Select minimum confidence threshold", min_value=0.1, max_value=1.0, value=0.3, step=0.05)

# Inform the user about the required columns
st.info("The uploaded CSV file must contain the following columns: 'date'(obj), 'time'(obj), 'transaction'(int), 'item'(obj).")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:

    # Read the uploaded CSV file
    database = pd.read_csv(uploaded_file)

    # Grouping transactions and formatting data
    txs = database.groupby(['transaction'])['item'].apply(lambda x: list(np.unique(x)))
    txs_list = txs.values.tolist()
    te = TransactionEncoder()
    txs_formatted = te.fit(txs_list).transform(txs_list)
    df = pd.DataFrame(txs_formatted, columns=te.columns_)

    # Calculate product frequencies
    product_max = pd.DataFrame(data=df[df.columns.values].sum(), columns=["numVeces"])
    product_max_Top10 = product_max.sort_values("numVeces", ascending=False).head(10)
    product_max_Top10["Producto"] = product_max_Top10.index

    # Function to set custom color palette
    def set_custom_palette(product_max_Top10, max_color='crimson', other_color='midnightblue'):
        max_val = product_max_Top10.max()
        pal = []
        for item in product_max_Top10:
            if item == max_val:
                pal.append(max_color)
            else:
                pal.append(other_color)
        return pal

    # Plot Top 10 Most Popular Products
    st.subheader("Top 10 Most Popular Products")
    fig, ax = plt.subplots(figsize=(30, 10))
    sns.set_theme(rc={'figure.figsize': (30, 10)})
    b = sns.barplot(data=product_max_Top10, x='Producto', y='numVeces',
                    palette=set_custom_palette(product_max_Top10['numVeces']))
    b.tick_params(axis="y", labelsize=25)
    b.tick_params(axis="x", labelsize=25)
    b.set_title("Top 10 Most Popular Products", fontsize=30)
    b.set_xlabel("Products", fontsize=25)
    b.set_ylabel("No. Transactions", fontsize=25)
    b.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    st.pyplot(fig)

    # Calculate and display association rules
    apriori_df = apriori(df, min_support=min_support, use_colnames=True)
    sorted_apriori_df = apriori_df.sort_values(by='support', ascending=False)
    # Convert frozenset to string for display
    sorted_apriori_df['itemsets'] = sorted_apriori_df['itemsets'].apply(lambda x: ', '.join(list(x)))

    # Display sorted_apriori_df
    st.subheader("Products (Sorted by Support)")
    st.text("Support is the proportion of transactions containing a certain item set.")
    st.write(sorted_apriori_df)

    rules_df = association_rules(apriori_df, metric="confidence", min_threshold = min_threshold)
    # Convert frozenset to string for display
    rules_df['antecedents'] = rules_df['antecedents'].apply(lambda x: ', '.join(list(x)))
    rules_df['consequents'] = rules_df['consequents'].apply(lambda x: ', '.join(list(x)))

    # Display rules_df
    st.subheader("Association Rules")
    st.text("Confidence is the probability that consequent item is present given that antecedent item is present.'")
    st.write(rules_df)

    # Plot Association Rules
    st.subheader("Association Rules Scatter Plot")
    st.text("Lift is a measure of the strength of the association between two items. The bigger the lift the stronger the association rule is")
    fig2, ax2 = plt.subplots(figsize=(15, 10))
    sns.scatterplot(x="support", y="confidence", data=rules_df, hue="lift", s=200, ax=ax2)
    plt.legend(loc="lower right", title="lift")
    plt.title("Association Rules", fontsize=20)
    ax2.set_xlabel("Support", fontsize=20)
    ax2.set_ylabel("Confidence", fontsize=20)
    st.pyplot(fig2)
else:
    st.info("Please upload a CSV file.")


# streamlit run app_bakery.py
# conda activate mdmaestria
# source .venv/bin/activate

