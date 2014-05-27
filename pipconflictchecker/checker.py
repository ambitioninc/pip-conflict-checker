import pip
from pkg_resources import parse_version


class Conflict(object):
    """
    Class that contains information about a dependency conflict
    """
    def __init__(self, project_name, required_project_name, comparison, expected_version, installed_version):
        super(Conflict, self).__init__()
        self.project_name = project_name
        self.required_project_name = required_project_name
        self.comparison = comparison
        self.expected_version = expected_version
        self.installed_version = installed_version


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

        # Gets aroung pep8 complaining about unused import
        assert parse_version

        # Find any requirement conflicts
        conflicts = []
        for project_name, requirements in requirement_versions.items():
            # If this requirement is not in the installed versions, just continue
            if project_name not in installed_versions:
                continue

            # Get the installed version
            installed_version = installed_versions[project_name]
            for required_project_name, specs in requirements.items():
                for spec in specs:
                    comparison = spec[0]
                    version = spec[1]
                    comparison_string = 'parse_version(installed_version) {0} parse_version(version)'.format(
                        comparison,
                    )

                    # Evaluate that the installed version passes the comparison of the required version
                    if not eval(comparison_string):
                        conflicts.append(Conflict(**{
                            'project_name': project_name,
                            'required_project_name': required_project_name,
                            'comparison': comparison,
                            'expected_version': version,
                            'installed_version': installed_version,
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
                '{required_project_name}({comparison}{expected_version})'
            )
            print(''.join(output_string).format(
                **conflict.__dict__
            ))
        return 1
    return 0
