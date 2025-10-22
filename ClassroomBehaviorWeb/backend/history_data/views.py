import os

import pandas as pd
from django.http import JsonResponse
from django.shortcuts import redirect

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIN_FILE = os.path.join(BASE_DIR, "login.txt")
DATA_FILE = os.path.join(BASE_DIR, "mydata.csv")
DATA_COLUMNS = [
    "frame",
    "persons",
    "head_up",
    "head_down",
    "head_up_rate",
    "head_up_rate_smooth",
]


def get_history_data(request):
    """
    处理历史数据查询请求，支持精确筛选和数值范围筛选
    请求参数支持：
    - 精确筛选：frame(帧号)、persons(人数)、head_up(抬头数)、head_down(低头数)
    - 范围筛选：
      - min_persons/max_persons：人数区间
      - min_head_up/max_head_up：抬头数区间
      - min_head_down/max_head_down：低头数区间
      - min_rate/max_rate：抬头率区间（对应head_up_rate）
      - min_rate_smooth/max_rate_smooth：平滑抬头率区间（对应head_up_rate_smooth）
    返回格式：{
        "code": 200,
        "message": "success",
        "data": {
            "columns": ["frame", "persons", "head_up", "head_down", "head_up_rate", "head_up_rate_smooth"],
            "rows": [记录列表...]
        }
    }
    """

    try:
        # 读取数据
        data_file = DATA_FILE
        df = pd.read_csv(
            data_file,
            header=None,
            names=DATA_COLUMNS,
            dtype=str,  # 先以字符串读取，后续按需转换为数值
        )

        # 1. 类型转换：将需要数值计算的字段转为float（避免字符串比较错误）
        numeric_fields = [
            "persons",
            "head_up",
            "head_down",
            "head_up_rate",
            "head_up_rate_smooth",
        ]
        for field in numeric_fields:
            df[field] = pd.to_numeric(df[field], errors="coerce")

        # 2. 精确筛选：支持所有字段的精确匹配（如frame=1）
        frame = request.GET.get("frame")
        if frame:
            df = df[df["frame"] == frame]

        # 3. 范围筛选：
        min_persons = request.GET.get("min_persons")
        max_persons = request.GET.get("max_persons")
        if min_persons:
            try:
                df = df[df["persons"] >= float(min_persons)]
            except ValueError:
                return JsonResponse(
                    {
                        "code": 400,
                        "message": "min_persons格式错误，需为数值",
                        "data": None,
                    }
                )
        if max_persons:
            try:
                df = df[df["persons"] <= float(max_persons)]
            except ValueError:
                return JsonResponse(
                    {
                        "code": 400,
                        "message": "max_persons格式错误，需为数值",
                        "data": None,
                    }
                )

        # 4. 范围筛选：抬头率（对应原需求的rate）
        min_rate = request.GET.get("min_rate")
        max_rate = request.GET.get("max_rate")
        if min_rate:
            try:
                df = df[df["head_up_rate"] >= float(min_rate)]
            except ValueError:
                return JsonResponse(
                    {"code": 400, "message": "min_rate格式错误，需为数值", "data": None}
                )
        if max_rate:
            try:
                df = df[df["head_up_rate"] <= float(max_rate)]
            except ValueError:
                return JsonResponse(
                    {"code": 400, "message": "max_rate格式错误，需为数值", "data": None}
                )

        # 5. 扩展范围筛选：其他数值字段（可选）
        min_head_up = request.GET.get("min_head_up")
        max_head_up = request.GET.get("max_head_up")
        if min_head_up:
            df = df[df["head_up"] >= float(min_head_up)]
        if max_head_up:
            df = df[df["head_up"] <= float(max_head_up)]

        min_head_down = request.GET.get("min_head_down")
        max_head_down = request.GET.get("max_head_down")
        if min_head_down:
            df = df[df["head_down"] >= float(min_head_down)]
        if max_head_down:
            df = df[df["head_down"] <= float(max_head_down)]

        min_rate_smooth = request.GET.get("min_rate_smooth")
        max_rate_smooth = request.GET.get("max_rate_smooth")
        if min_rate_smooth:
            df = df[df["head_up_rate_smooth"] >= float(min_rate_smooth)]
        if max_rate_smooth:
            df = df[df["head_up_rate_smooth"] <= float(max_rate_smooth)]

        # 过滤掉转换失败的NaN值
        df = df.dropna()
        # 格式
        # df['rate'] = df['rate'].astype(str) + '%'
        # df['date'] = df['date'].astype(str)  # 核心调整：日期对象转为字符串
        result_data = df.to_dict("records")
        # 构建返回结果
        result = {
            "code": 200,
            "message": "success",
            "data": {
                "columns": result_data,
                "total": len(df),  # 增加总记录数，方便前端分页
            },
        }
        return JsonResponse(result)

    except FileNotFoundError:
        return JsonResponse({"code": 404, "message": "数据文件不存在", "data": None})
    except Exception as e:
        return JsonResponse(
            {"code": 500, "message": f"服务器错误：{str(e)}", "data": None}
        )


def logout(request):
    request.session.flush()
    return redirect("/login/")
