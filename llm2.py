from haystack import Document
from haystack.components.readers import ExtractiveReader

content1 = """Ukrain and Russia are engaged in a war. Russia is currently ahead."""

docs = [
    Document(content=content1),
    # Document(content=content2),
]

reader = ExtractiveReader(model="deepset/tinyroberta-squad2")
reader.warm_up()

# question = "From negative one to positive one, give us a correlation score based on how much the article content impacts oil price movement; positive one being perfect correlation of upward price motion, negative meaning the opposite. \
# GIVE ME A NUMBER BETWEEN -1 AND 1"

question = "Who is winning the war?"

result = reader.run(query=question, documents=docs)

# print(result)

answer = result["answers"][0]
print(answer.data)
