Name:           cloudberry-db
Version:        %{version}
Release:        %{release}%{?dist}
Summary:        High-performance, open-source data warehouse based on PostgreSQL/Greenplum

License:        ASL 2.0
URL:            https://cloudberrydb.org
Vendor:         Cloudberry Open Source
Group:          Applications/Databases
Source0:        cloudberry-binary.tar.gz

# Disabled as we are shipping GO programs (e.g. gpbackup)
%define _missing_build_ids_terminate_build 0

# Disable debugsource files
%define _debugsource_template %{nil}

# Define the installation prefix
%define cloudberry_prefix /usr/local

# List runtime dependencies

Requires:       bash
Requires:       iproute
Requires:       iputils
Requires:       openssh
Requires:       openssh-clients
Requires:       openssh-server
Requires:       rsync

%if 0%{?rhel} == 8
Requires:       apr
Requires:       audit
Requires:       bzip2
Requires:       keyutils
Requires:       libcurl
Requires:       libevent
Requires:       libidn2
Requires:       libselinux
Requires:       libstdc++
Requires:       libuuid
Requires:       libuv
Requires:       libxml2
Requires:       libyaml
Requires:       libzstd
Requires:       lz4
Requires:       openldap
Requires:       pam
Requires:       perl
Requires:       python3
Requires:       readline
%endif

%if 0%{?rhel} == 9
Requires:       apr
Requires:       bzip2
Requires:       glibc
Requires:       keyutils
Requires:       libcap
Requires:       libcurl
Requires:       libidn2
Requires:       libpsl
Requires:       libssh
Requires:       libstdc++
Requires:       libxml2
Requires:       libyaml
Requires:       libzstd
Requires:       lz4
Requires:       openldap
Requires:       pam
Requires:       pcre2
Requires:       readline
Requires:       xz
%endif

%description

Cloudberry Database is an advanced, open-source, massively parallel
processing (MPP) data warehouse developed from PostgreSQL and
Greenplum. It is designed for high-performance analytics on
large-scale data sets, offering powerful analytical capabilities and
enhanced security features.

Key Features:

- Massively parallel processing for optimized performance
- Advanced analytics for complex data processing
- Integration with ETL and BI tools
- Compatibility with multiple data sources and formats
- Enhanced security features

Cloudberry Database supports both batch processing and real-time data
warehousing, making it a versatile solution for modern data
environments.

For more information, visit the official Cloudberry Database website
at https://cloudberrydb.org.

%prep
%setup -q -c -T
# Ensure the target directory exists
mkdir -p %{buildroot}%{cloudberry_prefix}
# Unpack the source tarball into the target directory
tar xzf %{SOURCE0} -C %{buildroot}%{cloudberry_prefix}

%build
# Normally you'd run your build system here (e.g., make), but we're using the pre-built binary.

%install
rm -rf %{buildroot}

# Create the versioned directory
mkdir -p %{buildroot}%{cloudberry_prefix}/cloudberry-%{version}

# Unpack the tarball
tar xzf %{SOURCE0} -C %{buildroot}%{cloudberry_prefix}/cloudberry-%{version}

# Move the contents of the cloudberry directory up one level
mv %{buildroot}%{cloudberry_prefix}/cloudberry-%{version}/cloudberry/* %{buildroot}%{cloudberry_prefix}/cloudberry-%{version}/

# Remove the now-empty cloudberry directory
rmdir %{buildroot}%{cloudberry_prefix}/cloudberry-%{version}/cloudberry

# Create the symbolic link
ln -sfn %{cloudberry_prefix}/cloudberry-%{version} %{buildroot}%{cloudberry_prefix}/cloudberry

%files
%{cloudberry_prefix}/cloudberry-%{version}
%{cloudberry_prefix}/cloudberry

%license %{cloudberry_prefix}/cloudberry-%{version}/LICENSE

%post
# Change ownership to gpadmin.gpadmin if the gpadmin user exists
if id "gpadmin" &>/dev/null; then
    chown -R gpadmin:gpadmin %{cloudberry_prefix}/cloudberry-%{version}
fi

%postun
if [ $1 -eq 0 ] ; then
  if [ "$(readlink -f "%{cloudberry_prefix}/cloudberry")" == "%{cloudberry_prefix}/cloudberry-%{version}" ]; then
    unlink "%{cloudberry_prefix}/cloudberry" || true
  fi
fi
