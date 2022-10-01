from flask import Flask, render_template, request, redirect, url_for, session, Response, abort
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
import sqlite3
import datetime, time
from datetime import timedelta
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField
from test_mail2 import mail_analyze
from midori_service import midori_service
from ito_chain import ito_chain
from sakurakko import sakurakko
import sys


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'mysecretkey'
#http://localhost:5001/

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# ログイン用ユーザー作成
users = {
    1: User(1, "yukinao0809", "a19781227")
}

# ユーザーチェックに使用する辞書作成
nested_dict = lambda: defaultdict(nested_dict)
user_check = nested_dict()
for i in users.values():
    user_check[i.name]["password"] = i.password
    user_check[i.name]["id"] = i.id

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

#tupleをdictに変換する関数
def db_to_dict(tuple):
    dic = {}
    tmp = list(tuple)
    dic['id'] = tmp[0]
    dic['store_name'] = tmp[1]
    dic['date'] = tmp[2]
    dic['item_name'] = tmp[3]
    dic['remain'] = tmp[4]
    dic['left'] = tmp[5]
    return dic

#日付の絞り込み関数
def date_range(range,dictlist):
    ans = []
    today = datetime.datetime.today()
    for i in dictlist:
        d = datetime.datetime.strptime(i['date'],"%Y-%m-%d")
        if range == 'ここ1週間':
            delta = today - timedelta(days=7)
            if d >= delta:
                ans.append(i)
        elif range == 'ここ1ヶ月':
            delta = today - timedelta(days=30)
            if d >= delta:
                ans.append(i)
        elif range == 'ここ3ヶ月':
            delta = today - timedelta(days=90)
            if d >= delta:
                ans.append(i)
        elif range == 'ここ半年':
            delta = today - timedelta(days=182)
            if d >= delta:
                ans.append(i)
        elif range == 'ここ1年間':
            delta = today - timedelta(days=365)
            if d >= delta:
                ans.append(i)
        else: #datechoice初期値
            delta = today - timedelta(days=7)
            if d >= delta:
                ans.append(i)
    return ans
        
#indexを店舗で絞り込む関数
def index_by_store(index,store): 
    ans = []
    for i in range(0,len(index)): #<-- for i in index:と書くとプログラムが死ぬ
        if index[i]['store_name'] == store: #storeに一致したらansに追加
            ans.append(index[i])
    if ans == []:
        ans = index #全てstoreに一致しなかったらそのままindexを渡す
    return ans

def get_index():
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    index = []
    for i in c.execute('select * from each_sales order by date'):
        index.append({'id':i[0],'store_name':i[1],'date':i[2],'item_name':i[3], 'remain':i[4], 'left':i[5]})
    conn.commit()
    conn.close()
    return index

def get_store():
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    store = []
    for i in c.execute('select * from store_name'):
        store.append({'id':i[0],'store_name':i[1]})
    conn.commit()
    conn.close()
    return store

def get_item():
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    items = []
    for i in c.execute('select * from item_name'):
        items.append({'id':i[0],'item_name':i[1],'item_value':i[2]})
    conn.commit()
    conn.close()
    return items

def update_index(prof):
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    c.execute('update each_sales set store_name=?,date=?,item_name=?,remain=?,left=? where id=?', (prof['store_name'],prof['date'],prof['item_name'],prof['remain'],prof['left'],prof['id']))
    conn.commit()
    conn.close()

def get_recent():
    index = []
    stores = get_store()
    items = get_item()
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    for store in stores:
        for item in items:
            for i in c.execute("select * from each_sales where store_name = ? and item_name = ? order by date DESC, id DESC",(store['store_name'],item['item_name'])):
                dic = db_to_dict(i)
                index.append(dic)
                break
    conn.commit()
    conn.close()
    return index

# ログインパス
@app.route('/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        # ユーザーチェック
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            login_user(users.get(user_check[request.form["username"]]["id"]))
            return redirect(url_for("home"))
        else:
            return abort(401)
    else:
        return render_template("login.html")

# ログアウトパス
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return Response('''
    logout success!<br />
    <a href="/">login</a>
    ''')


#内部上では日付を秒単位にしないと、同じ日に更新すると在庫状況に反映されない
#ルーティングによって呼び出す関数を分ける方法は？
#受信したメールが0件のときは何も起こさないかエラーメッセージを出すようにしよう
@app.route('/load_midori')
def load_midori(): #メールで取得したデータをeach_salesに更新
    none_dic = {'みどりのサービス仙台店': {'しそ巻(3個入り)': 0, 'しそ巻(5個入り)': 0, '勝負だれ': 0, '極': 0, '麻婆豆腐の素': 0}, 'み どりのサービス仙台南店': {'しそ巻(3個入り)': 0, 'しそ巻(5個入り)': 0, '勝負だれ': 0, '極': 0, '麻婆豆腐の素': 0}} 
    index = get_recent()
    mail_data = midori_service()
    if mail_data != none_dic:
        tdy = datetime.datetime.today()
        today = tdy.strftime('%Y-%m-%d')
        conn = sqlite3.connect('database.sqlite3')
        c = conn.cursor()
        for store, value in mail_data.items(): #maildataから店舗名(key)、商品名と数量(value)を取得
            for item, num in value.items():
                for i in index: #保存されている最新の在庫状況をfor文で取り出す
                    if store == i['store_name'] and item == i['item_name'] : #最新在庫状況にある店の名前と商品名、メールデータの店の名前と商品名の両方が一致したらinsert
                        #最新在庫状況から売れた個数を引いてinsert
                        c.execute('insert into each_sales(store_name,date,item_name,remain,left) values(?,?,?,?,?)',(store,today,item,i['left']-int(num),i['left']-int(num)))
        conn.commit()
        conn.close()
    return redirect(url_for("recent"))

@app.route('/load_ito')
def load_ito(): #メールで取得したデータをeach_salesに更新
    none_dic = {'伊藤チェーン泉店': {'しそ巻(3個入り)': 0, 'しそ巻(5個入り)': 0, '勝負だれ': 0, '極': 0, '麻婆豆腐の素': 0}, '伊藤チェ ーン玉浦店': {'しそ巻(3個入り)': 0, 'しそ巻(5個入り)': 0, '勝負だれ': 0, '極': 0, '麻婆豆腐の素': 0}, '伊藤チェーン松森 店': {'しそ巻(3個入り)': 0, 'しそ巻(5個入り)': 0, '勝負だれ': 0, '極': 0, '麻婆豆腐の素': 0}, '伊藤チェーン閖上店': {'しそ巻(3個入り)': 0, 'しそ巻(5個入り)': 0, '勝負だれ': 0, '極': 0, '麻婆豆腐の素': 0}}
    index = get_recent()
    mail_data = ito_chain()
    if mail_data != none_dic:
        tdy = datetime.datetime.today()
        today = tdy.strftime('%Y-%m-%d')
        conn = sqlite3.connect('database.sqlite3')
        c = conn.cursor()
        for store, value in mail_data.items(): #maildataから店舗名(key)、商品名と数量(value)を取得
            for item, num in value.items():
                for i in index: #保存されている最新の在庫状況をfor文で取り出す
                    if store == i['store_name'] and item == i['item_name']: #最新在庫状況にある店の名前と商品名、メールデータの店の名前と商品名の両方が一致したらinsert
                        #最新在庫状況から売れた個数を引いてinsert
                        c.execute('insert into each_sales(store_name,date,item_name,remain,left) values(?,?,?,?,?)',(store,today,item,i['left']-int(num),i['left']-int(num)))
        conn.commit()
        conn.close()
    return redirect(url_for("recent"))

@app.route('/load_sakurakko')
def load_sakurakko(): #メールで取得したデータをeach_salesに更新
    none_dic = {'さくらっこ': {'しそ巻(3個入り)': 0, 'しそ巻(5個入り)': 0, '極': 0, '麻婆豆腐の素': 0}}  #何も受信しなかったときは、更新しない
    index = get_recent()
    mail_data = sakurakko()
    if mail_data != none_dic:
        tdy = datetime.datetime.today()
        today = tdy.strftime('%Y-%m-%d')
        conn = sqlite3.connect('database.sqlite3')
        c = conn.cursor()
        for store, value in mail_data.items(): #maildataから店舗名(key)、商品名と数量(value)を取得
            for item, num in value.items():
                for i in index: #保存されている最新の在庫状況をfor文で取り出す
                    if store == i['store_name'] and item == i['item_name']: #最新在庫状況にある店の名前と商品名、メールデータの店の名前と商品名の両方が一致したらinsert
                        #最新在庫状況から売れた個数を引いてinsert
                        c.execute('insert into each_sales(store_name,date,item_name,remain,left) values(?,?,?,?,?)',(store,today,item,i['left']-int(num),i['left']-int(num)))
        conn.commit()
        conn.close()
    return redirect(url_for("recent"))


@app.route('/recent')
@login_required
def recent():
    index = get_recent()
    return render_template('recent.html', title='sql', index=index)

sess = {'store_name':'選択しない','date_choice':'ここ1週間'} #初期値
@app.route('/home', methods=['GET'])
@login_required
def home():   
    store_choices = []
    store_choices.append('選択しない')
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    for i in c.execute("select store_name from store_name"):
        store_choices.append(i[0])
    conn.commit()
    conn.close()
    if request.args.get('store_name') != None:
        sess['store_name'] = request.args.get('store_name')
    ind = get_index()
    index = index_by_store(ind,sess['store_name'])
    date_choices = ['ここ1週間','ここ1ヶ月','ここ3ヶ月','ここ半年','ここ1年間'] #htmlに渡すための変数
    if request.args.get('date_choice') != None:
        sess['date_choice'] = request.args.get('date_choice')
    final_index = date_range(sess['date_choice'],index)
    return render_template('profile.html', title='sql', each_sales=final_index, store_choices = store_choices,date_choices = date_choices, session = sess)


@app.route('/insert')
@login_required
def insert():
    class StoreForm(FlaskForm):
        conn = sqlite3.connect('database.sqlite3')
        c = conn.cursor()
        store_choices = []
        for i in c.execute("select store_name from store_name"):
            tmp = i + i
            store_choices.append((tmp))
        conn.commit()
        conn.close()
        store_name = SelectField(label = ('店舗名'), choices=store_choices)
    class ItemForm(FlaskForm):
        conn = sqlite3.connect('database.sqlite3')
        c = conn.cursor()
        item_choices = []
        for i in c.execute("select item_name from item_name"):
            tmp = i + i
            item_choices.append((tmp))
        conn.commit()
        conn.close()
        item_name = SelectField(label = ('商品名'), choices=item_choices)
    stform = StoreForm()
    itform = ItemForm()
    index = get_index()
    return render_template('insert.html', title='sql', each_sales=index,stform = stform,itform = itform)

@app.route('/edit_store')
@login_required
def edit_store():
    store = get_store()
    return render_template('store_name.html', title='sql', store_name=store)

@app.route('/edit_item')
@login_required
def edit_item():
    items = get_item()
    return render_template('item_name.html', title='sql', item_name=items)

@app.route('/edit/<int:id>')
@login_required
def edit(id):
    index = get_index()
    prof_dict = list(filter(lambda x: x["id"] == id,index))[0]
    store_initial = prof_dict['store_name']
    item_initial = prof_dict['item_name']
    class StoreForm(FlaskForm):
        conn = sqlite3.connect('database.sqlite3')
        c = conn.cursor()
        store_choices = []
        for i in c.execute("select store_name from store_name"):
            tmp = i + i
            store_choices.append((tmp))
        conn.commit()
        conn.close()
        store_name = SelectField(label = ('店舗名'), choices=store_choices, default = store_initial)
    class ItemForm(FlaskForm):
        conn = sqlite3.connect('database.sqlite3')
        c = conn.cursor()
        item_choices = []
        for i in c.execute("select item_name from item_name"):
            tmp = i + i
            item_choices.append((tmp))
        conn.commit()
        conn.close()
        item_name = SelectField(label = ('商品名'), choices=item_choices, default = item_initial)
    stform = StoreForm()
    itform = ItemForm()
    return render_template('edit.html', title='sql', each_sales=prof_dict,stform = stform, itform = itform)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    conn  = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    sql = ("delete from each_sales where id = ?")
    c.execute(sql,(id,))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route('/store_delete/<int:id>')
@login_required
def store_delete(id):
    conn  = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    sql = ("delete from store_name where id = ?")
    c.execute(sql,(id,))
    conn.commit()
    conn.close()
    return redirect(url_for("edit_store"))

@app.route('/item_delete/<int:id>')
@login_required
def item_delete(id):
    conn  = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    sql = ("delete from item_name where id = ?")
    c.execute(sql,(id,))
    conn.commit()
    conn.close()
    return redirect(url_for("edit_item"))

@app.route('/upd', methods=['POST'])
@login_required
def update_insert():
    prof = []
    # prof_dictの値を変更
    prof.append(request.form['store_name'])
    prof.append(request.form['date'])
    prof.append(request.form['item_name'])
    prof.append(request.form['remain'])
    prof.append(request.form['left'])
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    c.execute('insert into each_sales(store_name,date,item_name,remain,left) values(?,?,?,?,?)',(prof[0],prof[1],prof[2],prof[3],prof[4]))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route('/upd_store', methods=['POST'])
@login_required
def update_store():
    prof = []
    prof.append(request.form['store_name'])
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    sql = "insert into store_name(store_name) values(?)"
    c.execute(sql, (prof[0],))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route('/upd_item', methods=['POST'])
@login_required
def update_item():
    prof = []
    prof.append(request.form['item_name'])
    prof.append(request.form['item_value'])
    conn = sqlite3.connect('database.sqlite3')
    c = conn.cursor()
    sql = "insert into item_name(item_name,item_value) values(?,?)"
    c.execute(sql, (prof[0],prof[1]))
    conn.commit()
    conn.close()
    return redirect(url_for("home"))

@app.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    prof_list = get_index()
    prof_dict = list(filter(lambda x: x["id"] == id,prof_list))[0]
    # prof_dictの値を変更
    prof_dict['store_name'] = request.form['store_name']
    prof_dict['date'] = request.form['date']
    prof_dict['item_name'] = request.form['item_name']
    prof_dict['remain'] = request.form['remain']
    prof_dict['left'] = request.form['left']
    update_index(prof_dict)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, threaded=True)
