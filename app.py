from flask import Flask, render_template, url_for, request, session, redirect, abort, jsonify
from controllers.database import mongo
from werkzeug.utils import secure_filename
import os,re
import spacy, fitz,io
from bson.objectid import ObjectId
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import pathlib
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
from flask import flash
from utils import totalexperience
import logging


def allowedExtension(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ['docx','pdf']

def allowedExtensionPdf(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ['pdf']

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app.secret_key = "Resume_screening"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = ""
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json") #verify this
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)






UPLOAD_FOLDER = 'static/uploaded_resumes'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

app.config['MONGO_URI']= '#'


mongo.init_app(app)
resumeFetchedData = mongo.db.resumeFetchedData
Applied_EMP=mongo.db.Applied_EMP
IRS_USERS = mongo.db.IRS_USERS
JOBS = mongo.db.JOBS
resume_uploaded = False
mongo.db.IRS_USERS.create_index("Email", unique=True)
from controllers.Job_post import job_post
app.register_blueprint(job_post,url_prefix="/HR1")

###Spacy model
print("Loading Resume Parser model...")
nlp = spacy.load('model/ResumeModel/output/model-best')
print("Resume Parser model loaded")


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/emp')
def emp():
    if 'user_id' in session and 'user_name' in session:
        resume_data_id = session.get('resume_data_id')
        if resume_data_id:
            resume_data = resumeFetchedData.find_one({"_id": ObjectId(resume_data_id)})
            if resume_data:
                if 'YEARS OF EXPERIENCE' in resume_data:
                    resume_data['Total Experience'] = totalexperience.calculate_total_experience(resume_data['YEARS OF EXPERIENCE'])
                return render_template("EmployeeDashboard.html", resume_data=resume_data)
        return render_template("EmployeeDashboard.html")
    else:
        return render_template("index.html", errMsg="Login First")

@app.route('/login', methods=['POST', 'GET'])
def login():
    email = request.form.get('email').lower() 
    password = request.form.get('password')

    user = mongo.db.IRS_USERS.find_one({"Email": email})

    if user:
        if check_password_hash(user['Password'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['firstName']
            return redirect('/emp')
        else:
            flash('Invalid credentials, please try again.!', 'error')
            return redirect(url_for('index'))
    else:
        flash('No user found with that email.', 'error')
        return redirect(url_for('index'))

@app.route('/signup', methods=["POST"])

def signup():
    if request.method == 'POST':
        firstName = request.form.get('firstname')
        lastName = request.form.get('lastname')
        email = request.form.get('email').lower() 
        password = request.form.get('password')

        if not firstName or not lastName or not email or not password:
            return render_template("index.html", errMsg="All fields are required.")
        
        hashed_password = generate_password_hash(password)

        try:
            status = IRS_USERS.insert_one({
                "firstName": firstName,
                "lastName": lastName,
                "Email": email,
                "Password": hashed_password
            })
            # MongoDB insert_one returns an InsertOneResult, check inserted_id to confirm insertion
            if status.inserted_id:
                return render_template("index.html", successMsg="User Created Successfully!")
        except DuplicateKeyError:
            return render_template("index.html", errMsg="Email already exists. Please use a different email.")
        except Exception as e:
            return render_template("index.html", errMsg="Problem in user creation check data or try after some time: " + str(e))

    return render_template("index.html", errMsg="Invalid request method.")
@app.route("/logout")
def logout():
    session.pop('user_id',None)
    session.pop('user_name',None)
    session.pop('resume_data_id', None) 
    return redirect(url_for("index"))

@app.route('/HR_Homepage', methods=['GET', 'POST'])
def HR_Homepage():
    return render_template("CompanyDashboard.html")
    
@app.route('/HR', methods=['GET', 'POST'])
def HR():
    if request.method == 'POST':
        # Get the user's response from the form
        response = request.form['response']

        # Check the user's response and route accordingly
        if response == "777":
            
            return render_template("CompanyDashboard.html")
        elif response == "111":
            return render_template("CompanyDashboard.html")
            

        else:
            message = "Incorrect Id. Try Again !! "
        return render_template('form.html', message=message)

            
    else:
        # Render the form template
        return render_template('form.html')
    


@app.route('/test')
def test():
    return "Connection Successful"


@app.route("/uploadResume", methods=['POST'])
def uploadResume():
    if 'user_id' in session and 'user_name' in session:
        try:
            file = request.files['resume']
            filename = secure_filename(file.filename)
            # print("Extension:",file.filename.rsplit('.',1)[1].lower())
            if file and allowedExtension(file.filename):
                temp = resumeFetchedData.find_one({"UserId":ObjectId(session['user_id'])},{"ResumeTitle":1})

                if temp == None:
                    print("New Resume")
                else:
                    print("Document already exists with the same name ")
                    resumeFetchedData.delete_one({"UserId":ObjectId(session['user_id'])})
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'],temp['ResumeTitle']))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                print("Resume Uploaded")
                
                
                fname = "static/uploaded_resumes/"+filename
                print(fname)
                doc = fitz.open(fname)
                print("Resume taken as input")

                text_of_resume = " "
                for page in doc:
                    text_of_resume = text_of_resume + str(page.get_text())

                label_list=[]
                text_list = []
                dic = {}
                
                doc = nlp(text_of_resume)
                for ent in doc.ents:
                    label_list.append(ent.label_)
                    text_list.append(ent.text)
                
                print("Model work done")

                for i in range(len(label_list)):
                    if label_list[i] in dic:
                        # if the key already exists, append the new value to the list of values
                        dic[label_list[i]].append(text_list[i])
                    else:
                        # if the key does not exist, create a new key-value pair
                        dic[label_list[i]] = [text_list[i]]
                
                print(dic)
                resume_data_annotated = ''
                for key, value in dic.items():
                    for val in value:
                        resume_data_annotated += val + " "
               
                resume_name = dic.get('NAME')
                if resume_name is not None:
                    value_name = resume_name[0]
                else:
                    value_name = None

                resume_linkedin = dic.get('LINKEDIN LINK')
                if resume_linkedin is not None:
                    value_linkedin = resume_linkedin[0]
                    value_linkedin = re.sub('\n', '',value_linkedin)
                else:
                    value_linkedin= None


                resume_skills = dic.get('SKILLS')
                if resume_skills is not None:                  
                    value_skills = resume_skills
                else:
                    value_skills = None

                resume_certificate = dic.get('CERTIFICATION')
                if resume_certificate is not None:
                    value_certificate = resume_certificate
                else:
                    value_certificate=None

                resume_workedAs = dic.get('WORKED AS')
                if resume_workedAs is not None:
                    value_workedAs = resume_workedAs
                else:
                    value_workedAs = None
            

                resume_experience = dic.get('YEARS OF EXPERIENCE')
                if resume_experience is not None:
                    value_experience = resume_experience
                else:
                    value_experience = None
               
                
                result = None               
                result = resumeFetchedData.insert_one({"UserId":ObjectId(session['user_id']),"Name":value_name,"LINKEDIN LINK": resume_linkedin,"SKILLS": value_skills,"CERTIFICATION": value_certificate,"WORKED AS":value_workedAs,"YEARS OF EXPERIENCE":value_experience,"Appear":0,"ResumeTitle":filename,"ResumeAnnotatedData":resume_data_annotated,"ResumeData":text_of_resume})                
                
                
                if result.inserted_id:
                    session['resume_data_id'] = str(result.inserted_id)
                    resume_data = resumeFetchedData.find_one({"_id": result.inserted_id})
                    if 'YEARS OF EXPERIENCE' in resume_data:
                        resume_data['Total Experience'] = totalexperience.calculate_total_experience(resume_data['YEARS OF EXPERIENCE'])
                    return render_template("EmployeeDashboard.html", resume_data=resume_data, successMsg="Resume Uploaded Successfully!")
                
                else:
                    return render_template("EmployeeDashboard.html", errorMsg="Failed to store resume data.")
            else:
                return render_template("EmployeeDashboard.html", errorMsg="Invalid file type.")
        except Exception as e:
            return render_template("EmployeeDashboard.html", errorMsg=str(e))
    else:
        return render_template("index.html", errMsg="Login First")


@app.route('/viewdetails', methods=['POST', 'GET'])
def viewdetails():      
    employee_id = request.form['employee_id']     
    result = resumeFetchedData.find_one({"UserId": ObjectId(employee_id)})

    if not result:
        return jsonify({'error': 'No data found'}), 404
    
    name = result.get('Name', None)
    linkedin_link = result.get('LINKEDIN LINK', None)
    skills = result.get('SKILLS', None)
    certificate = result.get('CERTIFICATION', None)
    worked_as = result.get('WORKED AS', None)

    return jsonify({
        'name': name,
        'linkedin_link': linkedin_link,
        'skills': skills,
        'certificate': certificate,
        'worked_as': worked_as
    })

@app.route("/empSearch",methods=['POST'])
def empSearch():
    if request.method == 'POST':
        category = str(request.form.get('category'))
        print(category)
        
        job_cursor = JOBS.find({"Job_Profile": category}, {"_id": 1})
        job_ids = [job['_id'] for job in job_cursor]
        
        TopEmployeers = Applied_EMP.find({"job_id": {"$in": job_ids}}, {"user_id": 1, "Matching_percentage": 1}).sort([("Matching_percentage", -1)])
        
        if TopEmployeers is None:
            return render_template("CompanyDashboard.html", errorMsg="Problem in Category Fetched")
        
        selectedResumes = []
        
        for emp in TopEmployeers:
            se = IRS_USERS.find_one({"_id": ObjectId(emp['user_id'])}, {"firstName": 1, "Email": 1, "_id": 1})
            if se:
                selectedResumes.append({"Name": se.get('firstName', 'No Name'), 
                                        "Email": se.get('Email', 'No Email'), 
                                        "_id": se.get('_id'), 
                                        "Match": emp.get('Matching_percentage', 0)
                                        })
        
        return render_template("CompanyDashboard.html", data=selectedResumes)

if __name__ == '__main__':
    app.run(debug=True)    

if __name__=="__main__":
    app.run(debug=True)