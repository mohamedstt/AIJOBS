# APP.py
Imports and Initial Setup: The code imports necessary libraries and modules, sets up Flask, MongoDB, OAuth for Google login, and configurations related to file uploads and MongoDB URI.
Utility Functions: Two functions, allowedExtension and allowedExtensionPdf, are used to validate uploaded files based on their extensions, specifically for resumes.
Flask App Configuration: Flask configuration includes setting up the secret key, enabling insecure transport for OAuth in development, and configuring MongoDB initialization.
Google OAuth Setup: The application sets up OAuth flow with Google, specifying the client secrets file and required scopes.
Flask Routes:
Index and Employee Dashboard: Routes to handle the main page and the employee dashboard, checking session for user details.
Login and Signup: Authentication routes that handle user login and signup processes, including password hashing and handling duplicate key errors with MongoDB.
Logout: Route to clear session and logout a user.
File Upload: A route to handle resume file uploads, file validation, and parsing the resume using the SpaCy model loaded earlier. It processes and stores resume data in MongoDB.
View Details and Employee Search: Routes for displaying specific employee details and searching employees based on job categories, using MongoDB queries to match and sort data.
Error Handling and User Feedback: The application uses flash messages and redirects to provide feedback on user actions, such as invalid credentials or successful data storage.
Running the App: The __main__ block checks if the script is executed as the main program and runs the Flask app in debug mode.

# Matching.py
The code defines a Python function named Matching that is designed to evaluate the compatibility between a job description (JD) and a resume stored in a MongoDB database. This function is part of a Flask application, interacting with user session data and form inputs to perform its operations. Here's a detailed explanation of the code, step by step:

Imports and Global Variables: The code imports necessary modules like spacy, fitz (PyMuPDF), and io for handling file and text processing. It connects to MongoDB collections using mongo.db to fetch data about resumes and job descriptions.
Loading a SpaCy Model: It loads a pre-trained SpaCy model for parsing job descriptions (JDs). The model is expected to recognize relevant entities in the job descriptions.
Function Definition (Matching):
Fetching Job Description: It retrieves a job description from the MongoDB JOBS collection using a job ID provided by the user through a form. The JD is expected to be stored as binary data (FileData).
Reading Job Description: Uses fitz to open and read the PDF data stored in memory (BytesIO object). It concatenates text extracted from each page to form a complete job description text.
Entity Recognition: The job description text is processed by the SpaCy model (jd_model), which identifies entities and categorizes them into different labels like skills, experience, etc. The entities and their labels are stored in dictionaries for further analysis.
Fetching Resume Data: Retrieves specific information such as WORKED AS and YEARS OF EXPERIENCE from the resume data stored in the MongoDB resumeFetchedData collection for the user currently in session.
Parsing Experience: Both job description and resume experience data are processed to convert textual representations of experience into numerical values (years). This involves handling variations like months and combining them into a total year count.
Matching Logic:
Position Match: Compares job positions mentioned in the resume with those required in the job description. If a match is found, it calculates the experience similarity based on how closely the candidate's experience matches the JD requirements.
Skills Match: It uses a function get_search_results to enhance skill descriptions by searching presumably through an external API or database, although this part is hypothetical and depends on the implementation of get_search_results.
Calculating Total Similarity: Weighs different aspects of the match (job position, experience, skills) to calculate an overall similarity score. Each category's contribution to the total score is defined by predefined weights (30% for job position match, 20% for experience match, and 50% for skill match).
Return Value: The function calculates and returns a percentage representing the overall match quality between the resume and the job description.

# MediaWiki 

get_search_results(search_query)
This function searches Wikipedia using a provided query string and returns a summary of the first matching article.

Building the API Request: Constructs a URL to query Wikipedia's API, specifying parameters for action, format, search term, and other options to refine the search process.
Making the API Call: Sends a GET request to the constructed URL and waits for a response.
Processing the Response: Parses the JSON response to extract search results. If there are results, it retrieves the title of the first result.
Retrieving the Summary: Calls get_summary(title) with the title of the first search result to fetch a summary.
Return Value: If a summary is retrieved, it returns the summary. If no relevant articles are found or the summary cannot be retrieved, it returns None.
get_summary(title)
This function fetches a brief extract or summary from a Wikipedia page based on the provided title.

Building the API Request: Constructs a URL to query Wikipedia's API for extracts, specifying the title for which the summary is needed.
Making the API Call: Sends a GET request to the URL and waits for the response.
Processing the Response: Parses the JSON response to extract page data. Iterates over the page results to find the first page extract.
Return Value: Returns the text of the extract if available. If no extract is available, returns None.