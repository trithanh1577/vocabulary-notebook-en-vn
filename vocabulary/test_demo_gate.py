from django.test import SimpleTestCase


class DemoGateTests(SimpleTestCase):
    """Intentional failure kept only on the demo/red-check branch."""

    def test_ci_blocks_a_failing_pull_request(self):
        self.fail("Intentional demo failure: this pull request must not be merged.")
