from normalize import normalizeUrl

def test_normalizeUrl():
    # identity
    assert normalizeUrl("https://youtu.be/kvjQEyKkPaA") == "https://youtu.be/kvjQEyKkPaA"
    assert normalizeUrl("https://www.youtube.com/watch?v=kvjQEyKkPaA") == "https://www.youtube.com/watch?v=kvjQEyKkPaA"

    # strip query
    assert normalizeUrl("https://www.youtube.com/watch?v=kvjQEyKkPaA&list=RDkvjQEyKkPaA&start_radio=1") == "https://www.youtube.com/watch?v=kvjQEyKkPaA"

    # handle bogus video
    assert normalizeUrl("https://www.youtube.com/watch?v=") == "https://www.youtube.com/watch"