from numdoclint import helper


def test_read_file_str():
    file_str = helper.read_file_str('./tests/test_helper.py')
    assert isinstance(file_str, str)
    assert file_str != ''
    assert 'def' in file_str


def test_get_func_name_list():
    py_module_str = helper.read_file_str(
        file_path='./tests/test_helper.py')
    func_name_list = helper.get_func_name_list(
        py_module_str=py_module_str)
    assert 'test_read_file_str' in func_name_list
    assert 'test_get_func_name_list' in func_name_list
