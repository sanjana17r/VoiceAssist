import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time

API_KEY='t7sXqo87e5p0'
PROJECT_TOKEN='tdnO-YZ8r8JJ'
RUN_TOKEN='tzdxeSoLP_Cg'



class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params={
            'api_key':self.api_key
        }
        self.data = self.get_data()
    def get_data(self):#calls the reques and set attributes
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data', params={'api_key':API_KEY})#to get data from the parsehub last run
        data = json.loads(response.text)
        return data

    def get_total_cases(self):
        data = self.data['total']

        for content in data:
            if content['name']=='Coronavirus Cases:':
                return content['value']#returns the total cases in world

    def get_total_deaths(self):
        data = self.data['total']

        for content in data:
            if content['name']=='Deaths:':
                return content['value']#returns total edaths
        return '0'
    def get_country_data(self,country):
        data=self.data['country']

        for content in data:
            if content['name'].lower()==country.lower():
                return content

        return '0'


    def get_list_of_coutries(self):
        countries=[]
        for country in self.data['country']:
            countries.append(country['name'].lower())

        return countries

    def update_data(self):#initializes new run in parsehub
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)
        

        def poll():
            time.sleep(0.1)
            old_data= self.data
            while True:
                new_data=self.get_data()
                if(new_data != old_data):
                    self.data=new_data
                    print("DAta updated")
                    break
                time.sleep(5)



        t=threading.Thread(target=poll)#thread used to contstantly ask server for response, without interrupting program
        t.start()



def speak(text):
    engine=pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
        said=''

        try:
            said=r.recognize_google(audio)#audio is translated to text using google 


        except Exception as e:
            print('Exception: ',str(e))
    return said.lower()

def main():
    data=Data(API_KEY,PROJECT_TOKEN)
    print('started program')
    END_PHRASE="stop"
    country_list= (data.get_list_of_coutries())

    TOTAL_PATTERNS={ #any word before total and cases
                re.compile('[\w\s]+ total [\w\s]+ cases'):data.get_total_cases,
                re.compile('[\w\s]+ total cases'):data.get_total_cases,
                re.compile('[\w\s]+ total [\w\s]+ deaths'):data.get_total_deaths,
                re.compile('[\w\s]+ total deaths'):data.get_total_deaths, 
                }
            
    COUNTRY_PATTERNS={ #any word before total and cases
                re.compile('[\w\s]+ cases [\w\s]'):lambda country: data.get_country_data(country)['total_cases'],
                re.compile('[\w\s]+ deaths [\w\s]'):lambda country: data.get_country_data(country)['total_deaths']
                }
    
    UPDATE_COMMAND = 'update'

    while True:
        print("Listening.........")
        text = get_audio()
        print(text)
        result=None

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words=set(text.split(' '))#"how mnay in canada"
                for country in country_list:
                    if country in words:
                        result=func(country)
                        break
            

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result=func()#calls the associated function
                break

        if text==UPDATE_COMMAND:
            result="Data is being upated, may take a moment!!"
            data.update_data()
            
        if result:
            speak(result)
        

        if text.find(END_PHRASE) != -1:#stpo loop
            print('exit---')
            break

main()

