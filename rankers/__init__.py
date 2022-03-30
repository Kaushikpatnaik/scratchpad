from haystack.nodes import SentenceTransformersRanker


def get_st_ranker(model_name_or_path):
    return SentenceTransformersRanker(model_name_or_path)
