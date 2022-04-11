import math

from dotenv import load_dotenv

load_dotenv(".env")

from google.cloud import language_v1


def analyze_entity_sentiment(comment):
    text_content = comment.name
    upvotes = comment.score

    client = language_v1.LanguageServiceClient()

    # text_content = 'Grapes are good. Bananas are bad.'

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.types.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entity_sentiment(request={'document': document, 'encoding_type': encoding_type})

    results = []
    # Loop through entities returned from the API
    for entity in response.entities:
        result = {}
        print(u"Representative name for the entity: {}".format(entity.name))
        result['name'] = entity.name
        # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al
        print(u"Entity type: {}".format(language_v1.Entity.Type(entity.type_).name))
        result['type'] = language_v1.Entity.Type(entity.type_).name
        # Get the salience score associated with the entity in the [0, 1.0] range
        print(u"Salience score: {}".format(entity.salience))
        result['salience'] = entity.salience
        # Get the aggregate sentiment expressed for this entity in the provided document.
        sentiment = entity.sentiment
        print(u"Entity sentiment score: {}".format(sentiment.score))
        print(u"Entity sentiment magnitude: {}".format(sentiment.magnitude))
        result['sentiment'] = sentiment.score
        result['magnitude'] = sentiment.magnitude

        weighted_salience = 1 / (1 - math.log10(entity.salience))
        if sentiment.score >= 0:
            result['score'] = upvotes * weighted_salience * (1 + sentiment.score * sentiment.magnitude * 10)
        else:
            result['score'] = upvotes * weighted_salience * (-1 + sentiment.score * sentiment.magnitude * 10)
        # Loop over the metadata associated with entity. For many known entities,
        # the metadata is a Wikipedia URL (wikipedia_url) and Knowledge Graph MID (mid).
        # Some entity types may have additional metadata, e.g. ADDRESS entities
        # may have metadata for the address street_name, postal_code, et al.
        metadata = {}
        for metadata_name, metadata_value in entity.metadata.items():
            print(u"{} = {}".format(metadata_name, metadata_value))
            metadata[metadata_name] = metadata_value
        result['metadata'] = metadata

        # Loop over the mentions of this entity in the input document.
        # The API currently supports proper noun mentions.
        mentions = []
        for mention in entity.mentions:
            mention_dict = {}
            print(u"Mention text: {}".format(mention.text.content))
            mention_dict['text'] = mention.text.content
            # Get the mention type, e.g. PROPER for proper noun
            print(
                u"Mention type: {}".format(language_v1.EntityMention.Type(mention.type_).name)
            )
            mention_dict['type'] = language_v1.EntityMention.Type(mention.type_).name
            mentions.append(mention_dict)
        result['mentions'] = mentions
        result['comments'] = [comment]
        results.append(result)

    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
    print(u"Language of the text: {}".format(response.language))

#
# if __name__ == "__main__":
#     text_content = "Grapes are good. Bananas are bad."
#     analyze_entity_sentiment(text_content)
