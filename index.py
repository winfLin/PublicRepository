# -*- coding: UTF-8 -*-
from flask import Flask, render_template, request, redirect, url_for,session     
from werkzeug.utils import secure_filename
import os
import pymysql
from openpyxl import load_workbook
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import matplotlib
from urllib.parse import urlparse
import hashlib
import datetime

#SchoolId='中正國中'
#Grade=
#ClassId='09'
#UserId='1100001'
app = Flask(__name__)
app.secret_key = os.urandom(24)

domain = 'scoreranka.herokuapp.com'
#domain = '192.168.0.39'

db_settings = {
    "host": "us-cdbr-east-04.cleardb.com",
    "user": "b732fa551cdfe9",
    "password": "b26d2c37",
#    "host": "localhost",
#    "user": "winf",
#    "password": "I Love Taipower",
    "port": 3306,
    "db": 'heroku_e169d198c975e6d',        
    "charset": "utf8"
}  

def Score2DB(Title, ExamDate, Scores):
    try:
        r=str(random.random())
        datetime_dt = datetime.datetime.today()  # 獲得當地時間
        datetime_str = datetime_dt.strftime("%Y%m%d%H%M%S")

        sid=datetime_str + hashlib.md5(r.encode("utf-8")).hexdigest()              
        conn = pymysql.connect(**db_settings)

        with conn.cursor() as cursor:              
            sql="Insert into Exam (Sid, Title, ExamDate) values (%s, %s, %s)"
                
            cursor.execute(sql, (sid, Title, ExamDate,))            
            for Score in Scores.splitlines():        
                if Score!='':                    
                    sql="Insert into ExamScore (Sid, Score) values (%s, %s)"
                    cursor.execute(sql, (sid, Score,))
        conn.commit()        
        return sid              
    except Exception as e:
       print(str(e))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<string:Sid>')
def ShowRank(Sid):
    return render_template('rec/' + Sid + '.html')


@app.route('/SetScore/<int:step>', methods=['POST', 'GET'])
def SetScore(step):    
    if step==0:
        return render_template('UploadScore.html')    
    elif step==1:
        Title=request.values['examTitle']
        ExamDate=request.values['examDate'] 
        Scores=request.values['examScores']
        Color=request.values['Color']
        Alpha=float(request.values['Alpha'])
        Sid=Score2DB(Title, ExamDate, Scores)  
        Rank(Sid, Color, Alpha) 
        return redirect('/' + Sid)


def Rank(Sid, Color, Alpha):    
    fpath='templates/rec/' + Sid + ".html"        
    conn = pymysql.connect(**db_settings)
            
    with conn.cursor() as cursor:                        
        sql="""SELECT Title, ExamDate, COUNT(if(score between 0 and 9,true,null)) as '0~9', 
                    COUNT(if(score between 10 and 19,true,null)) as '10~19', 
                    COUNT(if(score between 20 and 29,true,null)) as '20~29', 
                    COUNT(if(score between 30 and 39,true,null)) as '30~39', 
                    COUNT(if(score between 40 and 49,true,null)) as '40~49', 
                    COUNT(if(score between 50 and 59,true,null)) as '50~59', 
                    COUNT(if(score between 60 and 69,true,null)) as '60~69', 
                    COUNT(if(score between 70 and 79,true,null)) as '70~79', 
                    COUNT(if(score between 80 and 89,true,null)) as '80~89', 
                    COUNT(if(score >=90,true,null)) as '90~', 
                    Round(Avg(Score),1) as '平均'
                    from ExamScore as S, Exam as E
                    where S.Sid=%s and E.Sid=%s"""
        cursor.execute(sql, ( Sid,Sid,))        
        result=cursor.fetchall()
        header=cursor.description
    print('-'*30)
    DrawRect(Sid, result, Color, Alpha)
    #return render_template('Rank.html')
    Html = render_template('Rank.html', result=result, header=header, Sid=Sid, domain=domain)
    f = open(fpath, "w", encoding='UTF-8')
    f.write(Html)
    f.close()    

def DrawRect(Sid, result, Color, Alpha):    
    col_count = 10
    bar_width = 0.5
    index = np.arange(col_count)    
    scoreList=[]
    for i in range(2,12):
        scoreList.append(result[0][i])
    title=result[0][0]
    examDate=result[0][1]
    plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']
    #font={'family': 'DFKai-SB'}
    #plt.rc('font', **font)

    A = plt.bar(index, scoreList, bar_width, alpha=Alpha, label=examDate, color=[Color]) 

    for item in A:
        height = item.get_height()
        plt.text(
            item.get_x()+item.get_width()/2., 
            height*1.05, 
            '%d' % int(height),
            ha = "center",
            va = "bottom",
        )


    plt.ylabel("人數")
    #plt.xlabel(examDate)
    plt.title(title)
    plt.xticks(index+.3 / 2 ,("0~9", "10~19", "20~29", "30~39", "40~49", "50~59", "60~69", "70~79", "80~89", "90~100"))
    plt.legend() 
    plt.grid(True)
    #plt.show()   
    filename=Sid + ".png"
    plt.savefig(   fname='static/rankImg/' + filename)            
    plt.close() 

if __name__ == '__main__':
    #app.secret_key = os.urandom(24)
    #app.secret_key = 'super secret key'
    app.config['SERVER_NAME'] = domain  # fine
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run('0.0.0.0', 80, debug=True)
