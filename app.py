from flask import Flask, render_template, jsonify, request
from usage import *
from input_to_diagnosis import *

app = Flask(__name__)

output_text = ''
diag = Diagnosis()

@app.route("/")
def renderHome():
	return render_template("home.htm")

# @app.route("/user_input")
# def renderUserInput():
# 	return render_template("user_input.htm")

@app.route("/user_input",methods=["GET","POST"])
def renderOutput():
	if request.method == 'POST':
		output_text = ''
		input_text = ''
		print(request.form)
		text = request.form.get('userinput')
		if text:
			print("Hi",text)
			input_text = text
			output_text = get_output(text)
			diag.set_prompt(output_text,text)
			return render_template("user_input.htm",output=output_text,input=input_text)
		elif diag.get_treated_prompt():
			if request.form.get('edittext'):
				text,original = diag.get_treated_prompt()
				diag.set_prompt(request.form.get('edittext'),original)
				text,original = diag.get_treated_prompt()
				return render_template("user_input.htm",output=text,input=original)
			else:
				text,original = diag.get_treated_prompt()
				diagnosis_text = submit_prompt(text)
				print("diagnose",diagnosis_text)
				return render_template("user_input.htm",output=text,input=original,diagnosis=diagnosis_text)
		else:
			return jsonify(output='Please provide a valid input')
	return render_template("user_input.htm")


# @app.route("/user_input",methods=["GET","POST"])
# def renderDiagnosis():
# 	text = diag.get_treated_prompt()
# 	print("text",text)
# 	if request.method == 'POST':
# 		if text:
# 			diagnosis_text = submit_prompt(text)
# 			print(diagnosis_text)
# 			return render_template("user_input.htm", diagnosis=diagnosis_text)
# 		else:
# 			return jsonify(output='Please provide a valid input')
# 	return render_template("user_input.htm")
		

app.run(port=80, debug=True)