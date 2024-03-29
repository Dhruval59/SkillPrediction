import nltk
import codecs
from nltk.corpus import stopwords
import csv
from random import shuffle
import json
import csv
import re
import spacy
import ast

nlp = spacy.load('en_core_web_sm')

stopset = dict(zip(stopwords.words("english"),range(len(stopwords.words("english")))))

class Preprocessor(object):
    def __init__(self, data_x_path):
        # print("-----Begin processor initialization-----")
        self.data_x_file = codecs.open(data_x_path, "rU", encoding='utf-8', errors='ignore')
        self.tokens_out = self.loadDicModel("data/input/tokens_out.json")
        self.y_dict = self.loadDicModel("data/input/y_dict.json")
        # print("-----End processor initialization-----")

    # Output Vector
    def get_output_vec(self, output_items):
        outputs = output_items.split(';')
        output = [0]*(len(self.tokens_out.keys())+1)
        tokens = []
        for y in outputs :
            y_l = y.lower()
            if y_l in self.y_dict.keys() :
                tokens +=self.y_dict.get(y_l)
        tokens = set(tokens)
        labels = []
        # print("Labels for this resume:")
        for token in tokens:
            if token in self.tokens_out:
                labels.append(self.tokens_out[token])
                # label.append(token)
                output[self.tokens_out[token]] = 1
        output[-1] = labels
        return output
    
    def clean(self, string):
        string = re.sub(re.compile(r'<.*?>'), '', string)
        string = re.sub(re.compile(r'[$&+,:;=?@#|\'<>^*()%!]'), '', string)
        # string = emoji.demojize(string)
        # string = re.sub(r'\:(.*?)\:','',string)
        # string = str(string).lower()    #Making string Lowercase
        # string = re.sub('\[.*?\]', '', string)
        # #The next 2 lines remove html string
        # string = BeautifulSoup(string, 'lxml').get_string()
        # string = re.sub('https?://\S+|www\.\S+', '', string)
        # string = re.sub('<.*?>+', '', string)
        # string = re.sub('\n', '', string)
        # string = re.sub('\w*\d\w*', '', string)
        # # replacing everything with space except (a-z, A-Z, ".", "?", "!", ",", "'")
        # string = re.sub(r"[^a-zA-Z?.!,¿']+", " ", string)
        return string
    
    def transform_data(self):
        self.data_x_file.seek(0)
        lines = self.data_x_file.read().splitlines()
        shuffle(lines)
        print("Lines shuffled")
        i = 1
        
        # List of roles to be removed from the resumes
        roles_words = ['Administrator', 'Developer', 'Analyst', 'Consultant', 'Technician', 
        'Architect', 'Specialist', 'Manager', 'Accountant', 'Associate', 
        'Representative', 'Assistant', 'Coordinator', 'President', 'Lead', 
        'Receptionist', 'Freelancer', 'Chief', 'Advisor', 'DBA', 'Support',
        'Member', 'Programmer', 'Recruiter', 'Instructor', 'Intern', 'Engineer', 'Agent',
        'Scientist', 'Expert', 'Professor', 'Director', 'Officer']

        with open('data/output/dataset_entities.csv', 'w') as f:
            # create the csv writer
            writer = csv.writer(f)
            writer.writerow(['Text','Skills','Education','Experience','Additional_Information','Software_Developer','Front_End_Developer','Network_Administrator','Web_Developer','Project_manager','Database_Administrator','Security_Analyst','Systems_Administrator','Python_Developer','Java_Developer','Labels'])
            
            # writer =  csv.writer(fp, delimiter = ',')
            for line in lines:
                res = {}
                # print("Processing Resume "+str(i)+"#.....")
                i += 1
                if line != "::::::" and not line.isspace():
                    line_items = line.split(":::")
                    if len(line_items) == 3 :
                        cv = self.clean(line_items[2])
                        # print(cv)
                        res['Text']=str(cv)
                        res['Skills']=list(set(re.split(';|,', line_items[1])))
                        
                        # Removing the set of roles from Resumes
                        roles_words_set = set(word.lower() for word in roles_words)
                        res['Skills'] = list(set(skill for skill in res['Skills'] if not roles_words_set.intersection(set(skill.lower().split()))))

                        res['Skills']=' '.join(res['Skills'])

                        # Tokenizing Resume Texts
                        cv_sents = nltk.sent_tokenize(cv)
                        experience = []
                        education = []
                        adinf = []
                        # link = []
                        # skills = []
                        for sent in cv_sents:
                            # if 'Link' in sent:
                            #     link.append(re.findall(r'(https?://[^\s]+)', sent))
                            if 'Work Experience' in sent:
                                experience.append(sent[sent.index('Work Experience')+16:])
                            if 'Additional Information' in sent:
                                adinf.append(sent[sent.index('Additional Information')+23:])
                            if 'Education' in sent:
                                if 'Skills' in sent:
                                    education.append(sent[sent.index('Education')+10:sent.index('Skills')-1])
                                else:
                                    education.append(sent[sent.index('Education')+10:])
                        
                        res['Education']=str(' '.join(education))
                        res['Experience']=str(' '.join(experience))
                        res['Additional_Information']=str(' '.join(adinf))
                        
                        # res['Links']=' '.join(link) if len(link)!=0 else ""
                        
                        output = self.get_output_vec(line_items[1])
                        res = res | dict(zip(self.tokens_out.keys(), output))
                        res['Label']=output[-1]
                        print(res)
                        # Writing res to csv file
                        writer.writerow(res.values())
                            
    def loadDicModel(self, file):
        with open(file) as json_file:
            return json.load(json_file)
