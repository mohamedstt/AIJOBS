import pytest
from unittest.mock import patch, MagicMock
from Matching import Matching
from flask import Flask

# Setup a fixture for the Flask app
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

# Setup a fixture for mocking MongoDB and other dependencies
@pytest.fixture
def mock_dependencies(app):
    with app.app_context():
        with patch('Matching.mongo.db.JOBS.find_one') as mock_find_one, \
             patch('Matching.mongo.db.resumeFetchedData.find_one') as mock_resume_find_one, \
             patch('Matching.request') as mock_request, \
             patch('Matching.session') as mock_session, \
             patch('Matching.spacy.load') as mock_spacy_load, \
             patch('Matching.fitz.open') as mock_fitz_open, \
             patch('Matching.get_search_results') as mock_get_search_results:

            # Setup mock returns
            mock_find_one.return_value = {"_id": "123", "FileData": b"dummy", "WeightJD": 30, "WeightExperience": 20, "WeightSkills": 50}
            mock_resume_find_one.side_effect = [
                {"WORKED AS": ["Developer"]},  # First call for WORKED AS
                {"YEARS OF EXPERIENCE": ["5 years"]},  # Second call for YEARS OF EXPERIENCE
                {"SKILLS": ["Python"]}  # Third call for SKILLS
            ]
            mock_request.form = {'job_id': '123'}
            mock_session.return_value = {'user_id': 'user123'}
            mock_spacy_load.return_value = MagicMock(ents=[MagicMock(text="Python", label_="SKILLS")])
            mock_fitz_open.return_value.__enter__.return_value = MagicMock(get_text=lambda: "Python Developer")
            mock_get_search_results.return_value = "Python"

            yield

# Test valid input and expect the function to return a similarity percentage
def test_matching_valid_input(mock_dependencies):
    response = Matching()  # Assuming this is how you've structured your Matching function to return response
    assert response == 100, "Should return correct matching percentage for valid input"

# More tests can be added here to handle different scenarios
