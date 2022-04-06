import pytest
import docker
import time

from haystack.schema import Document
from haystack.document_stores import ElasticsearchDocumentStore
from scratchpad.database.write_and_update_store import (
    write_docs_and_update_embed,
    write_docs,
)
from scratchpad.retrievers import get_nn_retriever


@pytest.fixture(scope="session", autouse=True)
def test_db():
    # docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.9.2
    client = docker.from_env()
    container = client.containers.run(
        "elasticsearch:7.9.2", detach=True, ports={"9200":"9200"}, environment={"discovery.type": "single-node"} , hostname="test-docker"
    )
    # allow docker some startup time
    time.sleep(30)
    document_store = ElasticsearchDocumentStore(
        host="localhost",
        port=9200,
        username="",
        password="",
        index="document",
        similarity="cosine",
    )
    return container, document_store


@pytest.fixture
def test_db_inputs():
    return [
        Document(
            content="Quod equidem non reprehendo.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quibus natura iure responderit non esse verum aliunde finem beate vivendi, a se principia rei gerendae peti; Quae enim adhuc protulisti, popularia sunt, ego autem a te elegantiora desidero. Duo Reges: constructio interrete. Tum Lucius: Mihi vero ista valde probata sunt, quod item fratri puto. Bestiarum vero nullum iudicium puto. Nihil enim iam habes, quod ad corpus referas; Deinde prima illa, quae in congressu solemus: Quid tu, inquit, huc? Et homini, qui ceteris animantibus plurimum praestat, praecipue a natura nihil datum esse dicemus?",
            meta={"file_name": "sample1.txt"},
        ),
        Document(
            content="Iam id ipsum absurdum, maximum malum neglegi. Quod ea non occurrentia fingunt, vincunt Aristonem; Atqui perspicuum est hominem e corpore animoque constare, cum primae sint animi partes, secundae corporis. Fieri, inquam, Triari, nullo pacto potest, ut non dicas, quid non probes eius, a quo dissentias. Equidem e Cn. An dubium est, quin virtus ita maximam partem optineat in rebus humanis, ut reliquas obruat?",
            meta={"file_name": "sample2.txt"},
        ),
    ]


def test_write_docs(test_db, test_db_inputs):
    _, db = test_db
    write_docs(db, test_db_inputs)
    assert db.get_document_count() == 2
    assert db.get_embedding_count() == 0
    assert sorted([x.content for x in db.get_all_documents()]) == sorted([x.content for x in test_db_inputs])


def test_write_docs_and_update_embed(test_db, test_db_inputs):
    _, db = test_db
    st_retriever = get_nn_retriever(db, "sentence-transformers/all-mpnet-base-v2")
    write_docs_and_update_embed(db, test_db_inputs, st_retriever)
    assert db.get_document_count() == 2
    assert db.get_embedding_count() == 2
    assert sorted([x.content for x in db.get_all_documents()]) == sorted([x.content for x in test_db_inputs])


@pytest.fixture(scope="session", autouse=True)
def cleanup(test_db):
    cnt, _ = test_db
    cnt.kill()
