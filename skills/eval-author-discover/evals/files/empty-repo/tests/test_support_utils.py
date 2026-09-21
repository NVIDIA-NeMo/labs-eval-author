# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for text normalization; no agent is invoked."""

import unittest

from support_utils import normalize_subject


class NormalizeSubjectTests(unittest.TestCase):
    def test_trims_whitespace_and_lowercases(self):
        self.assertEqual(normalize_subject("  Refund   QUESTION  "), "refund question")

    def test_empty_subject(self):
        self.assertEqual(normalize_subject("   "), "")


if __name__ == "__main__":
    unittest.main()
