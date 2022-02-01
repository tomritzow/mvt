# Mobile Verification Toolkit (MVT)
# Copyright (c) 2021-2022 The MVT Project Authors.
# Use of this software is governed by the MVT License 1.1 that can be found at
#   https://license.mvt.re/1.1/

import logging

from mvt.android.modules.adb.dumpsys_activities import DumpsysActivities

from .base import BugReportModule

log = logging.getLogger(__name__)


class Activities(BugReportModule):
    """This module extracts details on receivers for risky activities."""

    def __init__(self, file_path=None, base_folder=None, output_folder=None,
                 serial=None, fast_mode=False, log=None, results=[]):
        super().__init__(file_path=file_path, base_folder=base_folder,
                         output_folder=output_folder, fast_mode=fast_mode,
                         log=log, results=results)

        self.results = results if results else {}

    def check_indicators(self):
        if not self.indicators:
            return

        for intent, activities in self.results.items():
            for activity in activities:
                ioc = self.indicators.check_app_id(activity["package_name"])
                if ioc:
                    activity["matched_indicator"] = ioc
                    self.detected.append({intent: activity})
                    continue

    def run(self):
        dumpstate_files = self._get_files_by_pattern("dumpstate-*")
        if not dumpstate_files:
            return

        content = self._get_file_content(dumpstate_files[0])
        if not content:
            return

        in_activities = False
        lines = []
        for line in content.decode().split("\n"):
            if line.strip() == "DUMP OF SERVICE package:":
                in_activities = True
                continue

            if not in_activities:
                continue

            if line.strip() == "------------------------------------------------------------------------------":
                break

            lines.append(line)

        self.results = DumpsysActivities.parse_activity_resolver_table("\n".join(lines))
