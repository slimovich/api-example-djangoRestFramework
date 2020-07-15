from rest_framework.views import APIView
from rest_framework.response import Response
from src.api.models.towns import Towns

PREDICATE_MAPPING = {'equal': '=',
                      'gt' : '>',
                      'lt' : '<',
                      'contains' : 'LIKE'}
PREDICATE_FIELD_TYPE = {str: ['LIKE', '='],
                      int : ['=', '>', '<'],
                      float : ['=', '>', '<']}
FIELD_TYPE = { 'name': str ,
               'code': int ,
               'population': int ,
               'average_age': float ,
               'distr_code': int ,
               'dept_code': int ,
               'region_name': str ,
               'region_code': int}

class BuildQueryEndPoint(APIView):
    """
    -------------------------------------------------------------
    | {"fields": ["name", "population"]}            | SELECT name, population FROM towns
    ------------------------------------------------------------
    | {                                             |
    |     "fields": ["name"],                       | SELECT name 
    |     "filters": {                              | FROM towns
    |            "field": "distr_code", "value": 1  | WHERE distr_code = 1
    |     }                                         |
    | }                                             |
    -------------------------------------------------------------------
    | {                                             |
    |     “fields”: [“name”],                       |  SELECT name
    |     “filters”: {                              |  FROM towns
    |          “field”: “population”,               |  WHERE population > 10000   
    |          “value”: 10000,                      |
    |          “predicate”: “gt”                    |
    |     }                                         |
    | }                                             |
    ------------------------------------------------------------------------                                      
    | {
    |   “fields”: [“name”],
    |   “filters”: {“and”: 
    |           [{
    |           “field”: “population”, 
    |           “value”: 10000, 
    |           “predicate”: “gt”}, 
    |           {
    |               “field”: “region_name”, 
    |               “value”: “Hauts-de”, 
    |               “predicate”: “contains”
    |           }]
    | }                                      
    ---------------------------------------------------------

    """

    def post(self, request):
        """Convert json to sql"""
        # input data as json
        data = request.data

        # create the specific querySet according to the fields and filters mentionned in the data
        queryset = self.jsonToSql(data)

        return Response(queryset)

    def validateFieldsSelection(self, fields):
        """ validate the existance of the fields
            :param fields: list
            :rtype boolean
        """
        if len(fields) == 0:
            return False

        for field in fields:
            if field not in FIELD_TYPE.keys():
                return False

        return True

    def check_field_existance(self, field, value):
        """ validate the field existance and his type
            :param field: string
            :param value: string or integer
            :rtype boolean
        """
        if field in FIELD_TYPE.keys():
            return True
        return False

    def check_field_type(self, field, value):
        """ validate the field existance and his type
            :param field: string
            :param value: string or integer
            :rtype boolean
        """
        if type(value) == FIELD_TYPE[field]:
            return True
        return False

    def validatePredicate(self, predicate):
        """ validate predicate existance
            :param predicate: string
            :rtype None or string
        """
        if predicate in PREDICATE_MAPPING.keys():
            return PREDICATE_MAPPING[predicate]
        return None

    def generateCompoundFilter(self, filters, joiner=None):
        """ generate recusivly the filters part
            :param filters: dict
            :rtype string
        """
        result = ""
        conditions = []
        self.resultError = {}
        for key in filters:
            if type(key) != dict and not self.resultError:
                if (type(filters[key]) == list or type(filters[key]) == dict):
                    if key == "and":
                        result = self.generateCompoundFilter(filters[key], " AND ")
                        conditions.append(result)
                    elif key == "or":
                        result = self.generateCompoundFilter(filters[key], " OR ")
                        conditions.append(result)
            elif type(key) == dict and 'field' not in key.keys():
                result = self.generateCompoundFilter(key)
                conditions.append(result)
            # don't append query if there is errors
            elif not self.resultError:
                field = key['field']
                value = key['value']
                predicate = self.validatePredicate(key['predicate'])

                # check 'predicate' validation
                if not predicate:
                    self.resultError[
                        'error message'] = 'Please verify that the condition is in %s' % PREDICATE_MAPPING.keys()
                    break
                # check 'field' and 'value' validation
                if self.check_field_existance(field, value):
                    # check the right format of the conditions
                    # for where exemple WHERE field LIKE value => value should be a string
                    if type(value) in PREDICATE_FIELD_TYPE.keys() and predicate in PREDICATE_FIELD_TYPE[type(value)]:
                        if predicate == 'LIKE':
                            value = '%{0}%'.format(value)
                            queryCondition = "{0} {1} {2}".format(field, predicate, value)
                        else:
                            queryCondition = "{0} {1} {2}".format(field, predicate, value)
                    else:
                        self.resultError['error message'] = 'Please verify the condition is valid'
                        break
                else:
                    self.resultError[
                        'error message'] = 'Please verify the field => \'%s\' type or his existance' % field
                    break
                conditions.append(queryCondition)

        # check for errors
        if self.resultError:
            return self.resultError

        if len(conditions) > 1:
            return '(' + joiner.join(conditions) + ')'
        if len(conditions) == 1:
            return conditions[0]

    def jsonToSql(self, data):
        """ validate the  right format of the json data and finally generate the query
            :param predicate: dict
            :rtype String or dict
        """

        # list of first keys in the json data
        keys = data.keys()
        # retured result for errors
        result = {}
        # returned generated query
        queryset = None

        # select only fields
        # check if 'fields' existe as keys in data dict
        if 'fields' in keys and 'filters' not in keys:
            if self.validateFieldsSelection(data['fields']):
                queryset = "SELECT {0} FROM towns".format(','.join(data['fields']))
            else:
                result['error message'] = 'Please verify that the fields selected exist'
                return result

        # check if 'fields' and 'filters' existe as keys in data dict
        elif 'fields' in keys and 'filters' in keys:
            if not self.validateFieldsSelection(data['fields']):
                result['error message'] = 'Please verify that the fields selected exist'
                return result

            # simple filter without predicate
            # check if 'fields', 'value' existe as keys in data dict
            if 'predicate' not in data['filters'].keys() and 'field' in data['filters'].keys() and 'value' in data['filters'].keys():
                field = data['filters']['field']
                value = data['filters']['value']
                if self.check_field_existance(field, value):
                    queryset = "SELECT {0} FROM towns WHERE {1} = {2}".format(','.join(data['fields']), field, value)
                else:
                    result['error message'] = 'Please verify the type of the field = %s or his existance' % field
                    return result

            # compound filters
            elif 'and' in data['filters'].keys() or 'or' in data['filters'].keys():
                result_filters = self.generateCompoundFilter(data['filters'])
                if type(result_filters) == dict:
                    return result_filters

                # try to remove surplus of parenthesis
                conditions = result_filters[1:len(result_filters) - 1]
                queryset = "SELECT {0} FROM towns WHERE {1}".format(','.join(data['fields']), conditions)

            # simple filter with predicate
            # check if 'feild', 'value' and 'predicate' existe as keys in data dict
            elif 'predicate' in data['filters'].keys() and 'field' in data['filters'].keys() and 'value' in data['filters'].keys():
                field = data['filters']['field']
                value = data['filters']['value']
                predicate = self.validatePredicate(data['filters']['predicate'])

                # check 'predicate' validation
                if not predicate:
                    result['error message'] = 'Please verify that the condition is in %s' % PREDICATE_MAPPING.keys()
                    return result
                # check 'field' and 'value' validation
                if self.check_field_existance(field, value):
                    # check the right format of the conditions
                    # for where exemple WHERE field LIKE value => value should be a string
                    if type(value) in PREDICATE_FIELD_TYPE.keys() and predicate in PREDICATE_FIELD_TYPE[type(value)]:
                        if predicate == 'LIKE':
                            value = '%{0}%'.format(value)
                            queryset = "SELECT {0} FROM towns WHERE {1} {2} '{3}'".format(','.join(data['fields']), field, predicate, value)
                        else:
                            queryset = "SELECT {0} FROM towns WHERE {1} {2} {3}".format(','.join(data['fields']), field, predicate, value)
                    else:
                        result['error message'] = 'Please verify the condition is valid'
                        return result
                else:
                    result['error message'] = 'Please verify the field => \'%s\' type or his existance' % field
                    return result

            else:
                result['error message'] = 'Please verify the keys of the filters dict'
                return result
        else:
            result['error message'] = 'Please verify the keys of dict'
            return result
        return queryset