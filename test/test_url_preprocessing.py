import pytest

from scratchpad.preprocessing.website_converter import scrape_website_to_dict
from scratchpad.preprocessing.pre_processing import preprocess_add_websites


@pytest.fixture
def test_urls():
    return [
        "https://www.forbes.com/sites/robtoews/2022/03/27/a-wave-of-billion-dollar-language-ai-startups-is-coming/?utm_source=pocket_mylist&sh=63f8bc7f2b14",
        "https://foxhillkitchens.com/are-seed-oils-bad-for-you/?utm_source=pocket_mylist",
        "https://userpilot.com/blog/build-minimum-lovable-mlp-product/?utm_source=pocket_mylist",
        "https://future.a16z.com/data50/?utm_source=pocket_mylist",
        "https://www.mindtheproduct.com/the-product-market-fit-engine-by-rahul-vohra/",
    ]


def test_scrape_website_to_dict(urls):
    generated_docs = scrape_website_to_dict(urls)
    assert len(generated_docs) == 4
    expected_filenames = urls
    generated_docs_filenames = list(
        set([x["meta"]["file_name"] for x in generated_docs])
    )
    assert sorted(expected_filenames) == sorted(generated_docs_filenames)


def test_preprocess_add_websites(urls):
    processed_docs = preprocess_add_websites(urls)
    assert len(processed_docs) > 4
    expected_filenames = urls
    processed_filenames = list(set([x["meta"]["file_name"] for x in processed_docs]))
    assert sorted(expected_filenames) == sorted(processed_filenames)
