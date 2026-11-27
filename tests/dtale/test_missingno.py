import pandas as pd
import pytest
import sys
import mock

from dtale.app import build_app
from tests.dtale.test_views import URL
from tests.dtale import build_data_inst


@pytest.mark.parametrize(
    "freq, modern",
    [
        ("B", "B"), ("C", "C"), ("D", "D"), ("W", "W"), ("M", "ME"),
        ("SM", "SME"), ("BM", "BME"), ("CBM", "CBME"), ("MS", "MS"),
        ("SMS", "SMS"), ("BMS", "BMS"), ("CBMS", "CBMS"), ("Q", "QE"),
        ("BQ", "BQE"), ("QS", "QS"), ("BQS", "BQS"), ("Y", "YE"),
        ("BY", "BYE"), ("YS", "YS"), ("BYS", "BYS"), ("BH", "bh"),
        ("H", "h"), ("T", "min"), ("S", "s"), ("L", "ms"), ("U", "us"),
        ("N", "ns"),
    ],
)
def test_matrix_frequency_options(freq, modern):
    import dtale.views as views

    df = pd.DataFrame({"date": pd.to_datetime(["2020-01-01", "2020-01-02"]), "a": [1, 2]})
    with build_app(url=URL).test_client() as c:
        build_data_inst({c.port: df})
        with mock.patch.object(views.msno, "matrix", side_effect=ValueError("test")) as matrix:
            c.get(
                "/dtale/missingno/matrix/{}".format(c.port),
                query_string={"date_index": "date", "freq": freq},
            )
        actual = matrix.call_args[1]["freq"]
        assert actual == (modern if views.pandas_util.check_pandas_version("2.2.0") else freq)
        pd.tseries.frequencies.to_offset(actual)


@pytest.mark.parametrize("freq", ["BQ", "CBM"])
def test_matrix_legacy_frequency_on_old_pandas(freq):
    import dtale.views as views

    df = pd.DataFrame({"date": pd.to_datetime(["2020-01-01", "2020-01-02"]), "a": [1, 2]})
    with build_app(url=URL).test_client() as c:
        build_data_inst({c.port: df})
        with mock.patch.object(views.pandas_util, "check_pandas_version", return_value=False):
            with mock.patch.object(views.msno, "matrix", side_effect=ValueError("test")) as matrix:
                c.get(
                    "/dtale/missingno/matrix/{}".format(c.port),
                    query_string={"date_index": "date", "freq": freq},
                )
        assert matrix.call_args[1]["freq"] == freq


@pytest.mark.parametrize("freq", ["BQ", "CBM", "D"])
def test_matrix_with_date_frequency(freq):
    import matplotlib.pyplot as plt

    df = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=400), "a": range(400)})
    existing_figures = set(plt.get_fignums())
    try:
        with build_app(url=URL).test_client() as c:
            build_data_inst({c.port: df})
            resp = c.get(
                "/dtale/missingno/matrix/{}".format(c.port),
                query_string={"date_index": "date", "freq": freq},
            )
            assert resp.status_code == 200
            assert resp.content_type == "image/png"
            assert resp.data.startswith(b"\x89PNG\r\n\x1a\n")
    finally:
        for number in set(plt.get_fignums()) - existing_figures:
            plt.close(number)


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="requires python 3.9 or lower")
def test_matrix():
    import dtale.views as views

    df, _ = views.format_data(pd.DataFrame(dict(a=[1, 2, 3, 4, 5, 6])))
    with build_app(url=URL).test_client() as c:
        build_data_inst({c.port: df})

        resp = c.get("/dtale/missingno/matrix/{}".format(c.port))
        assert resp.content_type == "image/png"


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="requires python 3.9 or lower")
def test_bar():
    import dtale.views as views

    df, _ = views.format_data(pd.DataFrame(dict(a=[1, 2, 3, 4, 5, 6])))
    with build_app(url=URL).test_client() as c:
        build_data_inst({c.port: df})

        resp = c.get("/dtale/missingno/bar/{}".format(c.port))
        assert resp.content_type == "image/png"


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="requires python 3.9 or lower")
def test_heatmap():
    import dtale.views as views

    df, _ = views.format_data(pd.DataFrame(dict(a=[1, 2, 3, 4, 5, 6])))
    with build_app(url=URL).test_client() as c:
        build_data_inst({c.port: df})

        resp = c.get("/dtale/missingno/heatmap/{}".format(c.port))
        assert resp.content_type == "image/png"


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="requires python 3.9 or lower")
def test_dendrogram(rolling_data):
    import dtale.views as views

    df, _ = views.format_data(rolling_data)
    with build_app(url=URL).test_client() as c:
        build_data_inst({c.port: df})

        resp = c.get("/dtale/missingno/dendrogram/{}".format(c.port))
        assert resp.content_type == "image/png"
