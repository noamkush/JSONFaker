import faker
import faker.providers
import json
import jsonschema
import random
import copy
import collections
import unittest
import os

import rstr


class JSONProvider(faker.providers.BaseProvider):
    @staticmethod
    def _find_refeence_in_schema(path, schema):
        path_elements = path.split("/")
        if path.startswith("#"):
            path_elements = path_elements[1:]

        cschema = schema[path_elements[0]]
        if len(path_elements) == 1:
            return cschema
        else:
            return JSONProvider._find_refeence_in_schema("/".join(path_elements[1:]), cschema)

    @staticmethod
    def value_for_schema_element(schema_element, root_schema_element, fake=faker.Faker(), overrides=dict()):

        if "oneOf" in schema_element.keys():
            se = random.choice(schema_element["oneOf"])
            print "ONE OF"
            print se
        elif "allOf" in schema_element.keys():
            se = dict()
            for rs in schema_element['allOf']:
                se.update(rs)
        elif "anyOf" in schema_element.keys():
            se = collections.defaultdict(list)

            for d in (schema_element["anyOf"]):
                for key, value in d.iteritems():
                    se[key].append(value)
        else:
            se = copy.copy(schema_element)

        if "$ref" in se.keys():
            se = JSONProvider._find_refeence_in_schema(se['$ref'], root_schema_element)
        if "type" not in se.keys():
            element_type = "string"
        elif type(se['type']) == list:
            element_type = random.choice(se['type'])
        else:
            element_type = se["type"]

        if element_type == 'null':
            return None
        elif element_type == 'string':
            if se.get('pattern', None) is not None:
                return rstr.xeger(se['pattern'])
            elif se.get('enum', None) is not None:
                return random.choice(se['enum'])
            else:
                return fake.password(length=30, special_chars=True, digits=True, upper_case=True, lower_case=True)

        elif element_type == 'number':
            return round(random.uniform(se.get('minimum', -100000000), se.get('maximum', 10000000)),
                         random.randint(0, 5))

        elif element_type == 'integer':
            n = random.randint(se.get('minimum', 0), se.get('maximum', 10000000))
            return n - (n % se.get('multipleOf', 1))

        elif element_type == 'boolean':
            return fake.boolean(chance_of_getting_true=50)

        elif element_type == 'array':
            array_value = list()
            for _ in range(0, random.randint(0, random.randint(se.get('minItems', 3), se.get('maxItems', 100)))):
                array_value.append(JSONProvider.value_for_schema_element(se.get('items',
                                                                                {"type": random.choice(
                                                                                    ["string", "boolean", "number",
                                                                                     "integer"])}),
                                                                         root_schema_element,
                                                                         fake,
                                                                         overrides))
            # P TODO need to support 'unique items'
            return array_value

        elif element_type == 'object':
            object_value = dict()
            for k, v in se.get('properties', {}).items():
                if k in overrides.keys():
                    object_value[k] = overrides[k]()
                else:
                    object_value[k] = JSONProvider.value_for_schema_element(v,
                                                                            root_schema_element,
                                                                            fake,
                                                                            overrides)
            return object_value

        else:
            print type(se['type'])
            raise ValueError("Don't know have to create value for schema element type [{}]".format(se['type']))

    def json(self, json_schema):
        return self.value_for_schema_element(json_schema, json_schema)


class JSONProviderUnitTest(unittest.TestCase):
    def test_example_schemas(self):
        fake = faker.Faker()
        fake.add_provider(JSONProvider)

        schmeapath = os.getcwd() + os.sep + "exmple_schemas" + os.sep
        schema_files = [os.path.join(schmeapath, f) for f in os.listdir(schmeapath) if
                        os.path.isfile(os.path.join(schmeapath, f))]
        print schema_files
        for schema_file in schema_files:
            try:
                schema = json.load(open(schema_file))
                jsonschema.validate(fake.json(schema), schema)
            except Exception as e:
                self.fail("File <{}> failed with exception <{}>".format(schema_file, e))


if __name__ == "__main__":
    unittest.main()
