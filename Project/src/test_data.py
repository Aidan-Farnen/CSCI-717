from data_loader import load_better_recipes, recipes_to_docs

df = load_better_recipes("data/recipes.csv")
print(df.head(2)[["recipe_name", "ingredients_str", "cuisine_path"]])
docs = recipes_to_docs(df)
print(docs[0].keys())
