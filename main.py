from flask import Flask,render_template,request,url_for,flash,redirect,get_flashed_messages,jsonify
from unicodedata import category
import localfeeds
import database
import forms
import nationalfeeds
import worldheadlines
from database import update_news
from forms import updatepassword, addpapers, addcategories

from apscheduler.schedulers.background import BackgroundScheduler
update_news()
schedular=BackgroundScheduler()
schedular.add_job(func=update_news,trigger='interval',minutes=1)
schedular.start()


app=Flask(__name__)
app.secret_key='123abc'

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/index')
def index():
     # post1 = worldheadlines.get_world('https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml')
     # post2 = worldheadlines.get_world('https://www.washingtontimes.com/rss/headlines/news/world')
     # post3 = worldheadlines.get_world('http://rss.cnn.com/rss/money_topstories.rss')
     post1=database.get_news('nyt')
     post2 = database.get_news('wtt')
     post3 = database.get_news('cnn')
     return render_template('index.html', title="index page", post1=post1, post2=post2, post3=post3)

@app.route('/national')
def national():
     # post1 = nationalfeeds.get_national('https://timesofindia.indiatimes.com/rssfeedstopstories.cms')
     # post2 = nationalfeeds.get_national('https://www.news18.com/commonfeeds/v1/eng/rss/india.xml')
     # post3 = nationalfeeds.get_national('https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml')
     post1 = database.get_news('toi')
     post2 = database.get_news('n18')
     post3 = database.get_news('ht')
     return render_template('national.html', title="national page", post1=post1, post2=post2, post3=post3)

@app.route('/local')
def local():
     # post1 = localfeeds.get_local('https://www.greaterkashmir.com/feed/')
     # post2 = localfeeds.get_local('https://globalkashmir.net/feed/')
     # post3 = localfeeds.get_local('https://kashmirreader.com/feed/')
     post1 = database.get_news('gk')
     post2 = database.get_news('glk')
     post3 = database.get_news('krd')
     return render_template('local.html', title="local page", post1=post1, post2=post2, post3=post3)



@app.route('/about')
def about():
     return render_template('about.html',title="about")

@app.route('/login')
def login():
     form=forms.login()
     return render_template('login.html', title="login", form=form)

@app.route('/admin',methods=['POST'])
def admin():
     uname=request.form.get('username')
     password = request.form.get('password')
     data=database.get_users()
     dbuname=data[0][0]
     dbpassword=data[0][1]
     if uname==dbuname and password==dbpassword:
          updatepassword_form = forms.updatepassword()
          papers=database.get_papers()
          categories=database.get_categories()
          addpapers=forms.addpapers()
          addcategories=forms.addcategories()

          return render_template('admin.html', title="admin page", updatepassword_form=updatepassword_form,
                                 papers=papers,categories=categories, addpaper=addpapers, addcategories=addcategories)



     else:
          flash(' Invalid Username or Password !', 'danger')
          return redirect('login')



@app.route('/updatepassword',methods=['POST'])
def updatepassword():
     uname = request.form.get('user_name')
     password = request.form.get('pass_word')
     cpassword = request.form.get('confirm_pass_word')
     updatepassword_form = forms.updatepassword()
     papers = database.get_papers()
     categories = database.get_categories()
     addpapers = forms.addpapers()
     addcategories = forms.addcategories()

     if password==cpassword:
          flag=database.get_updatepassword(uname,password)
          if flag:
             flash('Password Updated Sucessfully','updatepassword-success')
          else:
             flash('Username Does Not Exist','updatepassword-danger')
          return render_template('admin.html', title="admin page", updatepassword_form=updatepassword_form,
                                 papers=papers,
                                 categories=categories, addpaper=addpapers, addcategories=addcategories)
     else:
          flash('Password and Confirm Password are not same','updatepassword-danger')
     return render_template('admin.html', title="admin page", updatepassword_form=updatepassword_form, papers=papers,
                            categories=categories, addpaper=addpapers, addcategories=addcategories)


@app.route('/addpaper',methods=['POST'])
def add_paper():
     try:
          paper_type = request.form.get('paper_type')
          paper_name = request.form.get('paper_name')
          updatepassword_form = forms.updatepassword()
          categories = database.get_categories()
          addpapers = forms.addpapers()
          addcategories = forms.addcategories()
          flag = database.add_paper(paper_name, paper_type)
          papers = database.get_papers()

          if flag:
               flash('Paper Added Successfully', 'addpaper-success')
          else:
               flash('Error! Paper Not Added', 'addpaper-danger')
          return render_template('admin.html', title="admin page", updatepassword_form=updatepassword_form,
                                 papers=papers,
                                 categories=categories, addpaper=addpapers, addcategories=addcategories)
     except:
          return render_template('405.html',title='405')


@app.route('/addcategory',methods=['POST'])
def add_category():
     try:
          paper_id = request.form.get('paper_id')
          category_name = request.form.get('category_name')
          category_link = request.form.get('category_link')
          updatepassword_form = forms.updatepassword()
          addpapers = forms.addpapers()
          addcategories = forms.addcategories()
          flag = database.add_category(category_name, category_link, paper_id)
          papers = database.get_papers()
          categories = database.get_categories()
          if flag:
               flash('Category Added Successfully', 'addcategories-success')
          else:
               flash(' Error!Category Not Added', 'addcategories-danger')

          return render_template('admin.html', title="admin page", updatepassword_form=updatepassword_form,
                                 papers=papers,
                                 categories=categories, addpaper=addpapers, addcategories=addcategories)
     except:
          return render_template('errors/403.html',title='403')



@app.route('/customize',methods=['GET','POST'])
def customize():
     try:
          posts = worldheadlines.get_world('https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml')
          form = forms.choicesform()
          if form.is_submitted():
               category_id = request.form.get('newscategory')
               link = database.get_link(category_id)
               posts = worldheadlines.get_world(link)

               return render_template('customize.html', title="Customized News", posts=posts, form=form)
          return render_template('customize.html', title="Customized News", posts=posts, form=form)



     except:
          return render_template('errors/404.html')




@app.route('/get_papers',methods=['GET','POST'])
def get_papers():
     try:
          if request.method == 'POST':
               zone = request.form['zone']
               papers = database.get_searched_papers(zone)

               return jsonify(papers)
     except:
          return render_template('errors/403.html',title='403')


@app.route('/get_categories',methods=['GET','POST'])
def get_categories():
     try:
          if request.method == 'POST':
               paper_id = request.form['paper_id']
               categories = database.get_searched_categories(paper_id)

               return jsonify(categories)
     except:
          return render_template('errors/403.html', title='403')

@app.errorhandler(403)
def error_403(error):
     return render_template('errors/403.html',title='403')


@app.errorhandler(404)
def error_404(error):
     return render_template('errors/404.html', title='404')


@app.errorhandler(405)
def error_405(error):
     return render_template('errors/405.html', title='405')


@app.errorhandler(500)
def error_500(error):
     return render_template('errors/403.html', title='500')




if __name__=='__main__':
    app.run(debug=True)











