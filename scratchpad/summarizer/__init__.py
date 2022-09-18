from haystack.nodes import TransformersSummarizer

def get_pegasus_summarizer(model_name_or_path="google/pegasus-xsum"):
    return TransformersSummarizer(model_name_or_path)
