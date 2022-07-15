from dask_ctl.tui.graphs.taskstream import color_to_int, int_to_color


def test_color_to_int():
    assert "#FF0000" == int_to_color(color_to_int("#FF0000"))
    assert "#00FF00" == int_to_color(color_to_int("#00FF00"))
    assert "#0000FF" == int_to_color(color_to_int("#0000FF"))
    assert "#000000" == int_to_color(color_to_int("#000000"))
