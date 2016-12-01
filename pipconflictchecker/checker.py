from __future__ import absolute_import
from __future__ import unicode_literals
import pip
from pkg_resources import parse_version


class Conflict(object):
    """
    Class that contains information about a dependency conflict
    """
    def __init__(self, project_name, required_project_name, installed_version, specs):
        super(Conflict, self).__init__()
        self.project_name = project_name
        self.required_project_name = required_project_name
        self.installed_version = installed_version
        self.specs = specs
        self.readable_specs = self.create_readable_specs()

    def create_readable_specs(self):
        readable_specs = []
        for spec in self.specs:
            readable_specs.append('{0}{1}'.format(
                spec[0],
                spec[1]
            ))
        return ','.join(readable_specs)


class Validator(object):
    def __init__(self, installed_version, required_version_specs):
        super(Validator, self).__init__()
        self.installed_version = installed_version
        self.required_version_specs = sorted(required_version_specs, key=lambda spec: parse_version(spec[1]))

    def is_valid(self):
        """
        Checks that the installed version is valid within the required versions
        """
        # Init is valid to false
        is_valid = False

        # Get the booleans of all the checks
        in_ranges = self.in_ranges()
        in_exacts = self.in_exacts()
        in_excludes = self.in_excludes()

        # Determine if this is a valid installed version
        if (in_ranges or in_exacts) and not in_excludes:
            is_valid = True

        return is_valid

    def in_ranges(self):
        """
        Determine if the installed version is in one of the required ranges
        """
        # Get the ranges
        ranges = self.get_required_version_ranges()

        # If there are no ranges return true
        if not len(ranges):
            return True

        # Set the default to false
        in_ranges = False

        # Keep a list of the results for determining if a version is within a range
        results = []

        # Loop over the ranges and determine if the installed version is in this range
        for spec_range in ranges:
            spec_results = []
            for spec in spec_range:
                if spec is not None:
                    conditional = 'parse_version(self.installed_version) {0} parse_version(spec[1])'.format(
                        spec[0]
                    )
                    spec_results.append(eval(conditional))

            # If any spec was false the overall range is false
            if False in spec_results:
                results.append(False)
            else:
                results.append(True)

        # If the installed version is within any of the ranges, the overall result is true
        if True in results:
            in_ranges = True

        # Return the result
        return in_ranges

    def in_exacts(self):
        """
        Determine if the installed version matches one of the exact versions
        """
        # Set the default response to false
        in_exacts = False

        # Loop over the specs and check for an exact match
        exacts = self.get_required_version_exacts()
        for spec in exacts:
            if spec[1] == self.installed_version:
                in_exacts = True

        # Return the response
        return in_exacts

    def in_excludes(self):
        """
        Determine if the installed version matches one of the excluded versions
        """
        # Set the default response to false
        in_excludes = False

        # Check installed version against the excluded versions
        excludes = self.get_required_version_excludes()
        for spec in excludes:
            if spec[1] == self.installed_version:
                in_excludes = True

        # Return the response
        return in_excludes

    def get_required_version_ranges(self):
        """
        Determines the ranges that a version has to exist within
        """
        # List of all allowed ranges
        ranges = []

        # Keep track of the minimum required spec
        min_spec = None

        # Keep track of the maximum required spec
        max_spec = None

        # Loop over all the required specs and calculate the ranges
        for spec in self.required_version_specs:
            comparison = spec[0]

            # Check if this should be the max
            if comparison in ['<=', '<']:
                max_spec = spec

            # Check if this should be the min value
            elif comparison in ['>=', '>']:
                min_spec = spec

            # Check if we have both a min and a max spec if so push it onto the ranges and reset
            if min_spec and max_spec:
                ranges.append((min_spec, max_spec))
                min_spec = None
                max_spec = None

        # Add the last range if we need to
        if min_spec or max_spec:
            ranges.append((min_spec, max_spec))

        # Return the ranges
        return ranges

    def get_required_version_exacts(self):
        """
        Returns a list of versions that must be exact
        """
        # List of exact versions
        exacts = []

        # Loop over all the required specs get the exacts
        for spec in self.required_version_specs:
            comparison = spec[0]

            # Check if the comparison is exact
            if comparison == '==':
                exacts.append(spec)

        # Return the exact versions
        return exacts

    def get_required_version_excludes(self):
        """
        Returns a list of versions that we need to exclude
        """
        # List of excluded versions
        excluded = []

        # Loop over all the required specs get the exacts
        for spec in self.required_version_specs:
            comparison = spec[0]

            # Check if the comparison is exact
            if comparison == '!=':
                excluded.append(spec)

        # Return the excluded version specs
        return excluded


class Checker(object):
    """
    Class that contains all the checker methods that find dependency conflicts
    """
    def get_requirement_versions(self):
        """
        Returns a dictionary of project_name => dict of projects that requires it with lists of requirements
        """
        distributions = pip.get_installed_distributions()
        dist_requirements = {}

        # Compute the dist requirements and versions
        for dist in distributions:
            dist_requirement_dict = dist_requirements.get(dist.project_name, {})
            dist_requirements[dist.project_name] = dist_requirement_dict
            for requirement in dist.requires():
                dist_requirement_dict = dist_requirements.get(requirement.project_name, {})
                dist_requirement_list = dist_requirement_dict.get(dist.project_name, set())
                for spec in requirement.specs:
                    dist_requirement_list.add(spec)
                dist_requirement_dict[dist.project_name] = dist_requirement_list
                dist_requirements[requirement.project_name] = dist_requirement_dict

        # Return the dict
        return dist_requirements

    def get_installed_versions(self):
        """
        Returns a dict of project_name => version installed
        """
        distributions = pip.get_installed_distributions()
        dist_versions = {}

        # Build the installed versions dict
        for dist in distributions:
            dist_versions[dist.project_name] = dist.version

        # Return the dict
        return dist_versions

    def get_conflicts(self):
        """
        Checks the requirements against the installed projects to find any version conflicts
        """
        requirement_versions = self.get_requirement_versions()
        installed_versions = self.get_installed_versions()

        # Gets around pep8 complaining about unused import
        assert parse_version

        # Find any requirement conflicts
        conflicts = []
        for project_name, requirements in requirement_versions.items():
            # If this requirement is not in the installed versions, just continue
            if project_name not in installed_versions:
                continue

            # Get the installed version
            installed_version = installed_versions[project_name]

            # Loop over the required dictionaries and determine if we have any dependency conflicts
            for required_project_name, specs in requirements.items():
                # Create a validator
                validator = Validator(installed_version=installed_version, required_version_specs=specs)
                if not validator.is_valid():
                    conflicts.append(Conflict(**{
                        'project_name': project_name,
                        'required_project_name': required_project_name,
                        'installed_version': installed_version,
                        'specs': specs
                    }))

        # Return the conflicts
        return conflicts


# Main entry point for console script
def main():
    checker = Checker()
    conflicts = checker.get_conflicts()
    if conflicts:
        print('-' * 50)
        print(' Conflicts Detected')
        print('-' * 50)
        for conflict in conflicts:
            output_string = (
                ' - ',
                '{project_name}({installed_version}) ',
                '{required_project_name}({readable_specs})'
            )
            print(''.join(output_string).format(
                **conflict.__dict__
            ))
        return 1
    return 0
