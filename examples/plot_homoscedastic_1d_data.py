"""
==========================================================
Estimate the prediction intervals of 1D homoscedastic data
==========================================================

:class:`mapie.MapieRegressor` is used to estimate
the prediction intervals of 1D homoscedastic data using
different methods.
"""
from typing import Any, Union

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from matplotlib import pyplot as plt

from mapie import MapieRegressor


def f(x: np.ndarray) -> np.ndarray:
    """Polynomial function used to generate one-dimensional data"""
    return 5*x + 5*x ** 4 - 9*x**2


def get_homoscedastic_data(
    n_samples: str = 200,
    n_test: int = 1000,
    sigma: float = 0.1
) -> Union[
    np.ndarray,
    np.ndarray,
    float,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    float
]:
    """
    Generate one-dimensional data from a given function,
    number of training and test samples and a given standard
    deviation for the noise.

    Parameters
    ----------
    n_samples (str, optional):
        Number of training samples. Defaults to 200.
    n_test (int, optional):
        Number of test samples. Defaults to 1000.
    sigma (float, optional):
        Standard deviation of noise. Defaults to 0.1.

    Returns
    -------
    Tuple[
        np.ndarray,
        np.ndarray,
        float,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        float
    ]:
        Generated training and test data.
    """
    np.random.seed(59)
    q90 = 1.8
    X_train = np.random.exponential(0.4, n_samples)
    X_test = np.linspace(0.001, 1.2, n_test, endpoint=False)
    y_train = f(X_train) + np.random.normal(0, sigma, n_samples)
    y_test = f(X_test)
    y_test_sig = q90*sigma
    return X_train, y_train, X_test, y_test, y_test_sig


def plot_1d_data(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    y_test_sigma: np.ndarray,
    y_pred: np.ndarray,
    y_pred_low: np.ndarray,
    y_pred_up: np.ndarray,
    ax: Any,
    title: str
) -> None:
    """
    Generate a figure showing the training data and estimated
    prediction intervals on test data.

    Parameters
    ----------
    X_train (np.ndarray):
        Training data.
    y_train (np.ndarray):
        Training labels.
    X_test (np.ndarray):
        Test data.
    y_test (np.ndarray):
        True function values on test data.
    y_test_sigma (np.ndarray):
        True standard deviation.
    y_pred (np.ndarray):
        Predictions on test data.
    y_pred_low (np.ndarray):
        Predicted lower bounds on test data.
    y_pred_up (np.ndarray):
        Predicted upper bounds on test data.
    axis (Any):
        Axis to plot.
    title (str):
        Title of the figure.
    """
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_xlim([0, 1.1])
    ax.set_ylim([0, 1])
    ax.scatter(X_train, y_train, color='red', alpha=0.3, label='training')
    ax.plot(X_test, y_test, color='gray', label='True confidence intervals')
    ax.plot(X_test, y_test-y_test_sigma, color='gray', ls='--')
    ax.plot(X_test, y_test+y_test_sigma, color='gray', ls='--')
    ax.plot(X_test, y_pred, label='Prediction intervals')
    ax.fill_between(X_test, y_pred_low, y_pred_up, alpha=0.3)
    ax.set_title(title)
    ax.legend()


X_train, y_train, X_test, y_test, y_test_sigma = get_homoscedastic_data(
    n_samples=200, n_test=200, sigma=0.1
)

polyn_model = Pipeline(
    [
        ('poly', PolynomialFeatures(degree=4)),
        ('linear', LinearRegression(fit_intercept=False))
    ]
)

methods = ['jackknife', 'jackknife_plus', 'jackknife_minmax', 'cv', 'cv_plus', 'cv_minmax']
preds, lows, ups = [], [], []
fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(3*6, 12))
axs = [ax1, ax2, ax3, ax4, ax5, ax6]
for i, method in enumerate(methods):
    pireg = MapieRegressor(
        polyn_model,
        method=method,
        alpha=0.05,
        n_splits=10,
        return_pred='ensemble'
    )
    pireg.fit(X_train.reshape(-1, 1), y_train)
    y_preds = pireg.predict(X_test.reshape(-1, 1))
    plot_1d_data(
        X_train,
        y_train,
        X_test,
        y_test,
        y_test_sigma,
        y_preds[:, 0],
        y_preds[:, 1],
        y_preds[:, 2],
        axs[i],
        method
    )
