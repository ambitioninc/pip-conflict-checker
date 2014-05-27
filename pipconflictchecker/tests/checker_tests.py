from mock import patch, Mock
from pip._vendor.pkg_resources import Distribution, Requirement
from unittest import TestCase
from pipconflictchecker.checker import Checker, main


class CheckerTest(TestCase):
    """
    Tests the checker functionality
    """
    expected_distributions = [
        'coverage',
        'pep8',
        'nose',
        'mock',
        'pyflakes'
    ]

    def test_get_requirement_versions(self):
        checker = Checker()
        distributions = checker.get_requirement_versions()
        for dist in self.expected_distributions:
            self.assertIn(dist, distributions)

    @patch('pipconflictchecker.checker.pip.get_installed_distributions')
    def test_get_requirement_versions_with_requirements(self, mock_get_installed_dists):
        # Create some fake requirements
        mock_req = Mock(Requirement)
        mock_req.return_value.specs = [('>=', '1.0')]
        mock_req.return_value.project_name = 'req'

        # Create some fake distributions
        mock_dist = Mock(Distribution)
        mock_dist.return_value.requires.return_value = [
            mock_req(),
            mock_req()
        ]
        mock_dist.return_value.project_name = 'test'
        mock_get_installed_dists.return_value = [
            mock_dist(),
            mock_dist()
        ]

        checker = Checker()
        distributions = checker.get_requirement_versions()

        # Assert that the main dist has no requirements
        self.assertFalse(len(distributions['test']))

        # Assert that the req dist has requirements
        self.assertTrue(len(distributions['req']))

    def test_get_installed_versions(self):
        checker = Checker()
        distributions = checker.get_installed_versions()
        for dist in self.expected_distributions:
            self.assertIn(dist, distributions)

    @patch('pipconflictchecker.checker.Checker.get_requirement_versions')
    @patch('pipconflictchecker.checker.Checker.get_installed_versions')
    def test_get_conflicts_no_conflicts(self, mock_installed, mock_requirement):
        # Create some fake installed versions
        mock_installed.return_value = {
            'one': '1.0',
            'two': '2.0',
            'three': '3.0'
        }

        # Create some fake requirements
        mock_requirement.return_value = {
            'one': {
                'three': [('>=', '1.0')]
            },
            'two': {
                'three': [('>=', '2.0')]
            }
        }

        checker = Checker()
        conflicts = checker.get_conflicts()
        self.assertFalse(len(conflicts))

    @patch('pipconflictchecker.checker.Checker.get_requirement_versions')
    @patch('pipconflictchecker.checker.Checker.get_installed_versions')
    def test_get_conflicts_with_greater_than_conflicts(self, mock_installed, mock_requirement):
        # Create some fake installed versions
        mock_installed.return_value = {
            'one': '1.0',
            'two': '2.0',
            'three': '3.0'
        }

        # Create some fake requirements
        mock_requirement.return_value = {
            'one': {
                'three': [('>=', '2.0')]
            },
            'two': {
                'three': [('>=', '3.0')]
            }
        }

        # Create the checker and get the conflicts
        checker = Checker()
        conflicts = checker.get_conflicts()

        # Assert we found the conflicts
        self.assertEqual(len(conflicts), 2)

    @patch('pipconflictchecker.checker.Checker.get_requirement_versions')
    @patch('pipconflictchecker.checker.Checker.get_installed_versions')
    def test_get_conflicts_with_less_than_conflicts(self, mock_installed, mock_requirement):
        # Create some fake installed versions
        mock_installed.return_value = {
            'one': '1.0',
            'two': '2.0',
            'three': '3.0'
        }

        # Create some fake requirements
        mock_requirement.return_value = {
            'one': {
                'three': [('<=', '0.9')]
            },
            'two': {
                'three': [('<=', '1.9')]
            }
        }

        # Create the checker and get the conflicts
        checker = Checker()
        conflicts = checker.get_conflicts()

        # Assert we found the conflicts
        self.assertEqual(len(conflicts), 2)

    @patch('pipconflictchecker.checker.Checker.get_requirement_versions')
    @patch('pipconflictchecker.checker.Checker.get_installed_versions')
    def test_get_conflicts_with_not_equal_to_conflicts(self, mock_installed, mock_requirement):
        # Create some fake installed versions
        mock_installed.return_value = {
            'one': '1.0',
            'two': '2.0',
            'three': '3.0'
        }

        # Create some fake requirements
        mock_requirement.return_value = {
            'one': {
                'three': [('!=', '1.0')]
            },
            'two': {
                'three': [('!=', '2.0')]
            }
        }

        # Create the checker and get the conflicts
        checker = Checker()
        conflicts = checker.get_conflicts()

        # Assert we found the conflicts
        self.assertEqual(len(conflicts), 2)

    @patch('pipconflictchecker.checker.Checker.get_requirement_versions')
    @patch('pipconflictchecker.checker.Checker.get_installed_versions')
    def test_get_conflicts_with_req_not_in_installed(self, mock_installed, mock_requirement):
        # Create some fake installed versions
        mock_installed.return_value = {
            'one': '1.0',
            'two': '2.0',
            'three': '3.0'
        }

        # Create some fake requirements
        mock_requirement.return_value = {
            'four': {
                'three': ['==', '1.0']
            }
        }

        # Create the checker and get the conflicts
        checker = Checker()
        conflicts = checker.get_conflicts()

        # Assert we found the conflicts
        self.assertEqual(len(conflicts), 0)

    def test_main_no_conflicts(self):
        self.assertFalse(main())

    @patch('pipconflictchecker.checker.Checker.get_requirement_versions')
    @patch('pipconflictchecker.checker.Checker.get_installed_versions')
    def test_main_with_conflicts(self, mock_installed, mock_requirement):
        # Create some fake installed versions
        mock_installed.return_value = {
            'one': '1.0',
            'two': '2.0',
            'three': '3.0'
        }

        # Create some fake requirements
        mock_requirement.return_value = {
            'one': {
                'three': [('>=', '2.0')]
            },
            'two': {
                'three': [('>=', '3.0')]
            }
        }

        # Assert we get a proper error return code
        self.assertEqual(main(), 1)
