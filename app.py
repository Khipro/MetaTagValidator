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
import sys
import pickle


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
    
    # Input the language option
    lang = request.args.get('lang')
    
    # Input the URL or the code snippet
    code = request.args.get('url')
    
    if code == "" or lang == "":
        flash('Failed to retrieve, Both input required ' , 'danger')
    
    else:
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        urlValidator = re.match(regex, code) is not None
        
        
        if not urlValidator:
            content_just_print = BeautifulSoup(code,'lxml').prettify()
            content1 = BeautifulSoup(code,'lxml')
            content = BeautifulSoup(code,'lxml')
            


        else:
            content1_pre = requests.get(code)
            content1 = BeautifulSoup(content1_pre.text, 'html.parser')
            content_pre = requests.get(code)
            content = BeautifulSoup(content_pre.text, 'lxml')

        # Search and add line number to charset
        meta_pre = content.find("meta", charset="utf-8")
        if meta_pre != None:
            meta_bite_remove=meta_pre.encode(formatter=SortAttributes())
            meta_bite_remove = meta_bite_remove.decode('utf8')
            for tag in content1.find_all("meta", charset="utf-8"):
                meta = str(tag.sourceline)+". "+str(meta_pre)
                print(meta)
        else:
            meta = "None"
            print(meta)
        
        # Search and add line number to title
        title_pre = content.find("title")
        if title_pre != 0:
            for tag in content1.find_all("title"):
                title = str(tag.sourceline)+". "+str(title_pre)
                print(title)
        else:
            title ="None"
            print(tit)

        # Search description and custom format
        description_pre = content.find('meta', {'name':'description'})
        description_pre2 = content.find('meta', {'name':'dcterms.description'})
        if description_pre != None:
            description_bite_remove=description_pre.encode(formatter=SortAttributes())
            description_bite_remove = description_bite_remove.decode('utf8')
            for tag in content1.find_all('meta', {'name':'description'}):
                description = str(tag.sourceline)+". "+str(description_bite_remove)
                print(description)
        elif description_pre2 != None:
            description_bite_remove=description_pre2.encode(formatter=SortAttributes())
            description_bite_remove = description_bite_remove.decode('utf8')
            for tag in content1.find_all('meta', {'name':'dcterms.description'}):
                description = str(tag.sourceline)+". "+str(description_bite_remove)
                print(description)
        else:
            description = "None"
            print(description)
        
        # Search keywords
        keywords_pre = content.find('meta', {'name':'keywords'})
        if keywords_pre!= None:    
            keywords_bite_remove=keywords_pre.encode(formatter=SortAttributes())
            keywords_bite_remove = keywords_bite_remove.decode('utf8')
            for tag in content1.find_all('meta', {'name':'keywords'}):
                keywords = str(tag.sourceline)+". "+str(keywords_bite_remove)
                print(keywords)
        else:
            keywords = "None"
            print(keywords)

        # Search scterms creator
        creator_pre = content.find('meta', {'name':'dcterms.creator'})
        if creator_pre!= None:    
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
        if title2_pre!= None:
            title2_bite_remove=title2_pre.encode(formatter=SortAttributes())
            title2_bite_remove = title2_bite_remove.decode('utf8')
            for tag in content1.find_all('meta', {'name':'dcterms.title'}):
                title2 = str(tag.sourceline)+". "+str(title2_bite_remove)
                print(title2)
        else:
            title2 = "None"
            print(title2)    
        
        # Finding date issued
        # Formatting it
        # Checking the date formatting
        date_issued_pre = content.find('meta', {'name':'dcterms.issued'})
        if date_issued_pre!= None:
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
                date_issued ="None"
                print(date_issued)
        else:
            date_issued ="None"
            print(date_issued)
        
        # Finding the date modified
        # Formatting it
        # Checking the date formating    
        
        date_modified_pre = content.find('meta', {'name':'dcterms.modified'})
        if date_modified_pre!= None:
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
                date_modified ="None"
                print(date_modified)
        else:
            date_modified ="None"
            print(date_modified)

        # Search for dcterms.subjects
        # Formatting it
        subject_pre = content.find('meta', {'name':'dcterms.subject'})
        if subject_pre!= None:
            subject_bite_remove=subject_pre.encode(formatter=SortAttributes())
            subject_bite_remove = subject_bite_remove.decode('utf8')
            for tag in content1.find_all('meta', {'name':'dcterms.subject'}):
                subject = str(tag.sourceline)+". "+str(subject_bite_remove)
                print(subject)
        else:
            subject = "None"
            print(subject)
        
        #Search for the dcterms.language
        language_pre = content.find('meta', {'name':'dcterms.language'})
        if language_pre!= None:
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
        else:
            language = "None"
            print(language)

        #find viewport
        #Validate and format it
        viewport_pre = content.find('meta', {'name':'viewport'})
        if viewport_pre!= None:    
            viewport_original = """<meta content="width=device-width,initial-scale=1" name="viewport"/>"""

            for tag in content1.find_all('meta', {'name':'viewport'}):
                if str(viewport_pre) == viewport_original:
                    viewport = str(tag.sourceline) + ". "+ str(viewport_pre)
                    print(viewport)
                else:
                    viewport = "None"
                    print(viewport)
        else:
            viewport = "None"
            print(viewport)


        #Searching for the url cononical
        #Validation and output formatting 
        
        url_canonical_pre = content.find('link', {'rel':'canonical'})
        if url_canonical_pre!= None:
            url_canonical_bite_remove=url_canonical_pre.encode(formatter=SortAttributes())
            url_canonical_bite_remove = url_canonical_bite_remove.decode('utf8')
            for tag in content1.find_all('link', {'rel':'canonical'}):
                url_canonical = str(tag.sourceline)+". "+str(url_canonical_bite_remove)
                print(url_canonical)
        else:
            url_canonical = "None"
            print(url_canonical)
        
        #Searching 1st Adobe tag
        #validating it.
        service_pre = content.find('meta', {'property':'dcterms:service'})
        if service_pre!= None:    
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
        else:
            service = "None"
            print(service)

        #Searching 2nd Adobe tag
        #validating it.
        access_rights_pre = content.find('meta', {'property':'dcterms:accessRights'})
        if access_rights_pre!= None:
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
        else:
            access_rights = "None"
            print(access_rights)

        
        #Finding the 3rd Adobe tag and validating
        #Both with and without https scraped and validated
        adobe_script = content.find('script', {'src':'https://assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js'})
        adobe_script2= content.find('script', {'src':'//assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js'})
        if adobe_script!= None:    
            adobe_original1= """<script src="https://assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js"></script>"""
            for tag in content1.find_all('script', {'src':'https://assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js'}):    
                if  str(adobe_script) == adobe_original1:
                    adobe_third = str(tag.sourceline)+". "+str(adobe_script)
                    print(adobe_third)   
        elif adobe_script2 != None:
            adobe_original2="""<script src="//assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js"></script>"""
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
        #Validate if it is maching the exact tag
        
        adobe = content.find_all('script',{"type":"text/javascript"})
        if adobe == [] or adobe == None:
                adobe_end_tag = "None"
                print(adobe_end_tag)
                
        for tag in content1.find_all('script',{"type":"text/javascript"}):  
            if adobe !=0: 
                x = len(adobe)-1
                adobe_end_tag = (adobe[x])
                adobe_original ="""<script type="text/javascript">_satellite.pageBottom();</script>"""
                if str(adobe_end_tag) == adobe_original:
                    adobe_end_tag = str(tag.sourceline) + ". " + str(adobe_end_tag)
                    print(adobe_end_tag)
                else:
                    adobe_end_tag = "None"
                    print(adobe_end_tag)
                    break
            else:
                adobe_end_tag = "None"
                print(adobe_end_tag)

        if not urlValidator:
            final_string = content_just_print
            print(final_string)       
        
        else:
            with open('\\Users\\KIPandSHREE\\Documents\\test1.txt', 'w') as file:
                file.write(content1_pre.text)

            path = "\\Users\\KIPandSHREE\\Documents\\test1.txt"
            file_path = str(path)


            with open(file_path, 'r') as f:
                list_pre =[]
                final_string =[]
                for i, line in enumerate(f, start=1):
                    first_list= '{}  {}'.format(i, line.strip())
                    list_pre.append(first_list)
                
                final_string = '\n'.join(list_pre)
                print(final_string)
        
        # Find Old tags
        old_title = content.find('meta', {'name':'title'})
        old_dc_title = content.find('meta', {'name':'dc.title'})
        old_dc_description = content.find('meta', {'name':'dc.description'})
        old_dcterms_description = content.find('meta', {'name':'dcterms.description'})
        old_date = content.find('meta', {'name':'date'})
        old_author = content.find('meta', {'name':'author'})
        old_dc_language = content.find('meta', {'name':'dc.language'})
        old_dc_subject = content.find('meta', {'name':'dc.subject'})
        old_dc_creator = content.find('meta', {'name':'dc.creator'})
        old_STCkeywords = content.find('meta', {'name':'STCkeywords'})
        old_STCtopic = content.find('meta', {'name':'STCtopic'})
        old_STCtopicID = content.find('meta', {'name':'STCtopicID'})
        old_STCsubtopic = content.find('meta', {'name':'STCsubtopic'})
        old_STCsubtopicID = content.find('meta', {'name':'STCsubtopicID'})
        old_STCtype = content.find('meta', {'name':'STCtype'})
        old_STCsource = content.find('meta', {'name':'STCsource'})
        old_STCstatus = content.find('meta', {'name':'STCstatus'})
        old_STClist = content.find('meta', {'name':'STClist'})
        old_STCthesaurus = content.find('meta', {'name':'STCthesaurus'})
        old_STCprice = content.find('meta', {'name':'STCprice'})
        


        return render_template('scrape.html', content=final_string, meta = meta, title = title,
         description = description , keywords=keywords,title2=title2,dateissued=date_issued,
         datemodified=date_modified, creator = creator, subject= subject, language=language,
         viewport = viewport, urlcanonical=url_canonical, service = service , accessrights =  access_rights,
         adobescript = adobe_third, adobeendtag= adobe_end_tag ,
        old_dc_description = old_dc_description,
        old_dcterms_description = old_dcterms_description,
        old_date =  old_date,
        old_author = old_author,
        old_dc_language = old_dc_language,
        old_dc_subject = old_dc_subject,
        old_dc_creator = old_dc_creator,
        old_STCkeywords = old_STCkeywords,
        old_STCtopic = old_STCtopic,
        old_STCtopicID = old_STCtopicID,
        old_STCsubtopic = old_STCsubtopic,
        old_STCsubtopicID = old_STCsubtopicID,
        old_STCtype = old_STCtype,
        old_STCsource = old_STCsource,
        old_STCstatus = old_STCstatus,
        old_STClist = old_STClist,
        old_STCthesaurus = old_STCthesaurus,
        old_STCprice = old_STCprice)

    return render_template('scrape.html', content=None, meta = None, title = None, description = None ,
     keywords=None,title2=None,dateissued=None,datemodified=None, creator =None, subject= None, language=None,
     viewport = None, urlcanonical= None, service = None , accessrights = None, adobescript = None,
     adobeendtag= None , old_dc_description = old_dc_description,
        old_dcterms_description = None,
        old_date =  None,
        old_author = None,
        old_dc_language = None,
        old_dc_subject = None,
        old_dc_creator = None,
        old_STCkeywords = None,
        old_STCtopic = None,
        old_STCtopicID = None,
        old_STCsubtopic = None,
        old_STCsubtopicID = None,
        old_STCtype = None,
        old_STCsource = None,
        old_STCstatus = None,
        old_STClist = None,
        old_STCthesaurus = None,
        old_STCprice = None)

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