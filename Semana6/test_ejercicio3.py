from Ejercicio3 import global_variable

def test_global_variable_prints_20(capsys):
    global_variable()
    captured = capsys.readouterr()
    assert captured.out.strip() == "20"

def test_global_variable_multiple_calls(capsys):
    global_variable()
    global_variable()
    captured = capsys.readouterr()
    assert captured.out.strip() == "20\n20"

def test_global_variable_no_call(capsys):
    captured = capsys.readouterr()
    assert captured.out.strip() == ""