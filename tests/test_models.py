from osint_tool.models import Finding, Status


def test_found_property():
    f = Finding(source="X", query="q", status=Status.FOUND)
    assert f.found is True

    f = Finding(source="X", query="q", status=Status.NOT_FOUND)
    assert f.found is False


def test_to_dict_roundtrip_shape():
    f = Finding(source="X", query="q", status=Status.FOUND, url="https://example.com", detail="d")
    d = f.to_dict()
    assert d["source"] == "X"
    assert d["status"] == "found"
    assert d["url"] == "https://example.com"
