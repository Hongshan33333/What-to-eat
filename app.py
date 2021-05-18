from flask import Flask,render_template,request,redirect,Markup

import requests

app = Flask(__name__)

params = {'minProtein': 0 ,'minFat' : 0,'minCalories' : 0,}
global Count
Count = 0


def GetNutrients(list,Count,nutrition_name): #1: The obtained list 2: The number of refreshes 3: The specific nutritional name, currently supports Protein, Fat, Calories
    results = list['results']
    results_Count = results[Count]
    nutrition0 = results_Count["nutrition"]
    nutrients = nutrition0['nutrients']

    if nutrition_name in ["Protein","Fat","Calories"]:
        if nutrition_name == "Protein":
            nutrition_name = 1
        if nutrition_name == "Fat":
            nutrition_name = 2
        if nutrition_name == "Calories":
            nutrition_name = 0
    else:
        return print("Please fill in correct nutrition_name")
    nutrition_info = nutrients[nutrition_name]
    info = nutrition_info['amount']
    return info


@app.route('/')
def getStart():
    return render_template("getStart.html")

@app.route('/goSelect')
def goSelect():
    # apikey
    params['apiKey'] = '9472cec15ae9453a88ae58da71df8875'
    return render_template("goSelect_FirestStep.html")

#The first step, choose allergies
@app.route("/goSelect_FirestStep",methods = ['GET','POST'])
def goSelect_FirestStep():

    # Convert the received array into a string linked by commas
    allergy_args_raw = ''
    allergy_list = request.args.getlist("intolerances")
    for v in allergy_list:
        allergy_args_raw = v + ',' +allergy_args_raw
    allergy_args = allergy_args_raw.rstrip(',')

    # Convert the dictionary into a string for passing parameters to Url
    intolerances = allergy_args

    #Send parameters
    params["intolerances"] = intolerances

    return render_template("goSelect_Step2.html")

#The second step, choose cuisine
@app.route("/goSelect_Step2")
def goSelect_Step2():
    cuisine = request.args.get('cuisine')
    params["cuisine"] = cuisine
    return render_template("goSelect_Step3.html")

#The third step, choose the type of dish
@app.route("/goSelect_Step3")
def goSelect_Step3():
    typee  = request.args.get('type')
    params["type"] = typee
    return redirect("/showResult")


# Put the final result on this route
@app.route("/showResult")
def showResult():
    # send the parameters received in the dictionary
    request = requests.get("https://api.spoonacular.com/recipes/complexSearch", params=params)

    # Instantiate a dictionary
    showResult = request.json()

    # Instantiate result as an Array
    results = showResult["results"]

    if results == [] :
        return render_template("showResult_none.html", title='Your taste is a bit picky.')

    global Count
    if Count == len(results):
        Count = 0

    results1 = results[Count]



    title = results1["title"]
    image = results1['image']
    id = results1['id']
    Calories = GetNutrients(showResult, Count, "Calories")
    Fat = GetNutrients(showResult, Count, "Fat")
    Protein = GetNutrients(showResult, Count, "Protein")

    if Calories > 500 :
        Calories_color = "red"

    else:
        Calories_color = "green"

    if Fat > 20 :
        Fat_color = "red"

    else:
        Fat_color = "green"

    VisualizeTaste = "https://api.spoonacular.com/recipes/" + str(id) + "/tasteWidget?apiKey=9472cec15ae9453a88ae58da71df8875"
    requesVisualizeTaste = requests.get(VisualizeTaste)
    requesVisualizeTasteHTML = requesVisualizeTaste.text


    requesVisualizeTasteHTML = Markup(requesVisualizeTasteHTML)

    return render_template("showResult.html",title = title,img = image, Count=Count, Calories=Calories, Fat=Fat, Protein=Protein, Calories_color = Calories_color, Fat_color=Fat_color, taste=requesVisualizeTasteHTML)


@app.route("/tryAgain")
def tryAgain():

    return redirect("/goSelect")

@app.route("/return")
def return1():
    returnname=request.args.get("pagename")
    print(returnname)
    returnpath=returnname+".html"
    print (returnpath)
    return render_template(returnpath)

@app.route("/Next")
def Next():
    global Count
    Count=Count+1


    return redirect("/showResult")


if __name__ == '__main__':
    app.run(debug=True)
