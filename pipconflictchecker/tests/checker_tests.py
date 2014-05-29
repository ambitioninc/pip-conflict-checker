from mock import patch, Mock
from pip._vendor.pkg_resources import Distribution, Requirement
from unittest import TestCase
from pipconflictchecker.checker import Checker, main, Validator


class ValidatorTest(TestCase):
    def test_init(self):
        installed_version = '1.0'
        specs = [
            ('<=', '2.0'),
            ('>=', '1.0')
        ]
        validator = Validator(installed_version, specs)

        # Assert that the properties were set
        self.assertTrue(validator.installed_version, installed_version)
        self.assertTrue(validator.required_version_specs, specs)

        # Assert that the required version specs were sorted properly
        self.assertTrue(validator.required_version_specs[0], specs[1])
        self.assertTrue(validator.required_version_specs[1], specs[0])

    def test_ranges_no_max(self):
        installed_version = '1.0'
        specs = [
            ('>=', '1.0')
        ]
        validator = Validator(installed_version, specs)
        ranges = validator.get_required_version_ranges()

        # Validate there is only one range
        self.assertEqual(len(ranges), 1)

        # Validate that there is no max spec
        self.assertIsNone(ranges[0][1])

    def test_ranges_no_min(self):
        installed_version = '0.1'
        specs = [
            ('<=', '1.0')
        ]
        validator = Validator(installed_version, specs)
        ranges = validator.get_required_version_ranges()

        # Validate there is only one range
        self.assertEqual(len(ranges), 1)

        # Validate that there is no max spec
        self.assertIsNone(ranges[0][0])

    def test_ranges_multiple_min(self):
        installed_version = '0.1'
        specs = [
            ('<=', '1.0'),
            ('<=', '2.0'),
        ]
        validator = Validator(installed_version, specs)
        ranges = validator.get_required_version_ranges()

        # Validate there is only one range
        self.assertEqual(len(ranges), 1)

        # Validate that there is no max spec
        self.assertIsNone(ranges[0][0])

    def test_ranges_min_and_max(self):
        installed_version = '1.0'
        specs = [
            ('<=', '2.0'),
            ('>=', '1.0')
        ]
        validator = Validator(installed_version, specs)
        ranges = validator.get_required_version_ranges()

        # Validate there is only one range
        self.assertEqual(len(ranges), 1)

        # Validate that the min and max are correct
        self.assertEqual(ranges[0][0], specs[1])
        self.assertEqual(ranges[0][1], specs[0])

    def test_ranges_multiple_no_max(self):
        installed_version = '1.0'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
            ('>=', '3.0'),
        ]
        validator = Validator(installed_version, specs)
        ranges = validator.get_required_version_ranges()

        # Validate the number of ranges
        self.assertEqual(len(ranges), 2)

    def test_exacts(self):
        installed_version = '1.0'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
            ('>=', '3.0'),
            ('==', '2.5'),
        ]
        validator = Validator(installed_version, specs)
        exacts = validator.get_required_version_exacts()

        # Validate the number of exacts
        self.assertEqual(len(exacts), 1)

    def test_excludes(self):
        installed_version = '1.0'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
            ('>=', '3.0'),
            ('!=', '3.5'),
        ]
        validator = Validator(installed_version, specs)
        excludes = validator.get_required_version_excludes()

        # Validate the number of exacts
        self.assertEqual(len(excludes), 1)

    def test_in_ranges_no_ranges(self):
        installed_version = '2.0'
        specs = [
        ]
        validator = Validator(installed_version, specs)

        # Validate we are in the range
        self.assertTrue(validator.in_ranges())

    def test_in_ranges_true_no_max_non_edge(self):
        installed_version = '2.0'
        specs = [
            ('>=', '1.0'),
        ]
        validator = Validator(installed_version, specs)

        # Validate we are in the range
        self.assertTrue(validator.in_ranges())

    def test_in_ranges_false_no_max_non_edge(self):
        installed_version = '0.9'
        specs = [
            ('>=', '1.0'),
        ]
        validator = Validator(installed_version, specs)

        # Validate we are not in the range
        self.assertFalse(validator.in_ranges())

    def test_in_ranges_true_no_max_edge(self):
        installed_version = '1.0'
        specs = [
            ('>=', '1.0'),
        ]
        validator = Validator(installed_version, specs)

        # Validate we are in the range
        self.assertTrue(validator.in_ranges())

    def test_in_ranges_false_no_max_edge(self):
        installed_version = '1.0'
        specs = [
            ('>', '1.0'),
        ]
        validator = Validator(installed_version, specs)

        # Validate we are not in the range
        self.assertFalse(validator.in_ranges())

    def test_in_ranges_true_min_and_max_non_edge(self):
        installed_version = '1.5'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
        ]
        validator = Validator(installed_version, specs)

        # Validate we are in the range
        self.assertTrue(validator.in_ranges())

    def test_in_ranges_false_min_and_max_non_edge(self):
        installed_version = '3.0'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
        ]
        validator = Validator(installed_version, specs)

        # Validate we are not in the range
        self.assertFalse(validator.in_ranges())

    def test_in_ranges_true_min_and_max_edge(self):
        installed_version = '2.0'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
        ]
        validator = Validator(installed_version, specs)

        # Validate we are in the range
        self.assertTrue(validator.in_ranges())

    def test_in_ranges_false_min_and_max_edge(self):
        installed_version = '2.0'
        specs = [
            ('>=', '1.0'),
            ('<', '2.0'),
        ]
        validator = Validator(installed_version, specs)

        # Validate we are not in the range
        self.assertFalse(validator.in_ranges())

    def test_in_exacts_true(self):
        installed_version = '1.0'
        specs = [
            ('==', '1.0'),
        ]
        validator = Validator(installed_version, specs)
        self.assertTrue(validator.in_exacts())

    def test_in_exacts_false(self):
        installed_version = '2.0'
        specs = [
            ('==', '1.0'),
        ]
        validator = Validator(installed_version, specs)
        self.assertFalse(validator.in_exacts())

    def test_in_excludes_true(self):
        installed_version = '1.1'
        specs = [
            ('>=', '1.0'),
            ('!=', '1.1'),
        ]
        validator = Validator(installed_version, specs)
        self.assertTrue(validator.in_excludes())

    def test_in_excludes_false(self):
        installed_version = '1.2'
        specs = [
            ('>=', '1.0'),
            ('!=', '1.1'),
        ]
        validator = Validator(installed_version, specs)
        self.assertFalse(validator.in_excludes())

    def test_is_valid_true_one_range(self):
        installed_version = '2.0'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
        ]
        validator = Validator(installed_version, specs)
        self.assertTrue(validator.is_valid())

    def test_is_valid_false_one_range(self):
        installed_version = '3.0'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
        ]
        validator = Validator(installed_version, specs)
        self.assertFalse(validator.is_valid())

    def test_is_valid_true_multi_range(self):
        installed_version = '2.0'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
            ('>=', '3.0'),
            ('<=', '4.0'),
        ]
        validator = Validator(installed_version, specs)
        self.assertTrue(validator.is_valid())

    def test_is_valid_false_multi_range(self):
        installed_version = '2.1'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
            ('>=', '3.0'),
            ('<=', '4.0'),
        ]
        validator = Validator(installed_version, specs)
        self.assertFalse(validator.is_valid())

    def test_is_valid_true_in_exacts_not_in_ranges(self):
        installed_version = '3.0'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
            ('==', '3.0'),
        ]
        validator = Validator(installed_version, specs)
        self.assertTrue(validator.is_valid())

    def test_is_valid_false_in_excludes_in_ranges(self):
        installed_version = '1.5'
        specs = [
            ('>=', '1.0'),
            ('<=', '2.0'),
            ('!=', '1.5'),
        ]
        validator = Validator(installed_version, specs)
        self.assertFalse(validator.is_valid())


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
