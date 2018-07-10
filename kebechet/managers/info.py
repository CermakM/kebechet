#!/usr/bin/env python3
# Kebechet
# Copyright(C) 2018 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Report information about repository and Kebechet itself."""

import logging
from tempfile import TemporaryDirectory
import typing

import git
from kebechet.source_management import close_issue_if_exists
from kebechet.source_management import get_issue
from kebechet.utils import cwd

from .manager import Manager
from .messages import INFO_REPORT

_INFO_ISSUE_NAME = 'Kebechet info'

_LOGGER = logging.getLogger(__name__)


class InfoManager(Manager):
    """Manager for submitting information about running Kebechet instance."""

    def run(self, slug: str, labels: list) -> typing.Optional[dict]:
        """Check for info issue and close it with a report."""
        issue = get_issue(slug, _INFO_ISSUE_NAME)
        if not issue:
            _LOGGER.info("No issue to report to, exiting")
            return

        _LOGGER.info(f"Found issue {_INFO_ISSUE_NAME}, generating report")
        with TemporaryDirectory() as repo_path, cwd(repo_path):
            # TODO: we should abstract this into the base Manager class once we introduce more managers.
            repo_url = f'git@github.com:{slug}.git'
            _LOGGER.info(f"Cloning repository {repo_url} to {repo_path}")
            repo = git.Repo.clone_from(repo_url, repo_path, branch='master', depth=1)

            # We could optimize this as the get_issue() does API calls as well. Keep it this simple now.
            close_issue_if_exists(
                slug,
                _INFO_ISSUE_NAME,
                INFO_REPORT.format(
                    sha=repo.head.commit.hexsha,
                    slug=slug,
                    environment_details=self.get_environment_details(),
                    dependency_graph=self.get_dependency_graph(graceful=True),
                )
            )
