import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from Matching import Matching  # Assegure-se que o módulo Matching está corretamente importado.

class TestMatchingFunction(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Simulação das dependências externas
        self.patcher1 = patch('app.mongo')  # Certifique-se que 'app' é o arquivo correto onde mongo é usado.
        self.patcher2 = patch('app.request')  # Assegure-se que está patcheando o uso de request dentro do app.
        self.patcher3 = patch('requests.get')  # Perfeito para simular respostas de API externas.
        
        self.mock_mongo = self.patcher1.start()
        self.mock_request = self.patcher2.start()
        self.mock_requests_get = self.patcher3.start()  # Mudança de nome para melhor clareza.

        # Configuração dos mocks para MongoDB
        self.mock_mongo.db.JOBS.find_one.return_value = {"_id": "123", "WeightJD": 30, "WeightExperience": 20, "WeightSkills": 50}
        self.mock_mongo.db.resumeFetchedData.find_one.side_effect = [
            {"WORKED AS": ["Engineer", "Developer"]},
            {"YEARS OF EXPERIENCE": ["5 years", "2 years"]},
            {"SKILLS": ["Python", "JavaScript"]}
        ]
        
        # Configuração do mock para request.form
        self.mock_request.form = MagicMock()
        self.mock_request.form.get.return_value = '123'  # Ajuste para simular o form.get corretamente.
        
        # Configuração do mock para get_search_results
        self.mock_requests_get.return_value = MagicMock()
        self.mock_requests_get.return_value.json.return_value = ["Technology Article"]

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()

    def test_matching_score(self):
        with self.app.app_context():
            score = Matching()  # Assegure-se que os argumentos necessários para Matching() estão sendo passados, se houver.
            # Ajuste esses valores esperados conforme determinado
            self.assertIsInstance(score, float)
            self.assertTrue(0 <= score <= 100)

    def test_no_skills_match(self):
        # Modificar o mock para testar cenário de não correspondência de habilidades
        self.mock_requests_get.return_value.json.return_value = []  # Simulação de uma lista vazia para testar a ausência de correspondência.
        with self.app.app_context():
            score = Matching()
            self.assertTrue(score < 100)  # Espera-se uma pontuação menor devido à não correspondência de habilidades

if __name__ == '__main__':
    unittest.main()
