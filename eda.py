import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from scipy import stats
from typing import Sequence

def is_symmetric(
    var: pd.Series | Sequence, 
    tolerance: float = 1
) -> bool:
    '''
    **Mô tả:** Ta có độ lệch S, ngưỡng đối xứng cho phép t. Hàm số thỏa mãn nếu |S| < t.

    **Đối số:**
    1. `var`: Biến cần xét.
    2. `tolerance`: Ngưỡng đối xứng cho phép (Mặc định 1).
    '''
    if not type(var) == pd.Series:
        var = pd.Series(var)

    S = var.skew()
    return np.abs(S) < tolerance

def check_df_symmetry(
    df: pd.DataFrame,
    tolerance: float = 1,
    visualize: bool = False
): 
    '''
    **Mô tả:** Kiểm tra đối xứng của các biến dạng số:

    **Đối số:**
    1. `df`: DataFrame.
    2. `tolerance`: Ngưỡng đối xứng cho phép.
    3. `visuallize`: Trực quan hóa biểu đồ histogram của các biến (Mặc định False).
    '''
    numeric_cols = df.select_dtypes(np.number)
    d = {}

    if visualize:
        cols = 4
        rows = int(np.ceil(numeric_cols.columns.shape[0] / cols))
        plt.figure().set_size_inches(25, 20)
    
    for i, col in enumerate(numeric_cols):
        is_sym = is_symmetric(df[col], tolerance)
        d[col] = is_sym

        if visualize:
            ax = plt.subplot(rows, cols, i+1)
            df[col].plot.hist(bins=20, color="lightgreen", edgecolor="black")
            plt.title("Symmetric" if is_sym else "Asymmetric")
            ax.set_xlabel(col)
    return d

def is_dependent(
    x: pd.Series | Sequence,
    y: pd.Series | Sequence,
    c: float = .95
):
    '''
    **Mô tả:** Kiểm tra sự phụ thuộc của biến $y$ đối với biến $x$:

    **Đối số:**
    1. `x`: Biến $x$.
    2. `y`: Biến $y$.
    3. `c`: Độ tin cậy (Mặc định 95%).
    '''
    rho, p = stats.pearsonr(x, y)
    alpha = 1 - c
    Ha = lambda p, a: p < a

    return Ha(p, alpha)

def check_df_dependency(
    df: pd.DataFrame,
    y: str,
    c: float = .95,
    visualize: bool = True
):
    '''
    ** Mô tả:** Kiểm tra sự phụ thuộc của biến y với các biến dạng số:

    **Đối số:**
    1. `df`: DataFrame.
    2. `y`: Biến phụ thuộc cần xét.
    3. `c`: Độ tin cậy (Mặc định 95%).
    4. `visualize`: Trực quan hóa bằng biểu đồ hồi quy (Mặc định True).
    '''
    numeric_cols = df.select_dtypes(np.number).columns
    d = {}

    if visualize:
        cols = 4
        rows = int(np.ceil(numeric_cols.shape[0] / cols))
        plt.figure().set_size_inches(25, 20)
    
    for i, col in enumerate(numeric_cols.drop(y)):
        dep = is_dependent(df[col], df[y], c=c)
        d[col] = dep
        
        if visualize:
            ax = plt.subplot(rows, cols, i+1)
            sns.regplot(df, x=col, y=y, ci=5)
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            plt.title("Có ảnh hưởng" if dep else "Không / Ít ảnh hưởng")
    return d

def dependency_ranking(
    df: pd.DataFrame,
    y: str,
    asc: bool = False
):
    '''
    **Mô tả:** Sắp xếp các biến có ảnh hưởng dựa trên hệ số tương quan:

    **Đối số:**
    1. `df`: DataFrame.
    2. `y`: Biến phụ thuộc.
    3. `asc`: Sắp xếp theo rank từ thấp đến cao (Mặc định False).
    '''
    deps = check_df_dependency(df, y, visualize=False)
    xs = {
        col: np.abs( df[col].corr(df[y]) )
            for col, is_dep in deps.items() 
        if is_dep
    }
    return sorted(xs, key=xs.get, reverse=not asc)

def categorical_dependency_ranking(
    df: pd.DataFrame,
    xs: Sequence[str] | str,
    y: str,
    min_freq: int = 3,
    asc: bool = False
):
    '''
    **Mô tả:** Sắp xếp các biến phân loại có ảnh hưởng dựa trên giá trị trung bình của biến đích:

    **Đối số:**
    1. `df`: DataFrame.
    2. `xs`: Tên (các) biến phân loại.
    3. `y`: Tên biến đích.
    4. `min_freq`: Tần suất tối thiểu của (tập) giá trị phân loại để tiến hành xem xét (Mặc định 3).
    5. `asc`: Sắp xếp theo rank từ thấp đến cao (Mặc định False).
    '''
    if type(xs) == str:
        xs = [xs]

    vars: np.ndarray[str] = np.concatenate([xs, [y]])
    groups = df[vars].groupby(xs)

    groups = groups.mean()[groups.count() >= min_freq].dropna()
    groups.sort_values(y, ascending=False, inplace=not asc)
    return groups.index.to_list()

def values_by_group(
    df: pd.DataFrame,
    xs: Sequence[str] | str,
    y: str
) -> dict:
    '''
    **Mô tả:** Tạo ra tập các giá trị của biến đích xuất hiện trong nhóm giá trị phân loại

    **Đối số:**
    1. `df`: DataFrame.
    2. `xs`: Tập các biến phân loại cần gom nhóm với nhau.
    3. `y`: Biến đích.
    '''
    grs = df.groupby(xs, observed=True).groups
    for g, idx in grs.items():
        grs[g] = df[y][idx]
    return grs

def is_dependent_categorical(
    x: pd.Series | Sequence,
    y: pd.Series | Sequence,
    c: float = .95
):
    '''
    **Mô tả:** Kiểm tra sự ảnh hưởng của biến phân loại đến biến phụ thuộc:

    **Đối số:**
    1. `x`: Các mẫu của biến phân loại $x$.
    2. `y`: Các mẫu của biến phụ thuộc $y$.
    3. `c`: Độ tin cây chp phép kiểm định (Mặc định 95%).
    '''
    df1 = pd.DataFrame({"x": x, "y": y})
    grs = values_by_group(df1, xs="x", y="y")

    if len(grs.keys()) == 1:
        return 0, 1
    
    F, p = stats.f_oneway(*grs.values())

    alpha = 1 - c
    return F, p < alpha

def k_best_categorical_vars(
    df: pd.DataFrame,
    y: str,
    k: int = 3,
    visualize: bool = True
):
    '''
    **Mô tả:** Chọn ra k biến có mức ảnh hưởng tốt nhất tới biến phụ thuộc:

    **Đối số:**
    1. `df`: DataFrame.
    2. `y`: Tên biến phụ thuộc.
    3. `k`: Số lượng biến tốt nhất cần chọn (Mặc định 3).
    4. `visualize`: Trực quan hóa các giá trị F bằng biểu đồ cột (Mặc định True).
    '''
    cat_vars = df.select_dtypes(['category', 'object'])
    
    if visualize:
        plt.ylabel("F Statistic")
        plt.xticks(rotation=90)
    
    lst = {}
    for col in cat_vars.columns:
        F, is_signif = is_dependent_categorical(
            df[col], df[y]
        )

        if is_signif:
            lst[col] = F
            if visualize:
                plt.bar(col, F, color="lightgreen", edgecolor="black")
    
    result = sorted(lst, key=lst.get, reverse=True)[:k]
    return result if k == -1 else result[:k]

def select_features(
    df: pd.DataFrame,
    y: str,
    k_numerical: int = 3,
    k_categorical: int = 0,
    exclude: str | Sequence[str] = None,
    one_hot: bool = True,
    test_size: float | None = None,
    random_state: int | None = None
):
    '''
    **Mô tả:** Chọn ra các đặc trưng tốt nhất từ dataset (đã được tiền xử lý)

    **Đối số:**
    1. `df`: DataFrame
    2. `y`: Tên biến phụ thuộc
    3. `k_numerical`: Số lượng biến dạng số cần chọn (Mặc định 3)
    4. `k_categorical`: Số lượng biến dạng phân loại cần chọn (Mặc định 0)
    5. `exclude`: Các tên biến được liệt kê sẽ không được xem xét (Mặc định None - xem xét tất cả)
    5. `one_hot`: Chuyển đổi biến phân loại thành dạng one-hot. (Mặc định True)
    6. `test_size`: Tỉ lệ phân chia dataset thành tập train (Mặc định None - không phân chia)
    7. `random_state`: Random seed (Mặc định None - không cố định)
    '''
    df = df.drop(columns=exclude) if exclude else df
    numerical_vars = dependency_ranking(df=df, y=y)
    numerical_vars = numerical_vars if k_numerical == -1 else numerical_vars[:k_numerical]
    categorical_vars = k_best_categorical_vars(df=df, y=y, k=k_categorical, visualize=False)
    X = df[numerical_vars + categorical_vars]
    if one_hot:
        X = pd.get_dummies(X, dtype=np.int8)
    Y = df[y]

    if test_size is None:
        return X, Y
    
    xtrain, xtest, ytrain, ytest = train_test_split(
        X, Y, 
        test_size=test_size, 
        random_state=random_state,
    )
    return (xtrain, ytrain), (xtest, ytest)

class FeatureSelector:
    def __init__(
        self,
        k_numerical: int = 4,
        k_categorical: int = 0,
        one_hot: bool = True
    ) -> None:
        self.k_numerical = k_numerical
        self.k_categorical = k_categorical
        self.one_hot = one_hot
    
    def fit(
        self, 
        df: pd.DataFrame,
        y: str,
    ):
        X, _ = self._select_features(df, y=y)
        self.feature_names = X.columns
        self.feature_dtypes = {
            name: dtype
            for name, dtype in zip(X.columns, X.dtypes)
        }
        self.y_name = y
        return self
    
    def select(
        self,
        df: pd.DataFrame,
    ):
        if self.one_hot:
            df = pd.get_dummies(df, dtype=np.int8)

            categories = set()
            for name, dtype in self.feature_dtypes.items():
                if dtype == "int8":
                    categories.add(name)
            
            not_exist = categories - set(df.select_dtypes(include=["bool", "int8"]).columns)
            for col in not_exist:
                df[col] = 0
        
        return df[self.feature_names], df[self.y_name]

    def _select_features(
        self,
        df: pd.DataFrame,
        y: str,
        exclude: str | Sequence[str] = None,
        test_size: float | None = None,
        random_state: int | None = None
    ):
        df = df.drop(columns=exclude) if exclude else df
        numerical_vars = dependency_ranking(df=df, y=y)
        numerical_vars = numerical_vars if self.k_numerical == -1 else numerical_vars[:self.k_numerical]
        categorical_vars = k_best_categorical_vars(df=df, y=y, k=self.k_categorical, visualize=False)
        X = df[numerical_vars + categorical_vars]
        if self.one_hot:
            X = pd.get_dummies(X, dtype=np.int8)
        Y = df[y]

        if test_size is None:
            return X, Y
        
        xtrain, xtest, ytrain, ytest = train_test_split(
            X, Y, 
            test_size=test_size, 
            random_state=random_state,
        )
        return (xtrain, ytrain), (xtest, ytest)