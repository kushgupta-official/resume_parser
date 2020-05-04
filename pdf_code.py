from pdfminer.converter import TextConverter
import docx2txt
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
from io import StringIO
import re
import nltk
import spacy
from nltk.corpus import stopwords
from spacy.matcher import Matcher
import pandas as pd


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        # iterate over all pages of PDF document
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            # creating a resoure manager
            resource_manager = PDFResourceManager()
            
            # create a file handle
            fake_file_handle = io.StringIO()
            
            # creating a text converter object
            converter = TextConverter(
                                resource_manager, 
                                fake_file_handle, 
                                codec='utf-8', 
                                laparams=LAParams()
                        )

            # creating a page interpreter
            page_interpreter = PDFPageInterpreter(
                                resource_manager, 
                                converter
                            )

            # process current page
            page_interpreter.process_page(page)
            
            # extract text
            text = fake_file_handle.getvalue()
            yield text

            # close open handles
            converter.close()
            fake_file_handle.close()

def extract_text_from_doc(doc_path):
    temp = docx2txt.process(doc_path)
    text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
    return ' '.join(text)


filename = 'similar_resume.pdf'
#filename = 'as.pdf'
#filename = 'ng.docx'
#filename = 'ab.pdf'
#filename = 'sc.pdf'
text = ''
# calling above function and extracting text

file_ext = re.findall(".pdf$", filename)
if (re.findall(".pdf$", filename)):
    for page in extract_text_from_pdf(filename):
        text += ' ' + page
    #print(text)
elif (re.findall(".doc$", filename)) or (re.findall(".docx$", filename)):
    text =  extract_text_from_doc(filename)
    #print(text)
else:
    print("Oops! Wrong file format.")


print("\n\n\n\n###############################################")
#extraction of name
x = re.findall(r'([A-Z][a-z]+(?: [A-Z][a-z]\.)? [A-Z][a-z]+)', text)
print(" NAME: " )

print("\n\n\n\n###############################################")
#extraction of phone numbers
def extract_mobile_number(text):
    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number

phone_no = extract_mobile_number(text)
print(" PHONE:" )
print(phone_no)

#extraction of email address
def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None

email = extract_email(text)
print("\n\n\n\n###############################################")
print(" EMAIL:" )
print(email)

#extraction of skills
# load pre-trained model
nlp = spacy.load('en_core_web_sm')

# Grad all general stop words
STOPWORDS = set(stopwords.words('english'))

# Education Degrees
EDUCATION = [
        'AA','A.A.','AS','A.S.','BEP','CAP','Dip.Arts','Dip.Lang.Stud.','Dip.Lang','Dip.Soc.Sc.','Dip.Ed','Dip.Mus.',
        'MB','M.B.','LLB', 'LL.B', 'BTech', 'B.Tech', 'BSA', 'BMath', 'B.Math', 'BLit', 'B.Lit.', 'BEng', 'B.Eng.', 
        'BE', 'B.E' ,'Bed', 'B.Ed.','BEC','B.E-COM.','BDSc','B.D.Sc.','BDS','B.D.S.','BChD','B.Ch.D.','BDent','B.Dent.',
        'BComm','B.Comm.','BCom','B.Com.','BBA','B.B.A.','BArch','B.Arch.','BAcy','B.Acy.','M.Arch.','MBA','M.B.A.',
        'MTech','M.Tech.', 'PhD', 'Ph.D.', 'DPhil', 'D.Phil.', 'DPh', 'D.Ph.', 'BE','B.E.', 'B.E', 'BS', 'B.S', 
            'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII','CA','ICWA'
        ]


def extract_education(resume_text):
    nlp_text = nlp(resume_text)

    # Sentence Tokenizer
    nlp_text = [sent.string.strip() for sent in nlp_text.sents]

    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex not in STOPWORDS:
                edu[tex] = text + nlp_text[index + 1]
    return edu


qualify = extract_education(text)
print("\n\n\n\n ###############################################")
print("QUALIFICATIONS:" )
print(qualify)


# load pre-trained model
nlp = spacy.load('en_core_web_sm')
# noun_chunks = nlp.noun_chunks
var = nlp(text)
# for chunk in var.noun_chunks:
#     print(chunk.text)

def extract_skills(resume_text):
    nlp_text = nlp(resume_text)

    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    
    # reading the csv file
    data = pd.read_csv("skills.csv") 
    
    # extract values
    skills = list(data.columns.values)
    
    skillset = []
    
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    
    # check for bi-grams and tri-grams (example: machine learning)
    for token in var:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset])]

intrest = extract_skills(text)
print("\n\n\n\n ###############################################")
print("INTRESTS :" )
print(intrest)