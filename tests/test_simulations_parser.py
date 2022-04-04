import unittest
from rigelcore.simulations.parser import SimulationRequirementsVisitor


class SimulationRequirementsVisitorTesting(unittest.TestCase):
    """
    Test suite for rigelcore.simulations.parser.SimulationRequirementsVisitor class.
    """

    def test_initial_data_structure(self) -> None:
        """
        Test if initial values are as expected.
        """
        visitor = SimulationRequirementsVisitor()
        self.assertEqual(visitor.pattern, 0)
        self.assertEqual(visitor.requirement, {})
        self.assertEqual(visitor.requirements, [])


if __name__ == '__main__':
    unittest.main()
