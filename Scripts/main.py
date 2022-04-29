'''
Created on 28-Apr-2022

@author: 223055789
'''

import json
import requests
import os

# Update the URL as per the Environment url.
# the API address present in REST -SERVER is '/uploadQutionnaries'.


RestServerUrl = "http://localhost:3001/v1/patients/uploadQutionnaries"

dirpath = os.path.normpath(os.getcwd() + os.sep + os.pardir)

QuestionList = []
def ReadSurveyJSJson():
    print("***Reading SurveyJS Questions from the Json***"+'\n')
    data = []
    json_data = open(os.path.join(dirpath,'surveyJson.json'))
    data = json.load(json_data)
    # print(data)
    # print(type(data['pages'][0]['elements']['type']))
    for i in range (0,len(data['pages'][0]['elements'])):
        
        QuestionType = {}
        # for radio button question
        if (data['pages'][0]['elements'][i]['type'] == 'radiogroup'):
            from radiogroupEntity import Entity
            objQuestion = Entity.radiogroupQuestions
            objQuestion['name'] = data['pages'][0]['elements'][i]['name']
            objQuestion['title'] = data['pages'][0]['elements'][i]['title']
            objQuestion['choises'] = data['pages'][0]['elements'][i]['choices']
            objQuestion['type'] = data['pages'][0]['elements'][i]['type']
            QuestionType['radiogroup']=objQuestion
        #for text box type Questions
        elif (data['pages'][0]['elements'][i]['type'] == 'text'):
            from textEntity import Entity
            objQuestion = Entity.textQuestions
            objQuestion['name'] = data['pages'][0]['elements'][i]['name']
            objQuestion['type'] = data['pages'][0]['elements'][i]['type']
            QuestionType['text']=objQuestion
        #for Check box type questions
        elif (data['pages'][0]['elements'][i]['type'] == 'checkbox'):
            from checkboxEntity import Entity
            objQuestion = Entity.checkboxQuestions
            objQuestion['name'] = data['pages'][0]['elements'][i]['name']
            objQuestion['title'] = data['pages'][0]['elements'][i]['title']
            objQuestion['choises'] = data['pages'][0]['elements'][i]['choices']
            objQuestion['type'] = data['pages'][0]['elements'][i]['type']
            QuestionType['checkbox']=objQuestion
        #for yes no type questions
        elif (data['pages'][0]['elements'][i]['type'] == 'boolean'):
            from booleanEntity import Entity
            objQuestion = Entity.booleanQuestions
            # print(data['pages'][0]['elements'][i]['type'])
            objQuestion['name'] = data['pages'][0]['elements'][i]['name']
            objQuestion['title'] = data['pages'][0]['elements'][i]['title']
            objQuestion['type'] = data['pages'][0]['elements'][i]['type']
            QuestionType['boolean']=objQuestion
        QuestionList.append(QuestionType)

            
def createFhirJson():
    # //cretae a json object
    fhirJson = {}
    fhirJson['resourceType']= "Questionnaire"
    fhirJson['meta']= {"profile":[
      "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire|2.7"
    ]}
    
    title = input('Enter new questionnaries name:')
    fhirJson["name"]= title.lower().replace(" ", "_")
    fhirJson["title"]= title
    fhirJson["status"]= "draft"
    
    LinkId = input("Enter LinkedId: sample: Vascular Assessment")
    {"linkId" : LinkId.lower().replace(" ", "_"),
      "text": LinkId,
      "type": "group",}  
    item_outer = []
    for question in QuestionList:
        for key, value in question.items():
            answerOptionList = []
            if key == 'checkbox' or key == 'radiogroup':
                item ={}
                for k in range(0,len(value['choises'])):
                    answerOptionDict = {}
                    answerOptionDict['valueCoding']= {
                    "code": value['choises'][k]['text'].lower(),
                    "display": value['choises'][k]['text']}
                        
                    answerOptionList.append(answerOptionDict)
                 
                item["item"] = {"extension": [{"url": "http://hl7.org/fhir/StructureDefinition/questionnaire-itemControl",
              "valueCodeableConcept":{"coding": [{"system": "http://hl7.org/fhir/questionnaire-item-control",
                    "code": "check-box",
                    "display": "Check Box"}],"text": "Check Box"}}],
                "answerOption":answerOptionList,
                "linkId":input("Enter LinkedId for each question: Sample = 'urinationControl'"),
                "code": [{
              "system": "http://loinc.org",
              "code": "72514-3",
              "display": value['choises'][k]['text']
            }],
            "text": value["title"],
          "type": "group",
          "required": 'false'
        },
                item_outer.append(item)    
            if key == 'boolean':
                item ={}
                item["item"] = {"linkId":input("Enter LinkedId for each question: Sample = 'urinationControl'"),"code":[{"system": "http://loinc.org",
                "code": "72514-3",
                "display": value["title"]}],
                "text": value["title"],
                "type": "boolean",
                "required": "false"
          }
                item_outer.append(item)    
        fhirJson["item"] = item_outer
    json_object = json.dumps(fhirJson, indent = 2)
    # Writing to sample.json
    with open(os.path.join(dirpath,'QuestionJson.json'), "w") as outfile:
        outfile.write(json_object)
    print("***Creating FHIR Object json Complete***")
            
def ApiCalltoRestServer():
    print("***Calling the OncoRPM Rest server***")
    json_data = open(os.path.join(dirpath,'QuestionJson.json'))
    data = json.load(json_data)
    response = requests.post(RestServerUrl,json=data)
    print(response)
    if response.status_code == 201:
        print("***Questionnarie uploaded sucessfully to CDIP***")
    else:
        print("***Questionnarie uploaded to CDIP got an error.***")

ReadSurveyJSJson()
createFhirJson()
ApiCalltoRestServer()