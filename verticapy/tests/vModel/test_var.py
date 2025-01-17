# (c) Copyright [2018-2022] Micro Focus or one of its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Pytest
import pytest

# Other Modules
import matplotlib.pyplot as plt

# VerticaPy
import verticapy
from verticapy import (
    drop,
    set_option,
    create_verticapy_schema,
)
from verticapy.connect import current_cursor
from verticapy.datasets import load_commodities
from verticapy.learn.tsa import VAR

set_option("print_info", False)


@pytest.fixture(scope="module")
def commodities_vd():
    commodities = load_commodities()
    yield commodities
    drop(name="public.commodities",)


@pytest.fixture(scope="module")
def model(commodities_vd):
    create_verticapy_schema()
    model_class = VAR("var_model_test", p=1)
    model_class.drop()
    model_class.fit("public.commodities", ["gold", "oil"], "date")
    yield model_class
    model_class.drop()


class TestVAR:
    def test_repr(self, model):
        assert "Additional Info" in model.__repr__()
        model_repr = VAR("var_repr")
        model_repr.drop()
        assert model_repr.__repr__() == "<VAR>"

    def test_deploySQL(self, model):
        expected_sql = [
            "1.1120689875238 + 1.01107552114177 * ar0_1 + -0.116704690001029 * ar1_1",
            "0.460229698493364 + 0.000830811806039611 * ar0_1 + 0.977086771447393 * ar1_1",
        ]
        result_sql = model.deploySQL()

        assert result_sql == expected_sql

    def test_drop(self):
        model_test = VAR("var_model_test_drop",)
        model_test.drop()
        model_test.fit("public.commodities", ["gold", "oil"], "date")

        current_cursor().execute(
            "SELECT model_name FROM verticapy.models WHERE model_name IN ('var_model_test_drop', '\"var_model_test_drop\"')"
        )
        assert current_cursor().fetchone()[0] in (
            "var_model_test_drop",
            '"var_model_test_drop"',
        )

        model_test.drop()
        current_cursor().execute(
            "SELECT model_name FROM verticapy.models WHERE model_name IN ('var_model_test_drop', '\"var_model_test_drop\"')"
        )
        assert current_cursor().fetchone() is None

    def test_get_attr(self, model):
        m_att = model.get_attr()

        assert m_att["attr_name"] == [
            "coefficients",
        ]

        m_att_details = model.get_attr(attr_name="coefficients")[0]

        assert m_att_details["predictor"] == [
            "Intercept",
            "ar0_1",
            "ar1_1",
        ]
        assert m_att_details["coefficient"][0] == pytest.approx(
            1.1120689875238, abs=1e-6
        )
        assert m_att_details["coefficient"][1] == pytest.approx(
            1.01107552114177, abs=1e-6
        )
        assert m_att_details["coefficient"][2] == pytest.approx(
            -0.116704690001029, abs=1e-6
        )

    def test_features_importance(self, model):
        importance = model.features_importance()
        plt.close("all")
        assert importance["importance"][0] == pytest.approx(99.18203872798854, abs=1e-6)
        assert importance["importance"][1] == pytest.approx(
            0.8179612720114593, abs=1e-6
        )
        assert importance["sign"][0] == 1
        assert importance["sign"][1] == -1

    def test_get_params(self, model):
        assert model.get_params() == {
            "max_iter": 1000,
            "p": 1,
            "solver": "Newton",
            "tol": 0.0001,
        }

    def test_get_plot(self, model):
        result = model.plot(color="r", nlead=10, dynamic=True, nlast=20, X_idx="gold")
        assert len(result.get_default_bbox_extra_artists()) == 18
        plt.close("all")

    def test_get_predicts(self, commodities_vd, model):
        result = model.predict(commodities_vd, name=["predict1", "predict2"], nlead=2,)

        assert result["predict1"].avg() == pytest.approx(727.596870938679, abs=1e-6)

    def test_regression_report(self, model):
        reg_rep = model.regression_report()

        assert reg_rep["index"] == [
            "explained_variance",
            "max_error",
            "median_absolute_error",
            "mean_absolute_error",
            "mean_squared_error",
            "root_mean_squared_error",
            "r2",
            "r2_adj",
            "aic",
            "bic",
        ]
        assert reg_rep["gold"][0] == pytest.approx(-2.98658192995962, abs=1e-6)
        assert reg_rep["gold"][1] == pytest.approx(3826.50124332351, abs=1e-6)
        assert reg_rep["gold"][2] == pytest.approx(845.6287404527, abs=1e-6)
        assert reg_rep["gold"][3] == pytest.approx(1440.72275115243, abs=1e-6)
        assert reg_rep["gold"][4] == pytest.approx(2958003.91618181, abs=1e-6)
        assert reg_rep["gold"][5] == pytest.approx(1719.8848555010334, abs=1e-6)
        assert reg_rep["gold"][6] == pytest.approx(0.995527309986537, abs=1e-6)
        assert reg_rep["gold"][7] == pytest.approx(0.9955056504707334, abs=1e-6)
        assert reg_rep["gold"][8] == pytest.approx(6189.568871325677, abs=1e-6)
        assert reg_rep["gold"][9] == pytest.approx(6201.595312725785, abs=1e-6)

    def test_score(self, model):
        # method = "max"
        assert model.score(method="max")["max"][0] == pytest.approx(
            3826.50124332351, abs=1e-6
        )
        # method = "mae"
        assert model.score(method="mae")["mae"][0] == pytest.approx(
            1440.72275115243, abs=1e-6
        )
        # method = "median"
        assert model.score(method="median")["median"][0] == pytest.approx(
            845.6287404527, abs=1e-6
        )
        # method = "mse"
        assert model.score(method="mse")["mse"][0] == pytest.approx(
            989.90872084164, abs=1e-6
        )
        # method = "rmse"
        assert model.score(method="rmse")["rmse"][0] == pytest.approx(
            31.462814890623502, abs=1e-6
        )
        # method = "r2"
        assert model.score()["r2"][0] == pytest.approx(0.995527309986537, abs=1e-6)
        # method = "r2a"
        assert model.score(method="r2a")["r2a"][0] == pytest.approx(
            0.9955056504707334, abs=1e-6
        )
        # method = "var"
        assert model.score(method="var")["var"][0] == pytest.approx(
            0.995527309986537, abs=1e-6
        )
        # method = "aic"
        assert model.score(method="aic")["aic"][0] == pytest.approx(
            6189.568871325677, abs=1e-6
        )
        # method = "bic"
        assert model.score(method="bic")["bic"][0] == pytest.approx(
            6201.595312725785, abs=1e-6
        )

    def test_set_params(self, model):
        model.set_params({"p": 2})

        assert model.get_params()["p"] == 2

    def test_model_from_vDF(self, commodities_vd):
        model_class = VAR("var_model_test_vdf", p=1)
        model_class.drop()
        model_class.fit(commodities_vd, ["gold", "oil"], "date")

        current_cursor().execute(
            "SELECT model_name FROM verticapy.models WHERE model_name IN ('var_model_test_vdf', '\"var_model_test_vdf\"')"
        )
        assert current_cursor().fetchone()[0] in (
            "var_model_test_vdf",
            '"var_model_test_vdf"',
        )

        model_class.drop()
