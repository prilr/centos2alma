# Copyright 1999 - 2023. Plesk International GmbH. All rights reserved.
from .action import ActiveAction

import os
import pwd
import shutil

from common import util, log, leapp_configs


# We should do rebundling of ruby applications after the conversion
# because some of our libraries will be missing.
# The prime example of missing library - libmysqlclient.so.18 required by mysql2 gem
class RebundleRubyApplications(ActiveAction):
    def __init__(self):
        self.name = "rebundling ruby applications"
        self.description = "rebundling ruby applications"

    def _find_file_in_domain(self, domain, file):
        for root, _, files in os.walk(domain):
            for subfile in files:
                if os.path.basename(subfile) == file:
                    return os.path.join(root, file)
        return None

    def _find_directory_in_domain(self, domain, directory):
        for root, directories, _ in os.walk(domain):
            for subdir in directories:
                if os.path.basename(subdir) == directory:
                    return os.path.join(root, directory)
        return None

    def _is_ruby_domain(self, domain_path):
        return os.path.exists(os.path.join(domain_path, ".rbenv"))

    def _is_required(self):
        if not os.path.exists("/var/lib/rbenv/versions/"):
            return False

        return any(self._is_ruby_domain(domain) for domain in os.scandir("/var/www/vhosts"))

    def _prepare_action(self):
        pass

    def _post_action(self):
        ruby_domains = (domain_path for domain_path in os.scandir("/var/www/vhosts") if self._is_ruby_domain(domain_path))
        for domain_path in ruby_domains:
            log.debug("Rebundling ruby application in domain: {}".format(domain_path.name))

            boundle = self._find_directory_in_domain(domain_path, "bundle")
            if boundle is None or not os.path.isdir(boundle):
                log.debug("Skip reboundling for non boundled domain '{}'".format(domain_path.name))
                continue

            app_directory = os.path.dirname(os.path.dirname(boundle))
            stat_info = os.stat(boundle)
            username = pwd.getpwuid(stat_info.st_uid).pw_name

            log.debug("Boundle: {}. App directory: {}. Username: {}".format(boundle, app_directory, username))

            shutil.rmtree(boundle)
            util.logged_check_call(["plesk", "sbin", "rubymng", "run-bundler", username, app_directory])

    def _revert_action(self):
        pass

    def estimate_post_time(self):
        return 60 * len([domain_path for domain_path in os.scandir("/var/www/vhosts") if self._is_ruby_domain(domain_path)])


class FixupImunify(ActiveAction):
    def __init__(self):
        self.name = "fixing up imunify360"

    def _is_required(self):
        return os.path.exists("/etc/yum.repos.d/imunify360.repo")

    def _prepare_action(self):
        repofiles = []
        for file in os.scandir("/etc/yum.repos.d"):
            if file.name.startswith("imunify") and file.name[-5:] == ".repo":
                repofiles.append(file.path)

        leapp_configs.add_repositories_mapping(repofiles)

        # For some reason leapp replace the libssh2 packageon installation. It's fine in most cases,
        # but imunify packages require libssh2. So we should use PRESENT action to keep it.
        leapp_configs.set_package_action("libssh2", leapp_configs.LeappActionType.PRESENT)

    def _post_action(self):
        pass

    def _revert_action(self):
        pass


class AdoptKolabRepositories(ActiveAction):
    def __init__(self):
        self.name = "adopting kolab repositories"

    def _is_required(self):
        for file in os.scandir("/etc/yum.repos.d"):
            if file.name.startswith("kolab") and file.name[-5:] == ".repo":
                return True

        return False

    def _prepare_action(self):
        repofiles = []

        for file in os.scandir("/etc/yum.repos.d"):
            if file.name.startswith("kolab") and file.name[-5:] == ".repo":
                repofiles.append(file.path)

        leapp_configs.add_repositories_mapping(repofiles, ignore=["kolab-16-source",
                                                                  "kolab-16-testing-source",
                                                                  "kolab-16-testing-candidate-source"])

    def _post_action(self):
        for file in os.scandir("/etc/yum.repos.d"):
            if not file.name.startswith("kolab") or file.name[-5:] != ".repo":
                continue

            leapp_configs.adopt_repositories(file.path)

        util.logged_check_call(["dnf", "-y", "update"])

    def _revert_action(self):
        pass

    def estimate_prepare_time(self):
        return 30

    def estimate_post_time(self):
        return 2 * 60