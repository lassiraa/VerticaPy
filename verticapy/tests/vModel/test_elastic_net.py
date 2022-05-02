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

# Standard Python Modules
import warnings

# Other Modules
import matplotlib.pyplot as plt

# VerticaPy
from verticapy import drop, set_option
from verticapy.connect import current_cursor
from verticapy.datasets import load_winequality
from verticapy.learn.linear_model import ElasticNet

set_option("print_info", False)


@pytest.fixture(scope="module")
def winequality_vd():
    winequality = load_winequality()
    yield winequality
    drop(name="public.winequality",)


@pytest.fixture(scope="module")
def model(winequality_vd):
    model_class = ElasticNet("elasticnet_model_test",)
    model_class.drop()
    model_class.fit(
        "public.winequality",
        ["total_sulfur_dioxide", "residual_sugar", "alcohol"],
        "quality",
    )
    yield model_class
    model_class.drop()


class TestElasticNet:
    def test_repr(self, model):
        assert "|coefficient|std_err |t_value |p_value" in model.__repr__()
        model_repr = ElasticNet("lin_repr")
        model_repr.drop()
        assert model_repr.__repr__() == "<LinearRegression>"

    def test_contour(self, winequality_vd):
        model_test = ElasticNet("model_contour",)
        model_test.drop()
        model_test.fit(
            winequality_vd, ["residual_sugar", "alcohol"], "quality",
        )
        with warnings.catch_warnings(record=True) as w:
            result = model_test.contour()
        assert len(result.get_default_bbox_extra_artists()) == 10
        model_test.drop()

    def test_deploySQL(self, model):
        expected_sql = 'PREDICT_LINEAR_REG("total_sulfur_dioxide", "residual_sugar", "alcohol" USING PARAMETERS model_name = \'elasticnet_model_test\', match_by_pos = \'true\')'
        result_sql = model.deploySQL()

        assert result_sql == expected_sql

    def test_drop(self):
        current_cursor().execute("DROP MODEL IF EXISTS enet_model_test_drop")
        model_test = ElasticNet("enet_model_test_drop",)
        model_test.fit("public.winequality", ["alcohol"], "quality")

        current_cursor().execute(
            "SELECT model_name FROM models WHERE model_name = 'enet_model_test_drop'"
        )
        assert current_cursor().fetchone()[0] == "enet_model_test_drop"

        model_test.drop()
        current_cursor().execute(
            "SELECT model_name FROM models WHERE model_name = 'enet_model_test_drop'"
        )
        assert current_cursor().fetchone() is None

    def test_features_importance(self, model):
        fim = model.features_importance()

        assert fim["index"] == ["total_sulfur_dioxide", "residual_sugar", "alcohol"]
        assert fim["importance"] == [100, 0, 0]
        assert fim["sign"] == [-1, 0, 0]
        plt.close("all")

    def test_get_attr(self, model):
        m_att = model.get_attr()

        assert m_att["attr_name"] == [
            "details",
            "regularization",
            "iteration_count",
            "rejected_row_count",
            "accepted_row_count",
            "call_string",
        ]
        assert m_att["attr_fields"] == [
            "predictor, coefficient, std_err, t_value, p_value",
            "type, lambda",
            "iteration_count",
            "rejected_row_count",
            "accepted_row_count",
            "call_string",
        ]
        assert m_att["#_of_rows"] == [4, 1, 1, 1, 1, 1]

        m_att_details = model.get_attr(attr_name="details")

        assert m_att_details["predictor"] == [
            "Intercept",
            "total_sulfur_dioxide",
            "residual_sugar",
            "alcohol",
        ]
        assert m_att_details["coefficient"][0] == pytest.approx(5.874258, abs=1e-6)
        assert m_att_details["coefficient"][1] == pytest.approx(-0.000482, abs=1e-6)
        assert m_att_details["coefficient"][2] == pytest.approx(0, abs=1e-6)
        assert m_att_details["coefficient"][3] == pytest.approx(0, abs=1e-6)
        assert m_att_details["std_err"][1] == pytest.approx(0.000221, abs=1e-6)
        assert m_att_details["t_value"][1] == pytest.approx(-2.176118, abs=1e-6)
        assert m_att_details["p_value"][1] == pytest.approx(0.029582, abs=1e-6)

        m_att_regularization = model.get_attr("regularization")

        assert m_att_regularization["type"][0] == "enet"
        assert m_att_regularization["lambda"][0] == 1

        assert model.get_attr("iteration_count")["iteration_count"][0] == 1
        assert model.get_attr("rejected_row_count")["rejected_row_count"][0] == 0
        assert model.get_attr("accepted_row_count")["accepted_row_count"][0] == 6497
        assert (
            model.get_attr("call_string")["call_string"][0]
            == "linear_reg('public.elasticnet_model_test', 'public.winequality', '\"quality\"', '\"total_sulfur_dioxide\", \"residual_sugar\", \"alcohol\"'\nUSING PARAMETERS optimizer='cgd', epsilon=1e-06, max_iterations=100, regularization='enet', lambda=1, alpha=0.5)"
        )

    def test_get_params(self, model):
        assert model.get_params() == {
            "solver": "cgd",
            "penalty": "enet",
            "max_iter": 100,
            "l1_ratio": 0.5,
            "C": 1,
            "tol": 1e-6,
        }

    def test_get_plot(self, winequality_vd):
        current_cursor().execute("DROP MODEL IF EXISTS model_test_plot")
        model_test = ElasticNet("model_test_plot",)
        model_test.fit(winequality_vd, ["alcohol"], "quality")
        result = model_test.plot()
        assert len(result.get_default_bbox_extra_artists()) == 9
        plt.close("all")
        model_test.drop()

    def test_to_python(self, model):
        current_cursor().execute(
            "SELECT PREDICT_LINEAR_REG(3.0, 11.0, 93. USING PARAMETERS model_name = '{}', match_by_pos=True)".format(
                model.name
            )
        )
        prediction = current_cursor().fetchone()[0]
        assert prediction == pytest.approx(
            model.to_python(return_str=False)([[3.0, 11.0, 93.0]])[0]
        )

    def test_to_sql(self, model):
        current_cursor().execute(
            "SELECT PREDICT_LINEAR_REG(3.0, 11.0, 93. USING PARAMETERS model_name = '{}', match_by_pos=True)::float, {}::float".format(
                model.name, model.to_sql([3.0, 11.0, 93.0])
            )
        )
        prediction = current_cursor().fetchone()
        assert prediction[0] == pytest.approx(prediction[1])

    def test_to_memmodel(self, model, winequality_vd):
        mmodel = model.to_memmodel()
        res = mmodel.predict([[3.0, 11.0, 93.0], [11.0, 1.0, 99.0]])
        res_py = model.to_python()([[3.0, 11.0, 93.0], [11.0, 1.0, 99.0]])
        assert res[0] == res_py[0]
        assert res[1] == res_py[1]
        vdf = winequality_vd.copy()
        vdf["prediction_sql"] = mmodel.predict_sql(
            ["total_sulfur_dioxide", "residual_sugar", "alcohol"]
        )
        model.predict(vdf, name="prediction_vertica_sql")
        score = vdf.score("prediction_sql", "prediction_vertica_sql", "r2")
        assert score == pytest.approx(1.0)

    def test_get_predicts(self, winequality_vd, model):
        winequality_copy = winequality_vd.copy()
        model.predict(
            winequality_copy,
            X=["total_sulfur_dioxide", "residual_sugar", "alcohol"],
            name="predicted_quality",
        )

        assert winequality_copy["predicted_quality"].mean() == pytest.approx(
            5.818377, abs=1e-6
        )

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
        assert reg_rep["value"][0] == pytest.approx(0.001610, abs=1e-6)
        assert reg_rep["value"][1] == pytest.approx(3.192849, abs=1e-6)
        assert reg_rep["value"][2] == pytest.approx(0.788321, abs=1e-6)
        assert reg_rep["value"][3] == pytest.approx(0.684299, abs=1e-6)
        assert reg_rep["value"][4] == pytest.approx(0.761229, abs=1e-6)
        assert reg_rep["value"][5] == pytest.approx(0.872484, abs=1e-6)
        assert reg_rep["value"][6] == pytest.approx(0.001610, abs=1e-6)
        assert reg_rep["value"][7] == pytest.approx(0.001148, abs=1e-6)
        assert reg_rep["value"][8] == pytest.approx(-1764.5050571146871, abs=1e-6)
        assert reg_rep["value"][9] == pytest.approx(-1737.394835300611, abs=1e-6)

        reg_rep_details = model.regression_report("details")
        assert reg_rep_details["value"][2:] == [
            6497.0,
            3,
            pytest.approx(0.00161000676361089),
            pytest.approx(0.001148714605947454),
            pytest.approx(2.116870802238774),
            pytest.approx(0.0958537016435304),
            pytest.approx(0.232322269343305),
            pytest.approx(0.189622693372695),
            pytest.approx(53.1115447611131),
        ]

        reg_rep_anova = model.regression_report("anova")
        assert reg_rep_anova["SS"] == [
            pytest.approx(4.83725377631033),
            pytest.approx(4945.71023360928),
            pytest.approx(4953.68570109281),
        ]
        assert reg_rep_anova["MS"][:-1] == [
            pytest.approx(1.6124179254367768),
            pytest.approx(0.7616987884813307),
        ]

    def test_score(self, model):
        # method = "max"
        assert model.score(method="max") == pytest.approx(3.192849, abs=1e-6)
        # method = "mae"
        assert model.score(method="mae") == pytest.approx(0.684299, abs=1e-6)
        # method = "median"
        assert model.score(method="median") == pytest.approx(0.788321, abs=1e-6)
        # method = "mse"
        assert model.score(method="mse") == pytest.approx(0.761229, abs=1e-6)
        # method = "rmse"
        assert model.score(method="rmse") == pytest.approx(0.8724848619460168, abs=1e-6)
        # method = "msl"
        assert model.score(method="msle") == pytest.approx(0.003171, abs=1e-6)
        # method = "r2"
        assert model.score(method="r2") == pytest.approx(0.001610, abs=1e-6)
        # method = "r2a"
        assert model.score(method="r2a") == pytest.approx(
            0.001148714605947454, abs=1e-6
        )
        # method = "var"
        assert model.score(method="var") == pytest.approx(0.001610, abs=1e-6)
        # method = "aic"
        assert model.score(method="aic") == pytest.approx(-1764.5050571146871, abs=1e-6)
        # method = "bic"
        assert model.score(method="bic") == pytest.approx(-1737.394835300611, abs=1e-6)

    def test_set_params(self, model):
        model.set_params({"max_iter": 1000})

        assert model.get_params()["max_iter"] == 1000

    def test_model_from_vDF(self, winequality_vd):
        current_cursor().execute("DROP MODEL IF EXISTS enet_from_vDF")
        model_test = ElasticNet("enet_from_vDF",)
        model_test.fit(winequality_vd, ["alcohol"], "quality")

        current_cursor().execute(
            "SELECT model_name FROM models WHERE model_name = 'enet_from_vDF'"
        )
        assert current_cursor().fetchone()[0] == "enet_from_vDF"

        model_test.drop()
