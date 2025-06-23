from text_editor.document.document_factory import DocumentFactory

def test_factory_creates_document():
    factory = DocumentFactory()
    doc = factory.create_document("hello")
    assert doc.content == "hello"

def test_factory_creates_empty_document():
    factory = DocumentFactory()
    doc = factory.create_document()
    assert doc.content == ""

def test_factory_creates_multiple_documents():
    factory = DocumentFactory()
    doc1 = factory.create_document("first")
    doc2 = factory.create_document("second")
    assert doc1.content == "first"
    assert doc2.content == "second"

def test_factory_documents_are_independent():
    factory = DocumentFactory()
    doc1 = factory.create_document("first")
    doc2 = factory.create_document("second")
    doc1.content = "changed"
    assert doc2.content == "second"

def test_factory_with_long_content():
    factory = DocumentFactory()
    long_content = "This is a very long text content that should be handled properly by the factory"
    doc = factory.create_document(long_content)
    assert doc.content == long_content

def test_factory_with_special_characters():
    factory = DocumentFactory()
    special_content = "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
    doc = factory.create_document(special_content)
    assert doc.content == special_content

def test_factory_unsupported_filetype():
    factory = DocumentFactory()
    try:
        factory.create_document("text", ".unsupported")
        assert False, "ValueError was not raised for unsupported file type"
    except ValueError as e:
        assert "Unsupported file type" in str(e) 