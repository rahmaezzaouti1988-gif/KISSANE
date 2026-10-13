from core.engine import run

def test_run():
    result = run()
    assert result["count"] == 3
