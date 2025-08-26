#!/usr/bin/env perl
use strict;
use warnings;
local $/;  # slurp
my $s = <>;

# Emails
$s =~ s/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/[redacted-email]/g;

# Common password/credential patterns
$s =~ s/(?:password|passwd)\s*[:=]\s*\S+/[redacted-password]/ig;
$s =~ s/(authentication\s*[:=]\s*)(\S.*?)(\s*\/\s*)(\S+)/$1\[redacted-user\]$3\[redacted-password\]/ig;

# App-passwords like "xxxx xxxx xxxx xxxx"
$s =~ s/\b([a-z]{4}\s){3}[a-z]{4}\b/[redacted-app-password]/ig;

# OAuth Client IDs/Secrets
$s =~ s/(client[_\s-]*id\s*[:=]\s*)(\S+)/$1[redacted-client-id]/ig;
$s =~ s/(client[_\s-]*secret\s*[:=]\s*)(\S+)/$1[redacted-client-secret]/ig;

# Tokens
$s =~ s/(access[_\s-]*token\s*[:=]\s*)(["']?).*?\2/$1$2[redacted-access-token]$2/ig;
$s =~ s/(refresh[_\s-]*token\s*[:=]\s*)(["']?).*?\2/$1$2[redacted-refresh-token]$2/ig;

print $s;
