import pytest

from pymongo import Connection


@pytest.fixture
def db(request):
    c = Connection()
    testDb = c.calibration_test

    def end():
        print("Closing database connection...")
        db.close()
        c.close()

    request.addfinalizer(end)
    return testDb


def test_using_mongo_to_store_data(db):

    db.trials.insert({'woof': 'woof'})
    documents = db.trials.find_one()

    assert "woof" in documents