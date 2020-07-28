######################################################
# 
# Libraries
#
######################################################

from flask import Flask
from flask import request
from flask import Response
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
import requests
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup
import json


######################################################
# 
# App instance
#
######################################################

app = Flask(__name__)
app.secret_key = "VERISIKRITKEY"

######################################################
# 
# Routes
#
######################################################

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/scrape')
def scrape():
    #flash(request.args.get('url'), 'success')
    #url = request.args.get('url')
    code = request.args.get('url')
    #print("Code:", code)
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    urlValidator = re.match(regex, code) is not None
    if code == "":
        flash('Failed to retrieve "%s"' % code, 'danger')
    if not urlValidator:
        content = BeautifulSoup(code,'lxml')
    else:
        content = requests.get(code)
        content = BeautifulSoup(content.text, 'lxml')
    meta = content.find("meta", charset="utf-8")
    title = content.find("title")
    description = content.find('meta', {'name':'description'})
    keywords = content.find('meta', {'name':'keywords'})
    title2 = content.find('meta', {'name':'dcterms.title'})
    dateissued = content.find('meta', {'name':'dcterms.issued'})
    datemodified = content.find('meta', {'name':'dcterms.modified'})
    creator = content.find('meta', {'name':'dcterms.creator'})
    subject = content.find('meta', {'name':'dcterms.subject'})
    language = content.find('meta', {'name':'dcterms.language'})
    urlcanonical = content.find('link', {'rel':'canonical'})
    service = content.find('meta', {'property':'dcterms:service'})
    accessrights = content.find('meta', {'property':'dcterms:accessRights'})
    adobescript = content.find('script', {'src':'https://assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js'})

    adobe = content.find_all('script',{"type":"text/javascript"})
    x = len(adobe)-1
    adobeendtag = (adobe[x])

    
    return render_template('scrape.html', content=content, meta = meta, title = title, description = description , keywords=keywords,title2=title2,dateissued=dateissued,datemodified=datemodified, creator = creator, subject= subject, language=language, urlcanonical=urlcanonical, service = service , accessrights =  accessrights, adobescript = adobescript, adobeendtag= adobeendtag)


    #try:       
      #  response = requests.get(url)
      #  content = BeautifulSoup(response.text, 'lxml').prettify()
       # content2 = BeautifulSoup(code, 'lxml').prettify()
        
    #except:
      #  flash('Failed to retrieve URL "%s"' % url, 'danger')
       # content = ''

   # return render_template('scrape.html', content=content)


# render results to screen
@app.route('/results')
def results():
    args = []
    results = []
    
    for index in range(0, len(request.args.getlist('tag'))):
        args.append({
            'tag': request.args.getlist('tag')[index],
            'css': request.args.getlist('css')[index],
            'attr': request.args.getlist('attr')[index],
        })
    
    response = requests.get(request.args.get('url'))
    content = BeautifulSoup(response.text, 'lxml')
    
    # item to store scraped results
    item = {}
    
    # loop over request arguments
    for arg in args:
        # store item
        item[arg['css']] = [one.text for one in content.findAll(arg['tag'], arg['css'])]
    
    # loop over row indexes
    for index in range(0, len(item[next(iter(item))])):
        row = {}
        
        # loop over stored data
        for key, value in item.items():
            # append value to the new row
            row[key] = '"' + value[index] + '"'
        
        # append new row to results list
        results.append(row)
    
    return render_template('results.html', results=results)



######################################################
# 
# Run app
#
######################################################

if __name__ == '__main__':
    app.run(debug=True, threaded=True)