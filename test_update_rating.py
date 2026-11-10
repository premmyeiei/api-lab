import pytest


# Updating stars at the boundaries saves 1 and 5 with 200 and refuses 0 and 6 with 400 without changing the saved rating.
@pytest.mark.parametrize(
    "stars, status",
    [(0, 400), (1, 200), (5, 200), (6, 400)],
)
def test_update_rating_boundaries(api, auth, rating, stars, status):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": stars}, headers=auth)
    assert res.status_code == status
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    expected_stars = stars if status == 200 else rating["stars"]
    assert saved.json()["stars"] == expected_stars

