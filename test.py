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

col_count = 10
bar_width = 0.5
index = np.arange(col_count)
A_scores = (1,2,3, 4, 5, 6, 7, 8, 9, 10, 11)
scoreList=list(A_scores)
print(type(A_scores))
plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']
font={'family': 'DFKai-SB'}
plt.rc('font', **font)

A = plt.bar(index, scoreList(11), bar_width, alpha=.4, label="K") 

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
#plt.xlabel("中文2")
plt.title("中文3")
plt.xticks(index+.3 / 2 ,("0~9", "10~19", "20~29", "30~39", "40~49", "50~59", "60~69", "70~79", "80~89", "90~100"))
plt.legend() 
plt.grid(True)
plt.show()