# -*- coding: utf-8 -*-
"""
Created by: Brian Kilburn
Date: 9/15/2018
Purpose: SMS Spam Filter
"""

import nltk as lang
#uncomment this if you do not have nltk module
#lang.download('all')

from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd
import csv
import arff

#import numpy as np
#from wordcloud import WordCloud
#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.feature_extraction import DictVectorizer
#from sklearn.linear_model import LogisticRegression
#from sklearn.model_selection import train_test_split
#from sklearn.naive_bayes import GaussianNB
#from sklearn.metrics import accuracy_score
#from sklearn.feature_extraction.text import CountVectorizer
#import sklearn as sk 
 
# measure the length of the message
def messageLength(data):
    messageLen = len(data)
    return messageLen

#get upper case word count
def checkUpper(data):
    count = 0
    for index, value in enumerate(data):
        if value.isupper():
            count += 1
    return count

#check if message has a website url
def hasWebsite(data):
    #print(data)
    for index, value in enumerate(data):
        if(value.startswith('www') or value.startswith('http//') or value.startswith('https//') or value.startswith('ftp//')):
            return 1
    return 0

#check for the most frequent words
def mostFrequentWords(data, word=True):   
    counts = Counter(data)
    if(word):
        item = counts.most_common(1)
        for index, value in enumerate(item):
            item = value[1]
            if item >= 3:
                return 1
        return 0
    else:
        #return string literal word
        item = counts.most_common(1)
        for index, value in enumerate(item):
            item = value[0]
        return item


#spam messages can be lengthy
def wordCount(data):
    length = len(data)
    
    if length > 10:
        return 1
    return 0
 

#spam word checker
def spamWords(data):
    
    spamWordList = ['free', 'urgent', 'call', 'freemsg', 'mob', 'txt', 'entry','reply','claim','download', '2']
    
    if any(map(lambda each: each in data, spamWordList)) == True:
        return 1
    else:
        return 0

def preProcessMessage(data,stop_words = True, stemm = True, lower = True, grams = 2, tokenize = True, punctuation = True):
    
    #set the words to lowercase, lists and series is tricky 
    if(lower):
        data = data.str.lower()
    
    #remove punctuations
    if(punctuation):
        data = data.str.translate(str.maketrans("","",'<>|-[]_.:;,!?&()''""\\'))
            
    #tokenize the data    
    if(tokenize):
        tokens = [lang.word_tokenize(token) for token in data]

    #remove the stopwords to improve efficiency
    if(stop_words):
        stop = stopwords.words('english')
        for index, value in enumerate(tokens):
            tokens[index] = [token for token in value if token not in stop]
        
    #the snowball stemmer is better than porter stemming per documentation, removes redundancy between word meanings.
    if(stemm):
        stemmer = SnowballStemmer('english')
        for index, value in enumerate(tokens):
            tokens[index] = [stemmer.stem(token) for token in value]
            
    if tokenize:
        return tokens
    return data

def featureExtract(df, action=None):
    featureFrame = []
    for i in range(len(df)):
      featureFrame.append(action(df['SMSMessage'][i]))
      
    return featureFrame
    
def main():
    
    #set column width to display data
    pd.set_option('display.max_colwidth', 100)
    #read file and create the dataframe
    data = pd.read_csv('./dataset/SMSSpamCollection.txt', sep='\t', quoting=csv.QUOTE_NONE, names=["label", "SMSMessage"], encoding="utf8")
    
    df = pd.DataFrame(data)
    
    #need to tokenize before searching a url and convert to lowercase
    df['SMSMessage'] = preProcessMessage(df['SMSMessage'])
    df['Website'] = featureExtract(df,hasWebsite)
    df['W-count'] = featureExtract(df,wordCount)
    df['F-WordCount'] = featureExtract(df,mostFrequentWords)
    df['Spamword'] = featureExtract(df, spamWords)
    
    #translate the message data back to string values for arff.dump
    #df['SMSMessage'] = '' + df['SMSMessage'].apply(lambda x: ' '.join(x))
    
    #print(arff.dumps('spam.arff',df.values, relation="spam"))
    df.drop(columns=['SMSMessage'], inplace=True, axis = 1)
    attr = ['label {ham, spam}','Website','W-count',
        'F-WordCount','Spamword']
    #create and export the processed dataset?
    df.to_csv('./SpamProcessedData.csv', encoding='utf-8-sig')
    #df['label'].replace({"spam": 1, "ham": 0}, inplace=True, regex=True)
    
    arff.dump('spam.arff',df.values , relation="spam", names=attr)
    print('done')
main()
