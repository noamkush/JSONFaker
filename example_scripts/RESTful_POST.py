import JSONFaker
import requests
import faker
import sys
import json

fake = faker.Faker()
fake.add_provider(JSONFaker.JSONProvider)

response = requests.post(sys.argv[1],
                         data=fake.json(json.load(open(sys.argv[2]))))
assert(response.status_code == 200), "Error: Response code was {}".format(response.status_code)
sys.exit(0)