from sim_server.cli import main


def test_main_returns_zero():
    assert main([]) == 0
