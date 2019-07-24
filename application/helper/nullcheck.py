# from logger import set_up_logging
# logger = set_up_logging()

from flask import current_app as app

from application.common.constants import SupportedDBType, ExecutionStatus


def qry_generator(columns, target_table):
    '''
    :param columns: columns (1 or more)
    :param target_table: table name
    :return: gives a custom query based for null check based on params.
    '''
    sub_query = ""
    for each_col in columns:
        if sub_query == "":
            sub_query = "SELECT * FROM {0} WHERE ".format(
                target_table) + each_col + " is NULL"
        else:
            sub_query = sub_query + " or " + each_col + " is NULL"
    return sub_query


def null_check(target_cursor, target_table, column, test_queries, db_type):
    """

    Args:
        target_cursor: target cursor
        target_table: table name of the case
        column: columns associated with case
        test_queries: queries associated with the case
        db_type: db_type of the case

    Returns: Runs the Null check on the particular case.

    """
    try:
        print("35", target_cursor, target_table, column, test_queries, db_type)
        col_list = []
        newlst = []
        if db_type == SupportedDBType().get_db_id_by_name('oracle'):
            target_cursor.execute("SELECT column_name FROM "
                                  "user_tab_cols"
                                  " WHERE table_name=UPPER('{0}')".format(
                target_table))
        else:
            print("else")
            target_cursor.execute(
                "SELECT COLUMN_NAME FROM "
                "information_schema.COLUMNS"
                " WHERE table_name='{0}'".format(target_table))

        for col in target_cursor:
            for each_col in col:
                col_list.append(each_col)
        if (test_queries == {} or test_queries['targetqry'].isspace()
                or test_queries['targetqry'] == ""):
            flag = True
            if column == []:
                sub_query = qry_generator(col_list, target_table)
                target_cursor.execute(sub_query)
            else:
                sub_query = qry_generator(column, target_table)
                target_cursor.execute(sub_query)
        else:
            flag = True
            if "select * from" in (test_queries["targetqry"].lower()):
                print("* qry exists")
                target_query = test_queries["targetqry"]
                newlst.append(target_query)
                target_cursor.execute(newlst[0])
            else:
                flag = False
                print("custom qry for cols.")
                qry = (test_queries["targetqry"]).lower()
                start = "select"
                end = "from"
                columns = qry[
                          qry.index(start) + len(start):
                          qry.index(end)]
                if "," in columns:
                    col_list_custom = columns.split(",")
                else:
                    col_list_custom = []
                    col_list_custom.append(columns)
                print(col_list_custom)
                target_query = test_queries["targetqry"]
                newlst.append(target_query)
                target_cursor.execute(newlst[0])

        all_results = []
        for row in target_cursor:
            all_results.append(list(map(str, row)))

        if all_results:
            if flag == True:
                all_results.insert(0, col_list)
            elif flag == False:
                all_results.insert(0, col_list_custom)

            return ({"res": ExecutionStatus().get_execution_status_id_by_name(
                'fail'),
                "Execution_log": {"src_log": None,
                                  "dest_log": all_results[:10]}})
        else:
            print("109")
            return {"res": ExecutionStatus().get_execution_status_id_by_name(
                'pass'), "Execution_log": None}

    except Exception as e:
        app.logger.debug(e)
        return {"res": ExecutionStatus().get_execution_status_id_by_name(
            'error'), "Execution_log": {"error_log": e}}
