# (c) Copyright [2018-2021] Micro Focus or one of its affiliates.
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
#
# |_     |~) _  _| _  /~\    _ |.
# |_)\/  |_)(_|(_||   \_/|_|(_|||
#    /
#              ____________       ______
#             / __        `\     /     /
#            |  \/         /    /     /
#            |______      /    /     /
#                   |____/    /     /
#          _____________     /     /
#          \           /    /     /
#           \         /    /     /
#            \_______/    /     /
#             ______     /     /
#             \    /    /     /
#              \  /    /     /
#               \/    /     /
#                    /     /
#                   /     /
#                   \    /
#                    \  /
#                     \/
#                    _
# \  / _  __|_. _ _ |_)
#  \/ (/_|  | |(_(_|| \/
#                     /
# VerticaPy is a Python library with scikit-like functionality to use to conduct
# data science projects on data stored in Vertica, taking advantage Vertica’s
# speed and built-in analytics and machine learning features. It supports the
# entire data science life cycle, uses a ‘pipeline’ mechanism to sequentialize
# data transformation operations, and offers beautiful graphical options.
#
# VerticaPy aims to solve all of these problems. The idea is simple: instead
# of moving data around for processing, VerticaPy brings the logic to the data.
#
#
# Modules
#
# Standard Python Modules
import numpy as np
from collections.abc import Iterable

# VerticaPy Modules
from verticapy.toolbox import *
from verticapy.errors import *

# ---#
def predict_from_binary_tree(X: Union[list, np.ndarray], 
                             children_left: list,
                             children_right: list,
                             feature: list,
                             threshold: list,
                             value: list,
                             classes: Union[list, np.ndarray] = [],
                             return_proba: bool = False,
                             is_regressor: bool = True,):
    """
    ---------------------------------------------------------------------------
    Predicts using a binary tree model and the input attributes.

    Parameters
    ----------
    X: list / numpy.array
        Data on which to make the prediction.
    children_left: list
        A list of node IDs, where children_left[i] is the node id of the left child of node i.
    children_right: list
        A list of node IDs, children_right[i] is the node id of the right child of node i.
    feature: list
        A list of features, where feature[i] is the feature to split on for the internal node i.
    threshold: list
        A list of thresholds, where threshold[i] is the threshold for the internal node i.
    value: list
        Contains the constant prediction value of each node.
    classes: list / numpy.array, optional
        The classes for the binary tree model.
    return_proba: bool, optional
        If set to True, the probability of each class is returned.
    is_regressor: bool, optional
        If set to True, the parameter 'value' corresponds to the result of
        a regression.

    Returns
    -------
    numpy.array
        Predicted values
    """
    check_types([("X", X, [list, np.ndarray,],),
                 ("children_left", children_left, [list,],),
                 ("children_right", children_right, [list,],),
                 ("feature", feature, [list,],),
                 ("threshold", threshold, [list,],),
                 ("value", value, [list,],),
                 ("classes", classes, [list, np.ndarray,],),
                 ("return_proba", return_proba, [bool,],),
                 ("is_regressor", is_regressor, [bool,],),])
    def predict_tree(children_left, children_right, feature, threshold, value,  node_id, X,):
        if children_left[node_id] == children_right[node_id]:
            if not(is_regressor) and not(return_proba) and isinstance(value, Iterable):
                if isinstance(classes, Iterable) and len(classes) > 0:
                    return classes[np.argmax(value[node_id])]
                else:
                    return np.argmax(value[node_id])
            else:
                return value[node_id]
        else:
            if (isinstance(threshold[node_id], str) and str(X[feature[node_id]]) == threshold[node_id]) or (not(isinstance(threshold[node_id], str)) and float(X[feature[node_id]]) < float(threshold[node_id])):
                return predict_tree(children_left, children_right, feature, threshold, value, children_left[node_id], X)
            else:
                return predict_tree(children_left, children_right, feature, threshold, value, children_right[node_id], X)
    def predict_tree_final(X,):
        return predict_tree(children_left, children_right, feature, threshold, value, 0, X,)
    return np.apply_along_axis(predict_tree_final, 1, np.array(X))

# ---#
def sql_from_binary_tree(X: Union[list, np.ndarray], 
                         children_left: list,
                         children_right: list,
                         feature: list,
                         threshold: list,
                         value: list,
                         classes: Union[list, np.ndarray] = [],
                         return_proba: bool = False,
                         is_regressor: bool = True,):
    """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy a binary tree model using its attributes.

    Parameters
    ----------
    X: list / numpy.array
        Data on which to make the prediction.
    children_left: list
        A list of node IDs, where children_left[i] is the node id of the left child of node i.
    children_right: list
        A list of node IDs, children_right[i] is the node id of the right child of node i.
    feature: list
        A list of features, where feature[i] is the feature to split on for the internal node i.
    threshold: list
        A list of thresholds, where threshold[i] is the threshold for the internal node i.
    value: list
        Contains the constant prediction value of each node. If used for classification and if return_proba is set to True, each element of the list must be a sublist
        with the probabilities of each classes.
    classes: list / numpy.array, optional
        The classes for the binary tree model.
    return_proba: bool, optional
        If set to True, the probability of each class is returned.
    is_regressor: bool, optional
        If set to True, the parameter 'value' corresponds to the result of
        a regression.

    Returns
    -------
    str / list
        SQL code
    """
    check_types([("X", X, [list, np.ndarray,],),
                 ("children_left", children_left, [list,],),
                 ("children_right", children_right, [list,],),
                 ("feature", feature, [list,],),
                 ("threshold", threshold, [list,],),
                 ("value", value, [list,],),
                 ("classes", classes, [list, np.ndarray,],),
                 ("return_proba", return_proba, [bool,],),
                 ("is_regressor", is_regressor, [bool,],),])
    def predict_tree(children_left, children_right, feature, threshold, value,  node_id, X, prob_ID = 0):
        if children_left[node_id] == children_right[node_id]:
            if return_proba:
                return value[node_id][prob_ID]
            else:
                if not(is_regressor) and isinstance(classes, Iterable) and len(classes) > 0:
                    result = classes[np.argmax(value[node_id])]
                    if isinstance(result, str):
                      return "'" + result + "'"
                    else:
                      return result
                else:
                    return value[node_id]
        else:
            op = '=' if isinstance(threshold[node_id], str) else '<'
            return "(CASE WHEN {} {} '{}' THEN {} ELSE {} END)".format(X[feature[node_id]], 
                                                                       op, threshold[node_id], 
                                                                       predict_tree(children_left, children_right, feature, threshold, value, children_left[node_id], X, prob_ID), 
                                                                       predict_tree(children_left, children_right, feature, threshold, value, children_right[node_id], X, prob_ID))
    if return_proba:
        n = max([len(l) if l != None else 0 for l in value])
        return [predict_tree(children_left, children_right, feature, threshold, value, 0, X, i) for i in range(n)]
    else:
        return predict_tree(children_left, children_right, feature, threshold, value, 0, X,)

# ---#
def predict_from_coef(X: Union[list, np.ndarray], 
                      coefficients: Union[list, np.ndarray], 
                      intercept: float, 
                      method: str = "LinearRegression",
                      return_proba: bool = False,):
    """
    ---------------------------------------------------------------------------
    Predicts using a linear regression model and the input attributes.

    Parameters
    ----------
    X: list / numpy.array
        Data on which to make the prediction.
    coefficients: list / numpy.array
        List of the model's coefficients.
    intercept: float
        The intercept or constant value.
    method: str, optional
        The model category, one of the following: 'LinearRegression', 'LinearSVR', 
        'LogisticRegression', or 'LinearSVC'.
    return_proba: bool, optional
        If set to True and the method is set to 'LogisticRegression' or 'LinearSVC', 
        the probability is returned.

    Returns
    -------
    numpy.array
        Predicted values
    """
    check_types([("X", X, [list, np.ndarray,],), 
                 ("coefficients", coefficients, [list, np.ndarray,],),
                 ("intercept", intercept, [float, int,],),
                 ("method", method, ["LinearRegression", "LinearSVR", "LogisticRegression", "LinearSVC"],),
                 ("return_proba", return_proba, [bool],),])
    result = intercept + np.sum(np.array(coefficients) * np.array(X), axis=1)
    if method in ("LogisticRegression", "LinearSVC",):
        result = 1 / (1 + np.exp(- (result)))
    else:
        return result
    if return_proba:
        return np.column_stack((1 - result, result))
    else:
        return np.where(result > 0.5, 1, 0)

# ---#
def sql_from_coef(X: list, 
                  coefficients: list, 
                  intercept: float, 
                  method: str = "LinearRegression",):
    """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy a linear model using its attributes.

    Parameters
    ----------
    X: list
        The name or values of the input predictors.
    coefficients: list
        List of the model's coefficients.
    intercept: float
        The intercept or constant value.
    method: str, optional
        The model category, one of the following: 'LinearRegression', 'LinearSVR', 
        'LogisticRegression', or 'LinearSVC'.

    Returns
    -------
    str
        SQL code
    """
    check_types([("X", X, [list],), 
                 ("coefficients", coefficients, [list],),
                 ("intercept", intercept, [float, int,],),
                 ("method", method, ["LinearRegression", "LinearSVR", "LogisticRegression", "LinearSVC"],),])
    assert len(X) == len(coefficients), ParameterError("The length of parameter 'X' must be equal to the number of coefficients.")
    sql = [str(intercept)] + [f"{coefficients[idx]} * {(X[idx])}" for idx in range(len(coefficients))]
    sql = " + ".join(sql)
    if method in ("LogisticRegression", "LinearSVC",):
        return f"1 / (1 + EXP(- ({sql})))"
    return sql

# ---#
def predict_from_bisecting_kmeans(X: Union[list, np.ndarray], 
                                  clusters: Union[list, np.ndarray],
                                  left_child: Union[list, np.ndarray],
                                  right_child: Union[list, np.ndarray],
                                  p: int = 2,):
    """
    ---------------------------------------------------------------------------
    Predicts using a bisecting k-means model and the input attributes.

    Parameters
    ----------
    X: list / numpy.array
        The data on which to make the prediction.
    clusters: list / numpy.array
        List of the model's cluster centers.
    left_child: list / numpy.array
        List of the model's left children IDs. ID i corresponds to the left 
        child ID of node i.
    right_child: list / numpy.array
        List of the model's right children IDs. ID i corresponds to the right 
        child ID of node i.
    p: int, optional
        The p corresponding to the one of the p-distances.

    Returns
    -------
    numpy.array
        Predicted values
    """
    check_types([("X", X, [list, np.ndarray,],), 
                 ("clusters", clusters, [list, np.ndarray,],),
                 ("left_child", left_child, [list, np.ndarray,],),
                 ("right_child", right_child, [list, np.ndarray,],),
                 ("p", p, [int,],),])
    centroids = np.array(clusters)
    def predict_tree(right_child, left_child, row, node_id, centroids):
        if left_child[node_id] == right_child[node_id] == None:
            return int(node_id)
        else:
            right_node = int(right_child[node_id])
            left_node = int(left_child[node_id])
            if np.sum((row - centroids[left_node]) ** p) < np.sum((row - centroids[right_node]) ** p):
                return predict_tree(right_child, left_child, row, left_node, centroids)
            else:
                return predict_tree(right_child, left_child, row, right_node, centroids)
    def predict_tree_final(row):
        return predict_tree(right_child, left_child, row, 0, centroids)
    return np.apply_along_axis(predict_tree_final, 1, X)

# ---#
def sql_from_bisecting_kmeans(X: list, 
                              clusters: list,
                              left_child: list,
                              right_child: list,
                              return_distance_clusters: bool = False,
                              p: int = 2,):
    """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy a bisecting k-means model using its 
    attributes.

    Parameters
    ----------
    X: list
        The names or values of the input predictors.
    clusters: list
        List of the model's cluster centers.
    left_child: list
        List of the model's left children IDs. ID i corresponds to the left 
        child ID of node i.
    right_child: list
        List of the model's right children IDs. ID i corresponds to the right 
        child ID of node i.
    return_distance_clusters: bool, optional
        If set to True, the distance to the clusters is returned.
    p: int, optional
        The p corresponding to the one of the p-distances.

    Returns
    -------
    str / list
        SQL code
    """
    check_types([("X", X, [list],), 
                 ("clusters", clusters, [list],),
                 ("left_child", left_child, [list],),
                 ("right_child", right_child, [list],),
                 ("return_distance_clusters", return_distance_clusters, [bool],),
                 ("p", p, [int,],),])
    for c in clusters:
        assert len(X) == len(c), ParameterError("The length of parameter 'X' must be the same as the length of each cluster.")
    clusters_distance = []
    for c in clusters:
        list_tmp = []
        for idx, col in enumerate(X):
            list_tmp += ["POWER({} - {}, {})".format((X[idx]), c[idx], p)]
        clusters_distance += ["POWER(" + " + ".join(list_tmp) + ", 1/{})".format(p)]
    if return_distance_clusters:
        return clusters_distance
    def predict_tree(right_child: list, left_child: list, node_id: int, clusters_distance: list):
        if left_child[node_id] == right_child[node_id] == None:
            return int(node_id)
        else:
            right_node = int(right_child[node_id])
            left_node = int(left_child[node_id])
            return "(CASE WHEN {} < {} THEN {} ELSE {} END)".format(clusters_distance[left_node], clusters_distance[right_node], predict_tree(right_child, left_child, left_node, clusters_distance), predict_tree(right_child, left_child, right_node, clusters_distance))
    sql_final = "(CASE WHEN {} THEN NULL ELSE {} END)".format(" OR ".join(["{} IS NULL".format(elem) for elem in X]), predict_tree(right_child, left_child, 0, clusters_distance))
    return sql_final

# ---#
def predict_from_clusters(X: Union[list, np.ndarray], 
                          clusters: Union[list, np.ndarray],
                          return_distance_clusters: bool = False,
                          return_proba: bool = False,
                          classes: Union[list, np.ndarray] = [],
                          p: int = 2,):
    """
    ---------------------------------------------------------------------------
    Predicts using a k-means or nearest centroid model and the input attributes.

    Parameters
    ----------
    X: list / numpy.array
        The data on which to make the prediction.
    clusters: list / numpy.array
        List of the model's cluster centers.
    return_distance_clusters: bool, optional
        If set to True, the distance to the clusters is returned.
    return_proba: bool, optional
        If set to True, the probability to belong to the clusters is returned.
    classes: list / numpy.array, optional
        The classes for the nearest centroids model.
    p: int, optional
        The p corresponding to the one of the p-distances.

    Returns
    -------
    numpy.array
        Predicted values
    """
    check_types([("X", X, [list, np.ndarray,],), 
                 ("clusters", clusters, [list, np.ndarray,],),
                 ("return_distance_clusters", return_distance_clusters, [bool,],),
                 ("return_proba", return_proba, [bool,],),
                 ("classes", classes, [list, np.ndarray,],),
                 ("p", p, [int,],),])
    assert not(return_distance_clusters) or not(return_proba), ParameterError("Parameters 'return_distance_clusters' and 'return_proba' cannot both be set to True.")
    centroids = np.array(clusters)
    result = []
    for centroid in centroids:
        result += [np.sum((np.array(centroid) - X) ** p, axis=1) ** (1 / p)]
    result = np.column_stack(result)
    if return_proba:
        result = 1 / (result + 1e-99) / np.sum(1 / (result + 1e-99), axis=1)[:,None]
    elif not(return_distance_clusters):
        result = np.argmin(result, axis=1)
        if classes:
            class_is_str = isinstance(classes[0], str)
            for idx, c in enumerate(classes):
                tmp_idx = str(idx) if class_is_str and idx > 0 else idx
                result = np.where(result == tmp_idx, c, result)
    return result

# ---#
def sql_from_clusters(X: list, 
                      clusters: list,
                      return_distance_clusters: bool = False,
                      return_proba: bool = False,
                      classes: list = [],
                      p: int = 2,):
    """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy a k-means or nearest centroids model 
    using its attributes.

    Parameters
    ----------
    X: list
        The names or values of the input predictors.
    clusters: list
        List of the model's cluster centers.
    return_distance_clusters: bool, optional
        If set to True, the distance to the clusters is returned.
    return_proba: bool, optional
        If set to True, the probability to belong to the clusters is returned.
    classes: list, optional
        The classes for the nearest centroids model.
    p: int, optional
        The p corresponding to the one of the p-distances.

    Returns
    -------
    str / list
        SQL code
    """
    check_types([("X", X, [list],), 
                 ("clusters", clusters, [list],),
                 ("return_distance_clusters", return_distance_clusters, [bool],),
                 ("return_proba", return_proba, [bool],),
                 ("classes", classes, [list],),])
    for c in clusters:
        assert len(X) == len(c), ParameterError("The length of parameter 'X' must be the same as the length of each cluster.")
    assert not(return_distance_clusters) or not(return_proba), ParameterError("Parameters 'return_distance_clusters' and 'return_proba' cannot be set to True.")
    classes_tmp = []
    for i in range(len(classes)):
        val = classes[i]
        if isinstance(val, str):
            val = "'{}'".format(classes[i])
        elif val == None:
            val = "NULL"
        classes_tmp += [val]
    clusters_distance = []
    for c in clusters:
        list_tmp = []
        for idx, col in enumerate(X):
            list_tmp += ["POWER({} - {}, {})".format((X[idx]), c[idx], p)]
        clusters_distance += ["POWER(" + " + ".join(list_tmp) + ", {})".format(p)]
    if return_distance_clusters:
        return clusters_distance
    if return_proba:
        sum_distance = " + ".join(["1 / ({})".format(d) for d in clusters_distance])
        proba = ["(CASE WHEN {} = 0 THEN 1.0 ELSE 1 / ({}) / ({}) END)".format(clusters_distance[i], clusters_distance[i], sum_distance) for i in range(len(clusters_distance))]
        return proba
    sql = []
    k = len(clusters_distance)
    for i in range(k):
        list_tmp = []
        for j in range(i):
            list_tmp += ["{} <= {}".format(clusters_distance[i], clusters_distance[j])]
        sql += [" AND ".join(list_tmp)]
    sql = sql[1:]
    sql.reverse()
    sql_final = "CASE WHEN {} THEN NULL".format(" OR ".join(["{} IS NULL".format(elem) for elem in X]))
    for i in range(k - 1):
        sql_final += " WHEN {} THEN {}".format(sql[i], k - i - 1 if not classes else classes_tmp[k - i - 1])
    sql_final += " ELSE {} END".format(0 if not classes else classes_tmp[0])
    return sql_final

# ---#
def transform_from_pca(X: Union[list, np.ndarray],
                       principal_components: Union[list, np.ndarray],
                       mean: Union[list, np.ndarray]):
    """
    ---------------------------------------------------------------------------
    Transforms the data with a PCA model using the input attributes.

    Parameters
    ----------
    X: list / numpy.array
        Data to transform.
    principal_components: list / numpy.array
        Matrix of the principal components.
    mean: list / numpy.array
        List of the averages of each input feature.

    Returns
    -------
    numpy.array
        Transformed data
    """
    check_types([("X", X, [list, np.ndarray,],), 
                 ("principal_components", principal_components, [list, np.ndarray,],),
                 ("mean", mean, [list, np.ndarray,],),])
    pca_values = np.array(principal_components)
    result = (X - np.array(mean))
    L, n = [], len(principal_components[0])
    for i in range(n):
        L += [np.sum(result * pca_values[:,i], axis=1)]
    return np.column_stack(L)

# ---#
def sql_from_pca(X: list, 
                 principal_components: list,
                 mean: list):
    """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy a PCA model using its attributes.

    Parameters
    ----------
    X: list
        Names or values of the input predictors.
    principal_components: list
        Matrix of the principal components.
    mean: list
        List of the averages of each input feature.

    Returns
    -------
    list
        SQL code
    """
    check_types([("X", X, [list],), 
                 ("principal_components", principal_components, [list],),
                 ("mean", mean, [list],),])
    assert len(X) == len(mean), ParameterError("The length of parameter 'X' must be equal to the length of the vector 'mean'.")
    sql = []
    for i in range(len(X)):
        sql_tmp = []
        for j in range(len(X)):
            sql_tmp += ["({} - {}) * {}".format((X[j]), mean[j], [pc[i] for pc in principal_components][j])]
        sql += [" + ".join(sql_tmp)]
    return sql

# ---#
def transform_from_svd(X: list, 
                       vectors: list,
                       values: list):
    """
    ---------------------------------------------------------------------------
    Transforms the data with an SVD model using the input attributes.

    Parameters
    ----------
    X: list / numpy.array
        Data to transform.
    vectors: list / numpy.array
        Matrix of the right singular vectors.
    values: list / numpy.array
        List of the singular values for each input feature.

    Returns
    -------
    numpy.array
        Transformed data
    """
    check_types([("X", X, [list],), 
                 ("vectors", vectors, [list],),
                 ("values", values, [list],),])
    svd_vectors = np.array(vectors)
    L, n = [], len(svd_vectors[0])
    for i in range(n):
        L += [np.sum(X * svd_vectors[:,i] / values[i], axis=1)]
    return np.column_stack(L)

# ---#
def sql_from_svd(X: list, 
                 vectors: list,
                 values: list):
    """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy a SVD model using its attributes.

    Parameters
    ----------
    X: list
        input predictors name or values.
    vectors: list
        List of the model's right singular vectors.
    values: list
        List of the singular values for each input feature.

    Returns
    -------
    list
        SQL code
    """
    check_types([("X", X, [list],), 
                 ("vectors", vectors, [list],),
                 ("values", values, [list],),])
    assert len(X) == len(values), ParameterError("The length of parameter 'X' must be equal to the length of the vector 'values'.")
    sql = []
    for i in range(len(X)):
        sql_tmp = []
        for j in range(len(X)):
            sql_tmp += ["{} * {} / {}".format((X[j]), [pc[i] for pc in vectors][j], values[i])]
        sql += [" + ".join(sql_tmp)]
    return sql

# ---#
def transform_from_normalizer(X: list, 
                              values: list,
                              method: str = "zscore",):
    """
    ---------------------------------------------------------------------------
    Transforms the data with a normalizer model using the input attributes.

    Parameters
    ----------
    X: list / numpy.array
        The data to transform.
    values: list
        List of tuples. These tuples depend on the specified method:
            'zscore': (mean, std)
            'robust_zscore': (median, mad)
            'minmax': (min, max)
    method: str, optional
        The model's category, one of the following: 'zscore', 'robust_zscore', or 'minmax'.

    Returns
    -------
    numpy.array
        Transformed data
    """
    check_types([("X", X, [list],), 
                 ("values", values, [list],),
                 ("method", method, ["zscore", "robust_zscore", "minmax"],),])
    a, b = np.array([elem[0] for elem in values]), np.array([elem[1] for elem in values])
    if method == "minmax":
        b = b - a
    return (np.array(X) - a) / b

# ---#
def sql_from_normalizer(X: list, 
                        values: list,
                        method: str = "zscore",):
    """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy a normalizer model using its attributes.

    Parameters
    ----------
    X: list
        Names or values of the input predictors.
    values: list
        List of tuples, including the model's attributes. These required tuple  
        depends on the specified method:
            'zscore': (mean, std)
            'robust_zscore': (median, mad)
            'minmax': (min, max)
    method: str, optional
        The model's category, one of the following: 'zscore', 'robust_zscore', or 'minmax'.

    Returns
    -------
    list
        SQL code
    """
    check_types([("X", X, [list],), 
                 ("values", values, [list],),
                 ("method", method, ["zscore", "robust_zscore", "minmax"],),])
    assert len(X) == len(values), ParameterError("The length of parameter 'X' must be equal to the length of the list 'values'.")
    sql = []
    for i in range(len(X)):
        sql += ["({} - {}) / {}".format(X[i], values[i][0], values[i][1] - values[i][0] if method == "minmax" else values[i][1],)]
    return sql

# ---#
def transform_from_one_hot_encoder(X: list, 
                                   categories: list,
                                   drop_first: bool = False,):
    """
    ---------------------------------------------------------------------------
    Transforms the data with a one-hot encoder model using the input attributes.

    Parameters
    ----------
    X: list / numpy.array
        Data to transform.
    categories: list
        List of the categories of the different input columns.
    drop_first: bool, optional
        If set to False, the first dummy of each category will be dropped.

    Returns
    -------
    list
        SQL code
    """
    check_types([("X", X, [list],), 
                 ("categories", categories, [list],),
                 ("drop_first", drop_first, [bool],),])
    def ooe_row(X):
        result = []
        for idx, elem in enumerate(X):
            for idx2, item in enumerate(categories[idx]):
                if idx2 != 0 or not(drop_first):
                    if str(elem) == str(item):
                        result += [1]
                    else:
                        result += [0]
        return result
    return np.apply_along_axis(ooe_row, 1, X)

# ---#
def sql_from_one_hot_encoder(X: list, 
                             categories: list,
                             drop_first: bool = False,
                             column_naming: str = None):
    """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy a one-hot encoder model using its 
    attributes.

    Parameters
    ----------
    X: list
        The names or values of the input predictors.
    categories: list
        List of the categories of the different input columns.
    drop_first: bool, optional
        If set to False, the first dummy of each category will be dropped.
    column_naming: str, optional
        Appends categorical levels to column names according to the specified method:
            indices    : Uses integer indices to represent categorical 
                                     levels.
            values/values_relaxed  : Both methods use categorical-level names. If 
                                     duplicate column names occur, the function 
                                     attempts to disambiguate them by appending _n, 
                                     where n is a zero-based integer index (_0, _1,…).

    Returns
    -------
    list
        SQL code
    """
    check_types([("X", X, [list],), 
                 ("categories", categories, [list],),
                 ("drop_first", drop_first, [bool],),
                 ("column_naming", column_naming, ["indices", "values", "values_relaxed", None,],),])
    assert len(X) == len(categories), ParameterError("The length of parameter 'X' must be equal to the length of the list 'values'.")
    sql = []
    for i in range(len(X)):
        sql_tmp = []
        for j in range(len(categories[i])):
            if not(drop_first) or j > 0:
                val = categories[i][j]
                if isinstance(val, str):
                    val = "'{}'".format(val)
                elif val == None:
                    val = "NULL"
                sql_tmp_feature = "(CASE WHEN {} = {} THEN 1 ELSE 0 END)".format(X[i], val)
                if column_naming == "indices":
                    sql_tmp_feature += " AS \"{}_{}\"".format((X[i]), j)
                elif column_naming in ("values", "values_relaxed",):
                    sql_tmp_feature += " AS \"{}_{}\"".format((X[i]), categories[i][j] if categories[i][j] != None else "NULL")
                sql_tmp += [sql_tmp_feature]
        sql += [sql_tmp]
    return sql

# ---#
class memModel:
    """
---------------------------------------------------------------------------
Independent machine learning models that can easily be deployed 
using standard SQL or standard Python code.

Parameters
----------
model_type: str
    The model type, one of the following: 'OneHotEncoder,' 'Normalizer,' 
    'SVD,' 'PCA,' 'BisectingKMeans,' 'KMeans,' 'NaiveBayes,' 
    'XGBoostClassifier,' 'XGBoostRegressor,' 'RandomForestClassifier,' 
    'RandomForestRegressor,' 'LinearSVR,' 'LinearSVC,' 'LogisticRegression,' 
    'LinearRegression', 'BinaryTreeRegressor', 'BinaryTreeClassifier'
attributes: dict
    Dictionary which includes all the model's attributes.
        For OneHotEncoder: {"categories": List of the different feature categories.
                            "drop_first": Boolean, whether the first category
                                          should be dropped.
                            "column_naming": Appends categorical levels to column names 
                                             according to the specified method. 
                                             It can be set to 'indices' or 'values'.}
        For LinearSVR, LinearSVC, LogisticRegression, LinearRegression: 
                           {"coefficients": List of the model's coefficients.
                            "intercept": Intercept or constant value.}
        For BisectingKMeans: 
                           {"clusters": List of the model's cluster centers.
                            "left_child": List of the model's left children IDs.
                            "right_child": List of the model's right children IDs.
                            "p": The p corresponding to the one of the p-distances.}
        For KMeans:        {"clusters": List of the model's cluster centers.
                            "p": The p corresponding to the one of the p-distances.}
        For NearestCentroids:
                           {"clusters": List of the model's cluster centers.
                            "p": The p corresponding to the one of the p-distances.
                            "classes": Represents the classes of the nearest centroids.}
        For PCA:           {"principal_components": Matrix of the principal components.
                            "mean": List of the input predictors average.}
        For SVD:           {"vectors": Matrix of the right singular vectors.
                            "values": List of the singular values.}
        For Normalizer:    {"values": List of tuples including the model's attributes.
                                The required tuple depends on the specified method: 
                                    'zscore': (mean, std)
                                    'robust_zscore': (median, mad)
                                    'minmax': (min, max)
                            "method": The model's category, one of the following: 'zscore', 
                                      'robust_zscore', or 'minmax'.}
        For BinaryTreeRegressor, BinaryTreeClassifier:
                            {children_left: A list of node IDs, where children_left[i] is the node id of the left 
                                            A list of node IDs, where child of node i.
                             children_right: children_right[i] is the node id of the 
                                             right child of node i.
                             feature: A list of features, where feature[i] is the feature to split on, for the internal 
                                      node i.
                             threshold: threshold[i] is the threshold for the internal node i.
                             value: Contains the constant prediction value of each node.
                             classes: [Only for Classifier] The classes for the binary tree model.}
        For RandomForestClassifier, RandomForestRegressor, XGBoostClassifier, XGBoostRegressor:
                            {trees: list of memModels of type 'BinaryTreeRegressor' or 
                                    'BinaryTreeClassifier'
                             learning_rate: [Only for XGBoostClassifier and XGBoostRegressor]
                                            Learning rate.
                             mean: [Only for XGBoostRegressor]
                                   Average of the response column.
                             logodds: [Only for XGBoostClassifier]
                                   List of the logodds of the response classes.}


    """
    #
    # Special Methods
    #
    # ---#
    def __init__(
        self,
        model_type: str,
        attributes: dict,
    ):
        check_types([("attributes", attributes, [dict],), 
                     ("model_type", model_type, ["OneHotEncoder", 
                                                  "Normalizer",
                                                  "SVD",
                                                  "PCA",
                                                  "BisectingKMeans",
                                                  "KMeans",
                                                  "NaiveBayes",
                                                  "XGBoostClassifier",
                                                  "XGBoostRegressor",
                                                  "RandomForestClassifier",
                                                  "BinaryTreeClassifier",
                                                  "BinaryTreeRegressor",
                                                  "RandomForestRegressor",
                                                  "LinearSVR",
                                                  "LinearSVC",
                                                  "LogisticRegression",
                                                  "LinearRegression",
                                                  "NearestCentroids",],),])
        attributes_ = {}
        if model_type in ("RandomForestRegressor", "XGBoostRegressor", "RandomForestClassifier", "XGBoostClassifier",):
            if ("trees" not in attributes):
                raise ParameterError("{}'s attributes must include a list of memModels representing each tree.".format(model_type))
            attributes_["trees"] = []
            for tree in attributes["trees"]:
                assert isinstance(tree, memModel), ParameterError("Each tree of the model must be a memModel, found '{}'.".format(type(tree)))
                if model_type in ("RandomForestClassifier", "XGBoostClassifier",):
                    assert tree.model_type_ in ("BinaryTreeClassifier",), ParameterError("Each tree of the model must be a BinaryTreeClassifier, found '{}'.".format(tree.model_type_))
                else:
                    assert tree.model_type_ in ("BinaryTreeRegressor",), ParameterError("Each tree of the model must be a BinaryTreeRegressor, found '{}'.".format(tree.model_type_))
                attributes_["trees"] += [tree]
            represent = "<{}>\n\nntrees = {}".format(model_type, len(attributes_["trees"]))
            if model_type == "XGBoostRegressor":
                if ("learning_rate" not in attributes or 'mean' not in attributes):
                    raise ParameterError("{}'s attributes must include the response average and the learning rate.".format(model_type))
                attributes_["mean"] = attributes["mean"]
                check_types([("mean", attributes_["mean"], [int, float,],),])
                represent += "\n\nmean = {}".format(attributes_["mean"])
            if model_type == "XGBoostClassifier":
                if ("learning_rate" not in attributes or 'logodds' not in attributes):
                    raise ParameterError("{}'s attributes must include the response classes logodds and the learning rate.".format(model_type))
                attributes_["logodds"] = np.copy(attributes["logodds"])
                check_types([("logodds", attributes_["logodds"], [list,],),])
                represent += "\n\nlogodds = {}".format(attributes_["logodds"])
            if model_type in ("XGBoostRegressor", "XGBoostClassifier",):
                attributes_["learning_rate"] = attributes["learning_rate"]
                check_types([("learning_rate", attributes_["learning_rate"], [int, float,],),])
                represent += "\n\nlearning_rate = {}".format(attributes_["learning_rate"])
        elif model_type in ("BinaryTreeClassifier", "BinaryTreeRegressor"):
            if ("children_left" not in attributes or "children_right" not in attributes or "feature" not in attributes or "threshold" not in attributes or "value" not in attributes):
                raise ParameterError("{}'s attributes must include at least the following lists: children_left, children_right, feature, threshold, value.".format(model_type))
            for elem in ("children_left", "children_right", "feature", "threshold", "value",):
                if isinstance(attributes[elem], list):
                    attributes_[elem] = attributes[elem].copy()
                else:
                    attributes_[elem] = np.copy(attributes[elem])
            check_types([("children_left", attributes_["children_left"], [list,],),
                         ("children_right", attributes_["children_right"], [list,],),
                         ("feature", attributes_["feature"], [list,],),
                         ("threshold", attributes_["threshold"], [list,],),
                         ("value", attributes_["value"], [list,],),])
            represent = "<{}>\n\nchildren_left = {}\n\nchildren_right = {}\n\nfeature = {}\n\nthreshold = {}\n\nvalue =\n{}".format(model_type, attributes_["children_left"], attributes_["children_right"], attributes_["feature"], attributes_["threshold"], attributes_["value"])
            if model_type in ("BinaryTreeClassifier",):
                if "classes" not in attributes:
                    attributes_["classes"] = []
                else:
                    attributes_["classes"] = np.copy(attributes["classes"])
                check_types([("classes", attributes_["classes"], [list,],),])
                represent += "\n\nclasses = {}".format(attributes_["classes"])
        elif model_type == "OneHotEncoder":
            if "categories" not in attributes:
                raise ParameterError("OneHotEncoder's attributes must include a list with all the feature categories for the 'categories' parameter.")
            attributes_["categories"] = attributes["categories"].copy()
            if "drop_first" not in attributes:
                attributes_["drop_first"] = False
            else:
                attributes_["drop_first"] = attributes["drop_first"]
            if "column_naming" not in attributes:
                attributes_["column_naming"] = "indices"
            else:
                attributes_["column_naming"] = attributes["column_naming"]
            check_types([("categories", attributes_["categories"], [list],),
                         ("drop_first", attributes_["drop_first"], [bool],),
                         ("column_naming", attributes_["column_naming"], ["indices", "values", None,],),])
            represent = "<{}>\n\ncategories = {}\n\ndrop_first = {}\n\ncolumn_naming = {}".format(model_type, attributes_["categories"], attributes_["drop_first"], attributes_["column_naming"])
        elif model_type in ("LinearSVR", "LinearSVC", "LogisticRegression", "LinearRegression",):
            if ("coefficients" not in attributes or "intercept" not in attributes):
                raise ParameterError("{}'s attributes must include a list with the 'coefficients' and the 'intercept' value.".format(model_type))
            attributes_["coefficients"] = np.copy(attributes["coefficients"])
            attributes_["intercept"] = attributes["intercept"]
            check_types([("coefficients", attributes_["coefficients"], [list],),
                         ("intercept", attributes_["intercept"], [int, float],),])
            represent = "<{}>\n\ncoefficients = {}\n\nintercept = {}".format(model_type, attributes_["coefficients"], attributes_["intercept"])
        elif model_type in ("BisectingKMeans",):
            if ("clusters" not in attributes or "left_child" not in attributes or "right_child" not in attributes):
                raise ParameterError("BisectingKMeans's attributes must include three lists: one with all the 'clusters' centers, one with all the cluster's right children, and one with all the cluster's left children.")
            attributes_["clusters"] = np.copy(attributes["clusters"])
            attributes_["left_child"] = np.copy(attributes["left_child"])
            attributes_["right_child"] = np.copy(attributes["right_child"])
            if "p" not in attributes:
                attributes_["p"] = 2
            else:
                attributes_["p"] = attributes["p"]
            check_types([("clusters", attributes_["clusters"], [list,],),
                         ("left_child", attributes_["left_child"], [list,],),
                         ("right_child", attributes_["right_child"], [list,],),
                         ("p", attributes_["p"], [int,],),])
            represent = "<{}>\n\nclusters = {}\n\nleft_child = {}\n\nright_child = {}\n\np = {}".format(model_type, attributes_["clusters"], attributes_["left_child"], attributes_["right_child"], attributes_["p"])
        elif model_type in ("KMeans", "NearestCentroids",):
            if ("clusters" not in attributes):
                raise ParameterError("{}'s attributes must include a list with all the 'clusters' centers.".format(model_type))
            attributes_["clusters"] = np.copy(attributes["clusters"])
            if "p" not in attributes:
                attributes_["p"] = 2
            else:
                attributes_["p"] = attributes["p"]
            check_types([("clusters", attributes_["clusters"], [list,],),
                         ("p", attributes_["p"], [int,],),])
            represent = "<{}>\n\nclusters = {}\n\np = {}".format(model_type, attributes_["clusters"], attributes_["p"])
            if model_type in ("NearestCentroids"):
                if "classes" not in attributes:
                    attributes_["classes"] = None
                else:
                    attributes_["classes"] = [c for c in attributes["classes"]]
                check_types([("classes", attributes_["classes"], [list,],),])
                represent += "\n\nclasses = {}".format(attributes_["classes"])
        elif model_type in ("PCA",):
            if ("principal_components" not in attributes or "mean" not in attributes):
                raise ParameterError("PCA's attributes must include two lists: one with all the principal components and one with all the averages of each input feature.")
            attributes_["principal_components"] = np.copy(attributes["principal_components"])
            attributes_["mean"] = np.copy(attributes["mean"])
            check_types([("principal_components", attributes_["principal_components"], [list,],),
                         ("mean", attributes_["mean"], [list,],),])
            represent = "<{}>\n\nprincipal_components = \n{}\n\nmean = {}".format(model_type, attributes_["principal_components"], attributes_["mean"])
        elif model_type in ("SVD",):
            if ("vectors" not in attributes or "values" not in attributes):
                raise ParameterError("SVD's attributes must include 2 lists: one with all the right singular vectors and one with the singular values of each input feature.")
            attributes_["vectors"] = np.copy(attributes["vectors"])
            attributes_["values"] = np.copy(attributes["values"])
            check_types([("vectors", attributes_["vectors"], [list,],),
                         ("values", attributes_["values"], [list,],),])
            represent = "<{}>\n\nvectors = \n{}\n\nvalues = {}".format(model_type, attributes_["vectors"], attributes_["values"])
        elif model_type in ("Normalizer",):
            if ("values" not in attributes or "method" not in attributes):
                raise ParameterError("Normalizer's attributes must include a list including the model's aggregations and a string representing the model's method.")
            attributes_["values"] = np.copy(attributes["values"])
            attributes_["method"] = attributes["method"]
            check_types([("values", attributes_["values"], [list,],),
                         ("method", attributes_["method"], ["minmax", "zscore", "robust_zscore",],),])
            represent = "<{}>\n\nvalues = {}\n\nmethod = {}".format(model_type, attributes_["values"], attributes_["method"])
        else:
            raise ParameterError("Model type '{}' is not yet available.".format(model_type))
        self.attributes_ = attributes_
        self.model_type_ = model_type
        self.represent_ = represent

    # ---#
    def __repr__(self):
        return self.represent_

    #
    # Methods
    #
    # ---#
    def get_attributes(self,):
        """
    ---------------------------------------------------------------------------
    Returns model's attributes.
        """
        return self.attributes_

    # ---#
    def set_attributes(self, attributes: dict,):
        """
    ---------------------------------------------------------------------------
    Sets new model's attributes.

    Parameters
    ----------
    attributes: dict
        New attributes. See method '__init__' for more information.
        """
        attributes_tmp = {}
        for elem in self.attributes_:
            attributes_tmp[elem] = self.attributes_[elem]
        for elem in attributes:
            attributes_tmp[elem] = attributes[elem]
        self.__init__(model_type=self.model_type_, attributes=attributes_tmp)

    # ---#
    def predict(self, X: list):
        """
    ---------------------------------------------------------------------------
    Predicts using the model's attributes.

    Parameters
    ----------
    X: list / numpy.array
        data.

    Returns
    -------
    numpy.array
        Predicted values
        """
        if self.model_type_ in ("LinearRegression", "LinearSVC", "LinearSVR", "LogisticRegression",):
            return predict_from_coef(X, self.attributes_["coefficients"], self.attributes_["intercept"], self.model_type_,)
        elif self.model_type_ in ("KMeans",):
            return predict_from_clusters(X, self.attributes_["clusters"], p=self.attributes_["p"])
        elif self.model_type_ in ("NearestCentroids",):
            return predict_from_clusters(X, self.attributes_["clusters"], p=self.attributes_["p"], classes=self.attributes_["classes"])
        elif self.model_type_ in ("BisectingKMeans",):
            return predict_from_bisecting_kmeans(X, self.attributes_["clusters"], self.attributes_["left_child"], self.attributes_["right_child"], p=self.attributes_["p"])
        elif self.model_type_ in ("BinaryTreeRegressor", "BinaryTreeClassifier",):
            return predict_from_binary_tree(X, self.attributes_["children_left"], self.attributes_["children_right"], self.attributes_["feature"], self.attributes_["threshold"], self.attributes_["value"], self.attributes_["classes"] if self.model_type_ in ("BinaryTreeClassifier",) else [], is_regressor=self.model_type_ in ("BinaryTreeRegressor",),)
        elif self.model_type_ in ("RandomForestRegressor", "XGBoostRegressor",):
            result = [tree.predict(X) for tree in self.attributes_["trees"]]
            if self.model_type_ in ("RandomForestRegressor",):
                return np.average(np.column_stack(result), axis=1)
            else:
                return np.sum(np.column_stack(result), axis=1) * self.attributes_["learning_rate"] + self.attributes_["mean"]
        elif self.model_type_ in ("RandomForestClassifier", "XGBoostClassifier",):
            result = np.argmax(self.predict_proba(X), axis=1)
            result = np.array([self.attributes_["trees"][0].attributes_["classes"][i] for i in result])
            return result
        else:
            raise FunctionError("Method 'predict' is not available for model type '{}'.".format(self.model_type_))

    # ---#
    def predict_sql(self, X: list):
        """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy the model.

    Parameters
    ----------
    X: list
        Names or values of the input predictors.

    Returns
    -------
    str
        SQL code
        """
        if self.model_type_ in ("LinearRegression", "LinearSVC", "LinearSVR", "LogisticRegression",):
            result = sql_from_coef(X, self.attributes_["coefficients"], self.attributes_["intercept"], self.model_type_,)
            if self.model_type_ in ("LinearSVC", "LogisticRegression",):
                result = "(({}) > 0.5)::int".format(result)
            return result
        elif self.model_type_ in ("KMeans",):
            return sql_from_clusters(X, self.attributes_["clusters"], p=self.attributes_["p"])
        elif self.model_type_ in ("NearestCentroids",):
            return sql_from_clusters(X, self.attributes_["clusters"], p=self.attributes_["p"], classes=self.attributes_["classes"])
        elif self.model_type_ in ("BisectingKMeans",):
            return sql_from_bisecting_kmeans(X, self.attributes_["clusters"], self.attributes_["left_child"], self.attributes_["right_child"], p=self.attributes_["p"])
        elif self.model_type_ in ("BinaryTreeRegressor", "BinaryTreeClassifier",):
            return sql_from_binary_tree(X, self.attributes_["children_left"], self.attributes_["children_right"], self.attributes_["feature"], self.attributes_["threshold"], self.attributes_["value"], self.attributes_["classes"] if self.model_type_ in ("BinaryTreeClassifier",) else [], is_regressor=self.model_type_ in ("BinaryTreeRegressor",),)
        elif self.model_type_ in ("RandomForestRegressor", "XGBoostRegressor",):
            result = [tree.predict_sql(X) for tree in self.attributes_["trees"]]
            if self.model_type_ in ("RandomForestRegressor",):
                return "(" + " + ".join(result) + ") / {}".format(len(result))
            else:
                return "(" + " + ".join(result) + ") * {} + {}".format(self.attributes_["learning_rate"], self.attributes_["mean"],)
        elif self.model_type_ in ("RandomForestClassifier", "XGBoostClassifier",):
            classes = self.attributes_["trees"][0].attributes_["classes"]
            m = len(classes)
            result_proba = self.predict_proba_sql(X,)
            if m == 2:
                return "(CASE WHEN {} > 0.5 THEN {} ELSE {} END)".format(result_proba[1], classes[1], classes[0])
            else:
                sql = []
                for i in range(m):
                    list_tmp = []
                    for j in range(i):
                        list_tmp += ["{} <= {}".format(result_proba[i], result_proba[j])]
                    sql += [" AND ".join(list_tmp)]
                sql = sql[1:]
                sql.reverse()
                sql_final = "CASE WHEN {} THEN NULL".format(" OR ".join(["{} IS NULL".format(elem) for elem in X]))
                for i in range(m - 1):
                    class_i = classes[m - i - 1]
                    sql_final += " WHEN {} THEN {}".format(sql[i], "'{}'".format(class_i) if isinstance(class_i, str) else class_i)
                sql_final += " ELSE {} END".format("'{}'".format(classes[0]) if isinstance(classes[0], str) else classes[0])
                return sql_final
        else:
            raise FunctionError("Method 'predict_sql' is not available for model type '{}'.".format(self.model_type_)) 

    # ---#
    def predict_proba(self, X: list,):
        """
    ---------------------------------------------------------------------------
    Predicts probabilities using the model's attributes.

    Parameters
    ----------
    X: list / numpy.array
        data.

    Returns
    -------
    numpy.array
        Predicted values
        """
        if self.model_type_ in ("LinearSVC", "LogisticRegression",):
            return predict_from_coef(X, self.attributes_["coefficients"], self.attributes_["intercept"], self.model_type_, return_proba=True,)
        elif self.model_type_ in ("KMeans",):
            return predict_from_clusters(X, self.attributes_["clusters"], p=self.attributes_["p"], return_proba=True,)
        elif self.model_type_ in ("NearestCentroids",):
            return predict_from_clusters(X, self.attributes_["clusters"], p=self.attributes_["p"], classes=self.attributes_["classes"], return_proba=True,)
        elif self.model_type_ in ("BinaryTreeClassifier",):
            return predict_from_binary_tree(X, self.attributes_["children_left"], self.attributes_["children_right"], self.attributes_["feature"], self.attributes_["threshold"], self.attributes_["value"], self.attributes_["classes"], True, is_regressor=False,)
        elif self.model_type_ in ("RandomForestClassifier",):
            result, n = 0, len(self.attributes_["trees"])
            for i in range(n):
                result_tmp = self.attributes_["trees"][i].predict_proba(X)
                result_tmp_arg = np.zeros_like(result_tmp)
                result_tmp_arg[np.arange(len(result_tmp)), result_tmp.argmax(1)] = 1
                result += result_tmp_arg
            return result / n
        elif self.model_type_ in ("XGBoostClassifier",):
            result = 0
            for tree in self.attributes_["trees"]:
                result += tree.predict_proba(X)
            result = self.attributes_["logodds"] + self.attributes_["learning_rate"] * result
            result = 1 / (1 + np.exp(- result))
            result /=  np.sum(result, axis=1)[:,None]
            return result
        else:
            raise FunctionError("Method 'predict_proba' is not available for model type '{}'.".format(self.model_type_))

    # ---#
    def predict_proba_sql(self, X: list):
        """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy the probabilities model.

    Parameters
    ----------
    X: list
        Names or values of the input predictors.

    Returns
    -------
    str
        SQL code
        """
        if self.model_type_ in ("LinearSVC", "LogisticRegression",):
            result = sql_from_coef(X, self.attributes_["coefficients"], self.attributes_["intercept"], self.model_type_,)
            return ["1 - ({})".format(result), result] 
        elif self.model_type_ in ("KMeans",):
            return sql_from_clusters(X, self.attributes_["clusters"], p=self.attributes_["p"], return_proba=True,)
        elif self.model_type_ in ("NearestCentroids",):
            return sql_from_clusters(X, self.attributes_["clusters"], p=self.attributes_["p"], classes=self.attributes_["classes"], return_proba=True,)
        elif self.model_type_ in ("BinaryTreeClassifier",):
            return sql_from_binary_tree(X, self.attributes_["children_left"], self.attributes_["children_right"], self.attributes_["feature"], self.attributes_["threshold"], self.attributes_["value"], self.attributes_["classes"], True, is_regressor=False,)
        elif self.model_type_ in ("RandomForestClassifier",):
            trees, n, m = [], len(self.attributes_["trees"]), len(self.attributes_["trees"][0].attributes_["classes"])
            for i in range(n):
                val = []
                for elem in self.attributes_["trees"][i].attributes_["value"]:
                    if isinstance(elem, type(None)):
                        val += [elem]
                    else:
                        value_tmp = np.zeros_like([elem])
                        value_tmp[np.arange(1), np.array([elem]).argmax(1)] = 1
                        val += [list(value_tmp[0])]
                tree = memModel("BinaryTreeClassifier", {"children_left": self.attributes_["trees"][i].attributes_["children_left"],
                                                         "children_right": self.attributes_["trees"][i].attributes_["children_right"],
                                                         "feature": self.attributes_["trees"][i].attributes_["feature"],
                                                         "threshold": self.attributes_["trees"][i].attributes_["threshold"],
                                                         "value": val,
                                                         "classes": self.attributes_["trees"][i].attributes_["classes"],})
                trees += [tree]
            result = [trees[i].predict_proba_sql(X) for i in range(n)]
            classes_proba = []
            for i in range(m):
                classes_proba += ["(" + " + ".join([val[i] for val in result]) + ") / {}".format(n)]
            return classes_proba
        elif self.model_type_ in ("XGBoostClassifier",):
            result, n, m = [], len(self.attributes_["trees"]), len(self.attributes_["trees"][0].attributes_["classes"])
            all_probas = [self.attributes_["trees"][i].predict_proba_sql(X) for i in range(n)]
            for i in range(m):
                result += ["(1 / (1 + EXP(- ({} + {} * (".format(self.attributes_["logodds"][i], self.attributes_["learning_rate"]) + " + ".join(all_probas[i]) + ")))))"]
            sum_result = "(" + " + ".join(result) + ")"
            result = [item + " / {}".format(sum_result) for item in result]
            return result
        else:
            raise FunctionError("Method 'predict_proba_sql' is not available for model type '{}'.".format(self.model_type_))

    # ---#
    def transform(self, X: list):
        """
    ---------------------------------------------------------------------------
    Transforms the data using the model's attributes.

    Parameters
    ----------
    X: list / numpy.array
        Data to transform.

    Returns
    -------
    numpy.array
        Transformed data
        """
        if self.model_type_ in ("Normalizer",):
            return transform_from_normalizer(X, self.attributes_["values"], self.attributes_["method"],)
        elif self.model_type_ in ("PCA",):
            return transform_from_pca(X, self.attributes_["principal_components"], self.attributes_["mean"],)
        elif self.model_type_ in ("SVD",):
            return transform_from_svd(X, self.attributes_["vectors"], self.attributes_["values"],)
        elif self.model_type_ in ("OneHotEncoder",):
            return transform_from_one_hot_encoder(X, self.attributes_["categories"], self.attributes_["drop_first"],)
        elif self.model_type_ in ("KMeans", "NearestCentroids", "BisectingKMeans",):
            return predict_from_clusters(X, self.attributes_["clusters"], return_distance_clusters=True)
        else:
            raise FunctionError("Method 'transform' is not available for model type '{}'.".format(self.model_type_))

    # ---#
    def transform_sql(self, X: list):
        """
    ---------------------------------------------------------------------------
    Returns the SQL code needed to deploy the model.

    Parameters
    ----------
    X: list
        Name or values of the input predictors.

    Returns
    -------
    list
        SQL code
        """
        if self.model_type_ in ("Normalizer",):
            return sql_from_normalizer(X, self.attributes_["values"], self.attributes_["method"],)
        elif self.model_type_ in ("PCA",):
            return sql_from_pca(X, self.attributes_["principal_components"], self.attributes_["mean"],)
        elif self.model_type_ in ("SVD",):
            return sql_from_svd(X, self.attributes_["vectors"], self.attributes_["values"],)
        elif self.model_type_ in ("OneHotEncoder",):
            return sql_from_one_hot_encoder(X, self.attributes_["categories"], self.attributes_["drop_first"], self.attributes_["column_naming"],)
        elif self.model_type_ in ("KMeans", "NearestCentroids", "BisectingKMeans",):
            return sql_from_clusters(X, self.attributes_["clusters"], return_distance_clusters=True)
        else:
            raise FunctionError("Method 'transform_sql' is not available for model type '{}'.".format(self.model_type_))

    # ---#
    def rotate(self, gamma: float = 1.0, q: int = 20, tol: float = 1e-6):
        """
    ---------------------------------------------------------------------------
    Performs a Oblimin (Varimax, Quartimax) rotation on the the model's 
    PCA matrix.

    Parameters
    ----------
    gamma: float, optional
        Oblimin rotation factor, determines the type of rotation.
        It must be between 0.0 and 1.0.
            gamma = 0.0 results in a Quartimax rotation.
            gamma = 1.0 results in a Varimax rotation.
    q: int, optional
        Maximum number of iterations.
    tol: float, optional
        The algorithm stops when the Frobenius norm of gradient is less than tol.

    Returns
    -------
    self
        memModel
        """
        from verticapy.learn.tools import matrix_rotation

        if self.model_type_ in ("PCA",):
            principal_components = matrix_rotation(self.get_attributes()["principal_components"], gamma, q, tol)
            self.set_attributes({"principal_components": principal_components})
        else:
            raise FunctionError("Method 'rotate' is not available for model type '{}'.".format(self.model_type_))
        return self