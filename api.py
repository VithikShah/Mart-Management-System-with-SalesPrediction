from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import fbprophet
import pandas as pd
from datetime import date,timedelta,datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import time
import io
import calendar

app = Flask(__name__)
db = MySQL(app)

app.secret_key = 'dbms'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vithik13&'
app.config['MYSQL_DB'] = 'dbms'
app.config['MYSQL_HOST'] = 'localhost'

#login
@app.route('/',methods=['GET','POST'])
def login():
	if request.method=='GET':
		return render_template('land.html')
	else:
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		username = request.form.get("username")
		cur.execute('SELECT * FROM EMPLOYEE WHERE Username = %s',(str(username),))
		l = cur.fetchone()
		if not l:
			return render_template('land.html', msg = 'Invalid Username')

		pwd = request.form.get("pwd")
		cur.execute('SELECT ShopID,EmpID,EmpPassword FROM EMPLOYEE WHERE Username = %s',(str(username),))

		row = cur.fetchone()
		if row and pwd == row['EmpPassword']:
			session['loggedin'] = True
			session['empid'] = row['EmpID']
			session['shopid'] = row['ShopID']
			session['username'] = str(username)
			cur.execute('SELECT * FROM MANAGES WHERE EmpID='+str(session['empid'])+' AND ShopID='+str(session['shopid'])+';')
			a = cur.fetchone()
			if a:
				session['manager'] = True
				return redirect(url_for('manager_add_item'))
			else:
				session['manager'] = False
				return redirect(url_for('index'))
		else:
			return render_template('land.html', msg = 'Invalid Password')
		cur.close()

#Index page for employee
@app.route('/index',methods=['GET','POST'])
def index():
	if session.get('empid') is None:
		return render_template('land.html', msg = 'Please Login as an Employee')
	cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
	query = "SELECT * FROM  INVENTORY WHERE ShopID = " + str(session['shopid'])
	cur.execute(query)
	items = cur.fetchall()
	query = "SELECT * FROM ITEMS"
	cur.execute(query)
	item_det = cur.fetchall()
	item_names = {}
	for x in item_det:
		item_names[x['ItemID']] = x['Name']
	if request.method=='GET':
		return render_template('index.html', items = items, item_names = item_names)
	if request.method=='POST':
		item_id = request.form.get("item_id")
		item_quantity = request.form.get("item_quantity")
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		query = "SELECT Units FROM  INVENTORY WHERE ShopID = " + str(session['shopid']) + " AND ItemID = " + str(item_id)
		cur.execute(query)
		old_value = cur.fetchone()['Units']
		new_value = int(old_value) - int(item_quantity)
		if new_value < 0:
			return render_template('index.html', items = items, item_names=item_names, msg = "Not enough items in inventory!")
		query = "UPDATE INVENTORY SET Units = " + str(new_value) + " WHERE ShopID = " + str(session['shopid']) + " AND ItemID = " +str(item_id)
		cur.execute(query)
		query = "INSERT INTO SALES VALUES(" + str(session['shopid']) + "," + str(item_id) + "," + str(item_quantity) + ",CURRENT_TIME())" 
		cur.execute(query) 
		cur.close()
		db.connection.commit()
		return redirect(url_for('index'))

#For adding item quantity
@app.route('/add',methods=['POST'])
def add():
	if request.method=='POST':
		item_id = request.form.get("item_id")
		item_quantity = request.form.get("item_quantity")
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		query = "SELECT Units FROM  INVENTORY WHERE ShopID = " + str(session['shopid']) + " AND ItemID = " + str(item_id)
		cur.execute(query)
		old_value = cur.fetchone()['Units']
		new_value = int(old_value) + int(item_quantity)
		query = "UPDATE INVENTORY SET Units = " + str(new_value) + " WHERE ShopID = " + str(session['shopid']) + " AND ItemID = " +str(item_id)
		cur.execute(query)
		cur.close()
		db.connection.commit()
		return redirect(url_for('index'))

#Adding new item
@app.route('/manager_add_item',methods=['GET','POST'])
def manager_add_item():
	cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
	query = "SELECT * FROM ITEMS"
	cur.execute(query)
	items = cur.fetchall()
	if request.method=='GET':
		if session.get('empid') is None or session['manager'] == False:
			return render_template('land.html', msg = 'Please Login as Manager')
		return render_template('manager_add_item.html', items = items)
	if request.method=='POST':
		item_id = request.form.get("item_id")
		item_quantity = request.form.get("item_quantity")
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		try:
			query = "INSERT INTO INVENTORY VALUES(" + str(session['shopid']) + "," +  str(item_id) + "," + str(item_quantity) + ")"
			cur.execute(query)
			cur.close()
			db.connection.commit()
		except:
			return render_template('manager_add_item.html', items = items, msg = "Item already exists in inventory!")
		return redirect(url_for('index'))

@app.route('/add_employee',methods=['GET','POST'])
def employee_add():
	if request.method=='GET':
		if session.get('empid') is None or session['manager'] == False:
			return render_template('land.html', msg = 'Please Login as Manager')
		return render_template('add_employee.html')
	else:
		name = request.form.get("name")
		uname = request.form.get("uname")
		pwd = request.form.get("pwd")
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('INSERT INTO EMPLOYEE (ShopID,EmpName,EmpPassword,Username) VALUES(%s,%s,%s,%s)',(str(session['shopid']),str(name),str(pwd),str(uname)))
		#query = "INSERT INTO EMPLOYEE (ShopID,EmpName,EmpPassword,Username) VALUES(" + str(session['shopid']) + "," +  str(name) + "," + str(pwd) + "," + str(uname) + ")"
		cur.close()
		db.connection.commit()
		return redirect(url_for('employee_add'))

@app.route('/add_items',methods=['GET','POST'])
def add_items():
	if request.method=='GET':
		if session.get('empid') is None or session['manager'] == False:
			return render_template('land.html', msg = 'Please Login as Manager')
		return render_template('add_items.html')
	else:
		name = request.form.get("name")
		cost = request.form.get("cost")
		cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('INSERT INTO ITEMS (Name,Cost) VALUES(%s,%s)',(str(name),str(cost)))
		#query = "INSERT INTO EMPLOYEE (ShopID,EmpName,EmpPassword,Username) VALUES(" + str(session['shopid']) + "," +  str(name) + "," + str(pwd) + "," + str(uname) + ")"
		cur.close()
		db.connection.commit()
		return redirect(url_for('add_items'))

@app.route('/sales',methods=['GET'])
def sales():
	if session.get('empid') is None or session['manager'] == False:
		return render_template('land.html', msg = 'Please Login as Manager')
	cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
	query = "SELECT * FROM SALES WHERE ShopID = " + str(session['shopid'])
	cur.execute(query)
	sales = cur.fetchall()
	query = "SELECT * FROM ITEMS"
	cur.execute(query)
	item_det = cur.fetchall()
	item_names = {}
	for x in item_det:
		item_names[x['ItemID']] = x['Name']
	cur.close()
	db.connection.commit()
	return render_template('sales.html', sales = sales, items = item_names)

@app.route('/logout',methods=['GET'])
def logout():
	session.clear()
	return render_template('land.html', msg = 'You have been logged out')


@app.route('/predict',methods=['GET'])
def predict():
	if session.get('empid') is None:
		return render_template('land.html', msg = 'Please Login as an Employee')
	shopid=str(session['shopid'])
	cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
	cur.execute('SELECT ItemID,Quantity,SaleDate FROM SALES WHERE ShopID='+shopid+';')
	l = cur.fetchall()
	sales = []
	for i in l:
		sales.append(i.values())

	ll = []
	today = datetime.strptime('2019-11-13','%Y-%m-%d')
	# today = date.today()
	for i in range(1,8):
		da = today + timedelta(days=i)
		ll.append(str(da))
	data = pd.DataFrame(sales,columns=['ItemID','y','ds'])
	prediction = pd.DataFrame(columns=list(data['ItemID'].unique())+['y'],index=ll)
	for i in prediction.columns:
		prediction[i]=0
	# print(prediction)
	for item in data['ItemID'].unique():
		d = data[data.ItemID==item].drop(['ItemID'],axis=1)
		model = fbprophet.Prophet()
		model.fit(d)

		START_DATE = datetime.strptime('2019-11-09','%Y-%m-%d')
		today = datetime.strptime('2019-11-13','%Y-%m-%d')
		per = today - START_DATE
		
		p = model.make_future_dataframe(periods=per.days+8)
		# print('ID:',item)
		# print(d)
		# print()
		# print(p)
		fc = model.predict(p)
		print(fc)
		for i in fc['ds']:
			if str(i) in prediction.index:
				prediction.loc[str(i)][item] += int(round(fc[fc.ds==i]['yhat']))

		for i in prediction.index:
			sum = 0
			for j in prediction.columns:
				if j!='y':
					sum+=prediction.loc[i][j]
			prediction.loc[i]['y'] = sum
	
	x = list(prediction.index)
	for i in range(len(x)):
		x[i] = datetime.strptime(x[i][:10],'%Y-%m-%d')
		# x[i] = calendar.day_name(datetime.strptime(x[i][:10],"%Y-%m-%d"))
	y = prediction['y']

	print(x)
	print(y)
	# print(type(x[0]))
	plt.plot(x,y)
	plt.tight_layout()
	plt.xlabel('Dates')
	plt.ylabel('No. of sales predicted')
	plt.savefig('static/images/foo.png')
	# print("PLOT SAVED")
	time.sleep(2)
	prediction.rename(columns = {'y':'Total Sales'},inplace=True)
	ind = {}
	for i in prediction.index:
		ind[i] = i[:10]
	prediction.rename(index = ind,inplace=True) 
	

	return render_template('timeseries.html', tables = [prediction.to_html(classes='data')],titles=prediction.columns.values)


if __name__ == '__main__':
	app.run(debug=True)
