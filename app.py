from flask import Flask, render_template, request, redirect, url_for

# この行がすべてのウェブサイトの命令の「一番上」になければなりません。
app = Flask(__name__)

# 献立データ（仮のデータ）
recipes = []

@app.route('/')
def index():
    # 探索結果ページから戻ってきた場合のURLパラメータを取得
    search_ingredients_str = request.args.get('search_ingredients', '')
    missing_count_str = request.args.get('missing_count', '0')
    
    return render_template('index.html', 
                           recipes=recipes,
                           search_ingredients_str=search_ingredients_str,
                           missing_count_str=missing_count_str)

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        
        # 複数の入力欄からすべての材料名を取得
        ingredients_list = request.form.getlist('ingredient')
        
        # 不要な空欄を削除し、カンマ区切りで統一
        ingredients_set = set()
        for item in ingredients_list:
            # 全角の「、」を半角の「,」に置換し、スペースを削除
            cleaned_item = item.replace('、', ',').strip()
            # カンマで分割して、各材料をセットに追加
            if cleaned_item:
                for ingredient in cleaned_item.split(','):
                    ingredient = ingredient.strip()
                    if ingredient:
                        ingredients_set.add(ingredient)
        
        ingredients = list(ingredients_set)

        recipes.append({'title': title, 'ingredients': ingredients})
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

@app.route('/delete_recipe/<title>', methods=['POST'])
def delete_recipe(title):
    global recipes
    recipes = [recipe for recipe in recipes if recipe['title'] != title]
    return redirect(url_for('index'))

@app.route('/search')
def search():
    search_ingredients_str = request.args.get('search_ingredients', '')
    
    # 全角の「、」を半角の「,」に置換する
    search_ingredients_str = search_ingredients_str.replace('、', ',')
    
    search_ingredients = set(s.strip() for s in search_ingredients_str.split(',') if s.strip())
    missing_count_str = request.args.get('missing_count', '0')
    missing_count = int(missing_count_str)

    results = []
    for recipe in recipes:
        required_ingredients = set(recipe['ingredients'])
        
        # ユーザーが持っている食材と、レシピに必要な食材の共通部分を求める
        common_ingredients = search_ingredients.intersection(required_ingredients)
        
        # レシピに必要なのに持っていない食材
        missing_ingredients = list(required_ingredients - common_ingredients)
        
        # 不足している食材の数が指定した数以下であれば、結果に追加
        if len(missing_ingredients) <= missing_count:
            recipe_with_missing = recipe.copy()
            recipe_with_missing['missing'] = missing_ingredients
            results.append(recipe_with_missing)

    return render_template('search_results.html', 
                           results=results,
                           search_ingredients=search_ingredients,
                           missing_count=missing_count)

if __name__ == '__main__':
    app.run(debug=True)
