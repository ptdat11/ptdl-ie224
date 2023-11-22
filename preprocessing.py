import pandas as pd
import numpy as np
import miceforest as mf
from typing import Any, Callable, Sequence, Literal
from datetime import datetime
import re

class PreprocessPipeline(dict):
    def __init__(
        self,
        steps: dict[
            str, 
            Callable[[pd.DataFrame], pd.DataFrame]
        ] = {}
    ) -> None:
        '''
        **Mô tả:** Khởi tạo object `PreprocessPipeline` và truyền vào các bước thực hiện.

        **Đối số:**
        1. `steps`: Các cặp giá trị (Tên bước xử lý, hàm số f(DataFrame) -> DataFrame)
        '''
        self._dict = super(PreprocessPipeline, self)
        self._dict.__init__(**steps)
    
    def __call__(self, df: pd.DataFrame):
        '''
        **Mô tả:** Áp dụng tất cả các bước xử lý lên DataFrame truyền vào.
        
        **Đối số:**
        1. `df`: DataFrame
        '''
        for step in self._dict.values():
            df = step(df)
        return df
    
    def add(self, name: str, handler: Callable[[pd.DataFrame], pd.DataFrame]):
        '''
        **Mô tả:** Thêm một bước xử lý vào cuối pipeline.

        **Đối số:**
        1. `name`: Tên bước tiền xử lý
            - Note: Nếu trùng tên với các bước trước, `name` sẽ đổi thành "<name>_<STT>"
        2. `handler`: Hàm xử lý
        '''
        key_matches = [
            re.match(rf"^{name}(?:_(\d+))?.*", step_name)
            for step_name in self._dict.keys()
        ]
        if any(key_matches):
            indices = [
                self._try_parse_int(match.group(1)) 
                for match in key_matches
            ]
            max_idx = np.max(indices)
            self._dict.__setitem__(f"{name}_{max_idx+1 if max_idx else 1}", handler)
        else: self._dict.__setitem__(f"{name}", handler)
    
    def _try_parse_int(self, value: Any):
        try:
            return int(value)
        except:
            return value

def map_cols(
    df: pd.DataFrame,
    cols: str | Sequence[str],
    callback: Callable,
    na_action: Literal["ignore"] | None = "ignore"
):
    '''
    **Mô tả:** ánh xạ các cột trong DataFrame theo một phép biến hình `callback`

    **Đối số:**
    1. `df`: DataFrame
    2. `cols`: (Các) cột cần ánh xạ
    3. `callback`: Phép biến hình $f(x) \rightarrow y$
    4. `na_action`: Chế độ xử lí NaN
        - "ignore": Giữ nguyên giá trị NaN (Mặc định)
        - None: Xử lý theo phép biến hình
    '''
    if type(cols) == str:
        cols = (cols,)
    for col in cols:
        df[col] = df[col].map(callback, na_action=na_action)
    return df

def map_unit(
    df: pd.DataFrame,
    cols: str | Sequence[str],
    unit_mapper: dict[str, float],
    quantity_mapper: Callable = None,
    na_action: Literal["ignore"] | None = "ignore"
):
    '''
    **Mô tả:** ánh xạ từ giá trị dạng chuỗi sang dạng số trong các cột thuộc DataFrame.

    **Đối số:**
    1. `df`: DataFrame
    2. `cols`: (Các) cột cần ánh xạ.
    3. `unit_mapper`: Phép ánh xạ đơn vị về định lượng.
    4. `quantity_mapper`: Hàm số ánh xạ định lượng dạng chuỗi về dạng số (Mặc định None: f(x) -> float(x))
    5. `na_action`: Chế độ xử lí NaN
        - "ignore": Giữ nguyên giá trị NaN (Mặc định)
        - None: Xử lý theo phép biến hình
    '''
    def map_callback(x: str):
        if type(x) != str:
            return x
        
        try:
            quantity, unit = x.rsplit(maxsplit=1)
        except:
            raise ValueError(f"The value {x} format requirement is not met")
        
        for key, val in unit_mapper.items():
            if key in unit:
                quantity_val = quantity_mapper(quantity) if quantity_mapper \
                    else float(quantity.replace(".", "").replace(",", "."))
                return quantity_val * val
    
    return map_cols(df, cols=cols, callback=map_callback, na_action=na_action)

def interval_quant_mapper(x: str):
    '''
    **Mô tả:** ánh xạ từ khoảng định lượng dạng chuỗi sang dạng số.

    **Đối số:**
    1. `x`: Chuỗi có dạng "<mốc dưới> - <mốc trên>"
    '''
    lower, upper = re.search(r"(\d+(?:,\d+)?)\s?[-–]\s?(\d+(?:,\d+)?)", x).groups()
    lower = float(lower.replace(".", "").replace(",", "."))
    upper = float(upper.replace(".", "").replace(",", "."))
    return (lower + upper) / 2

def map_keyword(
    df: pd.DataFrame,
    cols: str | Sequence[str],
    category_keywords_mapper: dict[str, Sequence[str]],
    nomatch_value: Any = np.nan
):
    '''
    **Mô tả:** ánh xạ từ giá trị dạng chuỗi theo giá trị phân loại theo keyword trong các cột thuộc DataFrame
    
    **Đối số:**
    1. `df`: DataFrame
    2. `cols`: (Các) cột cần ánh xạ
    3. `category_keywords_mapper`: Các cặp giá trị (category, các keywords)
        - Note: category phía trên đã khớp thì không xử lý các category dưới.
    4. `nomatch_value`: Giá trị mặc định khi chuỗi không thuộc category nào. (Mặc định NaN)
    '''
    def map_callback(x: str):
        if type(x) != str:
            return x
        
        lower_mapper = {
            cat: tuple(str.lower(kw) for kw in kws)
            for cat, kws in category_keywords_mapper.items()
        }

        for category, kws in lower_mapper.items():
            lower_x = str.lower(x)
            if any(str.lower(kw) in lower_x for kw in kws):
                return category
        return nomatch_value
        
    return map_cols(df, cols=cols, callback=map_callback)

def to_datetime(
    df: pd.DataFrame,
    cols_formats: dict[str, str],
    na_action: Literal["ignore"] | None = "ignore"
):
    '''
    **Mô tả:** chuyển đổi biến dạng chuỗi thành dạng datetime

    **Đối số:**
    1. `df`: DataFrame
    2. `cols_formats`: Các cặp giá trị (tên biến, định dạng datetime)
        - Note: Định dạng datetime có thể xem chi tiết ở [đây](https://www.w3schools.com/python/python_datetime.asp)
    3. `na_action`: Chế độ xử lí NaN
        - "ignore": Giữ nguyên giá trị NaN (Mặc định)
        - None: Xử lý theo phép biến hình
    '''
    for col, format in cols_formats.items():
        df[col] = pd.to_datetime(df[col], format=format)
    return df

def handle_low_freq(
    df: pd.DataFrame,
    by: str, 
    min_freq: int,
    separating_category: str = None,
    action: Literal["remove", "as_other"] = "remove"
):
    '''
    **Mô tả:** xử lý những mẫu có giá trị biến thuộc tần suất thấp

    **Đối số:**
    1. `df`: DataFrame
    2. `by`: Tên biến cần tính tần suất
    3. `min_freq`: Ngưỡng tần suất thấp nhất để giữ lại các mẫu
    4. `separating_category`: Xét riêng lẻ trên các giá trị của biến phân loại
    5. `action`: Hành động áp dụng lên các mẫu thuộc phân loại tần suất thấp
        - "remove": Loại bỏ mẫu.
        - "as_other": Gom thành phân loại `other` mới.
    '''
    groups = df.groupby(
        [by, separating_category] if separating_category is not None \
            else by, 
        observed=True
    )
    low_freq_indices = groups[by].transform('count').lt(min_freq)
    
    if action == "remove":
        df = df.loc[~low_freq_indices]
    elif action == "as_other":
        if df[by].dtype == 'category' and "other" not in df[by].cat.categories:
            df.loc[:, by] = df[by].cat.add_categories("other")
        df.loc[low_freq_indices, by] = "other"
    
    if df[by].dtype == "category":
        df.loc[:, by] = df[by].cat.remove_unused_categories()

    return df

def as_other(
    df: pd.DataFrame,
    by: str,
    categories: str | Sequence[str]
):
    '''
    **Mô tả:** chuyển đổi (các) giá trị phân loại của một biến thành "other"

    **Đối số:**
    1. `df`: DataFrame
    2. `by`: Tên biến cần chuyển giá trị
    3. `categories`: (Các) giá trị phân loại cần chuyển thành "other"
    '''
    if type(categories) == str:
        categories = (categories,)
        
    if df[by].dtype == 'category' and not "other" in df[by].cat.categories:
        df[by] = df[by].cat.add_categories("other")
    
    for category in categories:
        is_cat = df[by] == category
        df.loc[is_cat, by] = "other"
        if df[by].dtype == 'category':
            df[by] = df[by].cat.remove_categories(category)
    return df

def to_categorical(
    df: pd.DataFrame,
    cols_categories: dict[str, Sequence[Any] | None]
):
    '''
    **Mô tả:** chuyển đổi biến dạng chuỗi thành dạng phân loại

    **Đối số:**
    1. `df`: DataFrame
    2. `cols_categories`: Các cặp giá trị (tên biến, các giá trị phân loại của biến (categories) hoặc None)
        - None: Nominal
        - categories: Ordinal (sắp xếp theo chiều tăng dần)
    '''
    for col, categories in cols_categories.items():
        df[col] = pd.Categorical(
            df[col],
            categories=categories,
            ordered=categories is not None
        )
    return df
    
def remove_outliers(
    df: pd.DataFrame,
    by: str,
    method: Literal["boxplot", "z-score"] = "boxplot",
    separating_categories: str = None,
    range: float = None
):
    '''
    **Mô tả:** loại bỏ các giá trị ngoại lệ

    **Đối số:**
    1. `df`: DataFrame
    2. `by`: Tên biến cần xem xét giá trị
    3. `method`: Phương pháp loại bỏ
        - "boxplot": Sử dụng khoảng tứ phân vị (Mặc định)
        - "z-score": Sử dụng z-score
    4. `separating_category`: Xét riêng lẻ trên các giá trị của biến phân loại
    5. `range`: Độ rộng của không gian mẫu được giữ lại
        - "boxplot": Mặc định 1.5
        - "z-score": Mặc định 2.5
    '''
    sep_cat_uniques = df[separating_categories].unique()

    outlier_count = 0
    
    for cat in sep_cat_uniques:
        is_cat = df[separating_categories] == cat if cat is not None \
            else True

        lextr, uextr = df[by].min(), df[by].max()

        if method == "boxplot":
            range = 1.5 if range is None else range
            Q1, Q3 = np.percentile(df[by], [25, 75])
            IQR = Q3 - Q1
            lextr, uextr = Q1-range*IQR, Q3+range*IQR

        elif method == "z-score":
            range = 2.5 if range is None else range
            mean = df[by].mean()
            std = df[by].std()
            lextr, uextr = mean-range*std, mean+range*std

        print(f"{cat}: {lextr:.2f} < {by} < {uextr:.2f}")
        
        too_low = df[by] < lextr
        too_high = df[by] > uextr
        are_outliers = is_cat & (too_low | too_high)

        outlier_count += are_outliers.sum()
        df = df.loc[~are_outliers, :]

    sample_count = df.shape[0]
    outlier_p = outlier_count / sample_count * 100
    print(f"{outlier_count}/{sample_count} = {outlier_p:.2f}% of the samples are removed")
    return df

def fill_na(
    df: pd.DataFrame,
    by: str | Sequence[str],
    value: Any,
    indices: Sequence[bool] = True,
):
    if indices:
        indices =np.full((df.shape[0],), True)
    df.loc[indices, by] = df.loc[indices, by].fillna(value)
    return df

def mf_impute(
    df: pd.DataFrame,
    exclude: str | Sequence[str] = None,
    numeric_only: bool = True,
    iterations: int = 5
) -> pd.DataFrame:
    '''
    
    '''
    if type(exclude) == str:
        exclude = (exclude,)
    
    to_impute = df.select_dtypes(include=np.number) if numeric_only \
        else df
    not_numeric = df.select_dtypes(exclude=np.number).columns
    if exclude is not None:
        to_exclude = to_impute.columns.intersection(exclude)
        to_impute.drop(columns=to_exclude, inplace=True)
        to_exclude = to_exclude.union(not_numeric)

    kernel = mf.ImputationKernel(to_impute)
    kernel.mice(iterations=iterations)

    result = pd.concat([df[to_exclude], kernel.complete_data()], axis=1)
    return result