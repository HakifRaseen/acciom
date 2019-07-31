from application.helper.runnerclass import run_by_case_id
from application.model.models import TestSuite


def run_by_suite_id(current_user, suite_id, is_external=False):
    """
    Method will run suite by Id

    Args:
        current_user(Object): user object
        suite_id(int): suite_id of the suite.

    Returns: Runs each job in the test suite

    """
    test_suite = TestSuite.query.filter_by(
        test_suite_id=suite_id).first()
    for each_test in test_suite.test_case:
        run_by_case_id(each_test.test_case_id, current_user, is_external)
    return True
