attribute_weights * {
    "gender":3,
    "ethnicity":3,
    "current_employer":10,
    "disabilities": 10,
}

def removeScoresFromList(tupleList) :
    newList = []
    for i in range (len(tupleList)-1,-1,-1):
        newList.append(tupleList[i][0])
    return newList

def insertQuestion(currentQTuple, sortedQuestionList):
    if not len(sortedQuestionList)>0 :
        sortedQuestionList.append(currentQTuple)
    elif (len(sortedQuestionList) <20) or (currentQTuple[1] > sortedQuestionList[0][1]) :
        lo = 0
        hi = len(sortedQuestionList)
        while lo < hi:
            mid = (lo+hi)//2
            if currentQTuple[1] < sortedQuestionList[mid][1]:
                hi = mid
            else:
                lo = mid+1
        sortedQuestionList.insert(lo,currentQTuple)
        while len(sortedQuestionList)>20:
            sortedQuestionList.pop(0)
    
def recommend(userprofile, Question):
    tuplelist = []
    for question in Question.objects.all():
        questionscore = 0
        for tag in question.tags.all():
            if tag.attribute in ["gender", "current_employer"]:
                if getattr(userprofile, tag.attribute) == tag.value:
                    questionscore += attribute_weights[tag.value]
            else:
                attlist = getattr(userprofile, tag.attribute).split(str = ",", 1)
                if tag.value in attlist:
                    questionscore += attribute_weights[tag.value]
        questiontuple = (question, questionscore)
        insertQuestion(questiontuple, recommended_questions)
    questionslist = removeScoresFromList(tuplelist)
    return questionslist
