# VariableQuery/utils.py
import pymysql
def sql_server(db_type, db_host, db_port, db_name, db_username, db_password, sql_query):
    """
    执行数据库服务
    :param db_type:数据库类型
    :param db_host:数据库地址
    :param db_port:数据库端口
    :param db_name:数据库名称
    :param db_username:数据库用户
    :param db_password:数据库密码
    :param sql_query:数据库语句
    :return: {status， message， data}
    """
    if db_type == 'mysql':
        return mysql_query(db_host, db_port, db_name, db_username, db_password, sql_query)
    else:
        return {"status": "error", "message": f"不支持的数据库类型：{str(db_type)}"}


def mysql_query(db_host, db_port, db_name, db_username, db_password, sql_query):
    """
    执行mysql语句
    :param db_host:数据库地址
    :param db_port:数据库端口
    :param db_name:数据库名称
    :param db_username:数据库用户
    :param db_password:数据库密码
    :param sql_query:数据库语句
    :return: {status， message, data}
    """
    connection = None
    try:
        connection = pymysql.connect(host=db_host, port=db_port, db=db_name, user=db_username, password=db_password, charset='utf8mb4', cursorclass=pymysql.cursors.Cursor)
        with connection.cursor() as cursor:
            if sql_query.strip().upper().startswith('SELECT'):
                cursor.execute(sql_query)
                data = cursor.fetchall()[0][0]
                result = {"status": "success", "message": "mysql数据查询成功", "data": str(data)}
            else:
                result = {"status": "error", "message": f"mysql数据查询失败：仅支持SELECT语句"}
    except Exception as e:
        result = {"status": "error", "message": f"mysql数据查询失败：{str(e)}"}
    finally:
        if connection is not None and connection.open:
            connection.close()
    return result