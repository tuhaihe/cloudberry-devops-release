#!/usr/bin/env perl
# --------------------------------------------------------------------
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed
# with this work for additional information regarding copyright
# ownership.  The ASF licenses this file to You under the Apache
# License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License.  You may obtain a copy of the
# License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.
#
# --------------------------------------------------------------------
#
# Script: parse_results.pl
# Description: Processes Cloudberry test output to extract statistics
# and results.
#             Analyzes test log files to determine:
#             1. Overall test status (pass/fail)
#             2. Total number of tests run
#             3. Number of passed and failed tests
#             4. Names of failed tests
#             Results are written to a file for shell script processing.
#
# Arguments:
#   log-file    Path to test log file (required)
#
# Input File Format:
#   Expects test log files containing either:
#   - "All X tests passed."
#   - "Y of X tests failed."
#   And failed test entries in format:
#   - "test_name ... FAILED"
#
# Output File (test_results.txt):
#   Environment variable format:
#   STATUS=passed|failed
#   TOTAL_TESTS=<number>
#   FAILED_TESTS=<number>
#   PASSED_TESTS=<number>
#   FAILED_TEST_NAMES=<comma-separated-list>
#
# Prerequisites:
#   - Read access to input log file
#   - Write access to current directory
#   - Perl 5.x or higher
#
# Exit Codes:
#   0 - All tests passed
#   1 - Some tests failed (expected failure)
#   2 - Parse error or cannot access files
#
# Example Usage:
#   ./parse_results.pl test_output.log
#
# Error Handling:
#   - Validates input file existence and readability
#   - Verifies failed test count matches found failures
#   - Reports parsing errors with detailed messages
#
# --------------------------------------------------------------------

use strict;
use warnings;

# Exit codes
use constant {
    SUCCESS => 0,
    TEST_FAILURE => 1,
    PARSE_ERROR => 2
};

# Get log file path from command line argument
my $file = $ARGV[0] or die "Usage: $0 LOG_FILE\n";
print "Parsing test results from: $file\n";

# Check if file exists and is readable
unless (-e $file) {
    print "Error: File does not exist: $file\n";
    exit PARSE_ERROR;
}
unless (-r $file) {
    print "Error: File is not readable: $file\n";
    exit PARSE_ERROR;
}

# Open and parse the log file
open(my $fh, '<', $file) or do {
    print "Cannot open log file: $! (looking in $file)\n";
    exit PARSE_ERROR;
};

my ($status, $total_tests, $failed_tests, $passed_tests);
my @failed_test_list = ();

while (<$fh>) {
    # Match the summary lines
    if (/All (\d+) tests passed\./) {
        $status = 'passed';
        $total_tests = $1;
        $failed_tests = 0;
        $passed_tests = $1;
    }
    elsif (/(\d+) of (\d+) tests failed\./) {
        $status = 'failed';
        $failed_tests = $1;
        $total_tests = $2;
        $passed_tests = $2 - $1;
    }

    # Capture failed tests
    if (/^(?:\s+|test\s+)(\S+)\s+\.\.\.\s+FAILED\s+/) {
        push @failed_test_list, $1;
    }
}
close($fh);

unless (defined $status) {
    print "Error: Could not find test summary in $file\n";
    exit PARSE_ERROR;
}

# Validate failed test count matches found test names
if ($status eq 'failed' && scalar(@failed_test_list) != $failed_tests) {
    print "Error: Found $failed_tests failed tests in summary but found " . scalar(@failed_test_list) . " failed test names\n";
    print "Failed test names found:\n";
    foreach my $test (@failed_test_list) {
        print "  - $test\n";
    }
    exit PARSE_ERROR;
}

# Write results to file
open(my $out, '>', 'test_results.txt') or do {
    print "Cannot write results: $!\n";
    exit PARSE_ERROR;
};

print $out "STATUS=$status\n";
print $out "TOTAL_TESTS=$total_tests\n";
print $out "FAILED_TESTS=$failed_tests\n";
print $out "PASSED_TESTS=$passed_tests\n";
if (@failed_test_list) {
    print $out "FAILED_TEST_NAMES=" . join(",", @failed_test_list) . "\n";
}
close($out);

# Print to stdout for logging
print "Test Results:\n";
print "Status: $status\n";
print "Total Tests: $total_tests\n";
print "Failed Tests: $failed_tests\n";
print "Passed Tests: $passed_tests\n";
if (@failed_test_list) {
    print "Failed Test Names:\n";
    foreach my $test (@failed_test_list) {
        print "  - $test\n";
    }
}

# Exit with appropriate code
if ($status eq 'passed') {
    exit SUCCESS;
} elsif ($status eq 'failed') {
    exit TEST_FAILURE;
} else {
    exit PARSE_ERROR;
}
