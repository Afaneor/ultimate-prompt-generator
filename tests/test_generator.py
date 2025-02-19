from upg.core.generator import PromptGenerator


def test_extract_variables():
    """Test variable extraction from prompt"""
    prompt = 'Test with {var1} and {var2} and {var1}'
    variables = PromptGenerator.extract_variables(prompt)
    assert variables == {'var1', 'var2'}


def test_remove_empty_tags():
    """Test removal of empty XML tags"""
    text = """Test
<tag></tag>
<another>  </another>
text"""
    cleaned = PromptGenerator.remove_empty_tags(text)
    assert cleaned == 'Test\ntext'


def test_strip_last_sentence():
    """Test stripping of last sentence"""
    text = 'First sentence. Second sentence. Let me know if you.'
    stripped = PromptGenerator.strip_last_sentence(text)
    assert stripped == 'First sentence. Second sentence.'


def test_find_free_floating_variables():
    """Test detection of free-floating variables"""
    prompt = """
    This is a {$VAR1} test.
    <tag>{$VAR2}</tag>
    Another {$VAR3} test.
    """

    generator = PromptGenerator(None)
    floating_vars = generator.find_free_floating_variables(prompt)

    assert '{$VAR1}' in floating_vars
    assert '{$VAR3}' in floating_vars
    assert '{$VAR2}' not in floating_vars
