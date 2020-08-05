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
                error_meta =""
                print(error_meta)
        else:
            meta = ""
            print(meta)
            error_meta ="""Required meta tag [ <meta charset="utf-8"/> ] is missing. Please review your code."""
            print(error_meta)
        
        # Search and add line number to title
        title_pre = content.find("title")
        if title_pre != 0:
            for tag in content1.find_all("title"):
                title = str(tag.sourceline)+". "+str(title_pre)
                print(title)
                error_title = ""
                print(error_title)
        else:
            title =""
            print(tit)
            error_title = """Required meta tag [ title ] is missing. Please review your code."""
            print(error_title)

        # Search description and custom format
        description_pre = content.find('meta', {'name':'description'})
        if description_pre != None:
            description_bite_remove=description_pre.encode(formatter=SortAttributes())
            description_bite_remove = description_bite_remove.decode('utf8')
            for tag in content1.find_all('meta', {'name':'description'}):
                description = str(tag.sourceline)+". "+str(description_bite_remove)
                print(description)
                error_description = ""
                print(error_description)
        else:
            description = ""
            print(description)
            error_description = """Required meta tag [ description ] is missing. Please review your code."""
            print(error_description)

        # Search keywords
        keywords_pre = content.find('meta', {'name':'keywords'})
        if keywords_pre!= None:    
            keywords_bite_remove=keywords_pre.encode(formatter=SortAttributes())
            keywords_bite_remove = keywords_bite_remove.decode('utf8')
            for tag in content1.find_all('meta', {'name':'keywords'}):
                keywords = str(tag.sourceline)+". "+str(keywords_bite_remove)
                print(keywords)
                error_keywords = ""
                print(error_keywords)
        else:
            keywords = ""
            print(keywords)
            error_keywords = """Required meta tag [ keywords ] is missing. Please review your code."""
            print(error_keywords)

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
                        error_creator = ""
                        print(error_creator)
                    else:
                        creator = ""
                        print(creator)
                        error_creator = """Required meta tag [ dcterms.creator ] is missing. Please review your code."""
                        print(error_creator)
                elif lang == "French":
                    if str(creator_bite_remove) == creator_original_fra:
                        creator = str(tag.sourceline)+". "+str(creator_bite_remove)
                        print(creator)
                        error_creator = ""
                        print(error_creator)
                    else:
                        creator = ""
                        print(creator)
                        error_creator = """Required meta tag [ dcterms.creator ] is missing. Please review your code."""
                        print(error_creator)
        else:
            creator = ""
            print(creator)
            error_creator = """Required meta tag [ dcterms.creator ] is missing. Please review your code."""
            print(error_creator)

        # Searching the dcterms.title
        title2_pre = content.find('meta', {'name':'dcterms.title'})
        if title2_pre!= None:
            title2_bite_remove=title2_pre.encode(formatter=SortAttributes())
            title2_bite_remove = title2_bite_remove.decode('utf8')
            for tag in content1.find_all('meta', {'name':'dcterms.title'}):
                title2 = str(tag.sourceline)+". "+str(title2_bite_remove)
                print(title2)
                error_title2 =  ""
                print(error_title2) 
        else:
            title2 = ""
            print(title2)
            error_title2 =  """Required meta tag [ dcterms.title ] is missing. Please review your code."""
            print(error_title2)  
        
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
                    error_dcterms_issued = ""
                    print(error_dcterms_issued)
            else:
                date_issued =""
                print(date_issued)
                error_dcterms_issued = """Meta tag value for [ dcterms.issued ] appears to be in wrong format. Date fields should be in the format yyyy-mm-dd (e.g. 2020-04-29)"""
                print(error_dcterms_issued)
        else:
            date_issued =""
            print(date_issued)
            error_dcterms_issued = """Required meta tag [ dcterms.issued ] is missing. Please review your code."""
            print(error_dcterms_issued)

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
                    error_dcterms_modified = ""
                    print(error_dcterms_modified)
            else:
                date_modified =""
                print(date_modified)
                error_dcterms_modified = """Meta tag value for [ dcterms.modified ] appears to be in wrong format. Date fields should be in the format yyyy-mm-dd (e.g. 2020-04-29)"""
                print(error_dcterms_modified)
        else:
            date_modified =""
            print(date_modified)
            error_dcterms_modified = """Required meta tag [ dcterms.modified ] is missing. Please review your code."""
            print(error_dcterms_modified)

        # Search for dcterms.subjects
        # Formatting it
        subject_pre = content.find('meta', {'name':'dcterms.subject'})
        if subject_pre!= None:
            subject_bite_remove=subject_pre.encode(formatter=SortAttributes())
            subject_bite_remove = subject_bite_remove.decode('utf8')
            for tag in content1.find_all('meta', {'name':'dcterms.subject'}):
                subject = str(tag.sourceline)+". "+str(subject_bite_remove)
                print(subject)
                error_dcterms_subject = ""
                print(error_dcterms_subject)
        else:
            subject = ""
            print(subject)
            error_dcterms_subject = """Required meta tag [ dcterms.subject ] is missing. Please review your code."""
            print(error_dcterms_subject)
        
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
                        error_dcterms_language = ""
                        print(error_dcterms_language)

                    else:
                        language = ""
                        print(language)
                        error_dcterms_language = """Meta tag value for [ English ] appears to be in the wrong language for the page selected. Please refer to the values in the instructions or contact the Search Solutions Unit (SSU) for assistance."""
                        print(error_dcterms_language)

                elif lang == "French":
                    if str(language_bite_remove) == language_original_fra:
                        language = str(tag.sourceline)+". "+str(language_bite_remove)
                        print(language)
                        error_dcterms_language = ""
                        print(error_dcterms_language)
                    else:
                        language = ""
                        print(language)
                        error_dcterms_language = """Meta tag value for [ French ] appears to be in the wrong language for the page selected. Please refer to the values in the instructions or contact the Search Solutions Unit (SSU) for assistance."""
                        print(error_dcterms_language)
                else:
                    language = ""
                    print(language)
        else:
            language = ""
            print(language)
            error_dcterms_language = """Required meta tag [ dcterms.language ] is missing. Please review your code."""
            print(error_dcterms_language)

        #find viewport
        #Validate and format it
        viewport_pre = content.find('meta', {'name':'viewport'})
        if viewport_pre!= None:    
            viewport_original = """<meta content="width=device-width,initial-scale=1" name="viewport"/>"""

            for tag in content1.find_all('meta', {'name':'viewport'}):
                if str(viewport_pre) == viewport_original:
                    viewport = str(tag.sourceline) + ". "+ str(viewport_pre)
                    print(viewport)
                    error_viewport = ""
                    print(error_viewport)
                else:
                    viewport = ""
                    print(viewport)
                    error_viewport = """Required meta tag [ viewport ] is missing. Please review your code."""
                    print(error_viewport)
        else:
            viewport = ""
            print(viewport)
            error_viewport = """Required meta tag [ viewport ] is missing. Please review your code."""
            print(error_viewport)


        #Searching for the url cononical
        #Validation and output formatting 
        
        url_canonical_pre = content.find('link', {'rel':'canonical'})
        if url_canonical_pre!= None:
            url_canonical_bite_remove=url_canonical_pre.encode(formatter=SortAttributes())
            url_canonical_bite_remove = url_canonical_bite_remove.decode('utf8')
            for tag in content1.find_all('link', {'rel':'canonical'}):
                url_canonical = str(tag.sourceline)+". "+str(url_canonical_bite_remove)
                print(url_canonical)
                error_canonical = ""
                print(error_canonical)
        else:
            url_canonical = ""
            print(url_canonical)
            error_canonical = """No canonical tag found. Dynamic pages and high profile pages require a canonical tag. Please contact the Search Solutions Unit (SSU) to ensure the tags and values are appropriate for your page."""
            print(error_canonical)
        
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
                    error_service = ""
                    print(error_service)


                else:
                    service = ""
                    print(service)
                    error_service = """Required Adobe Analytics meta tags [ dcterms:service ] is missing from the <head> section. Please review your code. """
                    print(error_service)
        else:
            service = ""
            print(service)
            error_service = """Required Adobe Analytics meta tags [ dcterms:service ] is missing from the <head> section. Please review your code. """
            print(error_service)

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
                    error_accessRights = ""
                    print(error_accessRights)
                else:
                    access_rights = ""
                    print(access_rights)
                    error_accessRights = """Required Adobe Analytics meta tags [ dcterms:accessRights ] is missing from the <head> section. Please review your code."""
                    print(error_accessRights)
        else:
            access_rights = ""
            print(access_rights)
            error_accessRights = """Required Adobe Analytics meta tags [ dcterms:accessRights ] is missing from the <head> section. Please review your code."""
            print(error_accessRights)

        
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
                    error_adobe_third = ""
                    print(error_adobe_third)  
        elif adobe_script2 != None:
            adobe_original2="""<script src="//assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js"></script>"""
            for tag in content1.find_all('script', {'src':'//assets.adobedtm.com/caacec67651710193d2331efef325107c23a0145/satelliteLib-c2082deaf69c358c641c5eb20f94b615dd606662.js'}):
                if str(adobe_script2) == adobe_original2:
                    adobe_third = str(tag.sourceline)+". "+str(adobe_script2)
                    print(adobe_third)
                    error_adobe_third = ""
                    print(error_adobe_third) 

                else:
                    adobe_third = ""
                    print(adobe_third)
                    error_adobe_third = """Required Adobe Analytics JavaScript code is missing from the header. Please review your code. """
                    print(error_adobe_third)
        else:
            adobe_third = ""
            print(adobe_third)
            error_adobe_third = """Required Adobe Analytics JavaScript code is missing from the header. Please review your code. """
            print(error_adobe_third)


        #Validate the end location of the Adove tag
        #Validate if it is maching the exact tag
        
        adobe = content.find_all('script',{"type":"text/javascript"})
        if adobe == [] or adobe == None:
                adobe_end_tag = ""
                print(adobe_end_tag)
                error_adobe_end_tag = """Required Adobe Analytics JavaScript code is missing from the footer. Please review your code.  """
                print(error_adobe_end_tag)
                
        for tag in content1.find_all('script',{"type":"text/javascript"}):  
            if adobe !=0: 
                x = len(adobe)-1
                adobe_end_tag = (adobe[x])
                adobe_original ="""<script type="text/javascript">_satellite.pageBottom();</script>"""
                if str(adobe_end_tag) == adobe_original:
                    adobe_end_tag = str(tag.sourceline) + ". " + str(adobe_end_tag)
                    print(adobe_end_tag)
                    error_adobe_end_tag = ""
                    print(error_adobe_end_tag)
                else:
                    adobe_end_tag = ""
                    print(adobe_end_tag)
                    error_adobe_end_tag = """Required Adobe Analytics JavaScript code is missing from the footer. Please review your code.  """
                    print(error_adobe_end_tag)
                    break
            else:
                adobe_end_tag = ""
                print(adobe_end_tag)
                error_adobe_end_tag = """Required Adobe Analytics JavaScript code is missing from the footer. Please review your code.  """
                print(error_adobe_end_tag)

        
        ### To add line numbers to the main code snippet
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
        old_title_pre = content.find('meta', {'name':'title'})
        if old_title_pre !=None:
            old_title = "Old meta tag [ title ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_title = ""

        old_dc_title_pre = content.find('meta', {'name':'dc.title'})
        if old_dc_title_pre !=None:
            old_dc_title = "Old meta tag [ dc.title ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_dc_title = ""

        old_dc_description_pre = content.find('meta', {'name':'dc.description'})
        if old_dc_description_pre !=None:
            old_dc_description = "Old meta tag [ dc.description ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_dc_description = ""

        old_dcterms_description_pre = content.find('meta', {'name':'dcterms.description'})
        if old_dcterms_description_pre !=None:
            old_dcterms_description = "Old meta tag [ dcterms.description ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_dcterms_description = ""

        old_date_pre = content.find('meta', {'name':'date'})
        if old_date_pre !=None:
            old_date = "Old meta tag [ date ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_date = ""

        old_author_pre = content.find('meta', {'name':'author'})
        if old_author_pre !=None:
            old_author = "Old meta tag [ author ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_author = ""

        old_dc_language_pre = content.find('meta', {'name':'dc.language'})
        if old_dc_language_pre !=None:
            old_dc_language = "Old meta tag [ dc.language ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_dc_language = ""

        old_dc_subject_pre = content.find('meta', {'name':'dc.subject'})
        if old_dc_subject_pre !=None:
            old_dc_subject = "Old meta tag [ dc.subject ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_dc_subject = ""

        old_dc_creator_pre = content.find('meta', {'name':'dc.creator'})
        if old_dc_creator_pre !=None:
            old_dc_creator = "Old meta tag [ dc.creator ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_dc_creator = ""

        old_STCkeywords_pre = content.find('meta', {'name':'STCkeywords'})
        if old_STCkeywords_pre !=None:
            old_STCkeywords = "Old meta tag [ STCkeywords ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCkeywords = ""
            
        old_STCtopic_pre = content.find('meta', {'name':'STCtopic'})
        if old_STCtopic_pre !=None:
            old_STCtopic = "Old meta tag [ STCtopic ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCtopic = ""

        old_STCtopicID_pre = content.find('meta', {'name':'STCtopicID'})
        if old_STCtopicID_pre !=None:
            old_STCtopicID = "Old meta tag [ STCtopicID ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCtopicID = ""

        old_STCsubtopic_pre = content.find('meta', {'name':'STCsubtopic'})
        if old_STCsubtopic_pre !=None:
            old_STCsubtopic = "Old meta tag [ STCsubtopic ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCsubtopic = ""

        old_STCsubtopicID_pre = content.find('meta', {'name':'STCsubtopicID'})
        if old_STCsubtopicID_pre !=None:
            old_STCsubtopicID = "Old meta tag [ STCsubtopicID ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCsubtopicID = ""
            
        old_STCtype_pre = content.find('meta', {'name':'STCtype'})
        if old_STCtype_pre !=None:
            old_STCtype = "Old meta tag [ STCtype ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCtype = ""

        old_STCsource_pre = content.find('meta', {'name':'STCsource'})
        if old_STCsource_pre !=None:
            old_STCsource = "Old meta tag [ STCsource ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCsource = ""

        old_STCstatus_pre = content.find('meta', {'name':'STCstatus'})
        if old_STCstatus_pre !=None:
            old_STCstatus = "Old meta tag [ STCstatus ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCstatus = ""

        old_STClist_pre = content.find('meta', {'name':'STClist'})
        if old_STClist_pre !=None:
            old_STClist = "Old meta tag [ STClist ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STClist = ""

        old_STCthesaurus_pre = content.find('meta', {'name':'STCthesaurus'})
        if old_STCthesaurus_pre !=None:
            old_STCthesaurus = "Old meta tag [ STCthesaurus ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCthesaurus = ""

        old_STCprice_pre = content.find('meta', {'name':'STCprice'})
        if old_STCprice_pre !=None:
            old_STCprice = "Old meta tag [ STCprice ] found. These tags are no longer in use. Please contact the Search Solutions Unit (SSU) for further instructions." 
        else:
            old_STCprice = ""
        


        return render_template('scrape.html', content=final_string, 
        meta = meta,
        title = title,
        description = description,
        keywords=keywords,
        title2=title2,
        dateissued=date_issued,
        datemodified=date_modified,
        creator = creator,
        subject= subject,
        language=language,
        viewport = viewport,
        urlcanonical=url_canonical,
        service = service,
        accessrights =  access_rights,
        adobescript = adobe_third,
        adobeendtag= adobe_end_tag ,
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
        old_STCprice = old_STCprice,
        error_meta = error_meta,
        error_title = error_title,
        error_description = error_description,
        error_keywords=error_keywords,
        error_creator=error_creator,
        error_title2=error_title2,
        error_dcterms_issued=error_dcterms_issued,
        error_dcterms_modified=error_dcterms_modified,
        error_dcterms_subject=error_dcterms_subject,
        error_dcterms_language=error_dcterms_language,
        error_viewport=error_viewport,
        error_canonical=error_canonical,
        error_service=error_service,
        error_accessRights=error_accessRights,
        error_adobe_third=error_adobe_third,
        error_adobe_end_tag=error_adobe_end_tag )

    return render_template('scrape.html',
    content=None,
    meta = None,
    title = None,
    description = None ,
    keywords=None,
    title2=None,
    dateissued=None,
    datemodified=None,
    creator =None,
    subject= None,
    language=None,
    viewport = None,
    urlcanonical= None,
    service = None ,
    accessrights = None,
    adobescript = None,
    adobeendtag= None ,
    old_dc_description = None,
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