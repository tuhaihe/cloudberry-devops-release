Name:           cloudberry-db
Version:        %{version}
Release:        %{release}%{?dist}
Summary:        High-performance, open-source data warehouse based on PostgreSQL/Greenplum

License:        ASL 2.0
URL:            https://cloudberrydb.org
Source0:        cloudberry-binary.tar.gz

# Disable debugsource files
%define _debugsource_template %{nil}

# Define the installation prefix
%define cloudberry_prefix /usr/local

# List runtime dependencies
%if 0%{?rhel} == 8
Requires:       /bin/sh
Requires:       apr
Requires:       audit-libs
Requires:       brotli
Requires:       bzip2-libs
Requires:       cyrus-sasl-lib
Requires:       glibc
Requires:       iproute
Requires:       iputils
Requires:       keyutils-libs
Requires:       krb5-libs
Requires:       libcap-ng
Requires:       libcom_err
Requires:       libcurl
Requires:       libevent
Requires:       libgcc
Requires:       libidn2
Requires:       libnghttp2
Requires:       libpsl
Requires:       libselinux
Requires:       libssh
Requires:       libstdc++
Requires:       libunistring
Requires:       libuuid
Requires:       libuv
Requires:       libxcrypt
Requires:       libxml2
Requires:       libyaml
Requires:       libzstd
Requires:       lz4-libs
Requires:       ncurses-libs
Requires:       openldap
Requires:       openssh
Requires:       openssh-clients
Requires:       openssh-server
Requires:       openssl-libs
Requires:       pam
Requires:       pcre2
Requires:       perl
Requires:       perl-libs
Requires:       python3
Requires:       python3-libs
Requires:       readline
Requires:       rsync
Requires:       xz-libs
Requires:       zlib
%endif

%if 0%{?rhel} == 9
Requires:       /bin/sh
Requires:       apr
Requires:       audit-libs
Requires:       bzip2-libs
Requires:       cyrus-sasl-lib
Requires:       glibc
Requires:       iproute
Requires:       iputils
Requires:       keyutils-libs
Requires:       krb5-libs
Requires:       libbrotli
Requires:       libcap-ng
Requires:       libcom_err
Requires:       libcurl
Requires:       libeconf
Requires:       libevent
Requires:       libgcc
Requires:       libidn2
Requires:       libnghttp2
Requires:       libpsl
Requires:       libselinux
Requires:       libssh
Requires:       libstdc++
Requires:       libunistring
Requires:       libuuid
Requires:       libuv
Requires:       libxcrypt
Requires:       libxml2
Requires:       libyaml
Requires:       libzstd
Requires:       lz4-libs
Requires:       ncurses-libs
Requires:       openldap
Requires:       openssh
Requires:       openssh-clients
Requires:       openssh-server
Requires:       openssl-libs
Requires:       pam
Requires:       pcre2
Requires:       perl-libs
Requires:       python3-libs
Requires:       readline
Requires:       rsync
Requires:       xz-libs
Requires:       zlib
%endif

%description
Cloudberry Database is an advanced, open-source, and highly parallel
data warehouse developed from PostgreSQL and Greenplum. It offers
powerful analytical capabilities and enhanced security features,
making it suitable for complex data processing and analytics.

Key Features:
- Parallel query execution for optimized performance
- Integration with various ETL and BI tools
- Compatibility with multiple data sources and formats

Cloudberry Database is ideal for use cases requiring both batch
processing and real-time data warehousing.

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

%postun
if [ $1 -eq 0 ] ; then
  if [ "$(readlink -f "%{cloudberry_prefix}/cloudberry")" == "%{cloudberry_prefix}/cloudberry-%{version}" ]; then
    unlink "%{cloudberry_prefix}/cloudberry" || true
  fi
fi

%changelog
* Thu Aug 20 2024 Ed Espino  eespino@gmail.com - 1.5.4-1
- Initial package with binary files under Apache 2.0 License
