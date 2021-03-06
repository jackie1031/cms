#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2012 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2012 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2012 Matteo Boscariol <boscarim@hotmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from cms.grading.ScoreType import ScoreTypeAlone


# Dummy function to mark translatable string.
def N_(message):
    return message


class Sum(ScoreTypeAlone):
    """The score of a submission is the sum of the outcomes,
    multiplied by the integer parameter.

    """
    # Mark strings for localization.
    N_("Outcome")
    N_("Details")
    N_("Execution time")
    N_("Memory used")
    N_("N/A")
    TEMPLATE = """\
{% from cms.grading import format_status_text %}
{% from cms.server import format_size %}
{% from cms.locale import locale_format %}
<table class="testcase-list">
    <thead>
        <tr>
            <th class="idx">{{ _("#") }}</th>
            <th class="outcome">{{ _("Outcome") }}</th>
            <th class="details">{{ _("Details") }}</th>
            <th class="execution-time">{{ _("Execution time") }}</th>
            <th class="memory-used">{{ _("Memory used") }}</th>
        </tr>
    </thead>
    <tbody>
    {% for idx, tc in enumerate(details, start=1) %}
        {% if "outcome" in tc and "text" in tc %}
            {% if tc["outcome"] == "Correct" %}
        <tr class="correct">
            {% elif tc["outcome"] == "Not correct" %}
        <tr class="notcorrect">
            {% else %}
        <tr class="partiallycorrect">
            {% end %}
            <td class="idx">{{ idx }}</td>
            <td class="outcome">{{ _(tc["outcome"]) }}</td>
            <td class="details">{{ format_status_text(tc["text"], _) }}</td>
            <td class="execution-time">
            {% if tc["time"] is not None %}
                {{ locale_format(_, _("{seconds:0.3f} s"), seconds=tc["time"]) }}
            {% else %}
                {{ _("N/A") }}
            {% end %}
            </td>
            <td class="memory-used">
            {% if tc["memory"] is not None %}
                {{ format_size(tc["memory"], _) }}
            {% else %}
                {{ _("N/A") }}
            {% end %}
            </td>
        {% else %}
        <tr class="undefined">
            <td colspan="4">
                {{ _("N/A") }}
            </td>
        </tr>
        {% end %}
    {% end %}
    </tbody>
</table>"""

    def max_scores(self):
        """See ScoreType.max_score."""
        public_score = 0.0
        score = 0.0
        for public in self.public_testcases.itervalues():
            if public:
                public_score += self.parameters
            score += self.parameters
        return score, public_score, []

    def compute_score(self, submission_result):
        """See ScoreType.compute_score."""
        # Actually, this means it didn't even compile!
        if not submission_result.evaluated():
            return 0.0, "[]", 0.0, "[]", []

        # XXX Lexicographical order by codename
        indices = sorted(self.public_testcases.keys())
        evaluations = dict((ev.codename, ev)
                           for ev in submission_result.evaluations)
        testcases = []
        public_testcases = []
        score = 0.0
        public_score = 0.0

        for idx in indices:
            this_score = float(evaluations[idx].outcome) * self.parameters
            tc_outcome = self.get_public_outcome(this_score)
            score += this_score
            testcases.append({
                "idx": idx,
                "outcome": tc_outcome,
                "text": evaluations[idx].text,
                "time": evaluations[idx].execution_time,
                "memory": evaluations[idx].execution_memory,
                })
            if self.public_testcases[idx]:
                public_score += this_score
                public_testcases.append(testcases[-1])
            else:
                public_testcases.append({"idx": idx})

        return score, json.dumps(testcases), \
            public_score, json.dumps(public_testcases), \
            []

    def get_public_outcome(self, outcome):
        """Return a public outcome from an outcome.

        outcome (float): the outcome of the submission.

        return (float): the public output.

        """
        if outcome <= 0.0:
            return N_("Not correct")
        elif outcome >= self.parameters:
            return N_("Correct")
        else:
            return N_("Partially correct")
