from unittest import TestCase
from src.api.endpoints.buildQuery import BuildQueryEndPoint


PREDICATE_MAPPING = {'equal': '=',
                      'gt' : '>',
                      'lt' : '<',
                      'contains' : 'LIKE'}
FIELD_TYPE = { 'name': str ,
               'code': int ,
               'population': int ,
               'average_age': float ,
               'distr_code': int ,
               'dept_code': int ,
               'region_name': str ,
               'region_code': int}

class ApiTest(TestCase):
    def setUp(self):
        # Every test needs access to the BuildQueryEndPoint.
        self.bqe = BuildQueryEndPoint()

    def testValidateFieldsSelection(self):

        fields = ["name", "population"]
        assert self.bqe.validateFieldsSelection(fields) == True

        fields = ["name", "populatio"]
        assert self.bqe.validateFieldsSelection(fields) == False

        fields = ["nam", "populatio"]
        assert self.bqe.validateFieldsSelection(fields) == False

        fields = []
        assert self.bqe.validateFieldsSelection(fields) == False

        fields = [""]
        assert self.bqe.validateFieldsSelection(fields) == False

    def test_check_field_existance(self):

        assert self.bqe.check_field_type("name", 1) == False

        assert self.bqe.check_field_type("name", "test") == True

        assert self.bqe.check_field_type("name", None) == False

        assert self.bqe.check_field_type("region_code", 1) == True

    def testValidatePredicate(self):

        assert self.bqe.validatePredicate("name") == None

        assert self.bqe.validatePredicate("equal") == "="

        assert self.bqe.validatePredicate(1) == None

        assert self.bqe.validatePredicate("gt") == ">"

    def testGenerateCompoundFilter(self):
        filters = {"and": [{"field": "population", "value": 1000, "predicate": "gt"},
                                   {"field": "region_name", "value": "Hauts-de", "predicate": "contains"}]}
        result = "(population > 1000 AND region_name LIKE %Hauts-de%)"
        assert self.bqe.generateCompoundFilter(filters) == result

        filters = {"and": [{"or": [{"field": "population", "value": 50, "predicate": "gt"},
                                   {"field": "region_name", "value": "Hauts-de", "predicate": "contains"}]}, {
                               "or": [{"field": "population", "value": 1000, "predicate": "gt"},
                                      {"field": "region_name", "value": "Grand-Est", "predicate": "contains"}]}]}

        result = "((population > 50 OR region_name LIKE %Hauts-de%) AND (population > 1000 OR region_name LIKE %Grand-Est%))"
        assert self.bqe.generateCompoundFilter(filters) == result
