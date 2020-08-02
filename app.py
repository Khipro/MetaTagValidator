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
from datetime import datetime
import requests
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup
import json
from bs4.formatter import XMLFormatter


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

#Create custom odering of the tags
#Beautiful soup parser auto sorts elements within tags alpabetically
class SortAttributes(XMLFormatter):
    def attributes(self, tag):
        """Reorder a tag's attributes however you want."""
        attrib_order = ['name','title','property', 'content']
        new_order = []
        for element in attrib_order:
            if element in tag.attrs:
                new_order.append((element, tag[element]))
        for pair in tag.attrs.items():
            if pair not in new_order:
                new_order.append(pair)
        return new_order

#Date formating validation
def validate(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False

@app.route('/scrape')
def scrape():
    
    
    lang = request.args.get('lang')
    if lang == "":
        flash('Failed to retrieve "%s"' % lang, 'danger')
    else:
        print(lang)

    code = request.args.get('url')
    
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
        content1 = BeautifulSoup(code,'lxml')
        content = BeautifulSoup(code,'lxml')


    else:
        content1 = requests.get(code)
        content1 = BeautifulSoup(content1.text, 'html.parser')
        content = requests.get(code)
        content = BeautifulSoup(content.text, 'lxml')

    # Search and add line number to charset
    meta_pre = content.find("meta", charset="utf-8")
    meta_bite_remove=meta_pre.encode(formatter=SortAttributes())
    meta_bite_remove = meta_bite_remove.decode('utf8')
    for tag in content1.find_all("meta", charset="utf-8"):
        meta = str(tag.sourceline)+". "+str(meta_bite_remove)
        print(meta)
    
    # Search and add line number to title
    title_pre = content.find("title")
    title_bite_remove=title_pre.encode(formatter=SortAttributes())
    title_bite_remove = title_bite_remove.decode('utf8')
    for tag in content1.find_all("title"):
        title = str(tag.sourceline)+". "+str(title_bite_remove)
        print(title)
        
    # Search description and custom format
    description_pre = content.find('meta', {'name':'description'})
    description_bite_remove=description_pre.encode(formatter=SortAttributes())
    description_bite_remove = description_bite_remove.decode('utf8')
    for tag in content1.find_all('meta', {'name':'description'}):
        description = str(tag.sourceline)+". "+str(description_bite_remove)
        print(description)
    
    # Search keywords
    keywords_pre = content.find('meta', {'name':'keywords'})
    keywords_bite_remove=keywords_pre.encode(formatter=SortAttributes())
    keywords_bite_remove = keywords_bite_remove.decode('utf8')
    for tag in content1.find_all('meta', {'name':'keywords'}):
        keywords = str(tag.sourceline)+". "+str(keywords_bite_remove)
        print(keywords)

    # Search scterms creator
    creator_pre = content.find('meta', {'name':'dcterms.creator'})
    creator_bite_remove=creator_pre.encode(formatter=SortAttributes())
    creator_bite_remove = creator_bite_remove.decode('utf8')
    creator_original_eng = """<meta name="dcterms.creator" content="Government of Canada, Statistics Canada"/>"""
    creator_original_fra = """<meta name="dcterms.creator" content="Gouvernement du Canada, Statistique Canada"/>"""
    for tag in content1.find_all('meta', {'name':'dcterms.creator'}):    
        if lang == "English":
            if str(creator_bite_remove) == creator_original_eng:
                creator = str(tag.sourceline)+". "+str(creator_bite_remove)
                print(creator)
            else:
                creator = "None"
                print(creator)
        elif lang == "French":
            if str(creator_bite_remove) == creator_original_fra:
                creator = str(tag.sourceline)+". "+str(creator_bite_remove)
                print(creator)
            else:
                creator = "None"
                print(creator)
        else:
            creator = "None"
            print(creator)
    
    # Searching the dcterms.title
    title2_pre = content.find('meta', {'name':'dcterms.title'})
    title2_bite_remove=title2_pre.encode(formatter=SortAttributes())
    title2_bite_remove = title2_bite_remove.decode('utf8')
    for tag in content1.find_all('meta', {'name':'dcterms.title'}):
        title2 = str(tag.sourceline)+". "+str(title2_bite_remove)
        print(title2)
    
    
    # Finding date issued
    # Formatting it
    # Checking the date formatting
    date_issued_pre = content.find('meta', {'name':'dcterms.issued'})
    date_issued_bite_remove=date_issued_pre.encode(formatter=SortAttributes())
    date_issued_bite_remove = date_issued_bite_remove.decode('utf8')

    date_issued_string =str(date_issued_bite_remove)
    finding_date = BeautifulSoup(date_issued_string,'lxml').meta.attrs['content']


    validating_date_issued = validate(finding_date)
    if validating_date_issued == True:
        for tag in content1.find_all('meta', {'name':'dcterms.issued'}):
            date_issued = str(tag.sourceline)+". "+str(date_issued_bite_remove)
            print(date_issued)
    else:
        date_issued ="Date formatting issue"
        print(date_issued)
    
    # Finding the date modified
    # Formatting it
    # Checking the date formating    
    
    date_modified_pre = content.find('meta', {'name':'dcterms.modified'})
    date_modified_bite_remove=date_modified_pre.encode(formatter=SortAttributes())
    date_modified_bite_remove = date_modified_bite_remove.decode('utf8')

    date_modified_string =str(date_modified_bite_remove)
    finding_date = BeautifulSoup(date_modified_string,'lxml').meta.attrs['content']


    validating_date = validate(finding_date)
    if validating_date == True:
        for tag in content1.find_all('meta', {'name':'dcterms.modified'}):
            date_modified = str(tag.sourceline)+". "+str(date_modified_bite_remove)
            print(date_modified)
    else:
        date_modified ="Date formatting issue"
        print(date_modified)

    # Search for dcterms.subjects
    # Formatting it
    subject_pre = content.find('meta', {'name':'dcterms.subject'})
    subject_bite_remove=subject_pre.encode(formatter=SortAttributes())
    subject_bite_remove = subject_bite_remove.decode('utf8')
    for tag in content1.find_all('meta', {'name':'dcterms.subject'}):
        subject = str(tag.sourceline)+". "+str(subject_bite_remove)
        print(subject)
    
    #Search for the dcterms.language
    language_pre = content.find('meta', {'name':'dcterms.language'})
    language_bite_remove=language_pre.encode(formatter=SortAttributes())
    language_bite_remove = language_bite_remove.decode('utf8')
    language_original_eng = """<meta name="dcterms.language" title="ISO639-2" content="eng"/>"""
    language_original_fra = """<meta name="dcterms.language" title="ISO639-2" content="fra" />"""
    for tag in content1.find_all('meta', {'name':'dcterms.language'}):    
        if lang == "English":
            if str(language_bite_remove) == language_original_eng:
                language = str(tag.sourceline)+". "+str(language_bite_remove)
                print(language)
            else:
                language = "None"
                print(language)
        elif lang == "French":
            if str(language_bite_remove) == language_original_fra:
                language = str(tag.sourceline)+". "+str(language_bite_remove)
                print(language)
            else:
                language = "None"
                print(language)
        else:
            language = "None"
            print(language)

    #find viewport
    #Validate and format it
    viewport_pre = content.find('meta', {'name':'viewport'})
    print(viewport_pre)
    viewport_original = """<meta content="width=device-width,initial-scale=1" name="viewport"/>"""

    for tag in content1.find_all('meta', {'name':'viewport'}):
        if str(viewport_pre) == viewport_original:
            viewport = str(tag.sourceline) + ". "+ str(viewport_pre)
            print(viewport)
        else:
            viewport = "None"
            print(viewport)

    #Searching for the url cononical
    #Validation and output formatting 
    
    url_canonical_pre = content.find('link', {'rel':'canonical'})
    url_canonical_bite_remove=url_canonical_pre.encode(formatter=SortAttributes())
    url_canonical_bite_remove = url_canonical_bite_remove.decode('utf8')
    for tag in content1.find_all('link', {'rel':'canonical'}):
        url_canonical = str(tag.sourceline)+". "+str(url_canonical_bite_remove)
        print(url_canonical)
    
    #Searching 1st Adobe tag
    #validating it.
    service_pre = content.find('meta', {'property':'dcterms:service'})
    service_xml_string = str(service_pre)
    soup = BeautifulSoup(service_xml_string, 'html.parser')
    service_bite_remove=soup.encode(formatter=SortAttributes())
    service_bit_remove = service_bite_remove.decode('utf8')
    service_original = """<meta property="dcterms:service" content="StatCan"/>"""
    for tag in content1.find_all('meta', {'property':'dcterms:service'}):   
        if service_bit_remove == service_original:
            service = str(tag.sourceline)+". "+str(service_bit_remove)
            print(service)
        else:
            service = "None"
            print(service)

    #Searching 2nd Adobe tag
    #validating it.
    access_rights_pre = content.find('meta', {'property':'dcterms:accessRights'})
    xml_string = str(access_rights_pre)
    soup = BeautifulSoup(xml_string, 'html.parser')
    bite_remove=soup.encode(formatter=SortAttributes())
    bit_remove = bite_remove.decode('utf8')
    access_rights_original = """<meta property="dcterms:accessRights" content="2"/>"""
    for tag in content1.find_all('meta', {'property':'dcterms:accessRights'}):    
        if bit_remove == access_rights_original:
            access_rights = str(tag.sourceline)+". "+str(bit_remove)
            print(access_rights)
        else:
            access_rights = "None"
            print(access_rights)

    
    #Finding the 3rd Adobe tag and validating
    #Both with and without https scraped and validated
    adobe_script = content.find('script', {'src':'https://assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js'})
    adobe_original1= """<script src="https://assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js"></script>"""
    adobe_original2="""<script src="//assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js"></script>"""
    for tag in content1.find_all('script', {'src':'https://assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js'}):    
        if  str(adobe_script) == adobe_original1:
            adobe_third = str(tag.sourceline)+". "+str(adobe_script)
            print(adobe_third)   
        elif adobe_script == None:
            adobe_script2= content.find('script', {'src':'//assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js'})
            for tag in content1.find_all('script', {'src':'//assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js'}):
                if str(adobe_script2) == adobe_original2:
                    adobe_third = str(tag.sourceline)+". "+str(adobe_script2)
                    print(adobe_third)
                else:
                    adobe_third = "None"
                    print(adobe_third)
        else:
            adobe_third = "None"
            print(adobe_third)


    #Validate the end location of the Adove tag
    #Validate if it is maghing the exact tag
    adobe = content.find_all('script',{"type":"text/javascript"})
    for tag in content1.find_all('script',{"type":"text/javascript"}):
        if adobe == [] or adobe == None:
            adobe_end_tag = "None"
            print(adobe_end_tag)
        elif adobe !=0: 
            x = len(adobe)-1
            adobe_end_tag = (adobe[x])
            adobe_original ="""<script type="text/javascript">_satellite.pageBottom();</script>"""
            if str(adobe_end_tag) == adobe_original:
                adobe_end_tag = str(tag.sourceline) + ". " + str(adobe_end_tag)
                print(adobe_end_tag)
            else:
                adobe_end_tag = "None"
                print(adobe_end_tag)
        else:
            adobeendtag = "None"
            print(adobe_end_tag)


    return render_template('scrape.html', content=content1, meta = meta, title = title, description = description , keywords=keywords,title2=title2,dateissued=date_issued,datemodified=date_modified, creator = creator, subject= subject, language=language,viewport = viewport, urlcanonical=url_canonical, service = service , accessrights =  access_rights, adobescript = adobe_third, adobeendtag= adobe_end_tag)


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