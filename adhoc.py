from ParamsIndexRepo import get_df_human, get_df_tax

df = get_df_human()


df_tax = get_df_tax().reset_index()


def tax_list(df):
    return set([item for sublist in df["taxonomies"] for item in sublist])


for i in tax_list(df_tax[df_tax["lang"] == "nl"]):
    print(i)

print()

for i in tax_list(df_tax[df_tax["lang"] == "en"]):
    print(i)
