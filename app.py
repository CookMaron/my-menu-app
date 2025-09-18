import os
import json
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Flaskアプリケーションのセットアップ
app = Flask(__name__)

# SQLiteデータベースファイルの場所を指定
DB_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'recipes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_FILE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# データベースのモデルを定義
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    ingredients_json = db.Column(db.Text, nullable=False)

    def __init__(self, title, ingredients):
        self.title = title
        self.ingredients_json = json.dumps(ingredients, ensure_ascii=False)
    
    # JSON文字列をリストに変換するプロパティ
    @property
    def ingredients(self):
        return json.loads(self.ingredients_json)

# アプリケーションのコンテキスト内でデータベーステーブルを作成
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # データベースから全レシピを取得
    recipes = Recipe.query.all()
    
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
        ingredients_list = request.form.getlist('ingredient')
        ingredients = [i.strip() for i in ingredients_list if i.strip()]
        
        # 新しいレシピをデータベースに追加
        new_recipe = Recipe(title=title, ingredients=ingredients)
        db.session.add(new_recipe)
        db.session.commit()
        
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

@app.route('/edit_recipe/<title>', methods=['GET', 'POST'])
def edit_recipe(title):
    # データベースからレシピを検索
    recipe = Recipe.query.filter_by(title=title).first_or_404()
    
    if request.method == 'POST':
        new_title = request.form['title']
        ingredients_list = request.form.getlist('ingredient')
        new_ingredients = [i.strip() for i in ingredients_list if i.strip()]
        
        # データベースのレシピを更新
        recipe.title = new_title
        recipe.ingredients_json = json.dumps(new_ingredients, ensure_ascii=False)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/delete_recipe/<title>', methods=['POST'])
def delete_recipe(title):
    # データベースからレシピを検索して削除
    recipe = Recipe.query.filter_by(title=title).first_or_404()
    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search():
    search_ingredients_list = request.args.getlist('search_ingredient')
    search_ingredients = [s.strip() for s in search_ingredients_list if s.strip()]
    search_type = request.args.get('search_type', 'or')

    # データベースから全レシピを取得
    recipes = Recipe.query.all()
    results = []
    
    for recipe in recipes:
        required_ingredients = set(recipe.ingredients)
        search_ingredients_set = set(search_ingredients)
        
        if search_type == 'and':
            if search_ingredients_set.issubset(required_ingredients):
                results.append(recipe)
        elif search_type == 'or':
            if not search_ingredients_set.isdisjoint(required_ingredients):
                results.append(recipe)
    
    return render_template('search_results.html', 
                           results=results,
                           search_ingredients=search_ingredients,
                           search_type=search_type,
                           recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
