import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.base import RegressorMixin
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Any, Sequence, Literal

SupportedEvaluationMetrics = Literal["r2_score", "mse", "mae"]
SupportedMetricRankingMethods = {
    "r2_score": "max",
    "mse": "min",
    "mae": "min"
}

class SkLearnModelEvaluator(dict):
    '''
    Nhận vào danh sách các mô hình hồi quy thuộc Scikit-Learn để train và đánh giá dựa trên các thang đo nhất định.
    '''
    def __init__(
        self,
        name_model_pairs: dict[str, RegressorMixin],
    ) -> None:
        '''
        **Mô tả:** Khởi tạo object `SkLearnModelEvaluator` và truyền vào các model cần so sánh với nhau.

        **Đối số:**
        1. `name_model_pairs`: Các cặp giá trị (Tên model, model instance)
        '''
        self._pairs = name_model_pairs
        self.names = tuple(name_model_pairs.keys())
        self.models = tuple(name_model_pairs.values())

        super(SkLearnModelEvaluator, self).__init__(**name_model_pairs)

    def fit(
        self,
        data: Tuple[Any, Any],
        normalize: bool = False
    ):
        '''
        **Mô tả:** Huấn luyện hàng loạt các model đã được truyền vào `__init__`.

        **Đối số:**
        1. `data`: Cặp giá trị (X, y)
        2. `normalize`: Chuẩn hóa hay không (Mặc định False)
        '''
        X, y = data
        if normalize:
            X = self._normalize(X)
        
        for model in self.models:
            if not hasattr(model, "fit"):
                raise ValueError(f"fit method not found in {model.__class__} instance")
            
            model = model.fit(X, y)
        
        return self

    def evaluate(
        self,
        data: Tuple[Any, Any],
        metrics: Sequence[SupportedEvaluationMetrics] = ("r2_score",),
        normalize: bool = False,
    ):
        '''
        **Mô tả:** Đánh giá tất cả model đã cho bằng các loại thang đo.

        **Đối số:**
        1. `data`: Cặp giá trị (X, y)
        2. `metrics`: Các thang đo để đánh giá: "r2_score", "mse", "mae" (Mặc định "r2_score")
        3. `normalize`: Có chuẩn hóa hay không (Mặc định False)
        '''
        X, y = data
        
        model_evals = []
        for name, model in zip(self.names, self.models):
            preds = self._predict(model, X, normalize=normalize)

            evals = {
                "model_name": name
            }
            for metric in metrics:
                if metric == "mae":
                    metric_val = mean_absolute_error(y, preds)
                elif metric == "mse":
                    metric_val = mean_squared_error(y, preds)
                else: metric_val = r2_score(y, preds)
                evals[metric] = metric_val
        
            model_eval = pd.Series(evals)
            model_evals.append(model_eval)
        
        result = pd.concat(model_evals, axis=1).T.set_index("model_name")
        self.evals = result

        return result
    
    def best_model(
        self,
        data: Tuple[Any, Any] = None,
        metrics: Sequence[SupportedEvaluationMetrics] = ("r2score",),
        normalize: bool = False,
        show_evals: bool = False
    ):
        '''
        **Mô tả:** Chọn ra model tốt nhất.

        **Đối số:**
        1. `data`: Cặp giá trị (X, y). (Mặc định None - giả dụ rằng object đã gọi hàm `evaluate`)
        2. `metrics`: Các thang đo đánh giá: "r2_score", "mse", "mae" (Mặc định "r2_score")
        3. `normalize`: Có chuẩn hóa hay không (Mặc định False)
        4. `show_evals`: Có in ra bảng các chỉ số thang đó hay không (Mặc định False)
        '''
        if self.evals is None:
            if data is None:
                raise ValueError(f"No pre-computed evaluations or data provided to compute the new ones")
            self.evaluate(
                data=data, 
                metrics=metrics, 
                normalize=normalize
            )
        
        if show_evals:
            print(self.evals)

        eval_copy = self.evals.copy()
        for col in eval_copy.columns:
            method = SupportedMetricRankingMethods[col]
            if method == "min":
                eval_copy[col] = -eval_copy[col]
        
        best_model_name = eval_copy.sum(axis=1).idxmax()

        return self._pairs[best_model_name]
    
    def _normalize(self, data):
        X_df = pd.DataFrame(data)

        numerical_vars = X_df.select_dtypes(include=np.number).columns
        numerical_data = X_df[numerical_vars]
        
        scaler = StandardScaler()
        X_df[numerical_vars] = scaler.fit_transform(numerical_data)

        return X_df
    
    def _predict(self, model: RegressorMixin, X, normalize: bool = True):
        if normalize:
            X = self._normalize(X)
        
        if not hasattr(model, "predict"):
            raise ValueError(f"predict method not found in the {model.__class__} instance")
        
        return model.predict(X)

class ErrorTester:
    '''
    Thực hiện phép kiểm định dựa vào mô hình và tập dữ liệu cho trước.
    '''
    def __init__(
        self,
        model: RegressorMixin,
    ) -> None:
        self.model = model
    
    def fit(
        self,
        data: Tuple[Any, Any],
        c: float = .99
    ):
        self.diff = self._compute_diff(data)
        self.c = c
        self.alpha = 1 - c
        self.N: int = data[0].shape[0]
        self.mean: float = self.diff.mean()
        self.std: float = self.diff.std()

        if self.N > 30:
            self.zscore: float = stats.norm.ppf(self.c + self.alpha/2)
        else: self.zscore: float = stats.t.ppf(self.c + self.alpha/2)
        
        self.m = self.zscore * self.std
        self.lower_bound, self.upper_bound = self.mean-self.m, self.mean+self.m

        return self
    
    def predict(self, X):
        return self.model.predict(X)

    def test(
        self,
        data: Tuple[Any, Any]
    ):
        if self.lower_bound is None or self.upper_bound is None:
            raise ValueError(f"No lower_bound and upper_bound attrs found. Call fit(data) to compute them first")
        
        errors = self._compute_diff(data)
        return (self.lower_bound < errors) & (errors < self.upper_bound)
    
    def plot_fitted(self):
        sns.histplot(self.diff, kde=True)
        l_bound = plt.axvline(self.lower_bound, c="r")
        u_bound = plt.axvline(self.upper_bound, c="r", label="Bounds")
        plt.text(self.lower_bound, np.mean(plt.ylim()), f"{self.lower_bound:.2f}")
        plt.text(self.upper_bound, np.mean(plt.ylim()), f"{self.upper_bound:.2f}")
        plt.legend(loc="best")
    
    def _compute_diff(
        self, 
        data: Tuple[Any, Any]
    ):
        X, y = data
        preds = self.model.predict(X)
        return preds - y