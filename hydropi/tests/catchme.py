"""Test catchme decorator on methods."""

from hydropi.process.errors import catchme


class TestCatch:
    """Test catchme decorator on instance method."""

    x = 5

    @catchme
    def test(self):
        """Do something."""
        print(self.x + 1)
        raise ValueError("Killing myself now!")


if __name__ == '__main__':
    TestCatch().test()
    print("Now I'm continuing with my life!")
