import json
import logging
import os

import pandas as pd
from django.http import JsonResponse
from django.shortcuts import redirect, render

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIN_FILE = os.path.join(BASE_DIR, "login.txt")
DATA_FILE = os.path.join(BASE_DIR, "mydata.csv")
logger = logging.getLogger("attendance")


def register(request):
    """
    用户注册接口

    处理用户注册请求，仅支持 POST 方法。接收用户名和密码参数，
    验证参数完整性后检查用户是否已存在，不存在则写入存储文件完成注册。
    全程记录关键操作日志，便于问题追踪。

    Args:
        request (django.http.HttpRequest): Django 请求对象
            - 需通过 POST 方法传递参数：
              * username (str): 注册用户名（必填）
              * password (str): 注册密码（必填）

    Returns:
        django.http.JsonResponse: 标准化 JSON 响应
            - 成功响应：
              {
                  "code": 200,
                  "message": "注册成功"
              }
            - 失败响应（示例）：
              {
                  "code": 400,
                  "message": "用户名已存在"  # 具体信息随错误类型变化
              }

    关键逻辑说明：
        1. 方法校验：仅允许 POST 请求，其他方法返回 405 错误
        2. 参数校验：检查 username 和 password 是否为空，为空则返回 400 错误
        3. 查重逻辑：读取用户存储文件，遍历检查用户名是否已存在
        4. 写入逻辑：新用户信息以 "用户名,密码" 格式追加到存储文件
        5. 异常处理：捕获文件操作相关异常（如文件不存在），返回 500 错误

    日志记录：
        - INFO 级别：记录收到请求、注册成功等正常流程
        - WARNING 级别：记录参数为空、用户名已存在等客户端问题
        - ERROR/EXCEPTION 级别：记录文件不存在、读写失败等服务端异常
    """
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            logger.info(f"收到注册请求: 用户名={username}")
            # 验证用户名和密码不为空
            if not username or not password:
                logger.warning(f"注册失败: 用户名或密码为空，请求数据={request.POST}")
                return JsonResponse(
                    {"status": "error", "message": "用户名和密码不能为空"}
                )

            # 检查文件中是否已存在该用户
            existing_user = None
            try:
                with open(LOGIN_FILE) as f:
                    # 读取已有用户信息（假设一行一个用户，格式：用户名,密码）
                    for line in f:
                        line = line.strip()
                        if line:
                            user, _ = line.split(",", 1)
                            if user.strip() == username:
                                existing_user = user
                                break
            except FileNotFoundError:
                # 文件不存在表示还没有注册用户，无需处理
                pass
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "message": f"检查用户信息失败: {str(e)}"}
                )

            # 如果用户已存在，返回错误
            if existing_user:
                logger.warning(f"注册失败: 用户名 {username} 已存在")
                return JsonResponse({"status": "error", "message": "用户名已存在"})

            # 将新用户信息写入文件（追加模式）
            with open(LOGIN_FILE, "a") as f:
                f.write(f"{username},{password}\n")

            # 注册成功，可选择直接登录或让用户手动登录
            request.session["is_login"] = True
            request.session["username"] = username

            logger.info(f"注册成功: 用户名={username}")
            return JsonResponse({"status": "success", "message": "注册成功"})

        except json.JSONDecodeError as e:
            logger.exception(f"注册过程发生异常: {str(e)}")
            return JsonResponse({"status": "error", "message": "请求数据格式错误"})

        except Exception as e:
            logger.exception(f"注册过程发生异常: {str(e)}")
            return JsonResponse({"status": "error", "message": f"注册失败: {str(e)}"})

    # GET请求返回注册页面
    return render(request, "register.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # 读取正确的账号密码
        try:
            with open(LOGIN_FILE) as f:
                # 初始化变量存储验证结果
                is_valid = False
                for line in f:
                    line = line.strip()
                    # 跳过空行
                    if not line:
                        continue
                    # 分割用户名和密码
                    parts = line.split(",")
                    # 确保格式正确（包含逗号且分割后有两个部分）
                    if len(parts) == 2:
                        correct_user = parts[0].strip()
                        correct_pass = parts[1].strip()
                        # 找到匹配的用户时验证密码
                        if correct_user == username:
                            is_valid = correct_pass == password
                            break  # 找到目标用户后停止遍历

            if is_valid:
                pass
            else:
                pass
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"读取登录信息失败: {str(e)}"}
            )
        if username == correct_user and password == correct_pass:
            # 登录成功，设置会话
            request.session["is_login"] = True
            request.session["username"] = username
            return JsonResponse({"status": "success", "message": "登录成功"})
        else:
            return JsonResponse({"status": "error", "message": "账号或密码错误"})

    return render(request, "login.html")


def history_data(request):
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
        # 读取CSV数据（确保文件路径正确）
        data_file = DATA_FILE
        df = pd.read_csv(
            data_file,
            header=None,
            names=[
                "frame",
                "persons",
                "head_up",
                "head_down",
                "head_up_rate",
                "head_up_rate_smooth",
            ],
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
            df[field] = pd.to_numeric(
                df[field], errors="coerce"
            )  # 转换失败的设为NaN（后续会被过滤）

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
    # 清除会话
    request.session.flush()
    return redirect("/login/")
