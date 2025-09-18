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
