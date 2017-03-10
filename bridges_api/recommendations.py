attribute_weights = {
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
    recommended_questions = []
    for question in Question.objects.all():
        questionscore = 0
        for tag in question.tags.all():
            attlist = getattr(userprofile, tag.attribute).split(",")
            if tag.value in attlist:
                questionscore += attribute_weights[tag.attribute]
        questiontuple = (question, questionscore)
        insertQuestion(questiontuple, recommended_questions)
    questionslist = removeScoresFromList(recommended_questions)
    return questionslist
