def test_starting_simple_http_node_is_successful(simple_http_node, caplog):

    simple_http_node.start()

    simple_http_node.listener.start.assert_called_once_with()

    assert simple_http_node.machine_started is True

    assert "Starting Machine and services" in caplog.text
    assert "Machine has been started" in caplog.text
    assert "Service has been started" in caplog.text
    assert "Machine already started. Nothing to do" not in caplog.text


def test_starting_simple_http_node_when_already_started_does_nothing(
    simple_http_node, caplog
):

    simple_http_node.machine_started = True
    simple_http_node.start()

    simple_http_node.listener.start.assert_not_called()

    assert "Starting Machine and services" in caplog.text
    assert "Machine has been started" not in caplog.text
    assert "Service has been started" not in caplog.text
    assert "Machine already started. Nothing to do" in caplog.text


def test_stopping_simple_http_node_is_successful(simple_http_node, caplog):

    simple_http_node.machine_started = True
    simple_http_node.stop()

    simple_http_node.listener.stop.assert_called_once_with()

    assert simple_http_node.machine_started is False

    assert "Stopping services and machine" in caplog.text
    assert "Service stopped" in caplog.text
    assert "Machine stopped" in caplog.text
    assert "Machine already stopped. Nothing to do" not in caplog.text


def test_stopping_simple_http_node_when_already_stopped_does_nothing(
    simple_http_node, caplog
):

    simple_http_node.machine_started = False
    simple_http_node.stop()

    simple_http_node.listener.stop.assert_not_called()

    assert "Stopping services and machine" in caplog.text
    assert "Service stopped" not in caplog.text
    assert "Machine stopped" not in caplog.text
    assert "Machine already stopped. Nothing to do" in caplog.text
