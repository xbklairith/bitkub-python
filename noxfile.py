import nox


# An example nox task definition that runs on many supported Python versions:
@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "pypy3"])
def test(session):
    session.install(".")
    session.install("-rdev-requirements.txt")

    session.run("pytest", "tests/")
