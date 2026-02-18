from backend.voice.medical_vocabulary import MedicalVocabulary


def test_medical_vocabulary_replacement():
    vocab = MedicalVocabulary()

    # Test basic replacements
    assert vocab.post_process("I have ammonia") == "I have pneumonia"
    assert (
        vocab.post_process("patient has plural effusion")
        == "patient has pleural effusion"
    )

    # Test case insensitivity (simple check based on implementation)
    # The implementation is currently case-sensitive for keys but input usually lowercase from STT
    # Let's test the implemented behavior
    assert vocab.post_process("ammonia") == "pneumonia"

    # Test no change
    assert vocab.post_process("healthy patient") == "healthy patient"

    # Test empty
    assert vocab.post_process("") == ""
    assert vocab.post_process(None) == ""


def test_custom_corrections():
    custom = {"foo": "bar"}
    vocab = MedicalVocabulary(corrections=custom)
    assert vocab.post_process("this is foo") == "this is bar"
    assert (
        vocab.post_process("ammonia") == "ammonia"
    )  # Default not used if custom provided
