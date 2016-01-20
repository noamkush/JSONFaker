import JSONFaker
import faker
import json
import sys

fake = faker.Faker()
fake.add_provider(JSONFaker.JSONProvider)

print json.dumps(fake.json(json.load(open(sys.argv[1]))))