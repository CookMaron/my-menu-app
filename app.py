import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# データファイル名
DATA_FILE = 'recipes.json'

def load_recipes():
    """データファイルから献立を読み込む"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_recipes(recipes):
    """献立をデータファイルに保存する"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=4)

recipes = load_recipes()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    global recipes
    if request.method == 'POST':
        title = request.form['title']
        ingredients_list = request.form.getlist('ingredient')
        ingredients = [i.strip() for i in ingredients_list if i.strip()]
        
        recipes.append({'title': title, 'ingredients': ingredients})
        save_recipes(recipes)
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

@app.route('/delete_recipe/<title>', methods=['POST'])
def delete_recipe(title):
    global recipes
    recipes = [recipe for recipe in recipes if recipe['title'] != title]
    save_recipes(recipes)
    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search():
    search_ingredients_list = request.args.getlist('search_ingredient')
    search_ingredients = [s.strip() for s in search_ingredients_list if s.strip()]
    search_type = request.args.get('search_type', 'or')

    results = []
    for recipe in recipes:
        required_ingredients = set(recipe['ingredients'])
        search_ingredients_set = set(search_ingredients)
        
        if search_type == 'and':
            # AND検索: 全ての食材が含まれているか
            if search_ingredients_set.issubset(required_ingredients):
                results.append(recipe)
        elif search_type == 'or':
            # OR検索: いずれかの食材が含まれているか
            if not search_ingredients_set.isdisjoint(required_ingredients):
                results.append(recipe)

    return render_template('search_results.html', 
                           results=results,
                           search_ingredients=search_ingredients,
                           search_type=search_type,
                           recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
