import os
import pgml
import pytest
from multiprocessing import Pool
from typing import List, Dict, Any
import asyncio

####################################################################################
####################################################################################
## PLEASE BE AWARE THESE TESTS DO INVOLVE CHECKS ON LAZILY CREATED DATABASE ITEMS ##
## IF ANY OF THE COLLECTION NAMES ALREADY EXIST, SOME TESTS MAY FAIL              ##
## THIS DOES NOT MEAN THE SDK IS BROKEN. PLEASE CLEAR YOUR DATABASE INSTANCE      ##
## BEFORE RUNNING ANY TESTS                                                       ##
####################################################################################
####################################################################################

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL is None:
    print("No DATABASE_URL environment variable found. Please set one")
    exit(1)

pgml.py_init_logger()


def generate_dummy_documents(count: int) -> List[Dict[str, Any]]:
    dummy_documents = []
    for i in range(count):
        dummy_documents.append(
            {
                "id": i,
                "text": "This is a test document: {}".format(i),
                "some_random_thing": "This will be metadata on it",
                "metadata": {"uuid": i * 10, "name": "Test Document {}".format(i)},
            }
        )
    return dummy_documents


###################################################
## Test the API exposed is correct ################
###################################################


def test_can_create_collection():
    collection = pgml.Collection(name="test_p_c_tscc_0")
    assert collection is not None


def test_can_create_model():
    model = pgml.Model()
    assert model is not None


def test_can_create_splitter():
    splitter = pgml.Splitter()
    assert splitter is not None


def test_can_create_pipeline():
    model = pgml.Model()
    splitter = pgml.Splitter()
    pipeline = pgml.Pipeline("test_p_p_tccp_0", model, splitter)
    assert pipeline is not None


def test_can_create_builtins():
    builtins = pgml.Builtins()
    assert builtins is not None


###################################################
## Test various vector searches ###################
###################################################


@pytest.mark.asyncio
async def test_can_vector_search_with_local_embeddings():
    model = pgml.Model()
    splitter = pgml.Splitter()
    pipeline = pgml.Pipeline("test_p_p_tcvs_0", model, splitter)
    collection = pgml.Collection(name="test_p_c_tcvs_4")
    await collection.upsert_documents(generate_dummy_documents(3))
    await collection.add_pipeline(pipeline)
    results = await collection.vector_search("Here is some query", pipeline)
    assert len(results) == 3
    await collection.archive()


@pytest.mark.asyncio
async def test_can_vector_search_with_remote_embeddings():
    model = pgml.Model(name="text-embedding-ada-002", source="openai")
    splitter = pgml.Splitter()
    pipeline = pgml.Pipeline("test_p_p_tcvswre_0", model, splitter)
    collection = pgml.Collection(name="test_p_c_tcvswre_3")
    await collection.upsert_documents(generate_dummy_documents(3))
    await collection.add_pipeline(pipeline)
    results = await collection.vector_search("Here is some query", pipeline)
    assert len(results) == 3
    await collection.archive()


@pytest.mark.asyncio
async def test_can_vector_search_with_query_builder():
    model = pgml.Model()
    splitter = pgml.Splitter()
    pipeline = pgml.Pipeline("test_p_p_tcvswqb_1", model, splitter)
    collection = pgml.Collection(name="test_p_c_tcvswqb_5")
    await collection.upsert_documents(generate_dummy_documents(3))
    await collection.add_pipeline(pipeline)
    results = (
        await collection.query()
        .vector_recall("Here is some query", pipeline)
        .limit(10)
        .fetch_all()
    )
    assert len(results) == 3
    await collection.archive()


@pytest.mark.asyncio
async def test_can_vector_search_with_query_builder_with_remote_embeddings():
    model = pgml.Model(name="text-embedding-ada-002", source="openai")
    splitter = pgml.Splitter()
    pipeline = pgml.Pipeline("test_p_p_tcvswqbwre_1", model, splitter)
    collection = pgml.Collection(name="test_p_c_tcvswqbwre_1")
    await collection.upsert_documents(generate_dummy_documents(3))
    await collection.add_pipeline(pipeline)
    results = (
        await collection.query()
        .vector_recall("Here is some query", pipeline)
        .limit(10)
        .fetch_all()
    )
    assert len(results) == 3
    await collection.archive()


###################################################
## Test user output facing functions ##############
###################################################


@pytest.mark.asyncio
async def test_pipeline_to_dict():
    model = pgml.Model(name="text-embedding-ada-002", source="openai")
    splitter = pgml.Splitter()
    pipeline = pgml.Pipeline("test_p_p_tptd_1", model, splitter)
    collection = pgml.Collection(name="test_p_c_tptd_1")
    await collection.add_pipeline(pipeline)
    pipeline_dict = await pipeline.to_dict()
    assert pipeline_dict["name"] == "test_p_p_tptd_1"
    await collection.remove_pipeline(pipeline)
    await collection.archive()


###################################################
## Test with multiprocessing ######################
###################################################


def vector_search(collection_name, pipeline_name):
    collection = pgml.Collection(collection_name)
    pipeline = pgml.Pipeline(pipeline_name)
    result = asyncio.run(
        collection.query()
        .vector_recall("Here is some query", pipeline)
        .limit(10)
        .fetch_all()
    )
    print(result)
    return [0, 1, 2]


# @pytest.mark.asyncio
# async def test_multiprocessing():
#     collection_name = "test_p_p_tm_1"
#     pipeline_name = "test_p_c_tm_4"
#
#     model = pgml.Model()
#     splitter = pgml.Splitter()
#     pipeline = pgml.Pipeline(pipeline_name, model, splitter)
#
#     collection = pgml.Collection(collection_name)
#     await collection.upsert_documents(generate_dummy_documents(3))
#     await collection.add_pipeline(pipeline)
#
#     with Pool(5) as p:
#         results = p.starmap(
#             vector_search, [(collection_name, pipeline_name) for _ in range(5)]
#         )
#         for x in results:
#             print(x)
#             assert len(x) == 3
#
#     await collection.archive()


###################################################
## Manual tests ###################################
###################################################


async def silas_test_add_pipeline():
    model = pgml.Model()
    splitter = pgml.Splitter()
    pipeline = pgml.Pipeline("silas_test_p_1", model, splitter)
    collection = pgml.Collection(name="silas_test_c_10")
    await collection.add_pipeline(pipeline)

async def silas_test_upsert_documents():
    collection = pgml.Collection(name="silas_test_c_9")
    await collection.upsert_documents(generate_dummy_documents(10))

async def silas_test_vector_search():
    pipeline = pgml.Pipeline("silas_test_p_1")
    collection = pgml.Collection(name="silas_test_c_9")
    results = await collection.vector_search("Here is some query", pipeline)
    print(results)

# asyncio.run(silas_test_add_pipeline())
# asyncio.run(silas_test_upsert_documents())
# asyncio.run(silas_test_vector_search())
